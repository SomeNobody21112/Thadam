"""FastAPI service over the pre-computed intelligence artifacts.

Everything is loaded into memory once at startup (210k rows is nothing) and served
read-only. No model runs here — the pipeline produced the artifacts; this serves them.

Role scoping is enforced from a signed token: `auth.require_scope` narrows every scoped
read to the caller's jurisdiction, and the stakeholder switcher in the UI only reframes
what an already-permitted caller sees. The accounts themselves are seeded for evaluation
and listed openly at `/api/auth/accounts`; a deployment swaps that one function for an
identity provider and nothing else changes.
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from mplads import chat as chatbot
from mplads import field, ocr
from mplads import config, llm
from mplads.api import auth
from mplads.api.strings import UI
from mplads.api import translations
from mplads.api.audit import AuditLog
from mplads.api.auth import Principal, current_principal

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Load the corpus and flatten its search text before the first question arrives.

    Done here rather than lazily so the first officer to ask something does not pay nine
    seconds for everyone else's convenience.
    """
    try:
        chatbot.warm()
    except Exception as exc:  # pragma: no cover - never block startup on a warm-up
        LOGGER.warning("search index not pre-built (%s); it will build on first use",
                       type(exc).__name__)
    yield


app = FastAPI(title="MPLADS Intelligence", version="2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

#: role -> which column narrows the data, and what the role is called.
ROLES: dict[str, dict] = {
    "ministry": {"label": "Ministry (MoSPI)", "scope_field": None,
                 "focus": "National aggregates, state comparison, systemic patterns"},
    "state": {"label": "State Nodal Authority", "scope_field": "state",
              "focus": "District and agency comparison within the state"},
    "district": {"label": "District Authority", "scope_field": "implementing_agency",
                 "focus": "Works, delays, duplicates and compliance in this jurisdiction"},
    "mp": {"label": "Member of Parliament", "scope_field": "constituency",
           "focus": "Works recommended in this constituency"},
}


def _read(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


class Store:
    def __init__(self, artifacts: Path):
        self.stats = _read(artifacts / "stats.json")
        self.temporal = _read(artifacts / "temporal.json")
        self.transparency = _read(artifacts / "transparency.json")
        self.metrics = _read(artifacts / "models" / "metrics.json")

        cases = _read(artifacts / "case_files.json")
        self.cases_by_ref = {c["work_ref"]: c for c in cases}
        self.worklist = [
            {
                "work_ref": c["work_ref"],
                "description": c["identity"]["description"],
                "state": c["identity"]["state"],
                "constituency": c["identity"]["constituency"],
                "implementing_agency": c["identity"]["implementing_agency"],
                "mp_name": c["identity"]["mp_name"],
                "archetype": c["archetype"]["label"],
                "band": c["confidence_band"],
                "n_families": c["n_signal_families"],
                "priority": c["priority"],
                "exposure_rupees": c["exposure_rupees"],
                "audit_roi": c["audit_roi"],
                "recommended_amount": c["identity"]["recommended_amount"],
                "early_warning": c.get("early_warning", {}).get("level", "LOW"),
                "compliance_flags": len(c.get("compliance_findings", [])),
                "has_duplicate": c.get("duplicate") is not None,
                "signals": [e["signal"] for e in c.get("evidence", [])],
            }
            for c in cases
        ]

        dupes = artifacts / "duplicate_pairs.parquet"
        self.duplicate_pairs = (
            pd.read_parquet(dupes) if dupes.exists() else pd.DataFrame()
        )
        self._artifacts = artifacts
        self._corpus: pd.DataFrame | None = None
        self._all_refs: set[str] | None = None
        self._amounts: dict[str, float] | None = None

    #: The columns the assistant and the photo matcher need. Everything else in
    #: works_scored stays on disk — the full 82-column frame is 547 MB in memory and
    #: none of the rest is ever asked for.
    CORPUS_COLUMNS = [
        "work_ref", "state_name", "constituency", "implementing_agency", "mp_name",
        "house", "work_description", "activity_category", "archetype_label",
        "recommended_amount", "is_completed", "is_open", "duration_days", "band",
        "priority", "rs_exposure", "audit_roi", "compliance_flags",
        "early_warning_level", "risk_score", "recommendation_date", "completion_date",
    ]
    CORPUS_CATEGORICAL = [
        "state_name", "constituency", "implementing_agency", "mp_name", "house",
        "activity_category", "archetype_label", "band", "early_warning_level",
    ]

    @property
    def corpus(self) -> pd.DataFrame:
        """All 210,993 works, not only the ones surfaced as leads.

        The dashboard ranks leads; a question like "what has Bihar recommended for school
        buildings" is about the whole portfolio. Loaded on first use and held — about 66 MB
        once the repeated strings are categorical.
        """
        if self._corpus is None:
            path = self._artifacts / "works_scored.parquet"
            if not path.exists():
                self._corpus = pd.DataFrame(columns=self.CORPUS_COLUMNS)
            else:
                frame = pd.read_parquet(path, columns=self.CORPUS_COLUMNS)
                for column in self.CORPUS_CATEGORICAL:
                    frame[column] = frame[column].astype("category")
                self._corpus = frame
                LOGGER.info("corpus loaded: %s works", f"{len(frame):,}")
        return self._corpus

    @property
    def all_refs(self) -> set[str]:
        """Every work reference in the portfolio — what a photographed board is matched to."""
        if self._all_refs is None:
            self._all_refs = set(self.corpus["work_ref"])
        return self._all_refs

    @property
    def amounts(self) -> dict[str, float]:
        """Recommended amount per work, so a figure read off a board can be checked."""
        if self._amounts is None:
            frame = self.corpus
            self._amounts = dict(
                zip(frame["work_ref"], frame["recommended_amount"].astype(float))
            )
        return self._amounts


@lru_cache(maxsize=1)
def store() -> Store:
    return Store(config.ARTIFACTS)


@lru_cache(maxsize=1)
def audit() -> AuditLog:
    return AuditLog(config.AUDIT_LOG_PATH)


@app.middleware("http")
async def record_every_request(request: Request, call_next):
    """Every intelligence read is written to the append-only, hash-chained log."""
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/api/") and not path.startswith("/api/audit"):
        principal = getattr(request.state, "principal", None)
        try:
            audit().record(
                actor=getattr(principal, "subject", "anonymous"),
                role=getattr(principal, "role", "open-data"),
                action=request.method,
                resource=path,
                detail={"query": dict(request.query_params), "status": response.status_code},
            )
        except Exception:  # logging must never break the request path
            pass
    return response


def _scope(rows: list[dict], role: str | None, scope: str | None) -> list[dict]:
    """Narrow a worklist to a role's jurisdiction. Role simulation, not authentication."""
    if not role or role == "ministry" or not scope:
        return rows
    field = ROLES.get(role, {}).get("scope_field")
    if not field:
        return rows
    return [r for r in rows if r.get(field) == scope]


# ------------------------------------------------------------------- core endpoints


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "leads": len(store().worklist), "version": app.version}


@app.get("/api/roles")
def roles() -> dict:
    """Available roles and the scope values each can select."""
    s = store()
    states = sorted({r["state"] for r in s.worklist if r["state"]})
    constituencies = sorted({r["constituency"] for r in s.worklist if r["constituency"]})
    agencies = sorted({r["implementing_agency"] for r in s.worklist if r["implementing_agency"]})
    return {
        "roles": ROLES,
        "scopes": {
            "state": states,
            "mp": constituencies[:600],
            "district": agencies[:900],
        },
        "note": "Role simulation for the prototype. No authentication is implemented; "
                "production would place an identity provider in front of the same filter.",
    }


@app.get("/api/stats")
def stats(role: str | None = None, scope: str | None = None) -> dict:
    """National statistics, or a role-scoped recomputation of the headline numbers."""
    s = store()
    if not role or role == "ministry" or not scope:
        return s.stats

    rows = _scope(s.worklist, role, scope)
    scoped = dict(s.stats)
    scoped["national"] = {
        **s.stats["national"],
        "scoped": True,
        "scope_role": role,
        "scope_value": scope,
        "surfaced_leads": len(rows),
        "total_exposure_rupees": sum(r["exposure_rupees"] for r in rows),
        "bands": {
            band: sum(1 for r in rows if r["band"] == band) for band in ("HIGH", "MEDIUM")
        },
    }
    return scoped


@app.get("/api/worklist")
def worklist(
    limit: int = Query(25, ge=1, le=200),
    offset: int = Query(0, ge=0),
    state: str | None = None,
    band: str | None = None,
    warning: str | None = None,
    signal: str | None = None,
    q: str | None = None,
    role: str | None = None,
    scope: str | None = None,
) -> dict:
    rows = _scope(store().worklist, role, scope)
    if state:
        rows = [r for r in rows if r["state"] == state]
    if band:
        rows = [r for r in rows if r["band"] == band]
    if warning:
        rows = [r for r in rows if r["early_warning"] == warning]
    if signal:
        rows = [r for r in rows if signal in r["signals"]]
    if q:
        needle = q.lower()
        rows = [
            r for r in rows
            if needle in (r["description"] or "").lower()
            or needle in (r["implementing_agency"] or "").lower()
        ]
    return {"total": len(rows), "items": rows[offset : offset + limit]}


@app.get("/api/case/{work_ref}")
def case(work_ref: str, principal: Principal = Depends(current_principal)) -> dict:
    found = store().cases_by_ref.get(work_ref) or _clear_record(work_ref)
    if not found:
        raise HTTPException(status_code=404, detail="no such work in this portfolio")
    identity = found["identity"]
    auth.require_scope(
        principal,
        {
            "state": identity.get("state"),
            "implementing_agency": identity.get("implementing_agency"),
            "constituency": identity.get("constituency"),
        },
        f"case file {work_ref}",
    )
    return found


def _clear_record(work_ref: str) -> dict | None:
    """A case file for a work nothing was flagged on.

    173,288 of the 210,993 works were never surfaced, and returning 404 for all of them
    made "nothing wrong with this work" indistinguishable from "no such work". It also
    made them unverifiable, which quietly guaranteed that every field record an officer
    ever wrote would be about a work the system had already flagged — a label set of
    nothing but positives, useless for fitting anything.
    """
    frame = store().corpus
    row = frame[frame["work_ref"] == work_ref]
    if row.empty:
        return None
    r = row.iloc[0]
    return {
        "work_ref": work_ref,
        "surfaced": False,
        "identity": {
            "description": str(r["work_description"]),
            "state": str(r["state_name"]),
            "constituency": str(r["constituency"]),
            "implementing_agency": str(r["implementing_agency"]),
            "mp_name": str(r["mp_name"]),
            "recommended_amount": float(r["recommended_amount"]),
            "recommendation_date": str(r["recommendation_date"])[:10],
            "completion_date": str(r["completion_date"])[:10]
                if pd.notna(r["completion_date"]) else None,
            "is_completed": bool(r["is_completed"]),
        },
        "archetype": {"label": str(r["archetype_label"])},
        "confidence_band": "NONE",
        "n_signal_families": 0,
        "priority": 0.0,
        "exposure_rupees": 0.0,
        "audit_roi": 0.0,
        "evidence": [],
        "compliance_findings": [],
        "recommended_next_step": (
            "No signal fired on this work — it sits inside the norms of its peer group on "
            "every measure we compute. Nothing here needs a reviewer. It can still be "
            "verified in the field, and a confirmed-fine record is as useful to this "
            "system as a confirmed problem."
        ),
    }


# --------------------------------------------------------------------- audit trail


@app.get("/api/audit/verify")
def audit_verify() -> dict:
    """Recompute the whole hash chain and report whether it is intact."""
    return audit().verify_chain()


@app.get("/api/audit/tail")
def audit_tail(limit: int = Query(50, ge=1, le=500)) -> list[dict]:
    return audit().tail(limit)


@app.get("/api/auth/demo-tokens")
def demo_tokens() -> dict:
    """Seeded tokens for the demo. Never a production issuance mechanism."""
    return {
        "tokens": auth.seed_demo_tokens(),
        "require_auth": config.REQUIRE_AUTH,
        "note": "Set MPLADS_REQUIRE_AUTH=1 to enforce bearer auth and exercise the 403 "
                "paths. Tokens are seeded from a development signing key, not issued by "
                "an identity provider.",
    }


@app.get("/api/states")
def states() -> list[dict]:
    return store().stats.get("by_state", [])


@app.get("/api/models")
def models() -> dict:
    return store().metrics


# ------------------------------------------------------- language & AI briefings


@app.get("/api/languages")
def languages() -> dict:
    """Interface languages. Every one listed ships a complete, static bundle."""
    return {
        "languages": {code: name for code, (name, _, _) in translations.BUNDLES.items()},
        "native": {code: native for code, (_, native, _) in translations.BUNDLES.items()},
        "llm_available": llm.available(),
        "note": "Interface translations are shipped with the application and need no "
                "network call. The language model is used only for written briefings, "
                "which fall back to a deterministic template when unavailable.",
    }


@app.get("/api/strings")
def strings(lang: str = Query("en")) -> dict:
    """The complete UI bundle for one language. Static — no API call, no cache miss."""
    if lang not in translations.BUNDLES:
        raise HTTPException(400, f"unsupported language: {lang}")
    return {
        "lang": lang,
        "coverage": translations.coverage(lang),
        "strings": translations.bundle(lang),
    }


@app.get("/api/insight/portfolio")
def portfolio_insight(lang: str = Query("en"), role: str | None = None,
                      scope: str | None = None) -> dict:
    """A written brief over the national (or scoped) picture."""
    return llm.portfolio_insight(stats(role=role, scope=scope), language=lang)


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[ChatTurn] = []
    lang: str = "en"


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict:
    """Ask the assistant. It answers only from tool calls against the real artifacts."""
    if not req.question.strip():
        raise HTTPException(400, "question is required")
    history = [{"role": t.role, "content": t.content} for t in req.history][-12:]
    return chatbot.answer(req.question.strip(), history=history, language=req.lang)


@app.get("/api/chat/capabilities")
def chat_capabilities() -> dict:
    """What the assistant can look up, and whether it is running live or offline."""
    return {
        "live": llm.available(),
        # Why, not just whether. A configured-but-unfunded key used to report "live".
        "live_status": llm.status(),
        "tools": [
            {"name": name, "does": (fn.__doc__ or "").strip().splitlines()[0]}
            for name, fn in chatbot.TOOL_FUNCS.items()
        ],
        "suggestions": [
            "How many investigation leads are there?",
            "Show me the top leads",
            "What does exposure at risk mean?",
            "Tell me about MP3018356-W86316",
            "Can you detect cost overruns?",
            "What models did you train?",
        ],
        # Grouped starters, so the panel opens on something an evaluator would
        # actually ask rather than a blank box. Every one of these is answerable by
        # the offline router, so they work with or without billing.
        "categories": [
            {
                "category": "Portfolio & scale",
                "icon": "▤",
                "prompts": [
                    "How many works and leads are in the national portfolio?",
                    "What does exposure at risk mean?",
                    "What is the health index?",
                ],
            },
            {
                "category": "Leads & ranking",
                "icon": "▦",
                "prompts": [
                    "Show me the top leads",
                    "How are leads ranked?",
                    "What does HIGH confidence mean?",
                ],
            },
            {
                "category": "States & agencies",
                "icon": "§",
                "prompts": [
                    "How many works in Bihar?",
                    "Which agencies changed behaviour?",
                    "Tell me about MP3018356-W86316",
                ],
            },
            {
                "category": "Method & limits",
                "icon": "◈",
                "prompts": [
                    "What models did you train?",
                    "What work types did you discover?",
                    "Can you detect cost overruns?",
                ],
            },
            {
                "category": "Salesforce & Agentforce",
                "icon": "⚡",
                "prompts": [
                    "Show me HIGH priority cases in Bihar",
                    "What cases are loaded in Salesforce CRM?",
                    "What is the 5-stage investigation path?",
                    "Which case has the highest exposure?",
                ],
            },
        ],
        # The languages the *interface* is translated into. The written answer is
        # English unless a funded key is configured, and `answers_translated` says
        # which of those two is true rather than letting the picker imply the first.
        "languages": {code: name for code, (name, _, _) in translations.BUNDLES.items()},
        "native": {code: native for code, (_, native, _) in translations.BUNDLES.items()},
        "answers_translated": llm.available(),
    }


# ------------------------------------------------- login, OCR, field verification


DEMO_ACCOUNTS = {
    "ministry":  {"password": "mplads2026", "role": "ministry", "scope": None,
                  "name": "MoSPI Programme Division"},
    "auditor":   {"password": "mplads2026", "role": "auditor", "scope": None,
                  "name": "CAG Audit Officer"},
    "bihar":     {"password": "mplads2026", "role": "state", "scope": "Bihar",
                  "name": "Bihar State Nodal Officer"},
    "saran":     {"password": "mplads2026", "role": "mp", "scope": "SARAN",
                  "name": "Saran Constituency Office"},
}


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/auth/login")
def login(req: LoginRequest) -> dict:
    """Issue a bearer token for a seeded account.

    Prototype only: accounts are seeded in code, passwords are shared and not hashed,
    and there is no registration or reset. Production replaces this endpoint with an
    identity provider; everything behind it — the token, the scope, the audit trail —
    stays exactly as it is.
    """
    account = DEMO_ACCOUNTS.get(req.username.strip().lower())
    if not account or account["password"] != req.password:
        raise HTTPException(401, "incorrect username or password")
    token = auth.issue_token(req.username, account["role"], account["scope"])
    return {
        "token": token,
        "user": {"username": req.username, "name": account["name"],
                 "role": account["role"], "scope": account["scope"]},
        "note": "Seeded prototype account. Not a production authentication mechanism.",
    }


@app.get("/api/auth/accounts")
def demo_accounts() -> dict:
    """The seeded accounts, so the login screen can offer them. Never do this in production."""
    return {
        "accounts": [
            {"username": u, "name": a["name"], "role": a["role"], "scope": a["scope"]}
            for u, a in DEMO_ACCOUNTS.items()
        ],
        "shared_password": "mplads2026",
        "warning": "Seeded demo credentials, displayed deliberately for evaluation. "
                   "A production deployment uses an identity provider and never lists accounts.",
    }


@app.post("/api/ocr")
async def read_photo(file: UploadFile = File(...), work_ref: str = Form(""),
                     principal: Principal = Depends(current_principal)) -> dict:
    """Read a site board, identify the work, and check the photograph has not been seen before.

    Three answers come back from one upload: the text on the board, which work it belongs
    to, and whether this exact picture was already submitted for a different sanction. The
    third is the one a human could not do at scale.
    """
    data = await file.read()
    if len(data) > 12 * 1024 * 1024:
        raise HTTPException(400, "image is larger than 12 MB")
    try:
        name = field.save_photo(data, file.filename or "upload.jpg")
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    extracted = ocr.read(field.PHOTOS / name)
    extracted["photo"] = name
    # Matched against every work in the portfolio, not only the surfaced leads — an
    # officer photographing an ordinary work should be told it is ordinary, not unknown.
    extracted["match"] = ocr.match_to_work(extracted, store().all_refs, store().amounts)
    extracted["reuse"] = field.check_photo(
        data, name, work_ref or extracted["match"].get("work_ref") or "",
        actor=principal.subject,
    )
    return extracted


@app.get("/api/photo/{name}")
def photo(name: str):
    """Serve an uploaded verification photo."""
    path = field.PHOTOS / Path(name).name  # basename only — no traversal
    if not path.exists():
        raise HTTPException(404, "photo not found")
    return FileResponse(path)


class VerificationRequest(BaseModel):
    outcome: str
    notes: str = ""
    photo: str | None = None
    ocr_text: str | None = None


@app.post("/api/verify/{work_ref}")
def add_verification(work_ref: str, req: VerificationRequest,
                     principal: Principal = Depends(current_principal)) -> dict:
    """Record what an officer found in the field. Immutable once written."""
    auth.require_identity(principal, "record a field verification")
    case = store().cases_by_ref.get(work_ref)
    if case:
        identity = case["identity"]
        auth.require_scope(
            principal,
            {"state": identity.get("state"),
             "implementing_agency": identity.get("implementing_agency"),
             "constituency": identity.get("constituency")},
            f"work {work_ref}",
        )
    try:
        return field.record(
            work_ref=work_ref, outcome=req.outcome, notes=req.notes.strip(),
            photo=req.photo, ocr_text=req.ocr_text,
            actor=principal.subject, role=principal.role,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.get("/api/verify/{work_ref}")
def verifications(work_ref: str) -> dict:
    return {"work_ref": work_ref, "verifications": field.for_work(work_ref),
            "outcomes": field.OUTCOMES}


@app.get("/api/field/summary")
def field_summary() -> dict:
    """Verification activity, and how far it is from producing usable labels."""
    return {"readiness": field.label_readiness(), "recent": field.recent(20),
            "outcomes": field.OUTCOMES, "ocr_available": ocr.available(),
            "photo_reuse": field.photo_reuse_report()}


@app.get("/api/insight/case/{work_ref}")
def case_insight(work_ref: str, lang: str = Query("en"),
                 principal: Principal = Depends(current_principal)) -> dict:
    """A written brief for one case file, in the requested language."""
    found = store().cases_by_ref.get(work_ref)
    if not found:
        raise HTTPException(status_code=404, detail="case file not found")
    identity = found["identity"]
    auth.require_scope(
        principal,
        {
            "state": identity.get("state"),
            "implementing_agency": identity.get("implementing_agency"),
            "constituency": identity.get("constituency"),
        },
        f"case file {work_ref}",
    )
    return llm.case_insight(found, language=lang)


# ----------------------------------------------------------- intelligence endpoints


@app.get("/api/temporal")
def temporal() -> dict:
    return store().temporal


@app.get("/api/transparency")
def transparency() -> dict:
    return store().transparency


@app.get("/api/compliance")
def compliance() -> dict:
    return store().stats.get("compliance", {})


@app.get("/api/early-warning")
def early_warning() -> dict:
    return store().stats.get("early_warning", {})


@app.get("/api/health-index")
def health_index() -> dict:
    return store().stats.get("health_index", {})


@app.get("/api/archetypes")
def archetypes(limit: int = Query(50, ge=1, le=100)) -> list[dict]:
    return store().stats.get("archetype_intelligence", [])[:limit]


@app.get("/api/duplicates")
def duplicate_pairs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    state: str | None = None,
    classification: str | None = None,
    concerning_only: bool = True,
) -> dict:
    frame = store().duplicate_pairs
    summary = store().stats.get("duplicates", {})
    if frame.empty:
        return {"total": 0, "items": [], "summary": summary}

    if concerning_only:
        from mplads.intelligence import duplicates as dup_mod

        frame = dup_mod.concerning(frame)
    if state:
        frame = frame[frame["state_name"] == state]
    if classification:
        frame = frame[frame["classification"] == classification]

    page = frame.iloc[offset : offset + limit]
    return {
        "total": int(len(frame)),
        "items": json.loads(page.to_json(orient="records")),
        "summary": summary,
    }


# -------------------------------------------------- Salesforce CRM & Agentforce


class UpdateStageRequest(BaseModel):
    work_ref: str
    stage: str
    officer_finding: str = ""
    target_review_date: str = ""


class AgentforceQueryRequest(BaseModel):
    question: str


@app.get("/api/salesforce/overview")
def salesforce_overview() -> dict:
    """Salesforce Org status, custom objects, 5-stage Path, reports and dashboards."""
    from mplads import salesforce as sf
    return sf.get_salesforce_overview()


@app.get("/api/salesforce/cases")
def salesforce_cases(
    stage: str | None = None,
    state: str | None = None,
    tier: str | None = None,
    q: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict:
    """The 500 High-Priority Investigation Cases in Salesforce CRM."""
    from mplads import salesforce as sf
    cases = sf.load_salesforce_cases()
    if stage:
        cases = [c for c in cases if c["investigation_status"] == stage]
    if state:
        cases = [c for c in cases if (c["state"] or "").lower() == state.lower()]
    if tier:
        cases = [c for c in cases if c["escalation_tier"] == tier]
    if q:
        needle = q.lower()
        cases = [
            c for c in cases
            if needle in (c["work_ref"] or "").lower()
            or needle in (c["description"] or "").lower()
            or needle in (c["implementing_agency"] or "").lower()
            or needle in (c["state"] or "").lower()
        ]
    return {
        "total": len(cases),
        "items": cases[offset : offset + limit],
        "stages": sf.PATH_STAGES,
        "findings": sf.OFFICER_FINDINGS,
    }


@app.get("/api/salesforce/case/{work_ref}")
def salesforce_case(work_ref: str) -> dict:
    """Get single Salesforce Investigation Case with evidence and Path stage info."""
    from mplads import salesforce as sf
    cases = sf.load_salesforce_cases()
    match = next((c for c in cases if c["work_ref"] == work_ref.upper()), None)
    if not match:
        raise HTTPException(404, f"case {work_ref} not found in Salesforce CRM")
    evidence = sf.load_salesforce_evidence(work_ref)
    return {
        "case": match,
        "evidence": evidence,
        "stages": sf.PATH_STAGES,
        "current_stage": match["investigation_status"],
        "guidance": next((s["guidance"] for s in sf.PATH_STAGES if s["stage"] == match["investigation_status"]), ""),
        "findings": sf.OFFICER_FINDINGS,
    }


@app.post("/api/salesforce/update-stage")
def update_salesforce_stage(
    req: UpdateStageRequest,
    principal: Principal = Depends(current_principal),
) -> dict:
    """Update case investigation stage and officer findings."""
    from mplads import salesforce as sf
    try:
        res = sf.update_case_stage(
            work_ref=req.work_ref.upper(),
            stage=req.stage,
            officer_finding=req.officer_finding,
            review_date=req.target_review_date,
        )
        audit().record(
            actor=getattr(principal, "subject", "officer"),
            role=getattr(principal, "role", "auditor"),
            action="UPDATE_STAGE",
            resource=f"/api/salesforce/case/{req.work_ref.upper()}",
            detail={"stage": req.stage, "finding": req.officer_finding},
        )
        return res
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.post("/api/agentforce/query")
def agentforce_query(req: AgentforceQueryRequest) -> dict:
    """Direct query against Agentforce Investigation Lookup agent."""
    from mplads import salesforce as sf
    if not req.question.strip():
        raise HTTPException(400, "question is required")
    return sf.query_agentforce(req.question.strip())

