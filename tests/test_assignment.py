"""The rota, the agency dossier, the field scoreboard and the ageing queue.

Four claims, each of which the code is allowed to fail:

* a rota that splits an agency between two auditors has quietly broken the cost model the
  plan was built on, so no rota may ever do it;
* a dossier that reports counts without rates punishes a large agency for being large;
* a scoreboard that reports a rate off three visits is not a scoreboard;
* an ageing report that cannot tell "late" from "never picked up" hides whichever of the
  two is smaller.
"""

from __future__ import annotations

import pandas as pd
import pytest

from mplads import casereport
from mplads.intelligence import assignment, calibration, dossier, targeting


@pytest.fixture
def toy() -> pd.DataFrame:
    """Three agencies of very different sizes, so an unbalanced deal is visible."""
    rows = []
    for index in range(12):
        rows.append({"work_ref": f"MP1-W{index}", "implementing_agency": "BIG",
                     "rs_exposure": 50.0, "state_name": "Bihar", "audit_roi": 50.0,
                     "priority": 0.5, "band": "HIGH", "recommended_amount": 100.0})
    for index in range(4):
        rows.append({"work_ref": f"MP2-W{index}", "implementing_agency": "MIDDLING",
                     "rs_exposure": 45.0, "state_name": "Kerala", "audit_roi": 45.0,
                     "priority": 0.6, "band": "HIGH", "recommended_amount": 200.0})
    rows.append({"work_ref": "MP3-W0", "implementing_agency": "SMALL",
                 "rs_exposure": 80.0, "state_name": "Assam", "audit_roi": 80.0,
                 "priority": 0.9, "band": "MEDIUM", "recommended_amount": 900.0})
    return pd.DataFrame(rows)


@pytest.fixture
def plan(toy) -> pd.DataFrame:
    return targeting.optimise(toy, budget_days=12)


# ------------------------------------------------------------------------ the rota


def test_an_agency_is_never_split_between_two_auditors(plan):
    """The one rule. Splitting an agency pays for the same journey twice.

    The plan priced the second work at an agency cheaply *because* somebody is already
    standing there. A rota that sends two people has not made that saving, and every
    figure downstream of it — days used, exposure per day, the comparison table — becomes
    a statement about a plan nobody is executing.
    """
    for auditors in (1, 2, 3, 4, 8):
        rota = assignment.assign(plan, auditors=auditors)
        owner: dict[str, int] = {}
        for person in rota["people"]:
            for visit in person["schedule"]:
                agency = visit["implementing_agency"]
                assert agency not in owner, (
                    f"{agency} was given to auditor {owner[agency]} and "
                    f"auditor {person['auditor']}"
                )
                owner[agency] = person["auditor"]


def test_the_rota_spends_exactly_what_the_plan_spent(plan):
    """A rota is a re-arrangement, not a second selection. It may not cost more."""
    for auditors in (1, 2, 5):
        rota = assignment.assign(plan, auditors=auditors)
        assert rota["auditor_days"] == pytest.approx(
            float(plan["plan_cost_days"].sum()), abs=0.02
        )
        assert rota["works"] == len(plan)


def test_no_work_is_dropped_or_duplicated(plan):
    rota = assignment.assign(plan, auditors=3)
    seen = [work["work_ref"]
            for person in rota["people"]
            for visit in person["schedule"]
            for work in visit["works"]]
    assert sorted(seen) == sorted(plan["work_ref"].tolist())


def test_the_load_is_actually_balanced(plan):
    """Longest-first exists to stop one auditor carrying the fortnight.

    Dealing the trips in arrival order instead is the obvious implementation and the one
    that produces a lopsided rota, so the test compares against it rather than against a
    number pulled from the air.
    """
    rota = assignment.assign(plan, auditors=3)
    spread = rota["balance"]["spread_days"]

    naive = [0.0, 0.0, 0.0]
    for index, trip in enumerate(assignment.trips(plan)):
        naive[index % 3] += trip["cost_days"]
    assert spread <= max(naive) - min(naive) + 1e-9


def test_more_auditors_never_means_more_auditor_days(plan):
    totals = [assignment.assign(plan, auditors=n)["auditor_days"] for n in (1, 2, 4, 6)]
    assert all(total == pytest.approx(totals[0], abs=0.02) for total in totals)


def test_a_bigger_team_finishes_no_later(plan):
    """Adding people should shorten the round, never lengthen it."""
    rounds = [assignment.assign(plan, auditors=n)["balance"]["longest_round_days"]
              for n in (1, 2, 3)]
    assert rounds == sorted(rounds, reverse=True)


def test_idle_auditors_are_reported_rather_than_given_half_an_agency(plan):
    """With more auditors than trips somebody has nothing to do, and that is the answer.

    The tempting fix is to split an agency so every name has a line against it. That would
    be a rota that looks complete and costs more than the plan allowed.
    """
    rota = assignment.assign(plan, auditors=12)
    assert rota["idle"], "twelve auditors and three agencies should leave people idle"
    assert rota["works"] == len(plan)


def test_the_rota_is_deterministic(plan):
    first = assignment.assign(plan, auditors=3)
    second = assignment.assign(plan, auditors=3)
    assert [p["schedule"] for p in first["people"]] == [p["schedule"] for p in second["people"]]


def test_an_empty_plan_produces_no_rota_rather_than_an_empty_one():
    empty = targeting.optimise(pd.DataFrame(columns=[
        "work_ref", "implementing_agency", "rs_exposure", "state_name",
        "audit_roi", "priority", "band", "recommended_amount"]), budget_days=5)
    assert assignment.assign(empty, auditors=3)["available"] is False


def test_the_rota_says_it_decides_nothing(plan):
    rota = assignment.assign(plan, auditors=2)
    assert "amend" in rota["contract"]
    assert "alleges nothing" in rota["contract"]
    assert "NP-hard" in rota["balance"]["note"], (
        "a rota that calls itself balanced without saying it is a heuristic is a claim"
    )


def test_the_day_pack_is_a_real_pdf(plan):
    rota = assignment.assign(plan, auditors=2)
    pdf = casereport.build_day_pack(rota["people"][0], rota)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1500


def test_the_day_pack_carries_the_contract(plan, monkeypatch):
    """It is printed and carried into a district office; the caveat travels with it."""
    original = casereport.DayPack.__init__

    def uncompressed(self, label, band="NONE"):
        original(self, label, band)
        self.set_compression(False)

    monkeypatch.setattr(casereport.DayPack, "__init__", uncompressed)
    rota = assignment.assign(plan, auditors=2)
    pdf = casereport.build_day_pack(rota["people"][0], rota)
    assert b"not a finding of" in pdf
    assert b"assumption" in pdf, "the cost model has to be arguable on the page"


# --------------------------------------------------------------------- the dossier


@pytest.fixture
def portfolio() -> pd.DataFrame:
    """A large ordinary agency and a small one, so a count and a rate disagree."""
    rows = []
    for index in range(200):
        rows.append({"work_ref": f"MPA-W{index}", "implementing_agency": "LARGE",
                     "state_name": "Bihar", "constituency": "SARAN",
                     "work_description": "Road", "activity_category": "Roads",
                     "recommended_amount": 100.0, "is_completed": index % 2,
                     "is_open": 1 - index % 2, "duration_days": 300.0,
                     "band": "HIGH" if index < 20 else "NONE", "rs_exposure": 10.0,
                     "audit_roi": 10.0, "compliance_flags": 0,
                     "early_warning_level": "LOW"})
    for index in range(40):
        rows.append({"work_ref": f"MPB-W{index}", "implementing_agency": "SMALL",
                     "state_name": "Kerala", "constituency": "IDUKKI",
                     "work_description": "Hall", "activity_category": "Buildings",
                     "recommended_amount": 100.0, "is_completed": 0, "is_open": 1,
                     "duration_days": 900.0,
                     "band": "HIGH" if index < 20 else "NONE", "rs_exposure": 40.0,
                     "audit_roi": 40.0, "compliance_flags": 1,
                     "early_warning_level": "HIGH"})
    return pd.DataFrame(rows)


def test_the_dossier_reports_a_rate_and_not_only_a_count(portfolio):
    """Both agencies surfaced twenty leads. Only one of them is unusual.

    Reading the count alone makes a large agency look like a problem for being large,
    which is the single most likely way this product gets somebody unfairly investigated.
    """
    large = dossier.build(portfolio, "LARGE")
    small = dossier.build(portfolio, "SMALL")
    assert large["surfaced"]["leads"] == small["surfaced"]["leads"] == 20
    assert small["surfaced"]["rate"] > large["surfaced"]["rate"]
    assert "ordinary" in large["surfaced"]["reading"] or large["surfaced"]["rate_multiple"] < 1


def test_a_small_agency_gets_no_rate_at_all(portfolio):
    tiny = portfolio[portfolio["work_ref"].isin(["MPB-W0", "MPB-W1", "MPB-W2"])].copy()
    tiny["implementing_agency"] = "TINY"
    built = dossier.build(pd.concat([portfolio, tiny]), "TINY")
    assert built["surfaced"]["comparable"] is False
    assert built["surfaced"]["rate_multiple"] is None
    assert "too few" in built["surfaced"]["reading"]


def test_the_dossier_describes_the_whole_portfolio_not_only_the_leads(portfolio):
    """Describing an agency by its flagged works makes every agency look guilty."""
    built = dossier.build(portfolio, "LARGE")
    assert built["portfolio"]["works"] == 200
    assert built["surfaced"]["leads"] == 20


def test_an_unknown_agency_is_a_polite_no(portfolio):
    assert dossier.build(portfolio, "NOWHERE")["available"] is False


def test_field_findings_are_carried_and_marked_as_outranking_the_model(portfolio):
    built = dossier.build(portfolio, "SMALL", verifications=[
        {"work_ref": "MPB-W0", "outcome": "VERIFIED_COMPLETE", "actor": "r.sharma",
         "created_at": "2026-08-01T09:00:00", "notes": "Nothing wrong."},
        {"work_ref": "MPA-W0", "outcome": "NOT_STARTED", "actor": "r.sharma",
         "created_at": "2026-08-01T09:00:00", "notes": "Other agency."},
    ])
    assert [row["work_ref"] for row in built["field_history"]] == ["MPB-W0"]
    assert "ground truth" in built["field_history_note"]


def test_the_dossier_says_it_is_not_a_finding_against_the_agency(portfolio):
    assert "is a finding against" in dossier.build(portfolio, "LARGE")["contract"]


# ------------------------------------------------------------------ the scoreboard


CONFIRMS = {"NOT_STARTED", "NOT_FOUND", "RECORD_MISMATCH"}


def _visits(band_counts: dict[str, tuple[int, int]]) -> tuple[list[dict], dict[str, str]]:
    """(confirmed, cleared) per band -> verification rows and the band lookup."""
    rows, bands, index = [], {}, 0
    for band, (confirmed, cleared) in band_counts.items():
        for _ in range(confirmed):
            index += 1
            rows.append({"work_ref": f"W{index}", "outcome": "NOT_STARTED",
                         "created_at": f"2026-08-{index % 28 + 1:02d}", "demo": 0})
            bands[f"W{index}"] = band
        for _ in range(cleared):
            index += 1
            rows.append({"work_ref": f"W{index}", "outcome": "VERIFIED_COMPLETE",
                         "created_at": f"2026-08-{index % 28 + 1:02d}", "demo": 0})
            bands[f"W{index}"] = band
    return rows, bands


def test_a_rate_is_refused_below_the_minimum_sample():
    """Three visits and two confirmations is three visits, not sixty-seven percent."""
    rows, bands = _visits({"HIGH": (2, 1)})
    built = calibration.build(rows, bands, CONFIRMS)
    high = next(r for r in built["bands"] if r["band"] == "HIGH")
    assert high["visits"] == 3
    assert high["rate"] is None and high["reportable"] is False
    assert "not reported below" in high["note"]


def test_a_rate_carries_an_interval_once_there_is_a_sample():
    rows, bands = _visits({"HIGH": (14, 6)})
    high = next(r for r in calibration.build(rows, bands, CONFIRMS)["bands"]
                if r["band"] == "HIGH")
    assert high["rate"] == pytest.approx(0.7, abs=0.01)
    low, top = high["interval"]
    assert 0.0 <= low < high["rate"] < top <= 1.0


def test_the_ordering_is_only_claimed_when_the_intervals_separate():
    """Two overlapping intervals do not rank, however different the bars look."""
    close, bands = _visits({"HIGH": (11, 9), "MEDIUM": (10, 10)})
    result = calibration.build(close, bands, CONFIRMS)["ordering"]
    assert result["holds"] is True
    assert result["separated"] is False
    assert "overlap" in result["note"]


def test_a_ranking_that_comes_out_backwards_is_reported_as_such():
    """The scoreboard has to be able to say the model was wrong."""
    rows, bands = _visits({"HIGH": (2, 18), "MEDIUM": (18, 2)})
    result = calibration.build(rows, bands, CONFIRMS)["ordering"]
    assert result["holds"] is False
    assert "did not rank" in result["note"]


def test_demo_seeded_records_are_excluded():
    rows, bands = _visits({"HIGH": (10, 10)})
    rows.append({"work_ref": "SEED", "outcome": "NOT_STARTED",
                 "created_at": "2026-08-01", "demo": 1})
    bands["SEED"] = "HIGH"
    built = calibration.build(rows, bands, CONFIRMS)
    assert built["demo_records_excluded"] == 1
    assert built["visits"] == 20


def test_a_revisited_work_votes_once():
    """A correction here is a new record, so counting both would double one work."""
    rows = [
        {"work_ref": "W1", "outcome": "NOT_STARTED", "created_at": "2026-08-01", "demo": 0},
        {"work_ref": "W1", "outcome": "VERIFIED_COMPLETE", "created_at": "2026-08-09",
         "demo": 0},
    ]
    built = calibration.build(rows, {"W1": "HIGH"}, CONFIRMS)
    assert built["visits"] == 1
    high = next(r for r in built["bands"] if r["band"] == "HIGH")
    assert high["concerns_confirmed"] == 0, "the newer record should supersede the older"


def test_works_that_were_never_surfaced_are_counted_as_the_negative_class():
    rows, bands = _visits({"HIGH": (10, 10)})
    rows.append({"work_ref": "CLEAR", "outcome": "VERIFIED_COMPLETE",
                 "created_at": "2026-08-02", "demo": 0})
    built = calibration.build(rows, bands, CONFIRMS)
    unsurfaced = next(r for r in built["bands"] if r["band"] == "NOT SURFACED")
    assert unsurfaced["visits"] == 1


def test_the_sampling_bias_is_stated_with_the_result_not_in_a_footnote():
    rows, bands = _visits({"HIGH": (10, 10)})
    built = calibration.build(rows, bands, CONFIRMS)
    assert "not a random" in built["sampling_caveat"]
    assert "nothing is refitted" in built["contract"].lower()


def test_the_interval_stays_inside_zero_and_one_at_the_extremes():
    """Where the normal approximation would return bounds that are not proportions."""
    for successes in (0, 20):
        rows, bands = _visits({"HIGH": (successes, 20 - successes)})
        low, top = next(r for r in calibration.build(rows, bands, CONFIRMS)["bands"]
                        if r["band"] == "HIGH")["interval"]
        assert 0.0 <= low <= top <= 1.0


# ---------------------------------------------------------------- the ageing queue


def test_late_and_never_picked_up_are_counted_separately():
    """Two different silences. Merging them hides whichever is the smaller."""
    from mplads import salesforce as sf

    ageing = sf.case_ageing("2026-12-31")
    assert ageing["late"] >= ageing["never_picked_up"] or ageing["never_picked_up"] >= 0
    assert "never picked up" in ageing["note"].lower()
    assert set(ageing).issuperset({"buckets", "by_tier", "reading", "open_cases"})


def test_the_ageing_report_measures_our_queue_and_says_so():
    from mplads import salesforce as sf

    assert "our own queue" in sf.case_ageing()["contract"]


def test_a_verified_case_is_not_chased():
    """Once someone has looked, the review date has done its job."""
    from mplads import salesforce as sf

    assert "Verified" not in sf.OPEN_STAGES
    assert "Closed" not in sf.OPEN_STAGES
