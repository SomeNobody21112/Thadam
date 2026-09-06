"""Export the top investigation leads as Salesforce-ready CSVs.

A free Salesforce Developer Edition org holds roughly 2,500 records — every record counts
as 2 KB whether it is or not. The portfolio is 210,993 works, so it does not go in, and it
should not: Salesforce is where an officer *works a case*, not where a Cox model runs.

So this exports the leads that actually need a human, in a shape the Data Import Wizard
accepts on the first attempt. Every field is trimmed to a real Salesforce limit, dates are
ISO, picklists are clean single words, and nothing contains a stray newline.

Run:

    .venv/Scripts/python.exe scripts/export_for_salesforce.py            # 500 HIGH leads
    .venv/Scripts/python.exe scripts/export_for_salesforce.py --limit 200

Writes to salesforce_export/ and prints the exact field definitions to create.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mplads import config  # noqa: E402

OUT = config.REPO_ROOT / "salesforce_export"

#: Salesforce Text fields cap at 255. Anything longer needs a Long Text Area, which the
#: import wizard handles but which cannot be used in list views or most filters — so the
#: fields an officer scans are deliberately kept short.
TEXT = 255
LONG_TEXT = 32_000

#: (Field Label, API Name, Salesforce type, length) — printed at the end so the object can
#: be built by reading straight down the list.
CASE_FIELDS = [
    ("Work Reference", "Work_Ref__c", "Text (External ID, Unique)", 40),
    ("Description", "Description__c", "Long Text Area", 5000),
    ("State", "State__c", "Text", 80),
    ("Constituency", "Constituency__c", "Text", 120),
    ("Implementing Agency", "Implementing_Agency__c", "Text", TEXT),
    ("MP Name", "MP_Name__c", "Text", 120),
    ("Recommended Amount", "Recommended_Amount__c", "Currency (16,2)", None),
    ("Exposure", "Exposure__c", "Currency (16,2)", None),
    ("Audit ROI", "Audit_ROI__c", "Number (16,2)", None),
    ("Priority", "Priority__c", "Number (3,4)", None),
    ("Confidence Band", "Confidence_Band__c", "Picklist: HIGH, MEDIUM, LOW", None),
    ("Signal Families", "Signal_Families__c", "Number (2,0)", None),
    ("Work Type", "Work_Type__c", "Text", TEXT),
    ("Recommendation Date", "Recommendation_Date__c", "Date", None),
    ("Work Status", "Work_Status__c", "Picklist: Open, Completed", None),
    ("Evidence Summary", "Evidence_Summary__c", "Long Text Area", 5000),
    ("Recommended Next Step", "Recommended_Next_Step__c", "Long Text Area", 5000),
    ("Suggested Actions", "Suggested_Actions__c", "Long Text Area", 2000),
    ("Early Warning Level", "Early_Warning_Level__c",
     "Picklist: CRITICAL, HIGH, MEDIUM, LOW", None),
    ("Early Warning Reason", "Early_Warning_Reason__c", "Long Text Area", 2000),
    ("Compliance Findings", "Compliance_Findings__c", "Long Text Area", 2000),
    ("Escalation Tier", "Escalation_Tier__c",
     "Picklist: District Monitoring, State Nodal, Ministry Review", None),
    ("Target Review Date", "Target_Review_Date__c", "Date", None),
    ("Investigation Status", "Investigation_Status__c",
     "Picklist: New, Assigned, In Progress, Verified, Closed", None),
    ("Officer Finding", "Officer_Finding__c",
     "Picklist: (leave blank on import) Verified Complete, Verified In Progress, "
     "Not Started, Not Found, Record Mismatch, No Access, False Positive", None),
    ("Not A Fraud Finding", "Not_A_Fraud_Finding__c", "Checkbox (default TRUE)", None),
]

#: Who a case goes to. Derived from exposure, not invented hierarchy — the tiers match the
#: three stakeholder roles the product already models, and nothing here asserts a statutory
#: reporting line we have not verified.
ESCALATION_BANDS = [
    (5_00_00_000, "Ministry Review"),      # >= Rs 5 crore exposure
    (50_00_000, "State Nodal"),            # >= Rs 50 lakh
    (0, "District Monitoring"),
]

#: Days to first review, set by who has to do the reviewing. An SLA is a resourcing
#: commitment before it is anything else, and the escalation tier is what says how much
#: money is attached and therefore how quickly someone senior has to look.
TIER_REVIEW_DAYS = {"Ministry Review": 7, "State Nodal": 14, "District Monitoring": 30}

#: How much the clock stretches when the engine is less sure. Confidence does not set the
#: date, it relaxes it: chasing a MEDIUM case as hard as a HIGH one is how a queue with a
#: clock on it becomes a queue nobody believes.
BAND_REVIEW_MULTIPLE = {"HIGH": 1.0, "MEDIUM": 2.0, "LOW": 3.0}

EVIDENCE_FIELDS = [
    ("Work Reference", "Work_Ref__c", "Text (used to relate to the case)", 40),
    ("Investigation Case", "Investigation_Case__r.Work_Ref__c",
     "Lookup, resolved from the case's External ID at load time", None),
    ("Signal", "Signal__c", "Text", 120),
    ("Family", "Family__c", "Picklist: amount, duration, lifecycle, behaviour, "
                            "multivariate, duplication", None),
    ("Detail", "Detail__c", "Long Text Area", 5000),
]


#: Punctuation that arrives from work descriptions and archetype labels and has no reason
#: to survive into a CRM. Folded to ASCII because a bulk-load parser that trips on one
#: character reports it as a quoting error two hundred rows away, which is a bad half hour.
ASCII_FOLD = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201c": "'", "\u201d": "'",
    "\u2013": "-", "\u2014": "-", "\u00b7": "-", "\u2022": "-",
    "\u2026": "...", "\u20b9": "Rs ", "\u00a0": " ",
    "\u00d7": "x", "\u00b0": " deg ", "\u2044": "/",
    '"': "'",
})


def clean(value: object, limit: int = TEXT) -> str:
    """One line, no control characters, inside a Salesforce field limit.

    Work descriptions in this data routinely carry a pasted specification table. A raw
    newline inside a CSV cell is legal and the import wizard still reads it, but it turns
    a list view into an unreadable wall — so they are flattened here rather than in
    Salesforce, where fixing 500 records is 500 clicks.
    """
    text = " ".join(str(value if value is not None else "").split())
    text = text.translate(ASCII_FOLD)
    # Catch-all. The named substitutions above cover what this data actually contains;
    # this makes sure a character nobody anticipated cannot fail a 500-row bulk load with
    # an error that points at the wrong line.
    text = "".join(c if ord(c) < 128 else " " for c in text)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def money(value: object) -> str:
    """Plain number. No commas, no symbol — Salesforce parses the raw figure."""
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return ""


def iso_date(value: object) -> str:
    """YYYY-MM-DD. The single most common reason a first import fails."""
    text = str(value or "")[:10]
    return text if len(text) == 10 and text[4] == "-" else ""


def load_leads(limit: int, band: str) -> list[dict]:
    path = config.ARTIFACTS / "case_files.json"
    if not path.exists():
        raise SystemExit(f"no case files at {path} — run `mplads pipeline` first")
    cases = json.loads(path.read_text(encoding="utf-8"))
    chosen = [c for c in cases if c.get("confidence_band") == band] if band != "ALL" else cases
    chosen.sort(key=lambda c: (-float(c.get("audit_roi") or 0), c["work_ref"]))
    return chosen[:limit]


def write_cases(leads: list[dict]) -> Path:
    path = OUT / "investigation_cases.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, quoting=csv.QUOTE_ALL)
        writer.writerow([api for _, api, _, _ in CASE_FIELDS])
        for case in leads:
            identity = case["identity"]
            evidence = case.get("evidence") or []
            warning = case.get("early_warning") or {}
            tier = escalation_tier(case.get("exposure_rupees"))
            summary = "; ".join(
                f"{e.get('signal')}: {e.get('detail')}" for e in evidence
            )
            writer.writerow([
                clean(case["work_ref"], 40),
                clean(identity.get("description"), 5000),
                clean(identity.get("state"), 80),
                clean(identity.get("constituency"), 120),
                clean(identity.get("implementing_agency"), TEXT),
                clean(identity.get("mp_name"), 120),
                money(identity.get("recommended_amount")),
                money(case.get("exposure_rupees")),
                money(case.get("audit_roi")),
                f"{float(case.get('priority') or 0):.4f}",
                clean(case.get("confidence_band"), 20),
                str(int(case.get("n_signal_families") or 0)),
                clean((case.get("archetype") or {}).get("label"), TEXT),
                iso_date(identity.get("recommendation_date")),
                "Completed" if str(identity.get("status", "")).lower().startswith("comp")
                else "Open",
                clean(summary, 5000),
                clean(case.get("recommended_next_step"), 5000),
                clean(" | ".join(case.get("suggested_actions") or []), 2000),
                clean(warning.get("level") or "LOW", 20),
                clean(warning.get("reason"), 2000),
                clean("; ".join(
                    f"{f.get('check')} ({f.get('authority')})"
                    for f in case.get("compliance_findings") or []
                ), 2000),
                tier,
                review_due(identity.get("recommendation_date"),
                           case.get("confidence_band"), tier),
                "New",
                "",          # Officer Finding — filled in Salesforce, read back by feedback
                "TRUE",      # Not A Fraud Finding — the contract, on every record
            ])
    return path


def escalation_tier(exposure: object) -> str:
    """Who this case goes to, by how much money is attached.

    Derived from exposure rather than an invented reporting line. The three tiers match the
    stakeholder roles the product already models; nothing here asserts a statutory chain we
    have not verified, and a real deployment would replace this with the actual one.
    """
    try:
        amount = float(exposure or 0)
    except (TypeError, ValueError):
        amount = 0.0
    for floor, tier in ESCALATION_BANDS:
        if amount >= floor:
            return tier
    return "District Monitoring"


def review_due(recommendation_date: object, band: object, tier: str = "") -> str:
    """A first-review date, so the queue has a clock on it.

    The tier sets the clock and the band stretches it. Doing it the other way round is what
    the first version did, and it gave all five hundred cases the same date — every loaded
    case is HIGH, so a band-only clock carries no information at all and an ageing report
    built on it cannot tell a slipping five-crore case from a routine district one.
    """
    import datetime as dt

    days = round(TIER_REVIEW_DAYS.get(tier, 30)
                 * BAND_REVIEW_MULTIPLE.get(str(band), 2.0))
    return (config.SNAPSHOT_DATE + dt.timedelta(days=days)).isoformat()


def write_evidence(leads: list[dict]) -> Path:
    path = OUT / "evidence.csv"
    rows = 0
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, quoting=csv.QUOTE_ALL)
        writer.writerow([api for _, api, _, _ in EVIDENCE_FIELDS])
        for case in leads:
            for item in case.get("evidence") or []:
                writer.writerow([
                    clean(case["work_ref"], 40),
                    clean(case["work_ref"], 40),   # resolves the lookup via External ID
                    clean(item.get("signal"), 120),
                    clean(item.get("family"), 40),
                    clean(item.get("detail"), 5000),
                ])
                rows += 1
    print(f"  evidence.csv               {rows:,} rows")
    return path


def write_field_guide(leads: list[dict]) -> Path:
    """The object definition, so nobody has to guess a field type at 2 a.m."""
    path = OUT / "SALESFORCE_SETUP.md"
    lines = [
        "# Salesforce setup — build this object, then import",
        "",
        "Two objects. The second is optional; do it only if the first import worked and",
        "you still have time.",
        "",
        "## 1. Investigation_Case__c",
        "",
        "Setup -> Object Manager -> Create -> Custom Object.",
        "Label **Investigation Case**, Plural **Investigation Cases**, Record Name",
        "**Work Reference** as *Text*. Tick **Allow Reports** and **Allow Search**.",
        "",
        "Then create these fields:",
        "",
        "| Field Label | API Name | Type |",
        "| --- | --- | --- |",
    ]
    for label, api, kind, length in CASE_FIELDS:
        size = f", length {length}" if length else ""
        lines.append(f"| {label} | `{api}` | {kind}{size} |")

    lines += [
        "",
        "**Set `Work_Ref__c` as External ID and Unique.** It lets you re-run the import to",
        "update rather than duplicate, which you will want the second time.",
        "",
        "## 2. Evidence__c (optional)",
        "",
        "| Field Label | API Name | Type |",
        "| --- | --- | --- |",
    ]
    for label, api, kind, length in EVIDENCE_FIELDS:
        size = f", length {length}" if length else ""
        lines.append(f"| {label} | `{api}` | {kind}{size} |")

    lines += [
        "",
        "## 3. Import",
        "",
        "Setup -> Data Import Wizard -> Custom Objects -> Investigation Cases -> Add new",
        "records. Drop in `investigation_cases.csv`. The column headers already match the",
        "API names, so the mapping should come up green with nothing to fix.",
        "",
        "**If a row fails**, it is almost always one of three things: a date that is not",
        "`YYYY-MM-DD`, a picklist value you have not created on the field yet, or a text",
        "value longer than the field. This export controls all three, so a failure usually",
        "means a field was created with the wrong type — check that one first.",
        "",
        "## 4. What to say about why this is only 500 rows",
        "",
        "> \"A Developer Edition org holds about 2,500 records. We did not try to put two",
        "> lakh works in a CRM — the models run in Python where they belong. Salesforce",
        "> holds the cases that need a human: assignment, approval, audit, and the mobile",
        "> app an officer uses at the site. That split is the design.\"",
        "",
        "## 5. Agentforce, once the data is in",
        "",
        "Setup -> Agentforce (or Einstein Bots if Agentforce is not in your org).",
        "",
        "Create one agent with **one topic** — call it *Investigation Lookup*. Give it the",
        "standard record-query actions against Investigation Case. That is enough for it to",
        "answer:",
        "",
        "- \"Show me HIGH priority cases in Bihar\"",
        "- \"Which case has the highest exposure?\"",
        "- \"What is the recommended next step for MP3018356-W86316?\"",
        "",
        "**Do not build the callout to the Python API today.** Named Credentials plus Apex",
        "plus a tunnel is where the remaining hours go. The React app already has that",
        "assistant and it answers over all 210,993 works.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=500,
                        help="how many leads to export (default 500)")
    parser.add_argument("--band", default="HIGH",
                        choices=["HIGH", "MEDIUM", "LOW", "ALL"],
                        help="confidence band to export (default HIGH)")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    leads = load_leads(args.limit, args.band)
    if not leads:
        raise SystemExit(f"no {args.band} leads found")

    print(f"exporting {len(leads):,} {args.band} leads, highest Audit-ROI first\n")
    cases = write_cases(leads)
    print(f"  investigation_cases.csv    {len(leads):,} rows")
    write_evidence(leads)
    guide = write_field_guide(leads)

    total = sum(float(c.get("exposure_rupees") or 0) for c in leads)
    print(f"\n  exposure covered           Rs {total / 1e7:,.1f} crore")
    print(f"\nwritten to {OUT}")
    print(f"start with {guide.name} — it lists every field to create, in order.")


if __name__ == "__main__":
    main()
