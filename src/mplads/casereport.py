"""Generate a printable case report for one investigation lead.

An officer who decides a case warrants a visit needs to take something with them, and a
browser tab is not it. This produces the document that goes in the file: what the work is,
why it was surfaced, what the evidence actually says, what to check, and — on every single
page — the sentence that stops the document being read as an accusation.

**The footer is not decoration.** A PDF outlives the screen it came from. It gets emailed,
printed, attached to a note, and read months later by someone who never saw the caveat on
the case file. So the non-fraud contract is stamped on every page rather than buried in an
introduction nobody reaches.

Built on fpdf2, which ships core fonts only — those are Latin-1. Indian work descriptions
carry rupee signs, em-dashes and the occasional Devanagari fragment, so text is folded to
Latin-1 before it is drawn rather than crashing the export halfway down page two.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from io import BytesIO

from fpdf import FPDF

from mplads import config

LOGGER = logging.getLogger(__name__)

INK = (33, 29, 24)
MUTED = (110, 100, 88)
BRICK = (168, 69, 42)
FOREST = (47, 93, 63)
RULE = (221, 213, 198)
PANEL = (247, 244, 237)

#: Characters that appear constantly in this data and have no Latin-1 equivalent.
FOLD = {
    "₹": "Rs ", "—": " - ", "–": "-", "‘": "'", "’": "'",
    "“": '"', "”": '"', "…": "...", "·": "-", "→": "->",
    "◈": "*", "■": "*", "▲": "*", "◆": "*", "●": "*",
}


def _fold(text: object) -> str:
    """Latin-1 safe, single line, no control characters.

    Descriptions in this data routinely carry a pasted specification table. Collapsing the
    whitespace here keeps a paragraph from becoming three pages of ragged column headings.
    """
    value = " ".join(str(text if text is not None else "").split())
    for character, replacement in FOLD.items():
        value = value.replace(character, replacement)
    return value.encode("latin-1", "replace").decode("latin-1")


def _rupees(value: object) -> str:
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        return "unknown"
    if amount >= 1e7:
        return f"Rs {amount / 1e7:,.2f} crore"
    if amount >= 1e5:
        return f"Rs {amount / 1e5:,.2f} lakh"
    return f"Rs {amount:,.0f}"


class CaseReport(FPDF):
    """A4 report with a running header and the non-fraud contract on every page."""

    def __init__(self, work_ref: str, band: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.work_ref = _fold(work_ref)
        self.band = _fold(band or "NONE")
        self.set_auto_page_break(auto=True, margin=24)
        self.set_margins(18, 16, 18)
        self.set_title(f"Investigation case file {self.work_ref}")
        self.set_author("MPLADS Intelligence")

    def header(self) -> None:
        # Both halves get an explicit width. A zero-width cell means "run to the right
        # margin", so the first one leaves the cursor there and the second is born with
        # no room at all — which fpdf2 reports as being unable to render one character.
        self.set_xy(18, 16)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*BRICK)
        self.cell(100, 4, "MPLADS INVESTIGATION CASE FILE", align="L")
        self.set_text_color(*MUTED)
        self.set_font("Helvetica", "", 8)
        self.cell(74, 4, self.work_ref, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*RULE)
        self.set_line_width(0.3)
        self.line(18, 22, 192, 22)
        self.ln(8)

    def footer(self) -> None:
        self.set_y(-18)
        self.set_draw_color(*RULE)
        self.line(18, self.get_y() - 2, 192, self.get_y() - 2)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*MUTED)
        self.set_x(18)
        self.multi_cell(
            128, 3.4,
            "This is an investigation lead supported by evidence. It is not a finding of "
            "fraud, wrongdoing or misconduct by any person or body. A human reviews the "
            "evidence and decides what happens.",
            new_x="LMARGIN", new_y="NEXT",
        )
        self.set_xy(150, -18)
        self.set_font("Helvetica", "", 7)
        self.cell(42, 3.4, f"Page {self.page_no()}", align="R")

    # ---------------------------------------------------------------- building blocks

    def title_block(self, description: str) -> None:
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*INK)
        self.multi_cell(0, 7, _fold(description)[:180] or "MPLADS work", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        colour = {"HIGH": BRICK, "MEDIUM": (154, 107, 31), "LOW": FOREST}.get(
            self.band, MUTED)
        self.set_fill_color(*PANEL)
        self.set_text_color(*colour)
        self.set_font("Helvetica", "B", 8)
        label = (f"  {self.band} CONFIDENCE  " if self.band != "NONE"
                 else "  NOT SURFACED AS A LEAD  ")
        self.cell(self.get_string_width(label) + 2, 6, label, fill=True,
                  new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def section(self, heading: str) -> None:
        self.ln(3)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*BRICK)
        self.cell(0, 5, _fold(heading).upper(), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*RULE)
        self.line(18, self.get_y(), 192, self.get_y())
        self.ln(2.5)

    def field(self, label: str, value: str) -> None:
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTED)
        self.cell(42, 5, _fold(label))
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*INK)
        self.multi_cell(0, 5, _fold(value) or "-", new_x="LMARGIN", new_y="NEXT")

    def figures(self, items: list[tuple[str, str]]) -> None:
        """Headline numbers side by side, each in its own fixed column.

        Positioned explicitly rather than by cell flow: fpdf2 tracks one cursor, and a
        multi-column row built from `cell` alone ends up with columns whose width depends
        on what the previous one printed.
        """
        if not items:
            return
        left, usable = 18.0, 174.0
        width = usable / len(items)
        top = self.get_y()

        for index, (label, value) in enumerate(items):
            x = left + width * index
            self.set_xy(x, top)
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(*MUTED)
            self.cell(width, 4, _fold(label).upper())
            self.set_xy(x, top + 4)
            self.set_font("Helvetica", "B", 12)
            self.set_text_color(*INK)
            self.cell(width, 7, _fold(value))

        self.set_xy(left, top + 13)

    def bullet(self, text: str, marker: str = "-") -> None:
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*INK)
        self.cell(5, 5, marker)
        self.multi_cell(0, 5, _fold(text), new_x="LMARGIN", new_y="NEXT")

    def evidence_row(self, signal: str, family: str, detail: str) -> None:
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*INK)
        self.cell(0, 5, _fold(signal), new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 4, f"signal family: {_fold(family)}", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(*INK)
        self.multi_cell(0, 4.6, _fold(detail), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)


def build(case: dict, verifications: list[dict] | None = None) -> bytes:
    """Render one case file to PDF bytes."""
    identity = case.get("identity") or {}
    pdf = CaseReport(case.get("work_ref", "unknown"), case.get("confidence_band", "NONE"))
    pdf.add_page()

    pdf.title_block(identity.get("description", ""))

    pdf.figures([
        ("Recommended", _rupees(identity.get("recommended_amount"))),
        ("Exposure at risk", _rupees(case.get("exposure_rupees"))),
        ("Evidence families", f"{case.get('n_signal_families', 0)} of 6"),
    ])

    pdf.section("The work")
    pdf.field("Work reference", case.get("work_ref", ""))
    pdf.field("State", identity.get("state", ""))
    pdf.field("Constituency", identity.get("constituency", ""))
    pdf.field("Implementing agency", identity.get("implementing_agency", ""))
    pdf.field("Recommended by", identity.get("mp_name", ""))
    pdf.field("Recommended on", str(identity.get("recommendation_date", ""))[:10])
    pdf.field("Status", identity.get("status", ""))
    pdf.field("Work type", (case.get("archetype") or {}).get("label", ""))

    evidence = case.get("evidence") or []
    if evidence:
        pdf.section(f"Why this was surfaced - {len(evidence)} pieces of evidence")
        for item in evidence:
            pdf.evidence_row(item.get("signal", ""), item.get("family", ""),
                             item.get("detail", ""))
    else:
        pdf.section("Why this was surfaced")
        pdf.bullet("No signal fired on this work. It sits inside the norms of its peer "
                   "group on every measure computed.")

    peer = case.get("peer_context") or {}
    if peer:
        pdf.section("Peer context")
        pdf.field("Compared against", f"{peer.get('group_size', 0)} works "
                                      f"({_fold(peer.get('level', 'peer group'))})")
        percentile = peer.get("amount_percentile")
        if percentile is not None:
            pdf.field("Amount percentile", f"{round(float(percentile) * 100)}th")
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(0, 4, "A work is never compared against itself, and a peer group "
                             "smaller than the floor is widened rather than used thin.",
                        new_x="LMARGIN", new_y="NEXT")

    findings = case.get("compliance_findings") or []
    if findings:
        pdf.section("Lifecycle checks triggered")
        for finding in findings:
            pdf.bullet(f"{_fold(finding.get('check', ''))} "
                       f"({_fold(finding.get('authority', ''))}, "
                       f"{_fold(finding.get('severity', ''))}) - "
                       f"{_fold(finding.get('meaning', ''))}")
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(0, 4, "No check is asserted as an official rule. No statutory "
                             "threshold ships with this public data, so a statistical "
                             "outlier is never presented as a legal breach.",
                        new_x="LMARGIN", new_y="NEXT")

    warning = case.get("early_warning") or {}
    if warning.get("level") and warning["level"] != "LOW":
        pdf.section("Early warning")
        pdf.field("Level", warning.get("level", ""))
        pdf.field("Reason", warning.get("reason", ""))

    pdf.section("Recommended next step")
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 5, _fold(case.get("recommended_next_step", "")), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    for action in case.get("suggested_actions") or []:
        pdf.bullet(action, marker="[ ]")

    if verifications:
        pdf.section(f"Field verification history - {len(verifications)} record(s)")
        for record in verifications:
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*INK)
            outcome = _fold(record.get("outcome", "")).replace("_", " ")
            when = str(record.get("created_at", ""))[:10]
            pdf.cell(0, 5, f"{outcome}  -  {when}", new_x="LMARGIN", new_y="NEXT")
            if record.get("notes"):
                pdf.set_font("Helvetica", "", 8.5)
                pdf.multi_cell(0, 4.5, _fold(record["notes"]), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "I", 7.5)
            pdf.set_text_color(*MUTED)
            pdf.cell(0, 4, f"recorded by {_fold(record.get('actor', 'unknown'))} "
                           f"({_fold(record.get('role', ''))})",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1.5)

    pdf.section("How to read this document")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*INK)
    pdf.multi_cell(
        0, 4.6,
        _fold(
            "This work was selected by comparing it against works of the same kind in the "
            "same state, not against the portfolio as a whole. Confidence reflects how many "
            "independent families of evidence agree - one signal alone is usually noise. "
            "Exposure is the recommended amount weighted by the modelled chance the work "
            "does not complete on time; it is money to watch, not money lost, missing or "
            "stolen. No part of this system predicts wrongdoing, because the source data "
            "contains no examples of wrongdoing to learn from."
        ),
        new_x="LMARGIN", new_y="NEXT",
    )

    pdf.ln(3)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*MUTED)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pdf.multi_cell(0, 4, _fold(
        f"Generated {generated} from the MPLADS intelligence pipeline. "
        f"Data snapshot {config.SNAPSHOT_DATE.isoformat()}. "
        f"Figures are reproducible from the same snapshot."
    ), new_x="LMARGIN", new_y="NEXT")

    buffer = BytesIO()
    pdf.output(buffer)
    LOGGER.info("case report generated for %s", case.get("work_ref"))
    return buffer.getvalue()
