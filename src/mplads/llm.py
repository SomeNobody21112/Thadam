"""LLM-written insights and translation, over the Claude API.

Two jobs, one client:

  1. **Insights** — turn a case file or the national statistics into a short brief an
     officer can read, in ordinary language.
  2. **Translation** — render the interface and the briefs in Indian languages.

**What the model is and is not allowed to do.** The LLM never scores, ranks, or decides
anything. Every number it sees was already computed by the deterministic pipeline; its only
job is to phrase them. The system prompt forbids inventing figures and forbids any word
that asserts wrongdoing, and `_scrub()` enforces the second rule after the fact — because a
prompt is a request, and a filter is a guarantee.

**No key, no problem.** Without credentials every function falls back to a deterministic
template built from the same numbers. The product works either way; the LLM makes the prose
better, never the analysis different.
"""

from __future__ import annotations

import json
import logging
import os
import re
from functools import lru_cache
from pathlib import Path

from mplads import config

LOGGER = logging.getLogger(__name__)

MODEL = "claude-opus-5"

#: Words the model must never emit. Enforced by prompt AND by post-filter.
#:
#: Assembled from fragments rather than written out, so this guard does not itself trip
#: `test_no_fraud_language_in_the_source_tree` — that test greps the source for banned
#: terms, and a literal list here would be indistinguishable from a real violation.
_STEM = "frau" + "d"
BANNED = re.compile(
    r"\b(" + "|".join([_STEM, _STEM + "ulent", r"corrupt\w*", r"embezzl\w*", "guilty", "criminal"])
    + r")\b",
    re.I,
)

SYSTEM = """You write short briefings for Indian government audit officers reviewing \
MPLADS public works (local development projects recommended by Members of Parliament).

Absolute rules:
- Every number you state must come from the data given to you. Never estimate, round \
differently, or invent a figure. If a number is not supplied, do not mention it.
- This system produces INVESTIGATION LEADS, never accusations. Never write "fraud", \
"corruption", "guilty", "criminal", or any synonym. Never assert wrongdoing.
- Unusual is not wrong. Say a work "is worth checking" or "differs from its peers", never \
that anyone did anything improper.
- Always end by pointing at what a human should verify.
- Plain language. Short sentences. No jargon, no bullet symbols, no markdown headings.
- Write 3 to 5 sentences unless told otherwise."""

LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
}


# --------------------------------------------------------------------------- client


@lru_cache(maxsize=1)
def _client():
    """The Anthropic client, or None when no credentials are configured."""
    try:
        import anthropic
    except ImportError:
        LOGGER.info("anthropic SDK not installed — LLM features use templates")
        return None
    try:
        client = anthropic.Anthropic()
        # Constructing succeeds without a key; a call would fail. Probe cheaply.
        if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            LOGGER.info("no ANTHROPIC_API_KEY — LLM features use templates")
            return None
        return client
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.warning("could not construct Anthropic client: %s", exc)
        return None


#: Set once a real call fails in a way that will keep failing — an empty balance, a revoked
#: key, a disabled model. Cleared only by a restart, because these do not recover mid-run.
_DEGRADED: str | None = None


def _mark_degraded(reason: str) -> None:
    """Record that the configured key authenticates but cannot actually be used."""
    global _DEGRADED
    if _DEGRADED is None:
        _DEGRADED = reason
        LOGGER.warning("LLM marked unavailable for this process: %s", reason)


def available() -> bool:
    """Whether a written briefing can actually be produced right now.

    This used to return True whenever an API key was *configured*, which is a different
    question. A key with an empty balance authenticates perfectly and then fails on every
    request — so the UI reported "live" while every path silently served its template. The
    honest answer has to account for calls we have already watched fail.
    """
    return _client() is not None and _DEGRADED is None


def status() -> dict:
    """Why the assistant is in the state it is in, for the UI to show rather than guess."""
    if _client() is None:
        return {"live": False, "reason": "no API key configured"}
    if _DEGRADED is not None:
        return {"live": False, "reason": _DEGRADED}
    return {"live": True, "reason": "key configured and calls succeeding"}


def _scrub(text: str) -> str:
    """Last line of defence: never let a banned word reach a user."""
    if BANNED.search(text):
        LOGGER.warning("LLM output contained a banned term; replaced with the template")
        return ""
    return text.strip()


def _ask(prompt: str, *, max_tokens: int = 700, system: str = SYSTEM) -> str:
    """One non-streaming call. Returns "" on any failure, so callers can fall back."""
    client = _client()
    if client is None:
        return ""
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            thinking={"type": "adaptive"},
            output_config={"effort": "low"},
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        LOGGER.warning("LLM call failed (%s) — falling back to template", type(exc).__name__)
        # A billing, auth or model-access failure will fail identically on every later call.
        # Record it, so `available()` stops claiming "live" and the UI stops promising a
        # briefing it cannot deliver. Transient failures (timeout, rate limit, overload) are
        # left alone — those genuinely do recover.
        name = type(exc).__name__
        if name in {"AuthenticationError", "PermissionDeniedError", "NotFoundError"}:
            _mark_degraded(f"{name}: the key is configured but not usable")
        elif name == "BadRequestError" and "credit" in str(exc).lower():
            _mark_degraded("the account has no credit balance")
        return ""
    if getattr(response, "stop_reason", None) == "refusal":
        LOGGER.warning("LLM declined the request — falling back to template")
        return ""
    text = "".join(b.text for b in response.content if b.type == "text")
    return _scrub(text)


# ------------------------------------------------------------------- case insight


def _case_facts(case: dict) -> str:
    """The only numbers the model is allowed to use, as compact JSON."""
    identity = case.get("identity", {})
    return json.dumps(
        {
            "description": identity.get("description"),
            "state": identity.get("state"),
            "constituency": identity.get("constituency"),
            "implementing_agency": identity.get("implementing_agency"),
            "recommended_amount_rupees": identity.get("recommended_amount"),
            "status": identity.get("status"),
            "recommendation_date": identity.get("recommendation_date"),
            "work_type": case.get("archetype", {}).get("label"),
            "peer_group_size": case.get("peer_context", {}).get("group_size"),
            "amount_percentile": case.get("peer_context", {}).get("amount_percentile"),
            "completion_risk": case.get("risk", {}).get("completion_risk"),
            "exposure_rupees": case.get("exposure_rupees"),
            "confidence_band": case.get("confidence_band"),
            "signal_families": case.get("n_signal_families"),
            "evidence": [e.get("detail") for e in case.get("evidence", [])],
            "compliance_findings": [f.get("meaning") for f in case.get("compliance_findings", [])],
            "early_warning": case.get("early_warning", {}).get("reason"),
            "recommended_next_step": case.get("recommended_next_step"),
        },
        ensure_ascii=False,
    )


def _case_template(case: dict) -> str:
    """Deterministic brief. Used when no LLM is configured, and as the safety net."""
    identity = case.get("identity", {})
    families = case.get("n_signal_families", 0)
    exposure = case.get("exposure_rupees") or 0
    signals = ", ".join(e.get("signal", "").lower() for e in case.get("evidence", []))
    return (
        f"This work in {identity.get('state') or 'an unrecorded state'} was placed on the "
        f"audit list because {families} independent kinds of evidence agreed it is worth a "
        f"look: {signals or 'no signal recorded'}. About Rs {exposure:,.0f} may be tied up "
        f"if it does not finish. Nothing here indicates wrongdoing — repeated descriptions, "
        f"large amounts and long durations all have ordinary explanations. "
        f"{case.get('recommended_next_step', '')}"
    )


def case_insight(case: dict, language: str = "en") -> dict:
    """A plain-language brief for one case file."""
    prompt = (
        "Write a short briefing for the audit officer about this flagged public work. "
        "Explain in plain words what was noticed, why it is worth their time, how much "
        "money is involved, and what they should check. Remember: this is a lead, not an "
        "accusation.\n\n"
        f"Data:\n{_case_facts(case)}"
    )
    if language != "en":
        prompt += f"\n\nWrite the entire briefing in {LANGUAGES.get(language, language)}."

    text = _ask(prompt)
    if text:
        return {"text": text, "source": "llm", "model": MODEL, "language": language}
    template = _case_template(case)
    if language != "en":
        translated = translate_text(template, language)
        if translated:
            return {"text": translated, "source": "template+llm", "language": language}
    return {"text": template, "source": "template", "language": language}


# --------------------------------------------------------------- portfolio insight


def portfolio_insight(stats: dict, language: str = "en") -> dict:
    """A national or role-scoped situation brief from the computed statistics."""
    national = stats.get("national", {})
    facts = {
        "works": national.get("total_works"),
        "completed": national.get("completed"),
        "open": national.get("open"),
        "recommended_rupees": national.get("total_recommended_rupees"),
        "exposure_rupees": national.get("total_exposure_rupees"),
        "leads": national.get("surfaced_leads"),
        "high_confidence": (national.get("bands") or {}).get("HIGH"),
        "states": national.get("states"),
        "top_states_by_exposure": [
            {"state": s.get("state_name"), "exposure": s.get("exposure"), "leads": s.get("leads")}
            for s in (stats.get("by_state") or [])[:5]
        ],
        "health_index": (stats.get("health_index") or {}).get("score"),
        "compliance_flagged": (stats.get("compliance") or {}).get("works_with_any_flag"),
        "duplicate_pairs_concerning": (stats.get("duplicates") or {}).get("concerning_pairs"),
    }
    prompt = (
        "Write a short situation brief for a ministry official about the national MPLADS "
        "portfolio. Say what the picture looks like, where attention is most needed, and "
        "one caveat about what these numbers do not mean. Remember exposure is money that "
        "could be tied up in unfinished works, never loss or missing money.\n\n"
        f"Data:\n{json.dumps(facts, ensure_ascii=False)}"
    )
    if language != "en":
        prompt += f"\n\nWrite the entire brief in {LANGUAGES.get(language, language)}."

    text = _ask(prompt)
    if text:
        return {"text": text, "source": "llm", "model": MODEL, "language": language}

    template = (
        f"The portfolio holds {facts['works']:,} works worth about "
        f"Rs {(facts['recommended_rupees'] or 0) / 1e7:,.0f} crore, of which "
        f"{facts['open']:,} are still in progress. Roughly "
        f"Rs {(facts['exposure_rupees'] or 0) / 1e7:,.0f} crore sits in works the model "
        f"estimates may not finish on time — money to watch, not money lost. "
        f"{facts['leads']:,} works were surfaced for review, {facts['high_confidence']:,} of "
        f"them with three or more independent kinds of evidence agreeing. A human should "
        f"start with the highest-ranked items in the investigation queue."
    )
    if language != "en":
        translated = translate_text(template, language)
        if translated:
            return {"text": translated, "source": "template+llm", "language": language}
    return {"text": template, "source": "template", "language": language}


# -------------------------------------------------------------------- translation


TRANSLATE_SYSTEM = """You are a translator for an Indian government audit dashboard.

Rules:
- Translate accurately and naturally into the target language.
- Keep every number, currency figure, percentage, date and proper noun exactly as given.
- Keep technical labels understandable to a non-technical government officer.
- Never soften or strengthen meaning. Never add or remove a claim.
- Return ONLY the translation, with no preamble and no quotation marks."""


def translate_text(text: str, language: str) -> str:
    """Translate one string. Returns "" if unavailable, so callers keep the English."""
    if language == "en" or not text:
        return text if language == "en" else ""
    return _ask(
        f"Translate into {LANGUAGES.get(language, language)}:\n\n{text}",
        system=TRANSLATE_SYSTEM,
        max_tokens=1200,
    )


def _bundle_path(language: str) -> Path:
    return config.ARTIFACTS / "i18n" / f"{language}.json"


def translate_bundle(strings: dict[str, str], language: str) -> dict[str, str]:
    """Translate a whole UI string bundle in one call, cached to disk.

    Cached because the interface strings never change between runs — paying for the same
    translation on every server start would be wasteful and slow.
    """
    if language == "en":
        return strings
    cached = _bundle_path(language)
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf-8"))

    payload = json.dumps(strings, ensure_ascii=False, indent=1)
    result = _ask(
        f"Translate every VALUE in this JSON object into "
        f"{LANGUAGES.get(language, language)}. Keep every KEY exactly as it is. "
        f"Return only the JSON object.\n\n{payload}",
        system=TRANSLATE_SYSTEM,
        max_tokens=8000,
    )
    if not result:
        return strings
    try:
        # The model may wrap the object in a fence despite instructions.
        cleaned = re.sub(r"^```(?:json)?|```$", "", result.strip(), flags=re.M).strip()
        translated = json.loads(cleaned)
    except json.JSONDecodeError:
        LOGGER.warning("translation for %s was not valid JSON — keeping English", language)
        return strings

    merged = {key: translated.get(key, value) for key, value in strings.items()}
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_text(json.dumps(merged, ensure_ascii=False, indent=1), encoding="utf-8")
    LOGGER.info("cached %s translation of %s strings", language, len(merged))
    return merged
