"""Push the field rota into Salesforce, so an auditor's round is on their phone.

The plan and the rota are computed in Python — there is no knapsack solver and no bin
packing in Apex, and there does not need to be. What Salesforce is for is what happens
afterwards: an officer standing outside a district office at nine in the morning, opening
the app, and seeing which works they are there to look at. That is a records problem, not a
modelling one, and it is the half Salesforce is genuinely better at.

**Why a separate object.** An `Investigation_Case__c` is one work, and it lives for as long
as the question about that work does. An `Audit_Assignment__c` is one work *on one round,
for one auditor, under one budget* — a supervisor re-plans a fortnight without wanting to
touch the case history. Modelling them as one record is how a replan silently rewrites what
happened last quarter.

`Assignment_Key__c` is the External ID, so re-running a plan at the same budget and team
size updates the same rows rather than piling a second rota on top of the first. Change the
budget or the team and you get a different plan, which is a different key and a different
set of rows — deliberately, because it is a different fortnight.

Run:

    .venv/Scripts/python.exe scripts/export_audit_plan.py --budget-days 50 --auditors 4
    sf data import bulk --sobject Audit_Assignment__c \\
        --file salesforce_export/audit_assignments.csv --target-org mplads --wait 10
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mplads import config  # noqa: E402
from mplads.intelligence import assignment, targeting  # noqa: E402

OUT = config.REPO_ROOT / "salesforce_export"

COLUMNS = [
    "Assignment_Key__c", "Work_Ref__c", "Investigation_Case__r.Work_Ref__c",
    "Auditor__c", "Auditor_Label__c", "Implementing_Agency__c", "State__c",
    "Visit_Order__c", "Day_From__c", "Day_To__c", "Cost_Days__c", "Exposure__c",
    "Confidence_Band__c", "Repeat_Visit__c", "Plan_Budget_Days__c", "Team_Size__c",
    "Visit_Status__c", "Not_A_Fraud_Finding__c",
]

TEXT_LIMIT = 250


def clean(value: object, limit: int = TEXT_LIMIT) -> str:
    """One line, inside the field limit. Agency names arrive with odd whitespace."""
    text = " ".join(str(value if value is not None else "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget-days", type=float, default=targeting.DEFAULT_BUDGET)
    parser.add_argument("--auditors", type=int, default=4)
    args = parser.parse_args()

    scored = config.ARTIFACTS / "works_scored.parquet"
    if not scored.exists():
        raise SystemExit("works_scored.parquet is missing — run `mplads pipeline` first")

    frame = pd.read_parquet(scored, columns=[
        "work_ref", "implementing_agency", "rs_exposure", "state_name",
        "audit_roi", "priority", "band", "recommended_amount",
    ])
    rota = assignment.build(frame, budget_days=args.budget_days, auditors=args.auditors)
    if not rota.get("available"):
        raise SystemExit(rota.get("note", "no rota to export"))

    # Only works that are already loaded as cases get the lookup. The rest still export:
    # a plan reaches works nobody has opened a case on, and dropping those rows would hand
    # an auditor a round with holes in it.
    from mplads import salesforce as sf

    case_refs = {case["work_ref"] for case in sf.load_salesforce_cases()}

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "audit_assignments.csv"
    budget = f"{args.budget_days:.0f}"
    rows = 0
    linked = 0

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, quoting=csv.QUOTE_ALL)
        writer.writerow(COLUMNS)

        for person in rota["people"]:
            for order, visit in enumerate(person["schedule"], start=1):
                for work in visit["works"]:
                    is_linked = work["work_ref"] in case_refs
                    linked += is_linked
                    rows += 1
                    writer.writerow([
                        # Budget and team size are in the key on purpose: a different
                        # budget is a different fortnight, not an edit to this one.
                        clean(f"{budget}d-{args.auditors}a-{work['work_ref']}", 80),
                        clean(work["work_ref"], 40),
                        clean(work["work_ref"], 40) if is_linked else "",
                        person["auditor"],
                        clean(person["label"], 80),
                        clean(visit["implementing_agency"], 255),
                        clean(visit["state"], 80),
                        order,
                        visit["day_from"],
                        visit["day_to"],
                        f"{work['cost_days']:.2f}",
                        f"{work['exposure_rupees']:.2f}",
                        clean(work["band"], 20),
                        "TRUE" if work["cost_days"] < targeting.FIRST_VISIT_DAYS else "FALSE",
                        int(args.budget_days),
                        args.auditors,
                        "Planned",
                        "TRUE",
                    ])

    balance = rota["balance"]
    print(f"wrote {rows} assignment(s) to {path.name}")
    print(f"  budget                          : {budget} auditor-days")
    print(f"  team                            : {args.auditors} auditors, "
          f"{rota['trips']} agency visits")
    print(f"  busiest / quietest round        : {balance['busiest_days']} / "
          f"{balance['quietest_days']} auditor-days")
    print(f"  exposure covered                : "
          f"Rs {rota['exposure_rupees'] / 1e7:.2f} crore")
    print(f"  linked to a Salesforce case     : {linked} of {rows}"
          "  (the rest are works nobody has opened a case on)")
    if rota["idle"]:
        print(f"  idle at this team size          : {', '.join(rota['idle'])}"
              "  (an agency is never split to fill a gap)")
    print()
    print("import with:")
    print("  sf data import bulk --sobject Audit_Assignment__c \\")
    print(f"      --file salesforce_export/{path.name} --target-org mplads --wait 10")
    print()
    print("Assignment_Key__c is the External ID, so re-running the same budget and team "
          "updates rather than duplicating.")


if __name__ == "__main__":
    main()
