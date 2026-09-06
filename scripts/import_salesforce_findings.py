"""Read officer findings back out of Salesforce into the verification store.

This is the return leg, and it is the half that makes the Salesforce integration worth
having. The engine sends 500 leads out; officers work them; what they *found* has to come
back, or the system never learns anything and every weight stays a reasoned guess forever.

Export a report from Salesforce with two columns — `Work_Ref__c` and `Officer_Finding__c`,
plus optionally `Notes__c` and `Verified_By__c` — save it as CSV, and run this. Findings
land in the same immutable, attributed store the in-app field verification writes to, and
count towards `field.label_readiness()` exactly the same way.

Run:

    .venv/Scripts/python.exe scripts/import_salesforce_findings.py findings.csv
    .venv/Scripts/python.exe scripts/import_salesforce_findings.py findings.csv --dry-run

Nothing is overwritten. A verification is evidence; a correction is a new record.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mplads import field  # noqa: E402

#: Salesforce picklist label -> the outcome this project already understands.
#:
#: "False Positive" has no equivalent in `field.OUTCOMES` and that is deliberate: an officer
#: saying "we looked and there was nothing wrong" is the same finding as VERIFIED_COMPLETE,
#: and giving it a separate name would let it be quietly excluded from the label count. The
#: negatives are the half that makes the labels usable.
OUTCOME_MAP = {
    "Verified Complete": "VERIFIED_COMPLETE",
    "Verified In Progress": "VERIFIED_IN_PROGRESS",
    "Not Started": "NOT_STARTED",
    "Not Found": "NOT_FOUND",
    "Record Mismatch": "RECORD_MISMATCH",
    "No Access": "NO_ACCESS",
    "False Positive": "VERIFIED_COMPLETE",
}

#: Columns this reads. Salesforce report exports carry the API names when you export as CSV.
REF_COLUMNS = ("Work_Ref__c", "Work Reference", "Work_Ref", "work_ref")
FINDING_COLUMNS = ("Officer_Finding__c", "Officer Finding", "officer_finding")
NOTES_COLUMNS = ("Notes__c", "Notes", "notes", "Officer_Notes__c")
ACTOR_COLUMNS = ("Verified_By__c", "Verified By", "Owner", "Owner Name", "Assigned To")


def pick(row: dict, names: tuple[str, ...]) -> str:
    """First column present under any of these names, so a report layout can vary."""
    for name in names:
        if name in row and str(row[name] or "").strip():
            return str(row[name]).strip()
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="Salesforce report exported as CSV")
    parser.add_argument("--role", default="auditor",
                        help="role to attribute these findings to (default: auditor)")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would be written and write nothing")
    args = parser.parse_args()

    if not args.csv_path.exists():
        raise SystemExit(f"no such file: {args.csv_path}")

    # utf-8-sig: Salesforce exports carry a byte-order mark that turns the first column
    # name into something no lookup matches.
    with args.csv_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SystemExit("that file has no rows")

    written, skipped, unknown = 0, 0, []
    for row in rows:
        work_ref = pick(row, REF_COLUMNS).upper()
        finding = pick(row, FINDING_COLUMNS)
        if not work_ref or not finding:
            skipped += 1
            continue

        outcome = OUTCOME_MAP.get(finding)
        if outcome is None:
            unknown.append(finding)
            skipped += 1
            continue

        notes = pick(row, NOTES_COLUMNS)
        actor = pick(row, ACTOR_COLUMNS) or "salesforce.import"
        note = f"[via Salesforce] {notes}".strip() if notes else "[via Salesforce]"

        if args.dry_run:
            print(f"  would write  {work_ref:<22} {outcome:<22} by {actor}")
        else:
            field.record(work_ref=work_ref, outcome=outcome, actor=actor,
                         role=args.role, notes=note)
        written += 1

    print(f"\n{'would write' if args.dry_run else 'wrote'} {written} finding(s); "
          f"skipped {skipped} row(s) with no finding recorded")

    if unknown:
        print("\nunrecognised finding values — add them to OUTCOME_MAP or fix the picklist:")
        for value in sorted(set(unknown)):
            print(f"  {value!r}")

    if not args.dry_run and written:
        readiness = field.label_readiness()
        print(f"\nverification store now holds {readiness['verifications']} real record(s) "
              f"across {readiness['works_verified']} work(s).")
        print(f"{readiness['labels_needed_to_fit_weights']} more before the fusion weights "
              f"could be fitted to what officers actually found.")
        print("\nNothing is refitted until then, and no accuracy is claimed.")


if __name__ == "__main__":
    main()
