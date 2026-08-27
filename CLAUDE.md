# CLAUDE.md — mplads-intel

Read this first, every session. Do not re-read the whole repo.
For the full build history and open items, read `docs/HANDOFF.md`.

## What this is

An AI-assisted monitoring layer over MPLADS/eSAKSHI work-lifecycle data. It learns what
normal work looks like nationally, compares each work against its true peers, predicts
completion risk, detects duplicates and behavioural change, fuses those signals into an
explainable case file, and ranks case files by audit return-on-investment.

**SIH 2026 · PS 26102 (MoSPI) · Team Morior Invictus.**

**Status: feature-complete and demoable.** Pipeline, 3 trained models, 7 intelligence
engines, REST API with RBAC + audit log, React app with 9 screens, a data-grounded
chatbot, 10 languages, and a synthetic-validation harness all work end to end.

## The six hard constraints

Product constraints, not style preferences. They must survive into code and UI copy.

1. **No fraud verdicts.** Output is an *investigation lead* with evidence. No field,
   variable, column or label may be named `fraud_probability`, `is_fraud`, `fraud_score`
   or `fraudulent`. Enforced by `test_no_fraud_language_in_the_source_tree`, which greps
   the whole `src/` tree — it has caught real violations twice, including inside our own
   safety filters. **Rephrase, never exempt.**
2. **No fraud classifier.** There are no fraud labels in the data. Any supervised model
   claiming to predict fraud is fabricated. Scoring is transparent, weighted, rule-based.
3. **Silhouette is not accuracy.** Ours is 0.050. Say so, in code comments, docs and UI.
4. **`ACTUAL_AMOUNT` is not expenditure.** 98.35% of completed works have it exactly equal
   to `RECOMMENDED_AMOUNT`; zero exceed 1.05×. No overrun signal exists. DATA_CONTRACT §6.
5. **Human-in-the-loop.** Every recommendation ends in "a human should check X".
6. **Field verification is the only ground truth there will ever be.** No dataset says
   which works were problems, so nothing here has been validated against an outcome. What
   an officer found on site is the sole exception, which is why those records are
   immutable, attributed, and counted honestly: `field.label_readiness()` reports the gap
   to 500 rather than implying it is closed, and records seeded for a walkthrough are
   excluded from the count.

## Verified numbers — quote these, never estimate

| Measure | Value |
|---|---|
| Works | **210,993** (210,987 after dropping 6 with amount ≤ 0) |
| Raw stage rows | 480,768 = 3,987 MP-summary + 476,781 work-stage |
| Completed / open | 85,773 / 125,220 |
| Recommended / exposure | ₹11,565 Cr / ₹1,302 Cr |
| Leads | 37,705 (**4,478 HIGH**, 33,227 MEDIUM) |
| States / constituencies / agencies | 36 / 545 / 778 |
| Archetypes | 50 (49 named, 1 honestly "uninterpretable"), K by sweep, silhouette **0.050** |
| Cox C-index (held out) | **0.6759** |
| IsolationForest flagged | 4,220 |
| Duplicate pairs | 223,407 → **47,709 concerning** |
| Compliance-flagged works | 5,946 |
| Agencies changed | 73 of 697 |
| Health Index | 62.9 / 100 |
| Audit plan @ 50 auditor-days | **100 works / 23 agency visits / ₹47.1 Cr** covered |
| Same budget, ranking top-down | 74 works / 37 visits / ₹42.4 Cr (90%) |
| Synthetic validation | **69.2%** overall detection (stalled 96.1%, inflated 83.2%, break 58.0%, cloned 50.0%) |
| Tests | **210 passing**, 2 skipped |

## Stack & layout

Python 3.11 (`.venv/`, uv) · pandas · scikit-learn · lifelines · FastAPI · anthropic ·
React + Vite + Recharts. **Docker and Node: Node installed, Docker NOT.**

```
src/mplads/
  config.py            paths, seeds, SNAPSHOT_DATE=2026-05-26, weights, .env loader
  cli.py               mplads <paths|profile|ingest|pipeline|api|train|validate|tokens|audit>
  ingest/              loader.py (typed load) · normalise.py (canonical parquet) · schema.py
  train.py             3 trained models -> data/artifacts/models/
  pipeline.py          Learn->Compare->Predict->Explain->Prioritise -> data/artifacts/
  intelligence/        duplicates · temporal · compliance · early_warning · transparency · labels
  validation/synthetic.py   plant known anomalies, measure detection
  llm.py               Claude briefings + translation, template fallback
  chat.py              15 read-only tools over ALL 210,993 works + offline router
  intelligence/targeting.py  budgeted audit plan — travel-aware, beats the ranking
  casereport.py        one printable PDF per case, contract stamped on every page
  salesforce.py        CRM case mirror + Agentforce topic router
  ocr.py               read a work board; refuses to settle an ambiguous reference
  photohash.py         pHash + dHash — the same *picture*, not the same file
  field.py             immutable, attributed site-verification records
  api/                 app.py · auth.py (JWT/RBAC) · audit.py (hash chain) · strings/translations
frontend/src/          App · pages/ (12) · components/ · AuthContext · I18nContext · RoleContext
demo/                  WALKTHROUGH.md + 5 generated work-board photographs
scripts/               profile_data.py · make_demo_data.py
```

## Commands

```bash
.venv/Scripts/python.exe -m pytest                    # 210 tests
.venv/Scripts/python.exe -m mplads.cli ingest         # raw -> data/interim (~40s)
.venv/Scripts/python.exe -m mplads.cli train          # 3 models (~90s)
.venv/Scripts/python.exe -m mplads.cli pipeline       # artifacts (~50s)
.venv/Scripts/python.exe -m mplads.cli validate       # synthetic harness (~35s)
.venv/Scripts/python.exe scripts/make_demo_data.py    # demo boards + seeded records
.venv/Scripts/python.exe -m uvicorn mplads.api.app:app --port 8000
cd frontend && npm run dev                            # needs PATH="/c/Program Files/nodejs:$PATH"
```

Add a dependency: `python -m uv pip install --python .venv/Scripts/python.exe <pkg>`, then
add it to `pyproject.toml`. Do not add dependencies without asking.

## Conventions

- Type hints everywhere. `pathlib`, never string paths. No notebooks in `src/`.
- **Never hardcode a path, seed or date.** Import from `mplads.config`.
- Every transform logs row count at entry and exit. `_log_counts()` **raises** if a count
  changes without a stated reason — a silent drop is impossible, not merely discouraged.
- Deterministic: dedup sorts on `(recommendation_date, work_ref, source_file,
  raw_row_index)` so results never depend on file order.
- `Dataset/` is read-only. Never write into it.
- Expensive work is cached and skipped on rerun.

## Data facts you must not get wrong

Full detail in `docs/DATA_CONTRACT.md`. The ones that bite:

- **Join key is `(WORK_RECOMMENDATION_DTL_ID, mp_id)` → `work_ref`.** Never `WORK_ID`
  (82% null, issued only at completion — renamed `portal_work_id` as a guard rail).
- **No sanction date exists.** Sanction rows copy `RECOMMENDATION_DATE` verbatim on
  100.00% of 179,676 works. Presence is testable; timing is unknowable.
- **Censoring anchor = `max(RECOMMENDATION_DATE)` = 2026-05-26.** `max(all dates)` lands in
  2044 and inflates every open duration by ~18 years.
- **`ACTIVITY_NAME` is a composite**: `WS/MP<code>/<FY>/<serial>-<official category>`.
  Parsing yields **118 official categories at 93% coverage** — a free interpretable peer
  axis. Both the deck and the previous team called this field unusable; they never split it.
- **The 3,987 "corrupt" rows are MP-level totals.** They carry `Total_Amt`, which is null on
  all 476,781 work rows. Used as a reconciliation oracle — median ratio exactly 1.0000.
- **695 orphans** (no recommendation row), **70** completed-without-sanction, **1,194**
  back-dated, **9** out-of-window dates. Carry and flag; several are conformance signals.
- **No district column.** `IDA_NAME` is a district *office*; `CONSTITUENCY` is a
  constituency. All Rajya Sabha works share `CONSTITUENCY = "Sitting Rajya Sabha"`.
- **DO NOT USE:** `ACTUAL_AMOUNT`, `WORK_ID`, `AVERAGE_RATING`, `FILE_STATUS`, `Sno`,
  `MP_NAME`, `Total_Amt` at work grain.

## Design system (current)

Light **parchment** ground `#f7f4ed`, ink text, **terracotta `#a8452a`** primary, forest
green secondary, aged brass for figures. **No blue anywhere** — that was a deliberate move
away from the dark-blue dashboard look, which reads as an AI product. Fraunces (serif
display) + Noto Sans (body, with all Indic subsets) + Roboto Mono (figures).

**Severity is not a palette choice.** `frontend/src/severity.js` is the single source for
every band, level and classification colour, with measured contrast ratios in its header —
six pages each kept their own copy until HIGH and LOW ended up the same terracotta in two of
them. Red and amber cannot be separated under deuteranopia, so severity is never carried by
colour alone: every indicator also has a `glyph` (■ ▲ ◆ ● ·) and its text label.

## The field-verification loop

The one place in this product that creates data. `POST /api/ocr` reads a photographed work
board, matches it against **all 210,993 works** (not just the leads), and fingerprints it
against every photograph submitted before. `POST /api/verify/{work_ref}` appends what the
officer found. Three rules hold it together:

- **A match is never settled by the machine.** OCR confidence is confidence in the pixels.
  A weathered board reads one digit wrong at 99.6% and lands on a *different real work* —
  MPLADS references run in sequence. So `ocr.match_to_work` returns every real reference one
  character away, cross-checks the amount painted on the board, and sets
  `needs_confirmation`; the UI will not save until a human ticks the box.
- **A re-used photograph is a question, not a finding.** `photohash` catches a resized,
  re-compressed, brightened copy that a checksum misses — but two phases of one road
  legitimately look identical from the roadside. Report, never conclude.
- **Writing requires a name.** Reading is open (`REQUIRE_AUTH=0`); `auth.require_identity`
  refuses an unattributed verification. A presented token is honoured even when auth is
  optional — the flag says whether a badge is *required*, not whether we read the one given.

Works that were never surfaced return a "clear record" case file rather than 404. That is
not cosmetic: if only flagged works can be visited, every label ever collected is a positive
and the weights can never be corrected by one.

## The audit plan (UVP-7)

`intelligence/targeting.py` answers the question ranking cannot: *"I have twenty
auditor-days — where do I send them?"* Cases do not cost the same to check, so this is a
budgeted selection, not a sort:

- first work at an implementing agency costs **1.0 auditor-day** (travel, visit, write-up)
- every further work there costs **0.35** — the auditor is already standing there

That one dependency is why a plan beats the ranking it is built from. Opening an agency is
judged on the **bundle** it unlocks, not its best single case; a purely myopic greedy takes
a large remote work and never notices six mediocre ones going cheap next door.

**It is a heuristic and says so.** Ratio-greedy is not optimal — `test_the_planner_is_
greedy_and_does_not_pretend_otherwise` pins a case where it trails the clustered optimum.
The comparison table is built to be able to report that we lost; a table hard-wired to
crown our own strategy would be decoration, not evidence.

## The resolution loop

An officer finding recorded in the Salesforce hub writes an **immutable, attributed**
record into `field.py`, the same store the in-app verification writes to. Stage moves are
workflow and mutable; findings are evidence and are not. `salesforce.update_case_stage`
raises rather than writing "anonymous" into the label set, and "False Positive" maps to
`VERIFIED_COMPLETE` on purpose — a negative label is half of what makes a label set usable,
and giving it its own name is how it quietly stops being counted.

## Open items

1. **API key has no credits.** The key in `.env` authenticates but billing is empty, so
   every LLM path uses its fallback. Nothing else changes when credits are added.
   The key was pasted in plaintext in chat — **it should be rotated.**
2. **Docker not installed** — packaging is the only FRD phase not attempted.
3. **`FLAG = 2`** (957 works) meaning still UNVERIFIED. The Vonter file's
   `Rejected by IDA` column may answer it empirically. DATA_CONTRACT §13 Q1.
4. **Vite may bind 5174** if an old process holds 5173. Kill stale servers before demoing.
