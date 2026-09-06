# PROJECT CONSTITUTION v2 — SIH26102 MPLADS AI Monitoring

**Single source of truth · Team Morior Invictus · St. Joseph's Institute of Technology, Chennai**
**v1 synthesized 2026-08-24 · v2 re-synthesized 2026-08-27 against the running codebase**

> **How to use this document.** This is the authoritative reference. If any other document
> conflicts with it, resolve by: (1) prefer the latest validated real-data audit; (2) prefer
> actual computation over assumption; (3) preserve uncertainty when unresolved; (4) document
> conflicts, never silently pick the convenient answer.
>
> **Provenance of v2.** Every figure below was read out of the working tree on 2026-08-27 —
> `data/artifacts/stats.json`, `models/metrics.json`, `validation.json`, the FastAPI route
> table, and a full `pytest` run. Where v1 and the code disagree, **the code wins and the
> disagreement is recorded**. Nothing here is estimated.

---

## 0. What changed since v1 — read this first

v1 was written when the real-data modules were *specified but not implemented*. That is no
longer true, and v1 is now wrong in both directions.

### v1 said "not built" — it is built

| v1 claim | Reality on 2026-08-27 |
|---|---|
| §16 "real-data modules (Phases 1–7) specified but **NOT yet implemented**" | **All seven phases run end to end** in ~4 minutes on a laptop |
| §8 React dashboard "Prototype" | **12 screens shipped** |
| §8 RBAC + audit log "Prototype" | **JWT auth, 4 seeded roles, hash-chained audit log** |
| §2 Photo verification "Synthetic/Future" | **Built on real records** — pHash + dHash, OCR, immutable field records |
| §10 "3/3 tests" | **189 passing, 2 skipped** |

### v1 never anticipated these — they exist now

- **Salesforce CRM + Agentforce integration** — `salesforce.py`, 4 endpoints, a 12th screen, CSV export/import, a 5-stage investigation Path.
- **Field verification loop** — the only part of the product that *creates* data, and the only route to the fraud labels §3.2 says do not exist.
- **OCR of site display boards** — RapidOCR, CPU-only, refuses to settle an ambiguous reference.
- **Assistant** — 18 read-only tools, deterministic offline router, tool-trace receipts.
- **10-language interface** — 182 keys, 100% coverage, static bundles.

### v1 promised things still missing

Choropleth screen · audit-capacity budget · money-gap funnel · Docker · the evaluation depth
in §10. Tracked honestly in §16.

---

## 1. What we are building (unchanged from v1 — still correct)

An **AI-assisted forensic monitoring and decision-support system for MPLADS** that learns what
"normal" work looks like from the national portfolio, flags statistically and behaviourally
unusual activity **relative to genuine peers**, estimates **completion risk** and the **₹
exposure** attached to it, detects **when an administrative unit's behaviour changes**, and
helps authorities **prioritise limited investigative capacity** — producing **investigation
leads with evidence, never fraud verdicts.**

It is **not** "an AI dashboard that gives every work a fraud score." That framing was
considered and rejected (§7, §14).

**v2 adds one rung to the ladder that v1 did not have:**

```
What happened?          -> ingest + normalise the real MPLADS lifecycle
What looks unusual?     -> peer-conditional anomaly (not global)
Why is it unusual?      -> evidence fusion + explainable case file
Is behaviour changing?  -> entity trend + level-shift detection
What may go wrong?      -> completion-risk / time-to-event model
How much is at stake?   -> Rs exposure-at-risk quantification
Investigate first?      -> Audit-ROI ranking
WHAT DID WE FIND?       -> field verification: what the officer saw on site   [NEW in v2]
```

That last rung matters more than it looks. §3.2's central limitation is *"no fraud labels
exist."* Verification records **are** those labels, accumulating one site visit at a time.

---

## 2. Verified numbers — quote these, never estimate

Read from artifacts on 2026-08-27.

| Measure | Value | v1 said |
|---|---|---|
| Works | **210,993** (210,987 after dropping 6 with amount ≤ 0) | 210,993 ✓ |
| Raw stage rows | **480,768** = 3,987 MP-summary + 476,781 work-stage | 480,768 ✓ |
| Completed / open | **85,773 / 125,220** | 85,531 full-lifecycle (superseded) |
| Recommended / exposure | **₹11,565 Cr / ₹1,302 Cr** | not stated |
| States / constituencies / agencies | **36 / 545 / 778** | ✓ |
| Investigation leads | **37,705** | not stated |
| Confidence bands | **HIGH 4,478 · MEDIUM 33,227 · LOW 107,978 · NONE 65,310** | not stated |
| Archetypes | **50**, K by silhouette sweep, 187,865 descriptions clustered | "~30–60, not fixed 50" |
| Silhouette | **0.050** | ✓ (framing correct) |
| Cox C-index (held out) | **0.6759**, n_fit 60,000 | not stated |
| IsolationForest flagged | **4,220** | not stated |
| Duplicate pairs | **223,407** → **47,709 concerning** | ✓ |
| Compliance checks / works flagged | **8 checks / 6,711** | not stated |
| Agencies with a level shift | **73 of 697** | not stated |
| Health Index | **62.9 / 100** | not stated |
| Synthetic detection | **69.2%** overall (stalled 96.1 · inflated 83.2 · break 58.0 · cloned 50.0), 904 planted | "AP ≈ 0.95, precision@20 ≈ 0.95" — **superseded** |
| Tests | **189 passing, 2 skipped** | "3/3" |
| Interface languages | **10**, 182 keys, **100%** coverage | not in v1 |
| API endpoints | **35** | not in v1 |

⚠️ **v1's §10 headline "AP ≈ 0.95, precision@20 ≈ 0.95" is from the old synthetic prototype
and must not be quoted.** The current harness reports **69.2% detection** with recall@k
reported separately. Quoting 0.95 to a judge is quoting a system that no longer exists.

---

## 3. Data we have / do NOT have / consequences

### 3.1 Real and verified

- **210,993 works**, **480,768 stage rows**, 36 states/UTs, 545 constituencies, 778 agencies.
- Sources: **`Vonter/india-mplads-works`** (ODbL) and **`in-rolls/mplads`** (scraped from
  eSAKSHI, no repo licence → reproduce via its scraper and attribute). Both trace to official
  MPLADS/eSAKSHI portals.

### 3.2 What we do NOT have

- **No fraud labels.** None exist publicly. *(v2 caveat: field verification is now creating
  them — 2 real records, 498 short of the 500 needed. See §11.)*
- **No independent expenditure.** `ACTUAL_AMOUNT` equals `RECOMMENDED_AMOUNT` on **98.35%** of
  completed works and never exceeds 1.05×. It is a completion-confirmation figure.
- **No sanction date.** Sanction rows copy `RECOMMENDATION_DATE` verbatim on **100.00%** of
  179,676 works. Presence is testable; timing is unknowable.
- **No estimated cost, no vendor identity** (`IDA_NAME` is a district office, not a contractor).
- **No district column.** `IDA_NAME` is a district *office*; `CONSTITUENCY` is a constituency.
- **No reliable GPS.** No freely downloadable photographs (`ATTACH_ID` is login-gated).

### 3.3 Binding rules (unchanged, all still enforced in code)

1. **Never** describe the system as a supervised fraud classifier.
2. **Never** present `ACTUAL_AMOUNT` as expenditure or claim real-data cost-overrun.
3. Peer groups **cannot** use raw `ACTIVITY_NAME` unsplit.
4. Every real-data output is an **investigation lead**, never a fraud finding.
5. **Enforced by test**, not by discipline: `test_no_fraud_language_in_the_source_tree` greps
   the whole `src/` tree and fails the build. It has fired twice on our own safety code.

### 3.4 The v1 correction that changed the architecture

v1 §3.2 called `ACTIVITY_NAME` "near-free-text (180,701 unique)" and §7 killed it as a peer
axis. **That was half right.** It is a *composite string*:

```
WS/MP519/2023-2024/49391-Installation of multi-gym equipment
```

Split on the dash and it yields **118 official government categories at 93% coverage** — a
free, interpretable, unimpeachable peer axis. Both the problem-statement deck and the previous
team wrote this field off; nobody split it.

**Consequence:** archetypes are a *secondary* signal. The primary peer axis is the official
category. This is the single most important correction v2 makes to v1.

### 3.5 Data-quality facts that bite

- **Censoring anchor = `max(RECOMMENDATION_DATE)` = 2026-05-26.** `max(all dates)` lands in
  2044 and inflates every open duration by ~18 years.
- **695 orphans**, **70** completed-without-sanction, **1,194** back-dated, **9** out-of-window.
- **The 3,987 "corrupt" rows are MP-level totals**, carrying `Total_Amt` (null on all work
  rows). Used as a reconciliation oracle — median ratio exactly 1.0000.
- **DO NOT USE at work grain:** `ACTUAL_AMOUNT`, `WORK_ID` (82% null), `AVERAGE_RATING`,
  `FILE_STATUS`, `Sno`, `MP_NAME`, `Total_Amt`.

---

## 4. Architecture as built

```
Dataset/raw  ->  ingest/loader.py, normalise.py     deterministic parquet
   v  train.py            3 models -> data/artifacts/models/
   v  pipeline.py         Learn -> Compare -> Predict -> Explain -> Prioritise
   +--- peer comparison   official category x state, MIN_PEERS floor, hierarchical back-off,
   |                      leave-one-out percentile
   +--- completion risk   Cox PH (lifelines), right-censored at snapshot
   +--- anomaly           IsolationForest over [log_amount, age_days]
   +--- duplicates        MiniLM 384-d, narrowed to same-agency + near-identical amount
   +--- temporal          per-entity monthly volume + level-shift classification
   +--- compliance        8 checks, each declaring its authority tier
   v  FUSION              noisy-OR across independent signal families
   v  AUDIT-ROI           priority x rs_exposure x (1 + n_families)      [ranking, no budget]
   v  api/app.py          35 endpoints, JWT RBAC, hash-chained audit log
   v  frontend            12 screens, 10 languages, assistant with 18 tools
   v  field.py            what the officer found on site — the only write path
```

**Storage:** Parquet + JSON artifacts; SQLite for the audit log and field records.
⚠️ **v1 §8 specified PostgreSQL. We do not use it.** The whole pipeline runs in ~4 minutes on
a laptop, so a database server earned nothing. **The submitted SIH deck says DuckDB — also not
used.** Say this proactively; it reads as engineering judgement, not a gap.

---

## 5. UVP layer — status against v1's promises

| UVP | v1 promise | Built | Gap |
|---|---|---|---|
| **1 · Peer-conditional triage** | archetype × state × scale, size floor, back-off, LOO | ✅ **100%** | none — and improved by §3.4 |
| **2 · Completion risk** | KM + Cox, censoring, C-index, temporal holdout | 🟡 **85%** | no left-truncation, no KM baseline, no calibration curve |
| **3 · ₹ exposure** | risk × amount, broken down | ✅ **95%** | band/archetype breakdown only partly surfaced |
| **4 · Entity fingerprint** | 8-dimensional behavioural vector | ⚠️ **30%** | **only volume built** |
| **5 · Change-point** | CUSUM / Jensen-Shannon / `ruptures`, with change dates | ⚠️ **45%** | z-score + ratio heuristic; reports *that*, not *when* |
| **6 · Evidence fusion** | noisy-OR, L1–L4 ladder, confidence bands | ✅ **95%** | none material |
| **7 · Audit-ROI** | budgeted optimisation, ₹-coverage@K | ⚠️ **50%** | **ranking only — no capacity budget, no plan** |

**Be precise with judges about 4, 5 and 7.** v1 §22 bills entity change-point as the "punch"
and audit-ROI as the "decision" UVP. Both currently under-deliver against that billing. Claim
what is built:

- UVP-4: *"we profile each agency's volume over time"* — **not** "an eight-dimensional
  behavioural fingerprint."
- UVP-5: *"we detect that an agency's behaviour shifted"* — **not** "we detect when."
- UVP-7: *"we rank by risk × money × corroboration"* — **not** "we optimise under a budget."

---

## 6. ML architecture — what is ML vs statistics vs rules

| # | Stage | Type | Built |
|---|---|---|---|
| 1 | Description embedding (MiniLM 384-d) | ML (pretrained) | ✅ |
| 2 | Archetype discovery (MiniBatchKMeans, K=50) | ML (unsupervised) | ✅ |
| 3 | Peer anomaly (LOO percentile, back-off) | Statistics | ✅ |
| 4 | Completion risk (Cox PH) | Survival | 🟡 85% |
| 5 | Entity fingerprint | Data eng + stats | ⚠️ 30% |
| 6 | Level-shift / change detection | Statistics | ⚠️ 45% |
| 7 | IsolationForest cross-check | ML (unsupervised) | ✅ |
| 8 | Evidence fusion (noisy-OR) | Rules + probability | ✅ |
| 9 | Audit-ROI | Ranking *(v1 said optimisation)* | ⚠️ 50% |
| 10 | **Perceptual hashing (pHash + dHash)** | Signal processing | ✅ **new in v2** |
| 11 | **OCR (RapidOCR, ONNX, CPU)** | ML (pretrained) | ✅ **new in v2** |

We call stages 1, 2, 7, 11 "AI/ML" and the survival model "statistical ML." Fusion and
Audit-ROI are transparent rules. **We never call rules "AI."**

---

## 7. Killed / rejected approaches (unchanged — still a credibility weapon)

| Killed | Why it fails on real MPLADS data |
|---|---|
| Amount bunching | Amounts cluster at **round numbers**, not below an approval limit |
| Naive agency concentration | `IDA_NAME` is a District Collector office — structure, not corruption |
| Naive duplicate detection | Generic templates dominate; 223,407 → 47,709 after specificity filtering |
| Supervised fraud classifier | **No fraud labels exist**; a "fraud %" would be fabricated |
| Cost-overrun / payments (real data) | `ACTUAL_AMOUNT ≡ RECOMMENDED_AMOUNT` on 98.35% |
| Cross-state semantic twins as headline | Real but rare; secondary lead only |
| Raw `activity × state` peer groups | 180,701 values → median group size 1 → **replaced by the 118-category split (§3.4)** |
| GNN over MP↔agency graph | Graph is structural; embeddings re-discover geography |

All correctly absent from real-data paths. Verified by grep on 2026-08-27.

---

## 8. Technical stack as built

| Component | Role | Status |
|---|---|---|
| Python 3.11, pandas, NumPy, SciPy | core | ✅ |
| scikit-learn | KMeans, IsolationForest | ✅ |
| sentence-transformers (MiniLM) | embeddings | ✅ |
| lifelines | Cox PH survival | ✅ |
| FastAPI | 35 endpoints, JWT RBAC, audit log | ✅ |
| React + Vite + Recharts | 12 screens | ✅ (JS, **not TypeScript** as v1 said) |
| Parquet + JSON + SQLite | storage | ✅ **(replaces v1's PostgreSQL)** |
| RapidOCR (ONNX, CPU) | board reading | ✅ new |
| pHash + dHash | photo reuse | ✅ new |
| Salesforce CRM + Agentforce | case management | ✅ new |
| **`ruptures` / CUSUM** | change-point | ❌ **not used** |
| **Leaflet / MapLibre** | choropleth | ❌ **not used** |
| **Docker** | packaging | ❌ **not built** |
| FAISS, OR-Tools, Polars | optional | ❌ none (acceptable) |

---

## 9. Data model as built

Tags: **[R]** real · **[D]** derived · **[M]** model output · **[F]** future.

```
works_scored.parquet   [R] work_ref, mp_id, state_name, constituency, implementing_agency,
                           work_description, activity_category, recommended_amount,
                           recommendation_date, stage flags
                       [D] financial_year, age_days, is_open, is_completed, peer_level
                       [M] archetype_id, amount_pct, priority, rs_exposure, band, audit_roi
case_files.json        [M] work_ref, evidence[], confidence_band, n_signal_families,
                           peer_context, recommended_next_step, disclaimer
duplicate_pairs        [M] work_ref_a/b, similarity, classification, same_agency
temporal.json          [M] national_series, agency_trends, archetype_radar, counts
                       ❌ ChangePoint{entity, change_date, before/after} — NOT built (v1 §9)
                       ❌ BehaviourProfile 8-dim vector — only volume (v1 §9)
audit_log.sqlite       [R] hash-chained action log, verifiable end to end
field records          [R] work_ref, outcome, notes, photo hash, actor, timestamp  [NEW]
salesforce_export/     [M] investigation_cases.csv, evidence.csv                   [NEW]
Vendor/Payment/GPS     [F] not available
```

---

## 10. Evaluation — honest and incomplete

| Module | Metric | Status |
|---|---|---|
| Archetypes | silhouette **0.050** + manual coherence (49 named, 1 declared uninterpretable) | ✅ |
| Anomaly ranking | precision@K, recall@N | ✅ |
| Anomaly ranking | **AP, ablation, seed stability, top-30 FP audit** | ❌ **none run** |
| Completion risk | C-index **0.6759**, held-out | ✅ |
| Completion risk | calibration curve, explicit temporal holdout | ❌ |
| Change-point | synthetic change recovery | ❌ not in harness |
| Audit-ROI | ₹-coverage@K vs baseline | ❌ |

**What is strong:** the synthetic harness — 904 planted anomalies, **69.2% overall detection**,
with *detection* and *ranking* reported separately and the difference explained. Recall@5000 is
14.8% and that is **correct behaviour**: Audit-ROI multiplies by exposure, so a planted anomaly
in a ₹3 lakh work *should* rank below a genuine ₹6 crore one.

**Hard rule:** synthetic metrics are labelled synthetic and are **never** presented as
real-world fraud rates.

⚠️ **The gap that matters most:** v1 §18 names the **top-30 false-positive audit** as the
primary false-positive mitigation and §21 Q7 makes it the objective fallback trigger. **It has
never been run.** That safeguard does not currently exist.

---

## 11. The field-verification loop — new in v2, and strategically the biggest thing

The only place in this product that **creates** data. Everything upstream ends at *"a human
should check X"*; this records what the human found.

- `POST /api/ocr` reads a photographed work board, matches it against **all 210,993 works**,
  and fingerprints it against every photograph submitted before.
- `POST /api/verify/{work_ref}` appends what the officer found — immutable, attributed,
  timestamped.

**Three rules hold it together:**

1. **A match is never settled by the machine.** OCR confidence is confidence in the *pixels*.
   A weathered board reads one digit wrong and lands on a *different real work* — MPLADS
   references run in sequence. So `ocr.match_to_work` returns every real reference one
   character away, cross-checks the painted amount, and sets `needs_confirmation`.
2. **A re-used photograph is a question, not a finding.** Perceptual hashing catches a resized,
   re-compressed, brightened copy that a checksum misses — but two phases of one road
   legitimately look identical. Report, never conclude.
3. **Writing requires a name.** Reading is open; `auth.require_identity` refuses an
   unattributed verification.

**Why this is bigger than it looks.** v1 §3.2 states the central limitation: *"No fraud labels
(none exist publicly)."* These records **are** those labels.
`field.label_readiness()` reports **2 real records, 498 short of 500**, with demo records
excluded from the count. Nothing is refitted and no accuracy is claimed — the honest position,
and a stronger story than v1 could tell.

---

## 12. Security / ethics / governance

- **AI SHALL NOT DECLARE FRAUD.** Enforced by an automated grep test, not by discipline.
- **Human-in-the-loop** on every consequential action.
- **Explainability:** every case lists its signals, peer context, and confidence.
- **Compliance checks declare their authority** — `OFFICIAL_RULE`, `OBSERVED_BASELINE`,
  `STATISTICAL_OUTLIER`. **We assert no official rules**, because no statutory threshold ships
  with this data. Verified 2026-08-27: only `OBSERVED_BASELINE` and `STATISTICAL_OUTLIER` are
  in use. A test enforces it.
- **RBAC:** signed JWT, server-side scope enforcement — you cannot get another state's data by
  editing the URL. Demo-grade: the account list and shared password, labelled as such on screen.
- **Audit trail:** hash-chained, with `/api/audit/verify` recomputing the whole chain.
- **Accessibility as governance:** severity is never carried by colour alone. Red and amber are
  indistinguishable under deuteranopia, so every level also has a glyph (■ ▲ ◆ ●) and its text
  label. `frontend/src/severity.js` is the single source, with measured contrast ratios.

---

## 13. Screens as built — 12, against v1's 8

| v1 screen | Built as | Status |
|---|---|---|
| 1 National overview | `Overview` | 🟡 **money-gap funnel missing** |
| 2 State/district choropleth | — | ❌ **not built, no map library** |
| 3 Work-risk explorer | `Worklist` | ✅ |
| 4 Completion-risk / ₹ exposure | `Compliance` + early warning | ✅ |
| 5 Behavioural change timeline | `Trends` | 🟡 no per-entity timeline with marked change dates |
| 6 Investigation case file | `CaseFile` + `FieldVerify` | ✅ **exceeds spec** |
| 7 Audit prioritisation plan | — | ❌ **ranking exists, no budgeted plan** |
| 8 Methodology / transparency | `Transparency` | ✅ |
| — | `Landing`, `Login`, `Archetypes`, `Duplicates`, `HowItWorks`, **`SalesforceHub`** | ✅ beyond v1 |

---

## 14. Differentiation (unchanged, and stronger)

Peer-conditional (not global) anomaly; predictive completion-risk with survivorship-bias
correction; ₹ exposure; behavioural change detection; Audit-ROI; and a public killed-signals
disclosure.

**v2 adds three differentiators v1 did not have:**
- **Field verification** — the only team likely to have closed the loop from lead to site.
- **Perceptual photo hashing** — the one check a human genuinely cannot do at scale.
- **A 10-language government interface** — statically translated, never depending on a paid call.

---

## 15. Novelty position (unchanged — still scientifically honest)

- **Algorithmic novelty: ~none.** We did not invent embeddings, clustering, survival analysis,
  or noisy-OR.
- **Transfer novelty:** survival + peer-conditional forensics applied to the MPLADS lifecycle.
- **System novelty:** the specific composition as one pipeline.
- **Workflow novelty:** ₹ exposure + evidence case files + a field-verification loop matched to
  an auditor's actual decision.

**We claim transfer + system + workflow novelty — never algorithmic invention.**

---

## 16. Build status and what remains

**Overall: ~78% of v1's specified scope, plus substantial capability v1 never scoped.**

| Area | Done |
|---|---|
| Phases 0–10 | **85%** |
| PS requirement coverage | **85%** |
| ML stages | **78%** |
| Screens | **75%** (6 of 8, plus 6 extra) |
| UVP layer | **71%** |
| Evaluation | **48%** ⚠️ weakest |
| i18n | **100%** (182 keys × 10 languages) |

**Ranked remaining work — cheapest and highest demo value first:**

| # | Gap | Why it matters | Size |
|---|---|---|---|
| 1 | **Money-gap funnel** | v1 §11 demo step 2 promises it; the data is already computed | S |
| 2 | **Top-30 false-positive audit** | v1 §18's stated mitigation and §21 Q7's fallback trigger — never run | S |
| 3 | **Audit-ROI budget + ₹-coverage@K** | Turns a ranking formula into the decision-support claim §22 leads with | M |
| 4 | **Per-entity change timeline + change dates** | Screen 5 as specified; makes UVP-5 answer "when" | M |
| 5 | **Entity behavioural vector** (beyond volume) | UVP-4 is 30% built and billed as the "punch" | L |
| 6 | Choropleth explorer | Visually strong, no new modelling | M |
| 7 | Left-truncation + calibration | Closes §21 Q2, hardens §19 Q7 | M |
| 8 | Docker | Only if one-command start is required | S |

**If only three are done: 1, 2 and 3.** Each closes a gap between a claim already being made
and what the code actually does.

---

## 17. Open decisions (v1 §21, re-scored)

| # | Question | Status |
|---|---|---|
| 1 | Archetype K and method | ✅ **Resolved** — K=50 by silhouette sweep, MiniBatchKMeans |
| 2 | Survival covariates & censoring anchor | 🟡 **Partly** — anchor resolved (2026-05-26); **left-truncation still unhandled** |
| 3 | Entity granularity for fingerprints | ⚠️ **Open — silently defaulted to agency.** v1 warned against exactly this |
| 4 | Audit-capacity assumption | ⚠️ **Open** — blocks gap #3 |
| 5 | Semantic-ring inclusion | ✅ **Resolved** — shipped as a visible secondary lead |
| 6 | Synthetic module posture | ✅ **Superseded** — photo verification is real, not a preview |
| 7 | Fallback trigger to A³ (26056) | ⚠️ **Open** — threshold never set, and the FP audit it depends on has not run |

v1 said *"do not let a later session silently pick one."* **Two were silently picked (3 and 6).**
Recorded here rather than left buried.

---

## 18. Language / claim discipline (unchanged, with v2 additions)

**Safe to claim:** learns work archetypes unsupervised · flags works unusual relative to their
peers · estimates completion probability from observed historical patterns · quantifies ₹
exposure associated with elevated-risk works · detects when an agency's activity level shifts ·
ranks investigations by risk × money × corroboration · runs on 210,993 real public MPLADS works
· provides investigation leads with evidence · **records what an officer found on site** ·
**detects a re-used photograph** · **serves 10 Indian languages**.

**Only with qualification:** "detects anomalies" → *statistical, not fraud* · "duplicate works"
→ *semantically similar, a lead* · "risk score" → *investigation priority* · any synthetic
metric → *on planted data, not real-world fraud* · **"change-point"** → *we detect that a level
shifted, not when* · **"audit optimisation"** → *ranking, not a budgeted plan*.

**Never claim:** "detects fraud with X% accuracy" · "predicts fraud" · "prevents corruption" ·
"100% accurate" · "first in the world" · cost-overrun / payment fraud on real data · "the AI
decides audits" · "ACTUAL_AMOUNT is expenditure" · "we invented [method]".

⚠️ **New v2 prohibitions:**
- **Do not quote "AP ≈ 0.95."** Superseded by 69.2% detection.
- **Do not say PostgreSQL or DuckDB.** We use Parquet + SQLite.
- **Do not claim "100% accurate models."** There is no ground truth to be accurate against —
  that is the thesis, not a shortcoming.

---

## 19. Known defects and hygiene

| Issue | Where | Severity |
|---|---|---|
| **Blue in the UI** — `#3b82f6` on Salesforce stage colours | `salesforce.py:29`, `SalesforceHub.jsx`, `CaseFile.jsx:144` | Violates the "no blue anywhere" design rule |
| **`llm.available()` checks for a key, not credits** | `llm.py` | Assistant header says "live" while calls fail and fall back |
| **`--reload` unreliable** | uvicorn | Logs "Reloading…" but can serve a stale module — restart instead |
| **Stale dev servers hold 8000/5173/5174** | — | Demoing the wrong build; a stale bundle once produced a white screen |
| **Fabricated `chat.py` on `origin/main`** | root-level file | Invented state figures, non-existent `config.ARTIFACTS_DIR`, three `"authority": "Statutory Rule"` declarations — violates §3.3 and §18. Nothing imports it; **delete it** |

---

## 20. Demo story (real-data claims only)

1. "MPLADS has **210,993 real works** — no human inspects them all."
2. **Money-gap funnel** ⚠️ *not built — skip or build gap #1 first.*
3. The system **learning 50 work types** from descriptions, with no labels.
4. A work **normal globally but extreme within its peer group** — with the peer distribution.
5. **Completion risk** and the works with elevated delayed-completion risk.
6. **₹1,302 Cr exposure** by state — exposure, not loss.
7. An **agency whose activity level shifted** — 73 of 697.
8. An **investigation case file** — evidence ladder, confidence, verify-next, non-fraud contract.
9. **Field verification** — read the board, catch the recycled photograph, admit when unreadable.
10. Close: "The system does not declare fraud. It shows officials **where evidence warrants
    attention**, how much money is at stake, and — now — **what was actually found on site.**"

Full script: `docs/JUDGE_SCRIPT.md`.

---

## 21. CONSTITUTION CARD v2

```
PROJECT:      SIH26102 MPLADS AI Monitoring (MoSPI / DIID)
MISSION:      Help authorities find and prioritise unusual, at-risk MPLADS works
              with evidence, not fraud verdicts.
CORE PROBLEM: 210,993 works, reactive manual monitoring, no fraud labels, finite audit capacity.
CORE SOLUTION:Peer-conditional anomaly -> completion risk + Rs exposure -> behavioural shift
              -> evidence case files -> Audit-ROI ranking -> field verification.
PRIMARY UVP:  Survivorship-corrected completion risk + Rs exposure.
SECONDARY:    peer-conditional triage; evidence case files; field verification (new).
REAL DATA:    210,993 works; 85,773 completed / 125,220 open; 36 states / 545 constituencies
              / 778 agencies; Rs 11,565 Cr recommended, Rs 1,302 Cr exposure.
              Sources: Vonter (ODbL) + in-rolls (eSAKSHI).
MODELS:       MiniLM 384-d; MiniBatchKMeans K=50 (silhouette 0.050); Cox PH (C-index 0.6759);
              IsolationForest (4,220); noisy-OR fusion; pHash+dHash; RapidOCR.
VALIDATION:   69.2% synthetic detection (904 planted). 189 tests passing.
              NOT "AP 0.95" - that was the retired prototype.
STORAGE:      Parquet + JSON + SQLite. NOT PostgreSQL, NOT DuckDB.
LIMITATIONS:  no fraud labels (2 of 500 field records); ACTUAL_AMOUNT != expenditure;
              no sanction date; no district column; no payments/GPS/photos/estimates/vendor.
NOT BUILT:    choropleth; audit-capacity budget; money-gap funnel; Docker;
              8-dim entity fingerprint; true change-point dates; FP audit.
NEVER CLAIM:  fraud detected / fraud %; 100% accuracy; cost-overrun on real data;
              the AI decides audits; PostgreSQL/DuckDB; AP 0.95; invented algorithms.
DIFFERENTIATOR: prediction + decision-support + a closed field-verification loop
              + radical honesty (killed signals, published limits).
```
