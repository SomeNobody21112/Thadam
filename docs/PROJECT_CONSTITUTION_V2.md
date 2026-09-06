# PROJECT CONSTITUTION v2 — SIH26102 MPLADS AI Monitoring

**Single source of truth · Team Morior Invictus · St. Joseph's Institute of Technology, Chennai**
**v1 synthesized 2026-08-24 · v2 re-audited against the working tree 2026-08-27**

> **How to use this document.** Authoritative reference for the project. Where another
> document conflicts, resolve by: (1) prefer the latest validated real-data audit;
> (2) prefer actual computation over assumption; (3) preserve uncertainty when unresolved;
> (4) document conflicts, never silently pick the convenient answer.
>
> **Provenance of v2.** Every figure below was read out of the working tree on 2026-08-27 —
> `data/artifacts/*.json`, `data/artifacts/models/metrics.json`, a full `pytest` run, and a
> file-by-file inventory of `src/mplads/` and `frontend/src/`. Nothing is carried forward
> from v1 unverified; where v1 and the code disagree, §A records the correction.

---

## A. What changed since v1 — read this first

v1 was written when the real-data pipeline was **specified but not built**. It is now built,
and the project has grown well past what v1 describes. Three classes of change:

### A.1 v1 statements that are now WRONG

| v1 said | Reality on 2026-08-27 |
|---|---|
| §16: "real-data modules (Phases 1–7) are specified but **NOT yet implemented**" | **All seven are implemented and run end to end** in ~4 minutes |
| §2, §3.3: photo verification is **"Synthetic/Future"**, "clearly labelled" | **Built on real records** — `photohash.py`, `ocr.py`, `field.py` |
| §4: "K is experimentally chosen (~30–60), **not a fixed 50**" | **Resolved: K=50**, chosen by a documented silhouette sweep (20/30/40/50/60) |
| §8: PostgreSQL, Leaflet/MapLibre, `ruptures`, React **+ TypeScript** | **None of these are used.** Parquet + JSON + SQLite; no map; a z-score/ratio heuristic; React + plain JSX |
| §13: "8 screens" | **12 screens** |
| §10: "synthetic harness AP ≈ 0.95, precision@20 ≈ 0.95, 3/3 tests" | Superseded. Current harness: **904 planted, 69.25% detection**, **189 tests** |
| §3.1: "85,531 works with a full lifecycle" | **85,773 completed** by the current pipeline |
| §3.1: "210,448 recommended with a valid positive amount" | **210,987** after dropping the 6 non-positive |

### A.2 Built, but entirely absent from v1

Field verification · OCR · perceptual photo hashing · JWT auth + RBAC · hash-chained audit
log · the data-grounded chat agent · 10-language interface · the severity design system ·
**Salesforce CRM + Agentforce integration** · Health Index · early-warning engine ·
transparency engine · demo-data generator. Each is specified in §24–§32 below.

### A.3 Still specified in v1 and still NOT built

UVP-4 entity fingerprint (1 of 8 dimensions) · UVP-5 true change-point detection ·
UVP-7 capacity budget and audit plan · Screen 2 choropleth · Screen 7 audit plan ·
money-gap funnel · Docker · most of §10's evaluation battery. Tracked honestly in §33.

---

## 0. What we are building (unchanged from v1 — still correct)

An **AI-assisted forensic monitoring and decision-support system for MPLADS** that learns what
"normal" work looks like from the national portfolio, flags statistically and behaviourally
unusual activity **relative to genuine peers**, estimates **completion risk** and the
**₹ exposure** attached to it, detects **when an administrative unit's behaviour changes**,
helps authorities **prioritise limited investigative capacity**, and — new in v2 — **records
what an officer found when they went and looked**, producing **investigation leads with
evidence, never fraud verdicts.**

It is **not** "an AI dashboard that gives every work a fraud score."

---

## 1. The conceptual model (extended)

```
What happened?          -> ingest + normalise the real MPLADS lifecycle
What looks unusual?     -> archetype-conditional anomaly (peer-relative, not global)
Why is it unusual?      -> evidence fusion + explainable case file
Is behaviour changing?  -> entity trend + level-shift detection
What may go wrong?      -> completion-risk / time-to-event model
How much is at stake?   -> Rs exposure-at-risk quantification
Investigate first?      -> Audit-ROI ranking
--- v2 adds the rung the ladder was missing ---
What did we find?       -> field verification: the officer's own observation, recorded
Who may see it?         -> RBAC scope + hash-chained audit log
Who acts on it?         -> Salesforce case management, 5-stage investigation path
```

v1's ladder ended at "investigate first" — it produced leads and stopped. **The single
biggest conceptual addition in v2 is the last three rungs**: the loop now closes, is
access-controlled, and hands off to a real case-management system.

---

## 2. Official PS → Our Implementation (updated)

Problem Statement **26102** · MoSPI · DIID · Software · Miscellaneous. Dataset: MPLADS/eSAKSHI.

| PS requirement | How we implement it | Status |
|---|---|---|
| Anomaly detection | Peer-conditional leave-one-out percentile within `(archetype × state × scale)` | **Real** |
| Unusual patterns / deviations | Peer-relative outliers + entity level-shift | **Real** |
| Fraud / irregularity identification | Reframed as **investigation leads** with an evidence ladder | **Real (as leads)** |
| Inefficiency / fund utilization | Completion-risk + ₹ exposure. ⚠️ **money-gap funnel still not built** | **Partial** |
| Delayed projects | Cox PH survival with right-censoring | **Real** |
| Cost overruns | No independent expenditure exists | **Not built — honestly deferred** |
| Payments analysis | No payment-tranche data | **Not built — honestly deferred** |
| Cost estimates | No estimated-cost field | **Not built — honestly deferred** |
| Duplicate works | Semantic near-duplicates, agency+amount filtered | **Real (secondary)** |
| Asset creation / completion | Lifecycle stage + completion-risk | **Real** |
| Risk-based alerts | Fused priority + confidence bands + early-warning levels | **Real** |
| Predictive insights | Completion-risk model | **Real** |
| Early-warning mechanisms | ₹ exposure + early-warning engine (CRITICAL/HIGH/MEDIUM/LOW) | **Real** |
| Decision-support dashboards | **12 screens** (§13) | **Real — built** |
| Automated compliance monitoring | 8 lifecycle conformance checks with declared authority | **Real** |
| Trend analysis | Entity monthly trajectories + classification | **Partial (volume only)** |
| Improved transparency | Transparency screen + killed-signals + label-readiness counter | **Real** |
| Reduced manual monitoring effort | Audit-ROI ranking. ⚠️ **budgeted plan still not built** | **Partial** |
| **Photographs / asset verification** | **pHash + dHash reuse detection on real submitted photos** | **Real — was "Future" in v1** |
| **Field / site verification** | **Immutable attributed records of what an officer found** | **Real — absent from v1** |
| **Case management / workflow** | **Salesforce Investigation_Case__c + 5-stage Path + Agentforce** | **Real — absent from v1** |

---

## 3. Data (verified 2026-08-27)

### 3.1 What we have

| Measure | Value |
|---|---|
| Works | **210,993** (210,987 after dropping 6 with amount ≤ 0) |
| Raw stage rows | **480,768** = 3,987 MP-summary + 476,781 work-stage |
| Completed / open | **85,773 / 125,220** |
| Recommended / exposure | **₹11,565 Cr / ₹1,302 Cr** |
| States / constituencies / agencies | **36 / 545 / 778** |
| Descriptions clustered | **187,865** |

### 3.2 What we do NOT have (unchanged, and still binding)

- **No fraud labels.** None exist publicly. *(v2 nuance: field verification is now
  accumulating them — see §24.)*
- **No independent expenditure.** `ACTUAL_AMOUNT` equals `RECOMMENDED_AMOUNT` on **98.35%**
  of completed works; **zero** exceed 1.05×. It is a completion-confirmation figure.
- **No sanction date.** Sanction rows copy `RECOMMENDATION_DATE` verbatim on **100.00%** of
  179,676 works. Presence is testable; timing is unknowable.
- **No estimated cost, no vendor identity.** `IDA_NAME` is a district *office*.
- **No district column.** `IDA_NAME` is an office; `CONSTITUENCY` is a constituency.
- **No reliable GPS.**
- **No downloadable asset photographs** from the portal (`ATTACH_ID` is login-gated).
  *(v2 nuance: officers now submit their own, which is a different and legitimate source.)*

### 3.3 Consequences (binding rules — extended in v2)

1. **Never** describe the system as a supervised fraud classifier.
2. **Never** present `ACTUAL_AMOUNT` as expenditure or claim real-data cost-overrun.
3. ~~Photo-reuse is synthetic/future~~ → **Photo-reuse is real, and is a *question*, never a
   finding.** Two phases of one road legitimately look identical from the roadside.
4. Peer groups cannot use raw `ACTIVITY_NAME`.
5. Every real-data output is an **investigation lead**, never a fraud finding.
6. **(new)** No compliance check may assert `OFFICIAL_RULE`. No statutory threshold ships
   with this data; calling an outlier a legal breach would be inventing law. **A test
   enforces this.**
7. **(new)** Severity is never carried by colour alone — every level also has a glyph and a
   text label (§29).
8. **(new)** Interface translation must never depend on a network call (§28).
9. **(new)** A field verification cannot be written without an attributed identity, and once
   written it is immutable (§24).

### 3.4 The parse nobody else made

`ACTIVITY_NAME` looks unusable — 180,701 distinct values. Both the problem-statement deck and
the previous team wrote it off. It is a **composite string**:
`WS/MP519/2023-2024/49391-Installation of multi-gym equipment`.

Split on the dash and it yields **118 official government categories covering 93% of works** —
a free, interpretable, unimpeachable peer axis. This demoted archetype clustering to a
*secondary* signal, which is where the FRD hoped it would land.

### 3.5 Data quality (current)

- 6 non-positive amounts → dropped.
- **1,194** completion-before-recommendation rows → flagged as conformance signals, excluded
  from survival fitting.
- **695** orphans (no recommendation row); **70** completed-without-sanction; **9**
  out-of-window dates. Carried and flagged.
- **Censoring anchor = `max(RECOMMENDATION_DATE)` = 2026-05-26.** Anchoring on `max(all
  dates)` lands in 2044 and inflates every open duration by ~18 years.
- The 3,987 "corrupt" rows are **MP-level totals**, used as a reconciliation oracle —
  median ratio exactly 1.0000.

**DO NOT USE at work grain:** `ACTUAL_AMOUNT`, `WORK_ID` (82% null, renamed
`portal_work_id` as a guard rail), `AVERAGE_RATING`, `FILE_STATUS`, `Sno`, `MP_NAME`,
`Total_Amt`.

---

## 4. Core architecture (as built)

```
Dataset/raw/  (read-only)
   v  INGEST                loader.py -> normalise.py -> canonical parquet
   v  TRAIN                 3 models -> data/artifacts/models/
   v  PIPELINE              Learn -> Compare -> Predict -> Explain -> Prioritise
   |    +-- peer comparison       archetype x state x scale, LOO percentile, back-off
   |    +-- completion risk       Cox PH, right-censored at snapshot
   |    +-- multivariate outlier  IsolationForest cross-check
   |    +-- duplicates            embedding similarity + agency + amount filter
   |    +-- temporal              monthly entity trends + level-shift classification
   |    +-- compliance            8 checks, each declaring its authority
   |    +-- early warning         CRITICAL / HIGH / MEDIUM / LOW
   |    +-- transparency          what is measured, derived, unavailable
   v  FUSION                noisy-OR over independent families -> priority + band
   v  AUDIT-ROI             priority x exposure x (1 + n_families)      [ranking only]
   v  SERVE                 FastAPI, 35 endpoints, JWT scope, hash-chained audit log
   v  SURFACES              React (12 screens) · chat agent (15 tools) · Salesforce CRM
   ^  FIELD LOOP            OCR -> photo hash -> immutable verification record
```

---

## 5. UVP layer (status against v1's specification)

| UVP | v1 claim | Built | Gap |
|---|---|---|---|
| **1 · Archetype-conditional triage** | peer-conditional, LOO, back-off | ✅ **100%** | — |
| **2 · Completion-risk** | KM + Cox, censoring, C-index, temporal holdout | 🟡 **85%** | no left-truncation, no KM baseline, no calibration curve |
| **3 · ₹ exposure** | risk × amount, broken down | ✅ **95%** | band/archetype breakdown only partly surfaced |
| **4 · Entity fingerprint** | 8-dimensional time-varying vector | ⚠️ **30%** | **only volume built** |
| **5 · Change-point** | CUSUM / Jensen-Shannon / `ruptures`, *when* it changed | ⚠️ **45%** | z-score + ratio heuristic; **no change date**, no before/after distributions |
| **6 · Evidence fusion / case file** | noisy-OR, L1–L4 ladder, non-fraud contract | ✅ **95%** | — |
| **7 · Audit-ROI** | optimisation **under a capacity budget**, ₹-coverage@K | ⚠️ **50%** | **ranking only** — no budget, no plan, no coverage metric |

**Be precise with judges about UVP-4, 5 and 7.** The claims in v1 and in the pitch (§22)
currently outrun the code. Either build them (§33) or soften the claim.

---

## 6. ML architecture (as built)

| # | Stage | Type | Status |
|---|---|---|---|
| 1 | Description embedding — `all-MiniLM-L6-v2`, 384-d | ML (pretrained) | ✅ |
| 2 | Archetype discovery — MiniBatchKMeans, K=50 by sweep | ML (unsupervised) | ✅ |
| 3 | Peer anomaly — LOO percentile, hierarchical back-off | Statistics | ✅ |
| 4 | Completion risk — Cox PH (`lifelines`), right-censored | Survival | 🟡 |
| 5 | Entity fingerprint | Data eng + stats | ⚠️ volume only |
| 6 | Level-shift / "change-point" | Statistics | ⚠️ heuristic |
| 7 | IsolationForest over `[log_amount, age_days]` | ML (unsupervised) | ✅ cross-check |
| 8 | Evidence fusion — noisy-OR | Rules + probability | ✅ |
| 9 | Audit-ROI | Ranking *(not yet optimisation)* | ⚠️ |
| **10** | **OCR — RapidOCR (ONNX, CPU)** | **ML (pretrained)** | ✅ **new** |
| **11** | **Perceptual hashing — pHash + dHash** | **Signal processing** | ✅ **new** |
| **12** | **Chat agent — 15 read-only tools + offline router** | **LLM + deterministic** | ✅ **new** |

**We never call rules "AI."** Stages 8 and 9 are transparent rules and ranking.

### 6.1 Model metrics (verified)

| Model | Metric | Value | What it is **not** |
|---|---|---|---|
| Archetypes | silhouette @ K=50 | **0.050** | **Not accuracy.** A separation measure. Real text clusters overlap |
| Completion risk | held-out C-index | **0.6759** | **Not** a probability of wrongdoing. Ranks which finishes sooner ~68% of the time |
| Anomaly | works flagged | **4,220** | A corroborating outlier flag, never a verdict |

---

## 7. Killed / rejected approaches (unchanged — still a credibility weapon)

Amount bunching · naive agency concentration · naive duplicate detection · generic fraud
score / supervised classifier · cost-overrun on real data · cross-state semantic twins as
headline · raw `activity × state` peer groups · GNN over MP↔agency graph.

**Rationale for each is in v1 §7 and is unchanged.** ⚠️ Do not port the killed bunching /
concentration detectors onto real data.

---

## 8. Technical stack (as actually built)

| Component | Role | Status |
|---|---|---|
| Python 3.11 (`.venv`, uv) | core | ✅ |
| pandas / NumPy / SciPy | data + stats | ✅ |
| scikit-learn | MiniBatchKMeans, IsolationForest | ✅ |
| sentence-transformers (MiniLM 384-d) | embeddings | ✅ |
| lifelines | Cox PH survival | ✅ |
| FastAPI | 35-endpoint API | ✅ |
| PyJWT | auth tokens | ✅ **new** |
| SQLite | audit chain + field records | ✅ **new** |
| **Parquet + JSON artifacts** | storage | ✅ **replaces PostgreSQL** |
| RapidOCR (ONNX, CPU) | board reading | ✅ **new** |
| Pillow | perceptual hashing | ✅ **new** |
| anthropic | briefings + chat | 🟡 key present, **no credits** |
| React + Vite + Recharts (JSX, not TS) | 12 screens | ✅ |
| Salesforce SFDX package | CRM + Agentforce | ✅ **new** |
| ~~PostgreSQL~~ | — | ❌ replaced by Parquet, deliberately |
| ~~Leaflet / MapLibre~~ | — | ❌ **not built** (Screen 2) |
| ~~ruptures / CUSUM~~ | — | ❌ **not built** (UVP-5) |
| ~~Docker~~ | packaging | ❌ **not built** |
| ~~FAISS / OR-Tools / Polars~~ | optional | ❌ not needed |

> **Say this proactively if a judge has v1 or the SIH deck open.** The deck says **DuckDB**;
> v1 says **PostgreSQL**; we use **pandas + Parquet**. The whole pipeline runs in ~4 minutes
> on a laptop, so a database server earns nothing. That is engineering judgement, not a gap —
> but it reads badly if they find it before you say it.

---

## 9. Data model (as built)

Tags: **[R]** real ingested · **[D]** derived · **[M]** model output · **[F]** future ·
**[O]** officer-created.

```
Work             [R] work_ref (WORK_RECOMMENDATION_DTL_ID + mp_id), mp_id, mp_name,
                     state_name, constituency, implementing_agency, work_description,
                     activity_name, recommended_amount, recommendation_date, stage
                 [D] activity_category (118, parsed), financial_year, is_open, is_completed
                 [M] archetype_id, archetype_label, peer_level, amount_pct
RiskSignal       [M] work_ref, family (amount|duration|lifecycle|behaviour|
                     multivariate|duplication), score, detail
CompletionRisk   [M] work_ref, completion_risk, rs_exposure, basis
CaseFile         [M] work_ref, priority, confidence_band, n_signal_families, evidence[],
                     recommended_next_step, disclaimer, audit_roi
DuplicatePair    [M] work_ref_a, work_ref_b, similarity, classification, same_agency
ComplianceCheck  [M] key, check, authority, severity, works_affected, meaning
TemporalTrend    [M] entity, classification, explanation           [no change_date yet]
HealthIndex      [M] score, components[{name, weight, value, explanation}]
--- v2 additions ---
Verification     [O] id, work_ref, outcome, notes, photo, ocr_text, actor, role,
                     created_at  -- immutable, attributed, hash-chained
PhotoHash        [O] phash, dhash, work_ref, submitted_by, submitted_at
AuditEntry       [M] row hash + previous row hash (SHA-256 chain)
Principal        [R] username, role, scope, JWT
SalesforceCase   [M] Investigation_Case__c, Evidence__c, Stage, Escalation_Tier__c
Attachment       [F] attach_id — portal files remain access-controlled
Vendor/Payment/Estimate/GPS [F] not available
```

---

## 10. Evaluation (honest, label-free) — status

| Module | Metric | Status |
|---|---|---|
| Archetypes | silhouette | ✅ **0.050**, honestly framed |
| Archetypes | manual coherence | ✅ 49 named, 1 declared "uninterpretable" |
| Anomaly ranking | detection on planted anomalies | ✅ **69.25%** over **904** planted |
| Anomaly ranking | precision@K / recall@N | ✅ reported, and separated from detection |
| Anomaly ranking | average precision (AP) | ❌ **not computed** |
| Anomaly ranking | ablation | ❌ **not run** |
| Anomaly ranking | seed stability | ❌ **not run** |
| Anomaly ranking | **top-30 real-lead FP audit** | ❌ **not run** — §18's stated mitigation |
| Completion-risk | C-index | ✅ **0.6759** held out |
| Completion-risk | calibration curve | ❌ **not produced** |
| Completion-risk | explicit temporal holdout | 🟡 held-out split, not explicitly temporal |
| Change-point | synthetic recovery | ❌ **not in the harness** |
| Audit-ROI | ₹-coverage@K vs baseline | ❌ **not computed** |
| Whole system | automated test suite | ✅ **189 passed, 2 skipped** |

### 10.1 Synthetic validation detail

904 planted anomalies, **69.25% overall detection**:

| Perturbation | Detected |
|---|---|
| Stalled lifecycle | **96.1%** |
| Inflated amount | **83.2%** |
| Lifecycle break | **58.0%** |
| Cloned description | **50.0%** |

**Recall@k is deliberately lower than detection** (14.8% @5000 by Audit-ROI). That is correct
behaviour: Audit-ROI multiplies by rupee exposure, so a planted anomaly inside a ₹3 lakh work
*should* rank below a genuine ₹6 crore one. Report both and explain the difference.

**Hard rule:** synthetic metrics are labelled synthetic and are **never** presented as
real-world fraud rates.

---

## 11. Demo story (updated to what exists)

1. Landing — 2,10,993 works, ₹11,565 Cr; one minute each is over a year of work.
2. **Login** — RBAC, 4 evaluation accounts, scope enforced server-side. *(new)*
3. Overview — exposure explained as *amount × chance of not finishing*, never loss.
4. Investigation Queue — ranked by Audit-ROI; every row opens and says why.
5. Case file — evidence ladder, peer context, one recommended human action.
6. **Field verification** — read a board, catch a recycled photograph, admit when unsure. *(new)*
7. Temporal — 73 of 697 agencies show a level shift; a shift is not wrongdoing.
8. Duplicates — 223,407 → 47,709, and *why we threw most away*.
9. Compliance — every check declares its authority; **we assert no official rules**.
10. Transparency — what this data cannot tell you, with the measurement that proves it.
11. **Assistant** — 15 read-only tools, shows which one produced each figure. *(new)*
12. **Salesforce** — the lead becomes a case on a 5-stage path. *(new)*
13. Close: *"We never accuse anyone. We move oversight from 'what happened?' to 'where should
    I look first?'"*

⚠️ **Step 2 of v1's demo (money-gap funnel) does not exist.** Either build it or drop it from
the script.

---

## 12. Security / ethics / governance (extended)

Unchanged principles from v1 — AI shall not declare fraud; human-in-the-loop; explainability;
uncertainty surfaced; bias control; model monitoring — **plus, now actually implemented:**

- **RBAC.** JWT, 5 roles (`ministry`, `auditor`, `state`, `mp`, `district`). Scope is checked
  **server-side**, so another state's data is not reachable by editing a URL.
- **Hash-chained audit log.** Each row carries SHA-256 of its contents **plus the previous
  row's hash**; `verify_chain()` reports exactly where a break occurs.
  **It is tamper-*evident*, not tamper-proof** — a writer with database access can rewrite the
  chain from the edit point forward. Detecting that needs the head hash published somewhere
  the writer does not control. The architecture allows it; this prototype does not implement
  it, **and the UI says so.**
- **Attributed writes.** Reading is open; `auth.require_identity` refuses an unattributed
  verification. A presented token is honoured even when auth is optional.
- **Demo credentials are shown on screen deliberately**, and labelled as such.

---

## 13. Dashboard — 12 screens (was 8)

| # | Screen | Status |
|---|---|---|
| 1 | Landing | ✅ |
| 2 | **Login** | ✅ *(new)* |
| 3 | National Overview | 🟡 **money-gap funnel missing** |
| 4 | Investigation Queue | ✅ |
| 5 | Case File (+ **Field Verification**) | ✅ |
| 6 | Temporal | 🟡 no per-entity timeline with marked change dates |
| 7 | Near-Duplicates | ✅ |
| 8 | Compliance & Early Warning | ✅ |
| 9 | Work Archetypes | ✅ |
| 10 | Data Transparency | ✅ |
| 11 | How It Works | ✅ |
| 12 | **Salesforce Hub** | ✅ *(new)* |
| — | *State/district choropleth* (v1 Screen 2) | ❌ **not built** |
| — | *Audit prioritization plan* (v1 Screen 7) | ❌ **not built** |

Plus a **404** route and the **assistant panel** available on every screen.

---

## 24. Field verification — the loop closing *(new in v2)*

The one place in this product that **creates** data. Everything upstream ends at *"a human
should check X"*; this records what the human found.

**Why it matters more than it looks.** §3.2's central limitation is that no fraud labels
exist, so nothing can be validated against an outcome. Verification records **are** those
labels, accumulating one site visit at a time. At ~500 records the weights in
`config.SIGNAL_WEIGHTS` could stop being reasoned defaults and start being fitted to what
officers actually confirmed.

**We do not pretend that has happened.** `field.label_readiness()` reports the gap honestly,
and records seeded for a walkthrough are excluded from the count.

Three rules hold it together:

- **A match is never settled by the machine.** OCR confidence is confidence in the *pixels*.
  A weathered board reads one digit wrong at 99.6% and lands on a *different real work* —
  MPLADS references run in sequence. So `ocr.match_to_work` returns every real reference one
  character away, cross-checks the amount painted on the board, and sets `needs_confirmation`;
  the UI will not save until a human ticks the box.
- **A re-used photograph is a question, not a finding.** Two phases of one road legitimately
  look identical from the roadside. Report, never conclude.
- **Writing requires a name.** An unattributed verification is refused.

**Outcomes:** `VERIFIED_COMPLETE` · `VERIFIED_IN_PROGRESS` · `NOT_STARTED` · `NOT_FOUND` ·
`RECORD_MISMATCH` · `NO_ACCESS`.

Works never surfaced return a **"clear record" case file rather than 404** — if only flagged
works can be visited, every label collected is a positive and the weights can never be
corrected by a negative.

---

## 25. OCR *(new in v2)*

`ocr.py` — RapidOCR (ONNX, CPU, no GPU, no external binary). Reads the display board MPLADS
already requires at every site and pulls the work reference and sanctioned amount, so nobody
re-types a reference number standing in a field.

**What it is not:** it does not verify the work exists, matches its description, or that money
was spent. It reads text off an image the officer supplies. Every field returns with its
confidence and is shown for confirmation. If RapidOCR is unavailable it **degrades to manual
entry rather than failing.**

---

## 26. Perceptual photo hashing *(new in v2 — was "Future" in v1)*

A cryptographic hash answers *"is this the same file"*, which anyone defeats by re-saving.
A perceptual hash answers *"is this the same picture"*, and survives re-compression, resizing,
a slight crop and a brightness change. **That difference is the entire point** — a recycled
site photograph is almost never the identical file.

Two independent hashes, because they fail differently:

- **pHash** (DCT of 32×32 greyscale) — keys on low-frequency structure. Robust to compression
  and resizing; fooled by a heavy crop.
- **dHash** (adjacent-pixel gradients on 9×8 greyscale) — keys on relative brightness. Robust
  to gamma and exposure; sensitive to rotation.

**Agreement between them is what makes a match worth showing.**
Verdicts: `IDENTICAL` · `NEAR_IDENTICAL` · `SAME_SCENE` · `DIFFERENT`.

This is **the one check a human genuinely cannot do at scale** — nobody remembers a photograph
they approved eight months ago in a different district.

---

## 27. The chat agent *(new in v2)*

`chat.py` — **15 read-only tools** over all 210,993 works, plus a deterministic offline router.

**Tools are read-only by construction.** There is no tool that writes, scores, ranks, or
changes a threshold. The model supplies language and navigation; the pipeline supplies truth.

- **The LLM never computes anything.** It receives only figures the deterministic pipeline
  already produced. The prompt forbids inventing numbers and asserting wrongdoing; `_scrub()`
  then **discards** any output containing such a word. *A prompt is a request; a filter is a
  guarantee.*
- **Offline router.** Without credits, `answer_offline()` answers from the same tools and the
  same corpus — leads, exposure, states, specific works, ranking, confidence bands, compliance,
  health index, archetypes, behaviour change, model metrics, data limits. The feature demos
  with or without billing.
- **The panel shows its receipts.** Every answer carries the tools that produced it.
- **Page-aware.** Standing on a case file it offers questions about *that work*.
- Voice input + read-aloud, markdown tables, clickable work references, transcript export.

⚠️ **`llm.available()` checks for a key, not for credits.** It returns `True` while calls fail
with `BadRequestError` and silently fall back. The UI therefore says "live" when it is not.
**Fix before a judge asks.**

---

## 28. Multilingual *(new in v2)*

**182 interface keys × 10 languages** (en, hi, bn, ta, te, mr, gu, kn, ml, pa), **all at 100%
coverage**, enforced by `test_every_offered_language_has_a_complete_bundle`.

**Static, not LLM.** It was LLM-backed once and silently fell back to English when billing ran
out. **Chrome must never depend on a paid network call.** The model now only writes *content*
(briefings), which is allowed to degrade and which labels itself when it does.

*A half-translated language shown in a picker is worse than one honestly absent.*

---

## 29. Severity design system *(new in v2)*

`frontend/src/severity.js` is the **single source** for every band, level and classification
colour. Six pages each kept their own copy until HIGH and LOW ended up the same terracotta in
two of them.

Traffic-light hues, chosen against the parchment ground by computation, not by eye:

| Level | Fill | vs ground | Ink | on chip | Glyph |
|---|---|---|---|---|---|
| CRITICAL | `#8f1d14` | 8.12:1 | `#7d1d12` | 8.27:1 | ■ |
| HIGH | `#d13a2a` | 4.40:1 | `#a8301f` | 5.66:1 | ▲ |
| MEDIUM | `#b58200` | 3.10:1 | `#8a6508` | 4.62:1 | ◆ |
| LOW | `#43976a` | 3.25:1 | `#2b6b47` | 5.31:1 | ● |

**Red and amber cannot be separated under deuteranopia** — that is inherent to traffic-light
hues, not a bad pick. So **severity is never carried by colour alone**: every indicator also
has its own shape and its text label, and the four glyphs stay distinguishable in greyscale
and in print. Roughly one man in twelve is red-green colourblind, and this is a government tool.

**Design ground rule: no blue anywhere.** Parchment `#f7f4ed`, terracotta `#a8452a` primary,
forest green secondary, aged brass for figures. Fraunces + Noto Sans (all Indic subsets) +
Roboto Mono.

⚠️ **Currently violated** by `salesforce.py` (`var(--blue, #3b82f6)`) and `SalesforceHub.jsx`.
Fix or document the exception.

---

## 30. Salesforce CRM + Agentforce *(new in v2 — entirely absent from v1)*

Live bridge between the Python intelligence pipeline and a Salesforce org.

- **Objects:** `Investigation_Case__c`, `Evidence__c`.
- **5-stage Path:** New → *(triage)* → … → closure, each stage carrying written guidance for
  the officer and the fields that matter at that stage.
- **Agentforce** "Investigation Lookup" topic — `POST /api/agentforce/query`.
- **Reports & dashboards** shipped in the package.
- **Round trip:** `scripts/export_for_salesforce.py` out, `scripts/import_salesforce_findings.py`
  back — findings recorded in Salesforce return to the pipeline.
- **Artifacts:** `salesforce_export/` (`investigation_cases.csv`, `evidence.csv`,
  `SALESFORCE_SETUP.md`), `salesforce_package/` (SFDX: `force-app`, `sfdx-project.json`),
  `salesforce_extras/`.
- **Screen:** `SalesforceHub.jsx`; API `/api/salesforce/{overview,cases,case/{ref},update-stage}`.

**Why it matters for the pitch:** v1's ladder stopped at "here is a ranked list." This is the
answer to *"and then what happens?"* — the lead becomes a managed case in a system government
departments already run, with a defined workflow and an owner.

---

## 31. API surface *(new in v2)*

**35 endpoints.** Grouped:

- **Intelligence:** `/stats` `/worklist` `/case/{ref}` `/temporal` `/transparency`
  `/compliance` `/early-warning` `/health-index` `/archetypes` `/duplicates` `/states` `/models`
- **Auth & governance:** `/auth/login` `/auth/accounts` `/auth/demo-tokens` `/roles`
  `/audit/verify` `/audit/tail`
- **Field loop:** `/ocr` `/verify/{ref}` (GET+POST) `/field/summary` `/photo/{name}`
- **Assistant & language:** `/chat` `/chat/capabilities` `/languages` `/strings`
  `/insight/portfolio` `/insight/case/{ref}`
- **Salesforce:** `/salesforce/overview` `/salesforce/cases` `/salesforce/case/{ref}`
  `/salesforce/update-stage` `/agentforce/query`
- **Ops:** `/health`

---

## 32. Engineering conventions *(new in v2 — these are load-bearing)*

- Type hints everywhere. `pathlib`, never string paths. No notebooks in `src/`.
- **Never hardcode a path, seed or date.** Import from `mplads.config`.
- Every transform logs row count at entry and exit. **`_log_counts()` raises** if a count
  changes without a stated reason — a silent drop is impossible, not merely discouraged.
- **Deterministic:** dedup sorts on `(recommendation_date, work_ref, source_file,
  raw_row_index)`, so results never depend on file order.
- `Dataset/` is **read-only**. Never write into it.
- Expensive work is cached and skipped on rerun.
- **`test_no_fraud_language_in_the_source_tree`** greps the whole `src/` tree and fails the
  build on `fraud_probability`, `is_fraud`, `fraud_score`, `fraudulent`. **It has fired twice
  on our own safety code** — both times the fix was to rephrase or assemble the pattern from
  fragments, never to exempt the file. *The guard is the product.*
- Windows console is cp1252 — printing Devanagari or Tamil from a script needs
  `PYTHONIOENCODING=utf-8`.
- PowerShell execution policy blocks `npm.ps1` — **use `npm.cmd`**.

---

## 33. What is still NOT built — ranked by value

| # | Gap | Why it matters | Size |
|---|---|---|---|
| 1 | **Money-gap funnel** | v1 §11 demo step 2 and Screen 1 both promise it; data already computed | Small |
| 2 | **Top-30 real-lead FP audit** | §18's stated FP mitigation and §21 Q7's fallback trigger; answers "what if you flag an innocent district?" | Small |
| 3 | **Audit-ROI capacity budget + ₹-coverage@K** | Turns a ranking formula into the decision-support claim §22 leads with | Medium |
| 4 | **Per-entity change timeline + change dates** | Screen 5 as specified; makes UVP-5 answer *"when"* | Medium |
| 5 | **Entity behavioural vector (8 dims)** | UVP-4 is billed as the "punch" and is 30% built | Large |
| 6 | Choropleth explorer (Screen 2) | Visually strong, no new modelling | Medium |
| 7 | Left-truncation + calibration curve | Closes §21 Q2, hardens the survival defence | Medium |
| 8 | Evaluation battery (AP, ablation, seed stability, change-point recovery) | §10 is the weakest area at ~48% | Medium |
| 9 | Docker | Only if one-command start is required | Small |
| 10 | Fix `llm.available()` credit check; remove blue from Salesforce UI | Small correctness/consistency fixes | Small |

**If only three are done: 1, 2 and 3.** Each closes a gap where a claim already being made
outruns what the code does.

---

## 34. Open team decisions (v1 §21, re-audited)

| # | Question | Status |
|---|---|---|
| 1 | Archetype K and method | ✅ **Resolved** — K=50 by silhouette sweep, MiniBatchKMeans |
| 2 | Survival covariates & censoring anchor | 🟡 **Partly** — anchor resolved (2026-05-26); **left-truncation still unhandled** |
| 3 | Entity granularity for fingerprints | ❌ **Open** — agency used by default, never decided |
| 4 | Audit-capacity assumption | ❌ **Open** — blocks gap #3 |
| 5 | Semantic-ring inclusion | ✅ **Resolved** — shipped as a visible secondary lead |
| 6 | Synthetic module posture | ✅ **Superseded** — photo verification is real, not a preview |
| 7 | Fallback trigger to A³ (26056) | ❌ **Open** — threshold never set, and the FP audit it depends on has not run |

> v1 warned: *"resolve them as a team; do not let a later session silently pick one."*
> **Two were silently picked** (3 and 4). Decide them explicitly.

---

## 20. Language / claim discipline (updated)

**A. Safe to claim:** everything in v1 §20-A, plus — "records what an officer found on site,
attributed and immutable"; "detects a re-used photograph across submissions"; "reads a work
board and refuses to settle an ambiguous reference"; "role-scoped access with a
tamper-evident audit log"; "interface in 10 languages, no network call"; "an assistant that
shows which lookup produced every figure"; "hands a lead to Salesforce as a managed case".

**B. Only with qualification:** v1 §20-B, plus — "change-point" (→ *a level-shift
classification; it does not yet report* when); "audit-ROI optimisation" (→ *currently a
ranking; the capacity budget is not built*); "entity behavioural fingerprint" (→ *volume
trend only today*); "tamper-proof audit log" (→ ***tamper-evident***); "live AI assistant"
(→ *the offline router answers today; billing is empty*).

**C. Never claim:** everything in v1 §20-C — "detects fraud with X% accuracy"; "predicts
fraud"; "prevents corruption"; **"100% accurate"**; "first system in the world"; "cost
overrun / payment fraud" on real data; "the AI decides audits"; "`ACTUAL_AMOUNT` is
expenditure"; "we invented [method]" — plus, new: **"the models are 100% accurate."**

> There are no fraud labels, so there is nothing to be accurate *against*. A judge who hears
> "100% accurate" will ask "against what ground truth?", and the honest answer is "none
> exists" — which turns the project's strongest differentiator into a credibility hole.
> Quote **C-index 0.6759**, **69.25% synthetic detection**, **silhouette 0.050**, and say what
> each one is not.

---

## 35. CONSTITUTION CARD v2

```
PROJECT:      SIH26102 MPLADS AI Monitoring (MoSPI / DIID)
MISSION:      Help authorities find, prioritise and verify unusual, at-risk MPLADS works
              with evidence, not fraud verdicts.
CORE PROBLEM: 2.1 lakh works, reactive manual monitoring, no fraud labels, finite audit capacity.
CORE SOLUTION:Learn archetypes -> peer-conditional anomaly -> completion risk + Rs exposure
              -> behaviour shift -> evidence case files -> Audit-ROI ranking
              -> FIELD VERIFICATION -> Salesforce case management.
VERIFIED:     210,993 works | 85,773 done / 125,220 open | Rs 11,565 Cr rec | Rs 1,302 Cr exposure
              37,705 leads (4,478 HIGH / 33,227 MEDIUM) | 36 states / 545 const / 778 agencies
              50 archetypes (silhouette 0.050) | Cox C-index 0.6759 | IsolationForest 4,220
              223,407 dup pairs -> 47,709 concerning | 8 compliance checks | Health 62.9/100
              73 of 697 agencies shifted | synthetic detection 69.25% over 904 planted
              189 tests passing, 2 skipped | 35 API endpoints | 12 screens | 10 languages
NEW IN v2:    field verification (500-label readiness, at 3) · OCR · perceptual photo hashing
              · JWT RBAC (5 roles) · hash-chained audit log · 15-tool chat agent
              · 10-language static i18n · severity design system · SALESFORCE + AGENTFORCE
NOT BUILT:    money-gap funnel · top-30 FP audit · audit capacity budget & Rs-coverage@K
              · entity 8-dim fingerprint · true change-point with dates · choropleth
              · audit-plan screen · Docker · AP/ablation/calibration
LIMITATIONS:  no fraud labels; ACTUAL_AMOUNT != expenditure (98.35% identical); no sanction
              date; no district column; no payments/GPS/estimates/vendor.
NEVER CLAIM:  fraud detected / fraud % / 100% accurate; cost-overrun on real data;
              tamper-PROOF log; the AI decides audits; invented algorithms.
DIFFERENTIATOR: prediction + decision-support + a closed verification loop + radical honesty
              (killed signals, label-readiness counter, declared authority) — not another
              anomaly dashboard.
```
