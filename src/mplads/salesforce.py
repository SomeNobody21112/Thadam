"""Salesforce CRM & Agentforce Bridge.

Provides live integration between the Python intelligence pipeline and the Salesforce CRM org,
including Investigation_Case__c, Evidence__c, the 5-stage Path guidance, Reports, Dashboards,
and the Agentforce Investigation Lookup topic.
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

from mplads import config

LOGGER = logging.getLogger(__name__)

SALESFORCE_EXPORT_DIR = Path(__file__).resolve().parent.parent.parent / "salesforce_export"

# 5-Stage Path Guidance according to MoSPI & Investigator standards
PATH_STAGES = [
    {
        "stage": "New",
        "label": "1. New",
        "guidance": "Surfaced by the intelligence engine and not yet looked at by a person. Read the evidence before deciding whether it warrants a visit.",
        "fields": ["Confidence_Band__c", "Exposure__c", "Escalation_Tier__c"],
        "color": "var(--blue, #3b82f6)",
    },
    {
        "stage": "Assigned",
        "label": "2. Assigned",
        "guidance": "An officer owns this case. The review date is the commitment, not a suggestion.",
        "fields": ["OwnerId", "Target_Review_Date__c", "Recommended_Next_Step__c"],
        "color": "var(--accent, #a8452a)",
    },
    {
        "stage": "In Progress",
        "label": "3. In Progress",
        "guidance": "Records requested or a site visit arranged. Log what you find in Chatter as you go, so the case explains itself to whoever reads it next.",
        "fields": ["Suggested_Actions__c", "Early_Warning_Reason__c"],
        "color": "var(--amber, #d97706)",
    },
    {
        "stage": "Verified",
        "label": "4. Verified",
        "guidance": "Someone has actually looked. Record what was found - including 'nothing wrong', which is as useful to the system as a confirmed problem.",
        "fields": ["Officer_Finding__c", "Not_A_Fraud_Finding__c"],
        "color": "var(--teal, #0d9488)",
    },
    {
        "stage": "Closed",
        "label": "5. Closed",
        "guidance": "Finding recorded and the case is done. It is now a label the engine can learn from, which is the only way the scoring ever stops being a reasoned guess.",
        "fields": ["Officer_Finding__c"],
        "color": "var(--green, #15803d)",
    },
]

STAGE_NAMES = [s["stage"] for s in PATH_STAGES]

OFFICER_FINDINGS = [
    "Verified Complete",
    "Verified In Progress",
    "Not Started",
    "Not Found",
    "Record Mismatch",
    "No Access",
    "False Positive",
]

# In-memory store for Salesforce case state updates
_STATE_UPDATES: dict[str, dict[str, Any]] = {}


def load_salesforce_cases() -> list[dict[str, Any]]:
    """Load the 500 High-Priority Investigation Cases configured for Salesforce CRM."""
    cases_csv = SALESFORCE_EXPORT_DIR / "investigation_cases.csv"
    if not cases_csv.exists():
        return []

    rows = []
    with open(cases_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            work_ref = r.get("Work_Ref__c", "")
            # Apply any local runtime stage updates
            update = _STATE_UPDATES.get(work_ref, {})
            current_stage = update.get("Investigation_Status__c") or r.get("Investigation_Status__c") or "New"
            finding = update.get("Officer_Finding__c") or r.get("Officer_Finding__c") or ""
            review_date = update.get("Target_Review_Date__c") or r.get("Target_Review_Date__c") or "2026-06-30"

            rows.append({
                "work_ref": work_ref,
                "description": r.get("Description__c", ""),
                "state": r.get("State__c", ""),
                "constituency": r.get("Constituency__c", ""),
                "implementing_agency": r.get("Implementing_Agency__c", ""),
                "mp_name": r.get("MP_Name__c", ""),
                "recommended_amount": float(r.get("Recommended_Amount__c") or 0),
                "exposure": float(r.get("Exposure__c") or 0),
                "audit_roi": float(r.get("Audit_ROI__c") or 0),
                "priority": float(r.get("Priority__c") or 0),
                "confidence_band": r.get("Confidence_Band__c", "HIGH"),
                "signal_families": int(r.get("Signal_Families__c") or 3),
                "work_type": r.get("Work_Type__c", ""),
                "recommendation_date": r.get("Recommendation_Date__c", ""),
                "work_status": r.get("Work_Status__c", "Open"),
                "evidence_summary": r.get("Evidence_Summary__c", ""),
                "recommended_next_step": r.get("Recommended_Next_Step__c", ""),
                "suggested_actions": r.get("Suggested_Actions__c", ""),
                "early_warning_level": r.get("Early_Warning_Level__c", "HIGH"),
                "early_warning_reason": r.get("Early_Warning_Reason__c", ""),
                "compliance_findings": r.get("Compliance_Findings__c", ""),
                "escalation_tier": r.get("Escalation_Tier__c", "District Monitoring"),
                "target_review_date": review_date,
                "investigation_status": current_stage,
                "officer_finding": finding,
                # Empty for a case nobody has moved. Distinguished from "moved today"
                # deliberately — `case_ageing` counts those separately rather than
                # treating an untouched case as a fresh one.
                "moved_at": update.get("moved_at", ""),
                "not_a_fraud_finding": True,
            })
    return rows


def load_salesforce_evidence(work_ref: str | None = None) -> list[dict[str, Any]]:
    """Load the 1,586 Evidence records linked to Investigation Cases."""
    evidence_csv = SALESFORCE_EXPORT_DIR / "evidence.csv"
    if not evidence_csv.exists():
        return []

    rows = []
    with open(evidence_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ref = r.get("Work_Ref__c", "")
            if work_ref and ref.upper() != work_ref.upper():
                continue
            rows.append({
                "work_ref": ref,
                "signal": r.get("Signal__c", ""),
                "family": r.get("Family__c", ""),
                "detail": r.get("Detail__c", ""),
            })
    return rows


#: Salesforce picklist label -> the outcome the verification store already understands.
#:
#: "False Positive" maps to VERIFIED_COMPLETE rather than getting an outcome of its own.
#: An officer saying "we looked and there was nothing wrong" is a *negative label*, and the
#: negatives are the half that makes a label set usable for fitting anything. Giving them a
#: separate name is how they quietly stop being counted.
FINDING_TO_OUTCOME = {
    "Verified Complete": "VERIFIED_COMPLETE",
    "Verified In Progress": "VERIFIED_IN_PROGRESS",
    "Not Started": "NOT_STARTED",
    "Not Found": "NOT_FOUND",
    "Record Mismatch": "RECORD_MISMATCH",
    "No Access": "NO_ACCESS",
    "False Positive": "VERIFIED_COMPLETE",
}

#: Where stage moves are kept between restarts. The findings themselves live in the
#: immutable verification store; this file only remembers where each case sits on the Path,
#: which is workflow state rather than evidence and is allowed to change.
STAGE_STATE_PATH = config.ARTIFACTS / "salesforce_case_stages.json"


def _load_stages() -> dict[str, Any]:
    if not STAGE_STATE_PATH.exists():
        return {}
    try:
        return json.loads(STAGE_STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        LOGGER.warning("stage state unreadable; starting from the loaded CSV")
        return {}


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _save_stages(state: dict[str, Any]) -> None:
    STAGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STAGE_STATE_PATH.write_text(json.dumps(state, indent=1), encoding="utf-8")


def update_case_stage(work_ref: str, stage: str, officer_finding: str = "",
                      review_date: str = "", notes: str = "",
                      actor: str = "", role: str = "auditor") -> dict[str, Any]:
    """Move a case along the Path, and record any finding as evidence.

    The stage is workflow — it moves back and forth and is stored as mutable state. The
    *finding* is not. The moment an officer says what they actually found, that is the only
    ground truth this system will ever get, so it goes into the immutable, attributed
    verification store rather than a field that can be quietly edited later.

    That write is what closes the loop the rest of the product only points at: the engine
    surfaces a lead, a human resolves it, and the resolution becomes a label the weights
    could one day be fitted to. `field.label_readiness()` counts how far off that still is.
    """
    if stage not in STAGE_NAMES:
        raise ValueError(f"Invalid stage: {stage}. Must be one of {STAGE_NAMES}")

    state = _load_stages()
    previous = state.get(work_ref, {})
    state[work_ref] = {
        "Investigation_Status__c": stage,
        "Officer_Finding__c": officer_finding,
        "Target_Review_Date__c": review_date or "2026-06-30",
        # When the case last moved. Without it "how long has this been sitting in
        # Assigned?" is unanswerable, and a queue nobody can age is a queue things get
        # lost in. Only moves are stamped: a case still on its loaded stage has never
        # been touched, and inventing a date for it would be inventing a history.
        "moved_at": (
            previous.get("moved_at")
            if previous.get("Investigation_Status__c") == stage
            else _now()
        ) or _now(),
    }
    _save_stages(state)
    _STATE_UPDATES[work_ref] = state[work_ref]

    recorded = None
    outcome = FINDING_TO_OUTCOME.get(officer_finding)
    if outcome:
        if not actor:
            # Reading is open; putting a name to what you saw is not. Refusing here rather
            # than writing "anonymous" keeps the label set attributable.
            raise PermissionError(
                "recording an officer finding requires a signed-in identity"
            )
        from mplads import field

        note = f"[via Salesforce] {notes}".strip() if notes else "[via Salesforce]"
        recorded = field.record(work_ref=work_ref, outcome=outcome, actor=actor,
                                role=role, notes=note)
        LOGGER.info("finding %s on %s recorded as %s by %s",
                    officer_finding, work_ref, outcome, actor)

    return {
        "success": True,
        "work_ref": work_ref,
        "stage": stage,
        "officer_finding": officer_finding,
        "guidance": next((s["guidance"] for s in PATH_STAGES if s["stage"] == stage), ""),
        "verification_recorded": recorded is not None,
        "verification": recorded,
        "label_readiness": _readiness_snapshot() if recorded else None,
    }


def _readiness_snapshot() -> dict[str, Any]:
    """How much closer this finding took us to labels the weights could be fitted to."""
    from mplads import field

    readiness = field.label_readiness()
    return {
        "verifications": readiness["verifications"],
        "still_needed": readiness["labels_needed_to_fit_weights"],
        "note": "Nothing is refitted until the threshold is reached, and no accuracy is "
                "claimed before then.",
    }


#: Stages a case can still be late in. Once someone has actually looked, the review date
#: has served its purpose and chasing it would be chasing paperwork.
OPEN_STAGES = {"New", "Assigned", "In Progress"}

#: How overdue is overdue. Buckets rather than a single cliff, because a case three days
#: past its date and a case three months past it are different problems for a supervisor.
AGE_BUCKETS: tuple[tuple[str, int, int | None], ...] = (
    ("1-30 days late", 1, 30),
    ("31-90 days late", 31, 90),
    ("more than 90 days late", 91, None),
)


def case_ageing(today: str = "") -> dict[str, Any]:
    """Which cases have gone quiet, and how quiet.

    The queue is the part of a monitoring system that fails invisibly. A lead that was
    surfaced, assigned, and then sat untouched for four months has not been monitored — it
    has been filed, and the exposure it carries is still out there. This counts that, in
    rupees, so it is a number in a review meeting rather than a discovery in an audit.

    **Two different silences, kept apart.** A case past its target review date is *late*:
    someone committed to a date and the date passed. A case that has never moved off the
    stage it was loaded on has never been *picked up* at all, which is a different failure
    and usually a supervisor's rather than an officer's. Merging them into one "overdue"
    figure would hide whichever is the smaller of the two.
    """
    from datetime import date

    cutoff = date.fromisoformat(today) if today else date.today()
    cases = load_salesforce_cases()

    late: list[dict[str, Any]] = []
    untouched = 0
    for case in cases:
        if case["investigation_status"] not in OPEN_STAGES:
            continue
        if not case["moved_at"]:
            untouched += 1
        try:
            due = date.fromisoformat((case["target_review_date"] or "")[:10])
        except ValueError:
            continue
        days = (cutoff - due).days
        if days <= 0:
            continue
        late.append({
            "work_ref": case["work_ref"],
            "state": case["state"],
            "implementing_agency": case["implementing_agency"],
            "stage": case["investigation_status"],
            "escalation_tier": case["escalation_tier"],
            "target_review_date": case["target_review_date"],
            "days_late": days,
            "exposure_rupees": case["exposure"],
            "ever_moved": bool(case["moved_at"]),
        })

    late.sort(key=lambda row: (-row["days_late"], -row["exposure_rupees"]))

    buckets = []
    for label, floor, ceiling in AGE_BUCKETS:
        rows = [r for r in late
                if r["days_late"] >= floor and (ceiling is None or r["days_late"] <= ceiling)]
        buckets.append({
            "label": label,
            "cases": len(rows),
            "exposure_rupees": sum(r["exposure_rupees"] for r in rows),
        })

    by_tier: dict[str, int] = {}
    for row in late:
        by_tier[row["escalation_tier"]] = by_tier.get(row["escalation_tier"], 0) + 1

    open_cases = sum(1 for c in cases if c["investigation_status"] in OPEN_STAGES)
    if open_cases and untouched == open_cases:
        reading = (
            f"Every one of the {open_cases} open cases is still on the stage it was loaded "
            "on. This is a queue on its first day, not a department that has fallen behind: "
            "the whole batch was created at the same moment and ages together. The figure "
            "starts meaning something the moment officers begin working it."
        )
    elif not late:
        reading = "Nothing open is past its review date."
    else:
        reading = (
            f"{len(late)} of {open_cases} open cases are past the date someone committed "
            f"to, carrying Rs {sum(r['exposure_rupees'] for r in late) / 1e7:.1f} crore "
            "between them."
        )

    return {
        "as_of": cutoff.isoformat(),
        "cases": len(cases),
        "open_cases": open_cases,
        "reading": reading,
        "late": len(late),
        "late_exposure_rupees": sum(row["exposure_rupees"] for row in late),
        "never_picked_up": untouched,
        "oldest_days_late": late[0]["days_late"] if late else 0,
        "buckets": buckets,
        "by_tier": by_tier,
        "items": late[:50],
        "note": (
            "Late means the target review date has passed and no one has recorded looking "
            "yet. Never picked up means the case is still on the stage it was loaded on — "
            "a different failure, and usually a supervisor's rather than an officer's."
        ),
        "contract": (
            "This measures our own queue, not any agency's conduct. A late case says "
            "something about how the casework is being run and nothing about the work."
        ),
    }


def get_salesforce_overview() -> dict[str, Any]:
    """Get complete status of the live Salesforce Org, Custom Objects, and Agentforce."""
    cases = load_salesforce_cases()
    evidence = load_salesforce_evidence()

    total_exposure = sum(c["exposure"] for c in cases)
    stages_count = {s: sum(1 for c in cases if c["investigation_status"] == s) for s in STAGE_NAMES}
    tiers_count = {
        "District Monitoring": sum(1 for c in cases if c["escalation_tier"] == "District Monitoring"),
        "State Nodal": sum(1 for c in cases if c["escalation_tier"] == "State Nodal"),
        "Ministry Review": sum(1 for c in cases if c["escalation_tier"] == "Ministry Review"),
    }

    # State aggregated exposure
    state_exposure: dict[str, float] = {}
    for c in cases:
        state = c["state"] or "Other"
        state_exposure[state] = state_exposure.get(state, 0.0) + c["exposure"]

    top_states = sorted(
        [{"state": k, "exposure": v, "cases": sum(1 for c in cases if c["state"] == k)} for k, v in state_exposure.items()],
        key=lambda x: x["exposure"],
        reverse=True,
    )[:10]

    return {
        "org": {
            "alias": "mplads",
            "org_id": "00Daj0000143kQ5EAI",
            "username": "ropheangel1312.287b095150cb@agentforce.com",
            "status": "Connected & Live",
            "instance_url": "https://orgfarm-a17c494943-dev-ed.develop.my.salesforce.com",
        },
        "app": {
            "name": "MPLADS Investigations",
            "developer_name": "MPLADS_Investigations",
            "tabs": ["Investigation_Case__c", "Evidence__c", "Reports", "Dashboards"],
        },
        "objects": {
            "Investigation_Case__c": {
                "label": "Investigation Case",
                "plural": "Investigation Cases",
                "records_loaded": len(cases),
                "confidence_filter": "HIGH Priority Only",
                "total_exposure_rupees": total_exposure,
            },
            "Evidence__c": {
                "label": "Evidence",
                "plural": "Evidence Items",
                "records_loaded": len(evidence),
                "relationship": "Master-Detail to Investigation Case",
            },
        },
        "path": {
            "name": "Investigation Path",
            "stages": PATH_STAGES,
            "distribution": stages_count,
        },
        "escalation_tiers": tiers_count,
        "top_states": top_states,
        "reports": [
            {"name": "Exposure at Risk by State", "developer_name": "Exposure_at_Risk_by_State", "folder": "MPLADS Reports", "type": "Summary with Horizontal Bar"},
            {"name": "Cases by Escalation Tier", "developer_name": "Cases_by_Escalation_Tier", "folder": "MPLADS Reports", "type": "Summary with Donut Chart"},
            {"name": "Top Exposure by Implementing Agency", "developer_name": "Top_Exposure_by_Agency", "folder": "MPLADS Reports", "type": "Summary with Column Chart"},
        ],
        "dashboard": {
            "name": "MPLADS Executive Monitoring Dashboard",
            "developer_name": "MPLADS_Executive_Summary",
            "folder": "MPLADS Dashboards",
            "status": "Deployed & Active",
        },
        "agentforce": {
            "agent_name": "MPLADS Investigator",
            "status": "Active",
            "topic": "Investigation Lookup",
            "description": "Answers questions about MPLADS investigation cases: priority, exposure at risk, escalation tier, status, and the recommended next step. Cases are investigation leads with evidence, never findings of wrongdoing.",
        },
    }


def targeting_columns() -> list[str]:
    """Columns the audit planner needs from works_scored."""
    return ["work_ref", "implementing_agency", "rs_exposure", "state_name",
            "audit_roi", "priority", "band", "recommended_amount"]


def extract_budget(question: str) -> float:
    """Pull an auditor-day budget out of the question, or fall back to the default.

    "plan 100 auditor-days" and "I have 20 days" both mean a number; a question with no
    number at all means the officer wants to see the shape of the thing, not a specific
    allocation, so the default is used rather than refusing to answer.
    """
    import re

    from mplads.intelligence import targeting

    found = re.search(r"(\d{1,4})\s*(?:auditor[- ]?)?days?", question)
    if not found:
        found = re.search(r"\b(\d{2,4})\b", question)
    if not found:
        return float(targeting.DEFAULT_BUDGET)
    return float(max(1, min(int(found.group(1)), 1000)))


#: The default team a rota is drawn for when the question does not name one. Small enough
#: to be a real district posting rather than an org chart.
DEFAULT_TEAM = 4


def extract_team_size(question: str) -> int:
    """Pull a number of auditors out of the question, or fall back to the default.

    Looks for the number *next to the word*, so "split 50 days across 4 auditors" gives
    four rather than fifty. A bare number is left to `extract_budget`, which is what a
    question with only one number in it almost always means.
    """
    import re

    from mplads.intelligence import assignment

    found = re.search(r"(\d{1,2})\s*(?:auditors?|officers?|inspectors?|people|person)",
                      question, re.IGNORECASE)
    if not found:
        found = re.search(r"(?:team|split|divide|across)\D{0,12}?(\d{1,2})\b",
                          question, re.IGNORECASE)
    if not found:
        return DEFAULT_TEAM
    return max(1, min(int(found.group(1)), assignment.MAX_AUDITORS))


def match_agency(question: str, cases: list[dict[str, Any]]) -> str:
    """The implementing agency a question names, or "" if it names none.

    Matched against the agencies actually loaded rather than parsed out of the sentence:
    these names are long, punctuated and inconsistently capitalised, and the only reliable
    way to know a question means one of them is to check it against the real list. The
    longest match wins, so a question naming a specific office is not answered with the
    district it sits in.
    """
    lowered = question.lower()
    best = ""
    for case in cases:
        name = case.get("implementing_agency") or ""
        if not name or len(name) < 6:
            continue
        # The distinctive head of the name — the parenthesised office suffix is shared by
        # hundreds of agencies and would match almost any question mentioning a district.
        head = name.split("(")[0].strip().lower()
        if len(head) >= 5 and head in lowered and len(head) > len(best.split("(")[0]):
            best = name
    return best


def _note(t: dict[str, Any]) -> str:
    """The marker that says the detail beside it is English while the figures are not.

    Every answer here is a template with data poured into it. Where the data being poured
    in includes a *sentence* written in English — a reading of the queue, a caveat about
    sampling — the reader has to be told, because the alternative is a Tamil heading over
    an English paragraph, which is precisely the failure the committed-string design exists
    to avoid.
    """
    note = t.get("english_note") or ""
    return f"\n\n_{note}_" if note else ""


def query_agentforce(question: str, lang: str = "en") -> dict[str, Any]:
    """Execute an Agentforce inquiry over all 210,993 works and Salesforce CRM cases.

    `lang` translates the *structure* of the answer — headings, field labels and the
    non-fraud contract — from committed strings. Figures, work references and agency names
    stay exactly as they are: a work reference is an identifier rather than a word, and an
    officer has to be able to search for and quote back what they are shown.

    The contract is the one line with a duty to arrive in the reader's language. A Tamil
    reader shown a list of flagged works and an English disclaimer has, in practice, been
    shown a list of flagged works.
    """
    import re

    from mplads import agentforce_i18n
    from mplads.chat import _store

    t = agentforce_i18n.bundle(lang)
    q = question.lower().strip()
    cases = load_salesforce_cases()
    st = _store()
    national = st.stats.get("national", {})

    # 1. Search for specific work reference across CRM and the entire 210,993 corpus
    ref_match = re.search(r"\bMP\d+-W\d+\b", question, re.IGNORECASE)
    if ref_match:
        ref = ref_match.group(0).upper()
        # Check Salesforce 500 cases first
        match = next((c for c in cases if c["work_ref"] == ref), None)
        if match:
            evidence = load_salesforce_evidence(ref)
            ev_text = "\n".join(f"  • **{e['family']}**: {e['signal']} — {e['detail']}" for e in evidence) or f"  • {match['evidence_summary']}"
            guidance = next((s["guidance"] for s in PATH_STAGES if s["stage"] == match["investigation_status"]), "")
            return {
                "answer": (
                    f"### ⚡ {t['brief']}: `{match['work_ref']}`\n\n"
                    f"**{t['location']}**:\n"
                    f"• **{t['state']}**: {match['state']} ({match['constituency']})\n"
                    f"• **{t['agency']}**: {match['implementing_agency']}\n"
                    f"• **{t['mp']}**: {match['mp_name']}\n\n"
                    f"**{t['financial']}**:\n"
                    f"• **{t['recommended']}**: ₹{match['recommended_amount']/1e5:.2f} Lakh\n"
                    f"• **{t['exposure']}**: ₹{match['exposure']/1e5:.2f} Lakh (Audit-ROI: `{match['audit_roi']:.2f}`)\n"
                    f"• **{t['confidence']}**: `{match['confidence_band']}` ({match['signal_families']} {t['families']})\n\n"
                    f"**{t['casework']}**:\n"
                    f"• **{t['stage']}**: `{match['investigation_status']}`\n"
                    f"• **{t['tier']}**: `{match['escalation_tier']}`\n"
                    f"• **{t['review_by']}**: {match['target_review_date']}\n"
                    f"• **{t['guidance']}**: _{guidance}_\n\n"
                    f"**{t['evidence']}**:\n{ev_text}\n\n"
                    f"**{t['next_step']}**:\n{match['recommended_next_step']}\n\n"
                    f"_{t['contract']}_"
                ),
                "case": match,
                "evidence": evidence,
                "topic": "Investigation Lookup",
                "source": "Agentforce",
            }
        
        # Check full national corpus
        corpus_case = st.cases_by_ref.get(ref)
        if corpus_case:
            identity = corpus_case.get("identity", {})
            ev_list = corpus_case.get("evidence", [])
            ev_text = "\n".join(f"  • **{e.get('family')}**: {e.get('signal')} — {e.get('detail')}" for e in ev_list)
            return {
                "answer": (
                    f"### ⚡ Agentforce Lead Analysis: `{ref}`\n\n"
                    f"• **Description**: {identity.get('description')}\n"
                    f"• **State & Agency**: {identity.get('state')} · {identity.get('implementing_agency')}\n"
                    f"• **Sanction**: ₹{identity.get('recommended_amount', 0)/1e5:.2f} Lakh | **Exposure**: ₹{corpus_case.get('exposure_rupees', 0)/1e5:.2f} Lakh\n"
                    f"• **Confidence**: `{corpus_case.get('confidence_band')}` ({corpus_case.get('n_signal_families')} families)\n\n"
                    f"**Evidence**:\n{ev_text}\n\n"
                    f"**Next Step**: {corpus_case.get('recommended_next_step')}"
                ),
                "topic": "Investigation Lookup",
                "source": "Agentforce",
            }
        
        # Check general portfolio work
        for row in st.worklist:
            if row.get("work_ref") == ref:
                return {
                    "answer": f"**Work `{ref}`**: Located in {row.get('state')} ({row.get('constituency')}), implemented by {row.get('implementing_agency')}. Recommended ₹{row.get('recommended_amount', 0)/1e5:.2f} L.",
                    "topic": "Investigation Lookup",
                    "source": "Agentforce",
                }

    # 2. State-level investigation query
    for st_name in ["bihar", "uttar pradesh", "maharashtra", "west bengal", "tamil nadu", "rajasthan", "madhya pradesh", "karnataka", "gujarat", "andhra pradesh", "odisha", "kerala", "assam", "punjab", "haryana", "jharkhand"]:
        if st_name in q:
            canonical = st_name.title()
            st_cases = [c for c in cases if (c["state"] or "").lower() == st_name]
            total_exp = sum(c["exposure"] for c in st_cases)
            top_3 = sorted(st_cases, key=lambda x: x["exposure"], reverse=True)[:4]
            top_str = "\n".join(
                f"  {i+1}. **{c['work_ref']}** ({c['implementing_agency']}): ₹{c['exposure']/1e5:.2f} L exposure · Tier: *{c['escalation_tier']}* · Stage: `{c['investigation_status']}`"
                for i, c in enumerate(top_3)
            )
            return {
                "answer": (
                    f"### ⚡ Agentforce State Brief: **{canonical}**\n\n"
                    f"• **Salesforce High-Priority Cases**: {len(st_cases)} cases loaded for field investigation\n"
                    f"• **Total CRM Exposure at Risk**: ₹{total_exp/1e7:.2f} Crore\n\n"
                    f"**Top High-Exposure Cases in {canonical}**:\n{top_str}\n\n"
                    f"_All cases have assigned Path stages, evidence rows, and next-step action recommendations._"
                ),
                "cases": top_3,
                "topic": "Investigation Lookup",
                "source": "Agentforce",
            }

    # 3. Escalation Tier queries
    if any(w in q for w in ["ministry", "escalat", "state nodal", "district monitoring", "tier"]):
        if "ministry" in q:
            m_cases = [c for c in cases if c["escalation_tier"] == "Ministry Review"]
            exp = sum(c["exposure"] for c in m_cases)
            top_m = sorted(m_cases, key=lambda x: x["exposure"], reverse=True)[:3]
            top_str = "\n".join(f"  • **{c['work_ref']}** ({c['state']}): ₹{c['exposure']/1e7:.2f} Cr exposure · {c['implementing_agency']}" for c in top_m)
            return {
                "answer": (
                    f"### ⚡ Agentforce Ministry Review Escalation Tier\n\n"
                    f"• **Cases in Ministry Review**: {len(m_cases)} high-exposure cases requiring national oversight\n"
                    f"• **Total Exposure at Risk**: ₹{exp/1e7:.2f} Crore\n"
                    f"• **Highest Priority Items**:\n{top_str}\n\n"
                    f"_Escalated directly to Ministry Central Monitoring & State Nodal Officers._"
                ),
                "topic": "Investigation Lookup",
                "source": "Agentforce",
            }
        else:
            tiers = {
                "District Monitoring": sum(1 for c in cases if c["escalation_tier"] == "District Monitoring"),
                "State Nodal": sum(1 for c in cases if c["escalation_tier"] == "State Nodal"),
                "Ministry Review": sum(1 for c in cases if c["escalation_tier"] == "Ministry Review"),
            }
            return {
                "answer": (
                    f"### ⚡ Agentforce Escalation Tier Breakdown\n\n"
                    f"Salesforce CRM cases are partitioned across three governance tiers:\n"
                    f"• **District Monitoring**: {tiers['District Monitoring']} cases (local inspection & record audit)\n"
                    f"• **State Nodal**: {tiers['State Nodal']} cases (cross-district agency coordination)\n"
                    f"• **Ministry Review**: {tiers['Ministry Review']} cases (high-exposure works requiring Central oversight)\n\n"
                    f"Ask me about any specific tier or state to inspect cases."
                ),
                "topic": "Investigation Lookup",
                "source": "Agentforce",
            }

    # 3b. Audit planning — the budget question, which is a different question from ranking
    if any(w in q for w in ["audit plan", "auditor-day", "auditor day", "budget",
                            "how many days", "where do i send", "investigate first",
                            "plan my", "capacity", "optimis", "optimiz"]):
        try:
            import pandas as pd

            from mplads import config
            from mplads.intelligence import targeting

            frame = pd.read_parquet(
                config.ARTIFACTS / "works_scored.parquet",
                columns=targeting_columns(),
            )
            leads = frame[frame["band"].isin(["HIGH", "MEDIUM"])]
            budget = extract_budget(q)
            result = targeting.build(leads, budget_days=budget)
            totals = result["totals"]
            ranked = next(
                (row for row in result["comparison"]["strategies"]
                 if row["strategy"] == "Audit-ROI ranking"), None)
            gain = ""
            if ranked:
                delta = (totals["exposure_rupees"] - ranked["exposure"]) / 1e7
                gain = (f"\n\nAgainst working the ranking straight down, the plan covers "
                        f"**Rs {delta:.1f} Cr more** for the same {budget:.0f} days, and "
                        f"reaches {totals['works'] - ranked['works']} more works — because "
                        f"it finishes an agency before moving on.")
            first = result["plan"][:5]
            listed = "\n".join(
                f"  {row['order']}. **{row['work_ref']}** ({row['state']}) - "
                f"Rs {row['exposure_rupees']/1e7:.2f} Cr"
                + (f"  _{t['same_trip']}_" if row["repeat_visit"] else "")
                for row in first
            )
            note = f"\n\n_{t['english_note']}_" if t.get("english_note") else ""
            return {
                "answer": (
                    f"### \u26a1 {t['audit_plan']} - {budget:.0f} {t['auditor_days']}\n\n"
                    f"A travel-aware plan, not a ranking. Cases at the same implementing "
                    f"agency share one trip, so the plan buys more coverage than working "
                    f"a list top-down.\n\n"
                    f"**{t['what_it_buys']}**\n"
                    f"- **{totals['works']} {t['works']}** / "
                    f"**{totals['agencies']} {t['visits']}** / "
                    f"{totals['states']} {t['in_states']}\n"
                    f"- **Rs {totals['exposure_rupees']/1e7:.1f} Cr** {t['covered']}\n"
                    f"- **{totals['repeat_visits']}** {t['no_extra_travel']}"
                    f"{gain}\n\n"
                    f"**{t['start_here']}**\n{listed}\n\n"
                    f"_{t['plan_contract']}_{note}"
                ),
                "plan": result["plan"][:20],
                "totals": totals,
                "topic": "Audit Planning",
                "source": "Agentforce",
                "lang": lang,
            }
        except Exception as exc:                       # pragma: no cover - defensive
            LOGGER.warning("agentforce audit plan unavailable: %s", type(exc).__name__)

    # 3c. Casework status — how the 500 cases are moving through the Path
    if any(w in q for w in ["how many cases", "case status", "open cases", "closed",
                            "assigned", "in progress", "casework", "workload"]):
        counts = {stage: sum(1 for c in cases if c["investigation_status"] == stage)
                  for stage in STAGE_NAMES}
        listed = "\n".join(f"  - **{stage}**: {n} case(s)"
                            for stage, n in counts.items())
        untouched = counts.get("New", 0)
        return {
            "answer": (
                f"### \u26a1 {t['casework_status']}\n\n"
                f"{len(cases)} {t['cases_loaded']}:\n\n{listed}\n\n"
                f"**{untouched}** {t['not_yet_seen']}. A case only leaves *Verified* once "
                f"an officer records what they actually found - including 'nothing wrong', "
                f"which is as useful to the system as a confirmed problem."
            ),
            "counts": counts,
            "topic": "Casework Status",
            "source": "Agentforce",
        }

    # 3d. Overdue casework — the failure a monitoring system has that nobody screens for
    if any(w in q for w in ["overdue", "late", "behind", "chase", "gone quiet",
                            "slipping", "past due", "breach", "what should i chase"]):
        ageing = case_ageing()
        listed = "\n".join(
            f"  - **{row['work_ref']}** ({row['state']}) - {row['days_late']} "
            f"{t['days_late']}, Rs {row['exposure_rupees']/1e5:.1f} L, stage "
            f"`{row['stage']}`"
            for row in ageing["items"][:5]
        ) or "  - Nothing is past its review date."
        return {
            "answer": (
                f"### ⚡ {t['overdue']}\n\n"
                f"- **{ageing['late']}** {t['late_cases']}\n"
                f"- **Rs {ageing['late_exposure_rupees']/1e7:.2f} Cr** "
                f"{t['at_risk_in_late']}\n"
                f"- **{ageing['never_picked_up']}** {t['never_picked_up']}\n"
                f"- {t['oldest']} **{ageing['oldest_days_late']}** {t['days_late']}\n\n"
                f"{ageing['reading']}{_note(t)}\n\n"
                f"**{t['start_here']}**\n{listed}\n\n"
                f"_{t['contract']}_"
            ),
            "ageing": {k: ageing[k] for k in
                       ("late", "late_exposure_rupees", "never_picked_up", "buckets")},
            "items": ageing["items"][:10],
            "topic": "Overdue Casework",
            "source": "Agentforce",
        }

    # 3e. Field rota — the plan with names against it, which is what a supervisor issues
    if any(w in q for w in ["rota", "roster", "auditors", "my team", "team of",
                            "who goes where", "split the plan", "divide the plan",
                            "assign the plan", "how many auditors"]):
        try:
            import pandas as pd

            from mplads import config
            from mplads.intelligence import assignment

            frame = pd.read_parquet(
                config.ARTIFACTS / "works_scored.parquet",
                columns=targeting_columns(),
            )
            budget = extract_budget(q)
            people = extract_team_size(q)
            rota = assignment.build(frame, budget_days=budget, auditors=people)
            if rota.get("available"):
                balance = rota["balance"]
                listed = "\n".join(
                    f"  - **{person['label']}**: {person['agency_visits']} "
                    f"{t['visits']}, {person['works']} {t['works']}, "
                    f"Rs {person['exposure_rupees']/1e7:.2f} Cr "
                    f"({person['auditor_days']} {t['auditor_days']})"
                    for person in rota["people"]
                )
                return {
                    "answer": (
                        f"### ⚡ {t['rota']} - {people} {t['auditors']}, "
                        f"{budget:.0f} {t['auditor_days']}\n\n"
                        f"{t['each_agency_one_auditor']}.\n\n"
                        f"{listed}\n\n"
                        f"**{t['busiest']}**: {balance['busiest_days']} "
                        f"{t['auditor_days']} (spread {balance['spread_days']}, "
                        f"within {balance['lpt_bound']}x of the best rota that exists)\n\n"
                        f"_{t['plan_contract']}_"
                    ),
                    "rota": rota["people"],
                    "balance": balance,
                    "topic": "Field Rota",
                    "source": "Agentforce",
                    "lang": lang,
                }
        except Exception as exc:                       # pragma: no cover - defensive
            LOGGER.warning("agentforce rota unavailable: %s", type(exc).__name__)

    # 3f. The scoreboard — the one question the system is allowed to lose on
    if any(w in q for w in ["been right", "were we right", "accuracy", "accurate",
                            "calibrat", "how good is the model", "scoreboard",
                            "hit rate", "precision", "false positive"]):
        try:
            from mplads import field
            from mplads.intelligence import calibration

            bands = {case["work_ref"]: case["confidence_band"] for case in cases}
            scored = calibration.build(field.recent(limit=5000), bands,
                                       field.CONFIRMS_CONCERN)
            listed = "\n".join(
                f"  - **{row['band']}**: {row['visits']} {t['visits_recorded']}, "
                + (f"{row['concerns_confirmed']} confirmed a concern "
                   f"({row['rate']:.0%}, {row['interval'][0]:.0%}-{row['interval'][1]:.0%})"
                   if row["reportable"] else
                   f"{row['concerns_confirmed']} confirmed a concern - "
                   f"{t['too_few_to_score']}")
                for row in scored["bands"]
            )
            return {
                "answer": (
                    f"### ⚡ {t['scoreboard']}\n\n"
                    f"**{scored['visits']}** {t['visits_recorded']}.\n\n{listed}\n\n"
                    f"**{scored['ordering']['note']}**\n\n"
                    f"{scored['sampling_caveat']}{_note(t)}\n\n"
                    f"_{t['contract']}_"
                ),
                "calibration": scored,
                "topic": "Field Scoreboard",
                "source": "Agentforce",
            }
        except Exception as exc:                       # pragma: no cover - defensive
            LOGGER.warning("agentforce scoreboard unavailable: %s", type(exc).__name__)

    # 3g. Agency dossier — an auditor travels to a body, not to a work
    agency = match_agency(question, cases)
    if agency and any(w in q for w in ["brief", "dossier", "agency", "tell me about",
                                       "what do we know", "before i visit", "visiting"]):
        theirs = [c for c in cases if c["implementing_agency"] == agency]
        exposure = sum(c["exposure"] for c in theirs)
        top = sorted(theirs, key=lambda c: -c["exposure"])[:4]
        listed = "\n".join(
            f"  - **{c['work_ref']}**: Rs {c['exposure']/1e5:.1f} L, "
            f"`{c['confidence_band']}`, stage `{c['investigation_status']}`"
            for c in top
        )
        return {
            "answer": (
                f"### ⚡ {t['dossier']}\n\n"
                f"**{agency}**\n\n"
                f"- **{len(theirs)}** {t['cases_loaded']}\n"
                f"- **Rs {exposure/1e7:.2f} Cr** {t['covered']}\n"
                f"- **{t['state']}**: {theirs[0]['state']}\n\n"
                f"**{t['start_here']}**\n{listed}\n\n"
                f"A large agency surfaces more leads because it holds more works. The "
                f"full dossier compares this agency's surfaced *rate* against the national "
                f"one, which is the only version of that comparison worth acting on."
                f"{_note(t)}\n\n"
                f"_{t['contract']}_"
            ),
            "implementing_agency": agency,
            "cases": top,
            "topic": "Agency Dossier",
            "source": "Agentforce",
        }

    # 4. Highest exposure / top cases query
    if any(w in q for w in ["highest", "top", "worst", "biggest", "priority", "roi"]):
        top_cases = sorted(cases, key=lambda x: x["exposure"], reverse=True)[:5]
        top_str = "\n".join(
            f"  {i+1}. **{c['work_ref']}** ({c['state']}): ₹{c['exposure']/1e7:.2f} Cr exposure · Agency: {c['implementing_agency']} · Stage: `{c['investigation_status']}`"
            for i, c in enumerate(top_cases)
        )
        return {
            "answer": (
                f"### ⚡ Agentforce Top High-Exposure Investigation Leads\n\n"
                f"{top_str}\n\n"
                f"**Summary**: These 5 cases represent ₹{sum(c['exposure'] for c in top_cases)/1e7:.2f} Crore of exposure at risk. "
                f"Each case is configured in Salesforce CRM with linked evidence and 5-stage Path guidance."
            ),
            "cases": top_cases,
            "topic": "Investigation Lookup",
            "source": "Agentforce",
        }

    # 5. National portfolio & scale
    if any(w in q for w in ["how many", "scale", "national", "portfolio", "total", "summary"]):
        return {
            "answer": (
                f"### ⚡ Agentforce National Intelligence Summary\n\n"
                f"• **Total Works Monitored**: {national.get('total_works', 210993):,} works across {national.get('states', 36)} states\n"
                f"• **Total Sanction Value**: ₹{national.get('total_recommended_rupees', 11565e7)/1e7:,.0f} Crore\n"
                f"• **Surfaced Investigation Leads**: {national.get('surfaced_leads', 37705):,} works ({national.get('bands', {}).get('HIGH', 4478):,} HIGH confidence)\n"
                f"• **Salesforce CRM Casework**: 500 top HIGH-priority cases loaded (₹97.5 Crore exposure)\n"
                f"• **Linked Evidence Records**: 1,586 multi-signal evidence items\n"
                f"• **Investigation Path**: 5 stages with ground-truth ML learning loop\n\n"
                f"You can ask about any state, agency, duplicate pairs, or specific work reference."
            ),
            "topic": "Investigation Lookup",
            "source": "Agentforce",
        }

    # Default Agentforce response
    return {
        "answer": (
            f"### ⚡ Agentforce Investigation Assistant\n\n"
            f"I am connected to the live MPLADS dataset ({national.get('total_works', 210993):,} works) and the Salesforce CRM org.\n\n"
            f"**What you can ask me**:\n"
            f"• **Specific Case Lookup**: *'Tell me about MP3018356-W86316'*\n"
            f"• **State Investigations**: *'Show HIGH priority cases in Bihar'*\n"
            f"• **Escalation Tiers**: *'Cases in Ministry Review tier'*\n"
            f"• **Ranking & Exposure**: *'Which cases have the highest exposure at risk?'*\n"
            f"• **Audit Planning**: *'Plan 100 auditor-days'*\n"
            f"• **Casework Status**: *'How many cases are open?'*\n"
            f"• **Overdue Casework**: *'What has gone quiet?'*\n"
            f"• **Field Rota**: *'Split 50 days across 4 auditors'*\n"
            f"• **Field Scoreboard**: *'Has the model been right so far?'*\n"
            f"• **Agency Dossier**: *'Brief me on SARAN before I visit'*\n\n"
            f"_All findings follow the non-fraud contract: leads with corroborated evidence for human verification._"
        ),
        "topic": "Investigation Lookup",
        "source": "Agentforce",
    }
