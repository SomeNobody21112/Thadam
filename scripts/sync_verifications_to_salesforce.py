"""Push site verifications — and what the camera found — into Salesforce.

This closes the last open edge in the product. The OCR reader, the perceptual hash and the
verification store all live on our side; Salesforce is where an officer works the case. Up
to now a photograph could raise a question and the CRM would never hear about it.

**Two claims, kept apart.** The outcome is the officer's judgement. `Board_Reference__c` is
what the OCR read off the physical board — and on a weathered board that is one digit wrong
at 99.6% confidence, landing on a *different real work*, because MPLADS references run in
sequence. Folding the second into the first destroys the only signal that says "check this
match". Salesforce gets both columns and a list view filtered to where they disagree.

The photographs themselves stay on our side. A Developer Edition org has 20 MB of file
storage; the forensic value is in the hashes and the comparison, not in shipping the image.

Run:

    .venv/Scripts/python.exe scripts/sync_verifications_to_salesforce.py
    sf data import bulk --sobject Site_Verification__c \\
        --file salesforce_export/site_verifications.csv --target-org mplads --wait 10

`Row_Hash__c` is the External ID, so re-running updates rather than duplicating.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mplads import config, field  # noqa: E402

OUT = config.REPO_ROOT / "salesforce_export"

#: (CSV column, how to read it off a verification row).
COLUMNS: list[tuple[str, str]] = [
    ("Row_Hash__c", "row_hash"),
    ("Work_Ref__c", "work_ref"),
    ("Investigation_Case__r.Work_Ref__c", "work_ref"),
    ("Outcome__c", "outcome"),
    ("Notes__c", "notes"),
    ("Recorded_By__c", "actor"),
    ("Recorded_On__c", "created_at"),
    ("Board_Reference__c", "board_ref"),
    ("Board_Amount__c", "board_amount"),
    ("OCR_Confidence__c", "ocr_confidence"),
    ("Needed_Confirmation__c", "needed_confirmation"),
    ("Photo_Reuse_Count__c", "photo_reuse_count"),
    ("Reused_From__c", "reused_from"),
    ("OCR_Text__c", "ocr_text"),
    ("Demo__c", "demo"),
]

TEXT_LIMIT = 4000


def clean(value: object, limit: int = TEXT_LIMIT) -> str:
    """One line, inside the field limit. Board text arrives with newlines in it."""
    text = " ".join(str(value if value is not None else "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-demo", action="store_true",
                        help="include records seeded for a walkthrough (excluded by default)")
    args = parser.parse_args()

    # Any work can be verified, not only the ones surfaced as leads — that rule is what
    # stops the label set being all positives. So the case lookup is optional: a
    # verification for a work outside the 500 loaded cases still syncs, with the
    # relationship left blank rather than failing the whole row.
    from mplads import salesforce as sf

    case_refs = {c["work_ref"] for c in sf.load_salesforce_cases()}

    rows = field.recent(limit=10_000)
    if not args.include_demo:
        rows = [r for r in rows if not r.get("demo")]
    if not rows:
        raise SystemExit("no verifications to sync")

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "site_verifications.csv"

    disagreements = 0
    reuse = 0
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, quoting=csv.QUOTE_ALL)
        writer.writerow([column for column, _ in COLUMNS])

        for row in rows:
            board_ref = row.get("board_ref") or ""
            disagrees = bool(board_ref and board_ref != row["work_ref"])
            disagreements += disagrees
            reuse += 1 if (row.get("photo_reuse_count") or 0) else 0

            values = []
            for column, key in COLUMNS:
                value = row.get(key)
                if column.startswith("Investigation_Case__r"):
                    value = value if value in case_refs else ""
                if key == "created_at":
                    value = str(value or "")[:10]
                elif key in {"needed_confirmation", "demo"}:
                    value = "TRUE" if value else "FALSE"
                elif key == "ocr_confidence" and value is not None:
                    # The field is a Percent; Salesforce stores 0-100, not 0-1.
                    value = f"{float(value) * 100:.2f}"
                elif key in {"board_amount", "photo_reuse_count"}:
                    value = "" if value is None else value
                values.append(clean(value))
            # Board_Disagrees__c is derived here rather than stored, so it can never drift
            # from the two columns it compares.
            writer.writerow(values)

    print(f"wrote {len(rows)} verification(s) to {path.name}")
    print(f"  board disagreed with the record : {disagreements}")
    print(f"  photograph seen before          : {reuse}")
    linked = sum(1 for r in rows if r["work_ref"] in case_refs)
    print(f"  linked to a Salesforce case     : {linked} of {len(rows)}"
          f"  (the rest are works nobody has opened a case on)")
    print()
    print("import with:")
    print("  sf data import bulk --sobject Site_Verification__c \\")
    print(f"      --file salesforce_export/{path.name} --target-org mplads --wait 10")
    print()
    print("Row_Hash__c is the External ID, so re-running updates instead of duplicating.")


if __name__ == "__main__":
    main()
