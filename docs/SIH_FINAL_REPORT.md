# SIH 2026 — Final Report

**Team Morior Invictus · PS SIH26102 (MoSPI / DIID) · St. Joseph's Institute of Technology, Chennai**
**Compiled 2026-09-06, audited against the working tree and the revised deck**

This report has three parts:

| Part | Answers |
|---|---|
| **1** | What we built that the deck does not yet show — and two numbers in the deck that must be corrected |
| **2** | How the system moves from a scraped snapshot to a **live eSAKSHI feed** — plan, architecture, and what actually has to happen |
| **3** | The innovations that live data unlocks — real-world impact, and how to pitch each one |

---
---

# PART 1 — Deck vs. what is actually built

## 1.1 ⚠️ Two corrections the deck needs before submission

These are not opinions. They were read out of `data/artifacts/models/metrics.json` and a full
test run on 2026-09-06.

| Deck slide 3 says | The code produces | Action |
|---|---|---|
| **"Completion risk: Cox PH — right-censored (C-index 0.743)"** | **C-index = 0.6759** | **Fix the slide.** `0.743` appears nowhere in the repository |
| "Testing: 186 automated tests passing, 2 skipped" | **189 passing, 2 skipped** | Update — the suite grew |

**Why the first one matters so much.** A C-index of 0.743 versus 0.676 is the difference
between "good discrimination" and "moderate discrimination." If a judge asks to see the
metric — and on a modelling-heavy PS they might — the screen will say 0.6759 while the slide
says 0.743. That single mismatch would undermine the honesty positioning that the entire rest
of the deck is built on. **0.6759 is a perfectly defensible number.** Quote it, and explain
what it means: *given two works, the model ranks which finishes sooner correctly about 68% of
the time.*

## 1.2 What the revised deck already gets right

Credit where due — the revised deck fixed things the first version got wrong:

- **Backend now says "Parquet + JSON (SQLite audit log)"** — the earlier DuckDB claim is gone.
- **Change-points are honestly labelled "level-shift heuristic (change-date: planned)"** — this
  is exactly the right posture; it does not overclaim.
- **Peer comparison is described as same-state k=100 kNN**, which matches the implementation.
- **The governance layer** (RBAC, tamper-evident hash-chained audit log, methodology
  transparency) is on the architecture diagram.

## 1.3 Built and working, but **absent from the deck**

The deck's architecture diagram shows 7 layers and 3 frontend screens. The product has
**35 API endpoints and 12 screens.** Everything below exists, is tested, and demos.

### A. The field verification loop — *the biggest omission*

The deck's ladder ends at "CONSUMERS — human action." It does not show that **the human's
finding comes back into the system.**

| Feature | What it does |
|---|---|
| **OCR of work boards** (`ocr.py`) | RapidOCR reads the display board MPLADS already requires at every site — work reference and sanctioned amount — so nobody re-types a reference standing in a field. CPU-only, no GPU, degrades to manual entry rather than failing |
| **Ambiguity refusal** | OCR confidence is confidence in *pixels*. A weathered board reads one digit wrong at 99.6% and lands on a **different real work** — MPLADS references run in sequence. So the matcher returns every real reference one character away, cross-checks the painted amount, and **will not save until a human confirms** |
| **Perceptual photo hashing** (`photohash.py`) | pHash + dHash. A checksum answers *"same file"*; a perceptual hash answers *"same picture"* — surviving re-compression, resize, crop and brightness change. Catches a recycled site photograph, **the one check a human cannot do at scale** |
| **Immutable attributed records** (`field.py`) | Every verification carries who, when, what they found. Reading is open; writing requires a name |
| **Label-readiness counter** | Verifications **are** the fraud labels that §"no labels exist" says do not exist. At ~500 records the fusion weights could be fitted to what officers actually confirmed. We are at **3**, and the Transparency screen says **3**, not "coming soon" |

**This deserves its own slide.** It is the answer to the deck's own honesty problem: *"no fraud
ground truth"* is listed as Challenge #1 on slide 4, and this is the mechanism that
manufactures ground truth, one site visit at a time.

### B. Salesforce CRM + Agentforce integration

The deck's layer 7 says "CONSUMERS — human action" with three icons. In reality the lead
becomes a **managed case in Salesforce**:

- `Investigation_Case__c` and `Evidence__c` custom objects
- A **5-stage investigation Path** with written guidance at each stage
- **Agentforce** "Investigation Lookup" topic
- Reports and dashboards shipped in an SFDX package
- **Round trip**: findings recorded in Salesforce come back to the pipeline

This answers the question the deck currently leaves open — *"and then what happens?"*

### C. The data-grounded assistant

15 read-only tools over all 210,993 works, plus a deterministic offline router that answers
without any API key.

- **The model never computes.** It receives only figures the pipeline already produced. The
  prompt forbids inventing numbers; a filter then **discards** output containing forbidden
  words. *A prompt is a request; a filter is a guarantee.*
- **It shows its receipts** — every answer lists which tools produced it.
- **It is page-aware** — on a case file it offers questions about that work.
- Voice input, read-aloud, markdown tables, clickable work references, transcript export.

### D. Everything else missing from the deck

| Feature | Status |
|---|---|
| **10-language interface** — 182 keys × 10 languages, 100% coverage, **static** (never a network call) | ✅ |
| **Severity design system** — traffic-light with **measured contrast ratios**, and a distinct glyph per level because red/amber are indistinguishable under deuteranopia | ✅ |
| **Health Index** — 62.9/100, five weighted components, each shown with its explanation | ✅ |
| **Early-warning engine** — CRITICAL / HIGH / MEDIUM / LOW over open works | ✅ |
| **Compliance engine** — 8 checks, each **declaring its authority**; we assert **no official rules**, enforced by a test | ✅ |
| **Duplicates engine** — 223,407 pairs → **47,709 concerning**, and the reasoning for discarding the rest | ✅ |
| **Transparency screen** — what is measured, derived, and **unavailable and not faked** | ✅ |
| **Synthetic validation harness** — 904 planted anomalies, **69.25% detection** | ✅ |
| **RBAC login** — JWT, 5 roles, scope enforced server-side | ✅ |
| **Hash-chained audit log** — tamper-**evident**, with `verify_chain()` | ✅ |
| **12 screens**, **35 endpoints** | ✅ |

## 1.4 Suggested slide changes

| Slide | Change |
|---|---|
| 3 — Technical Approach | Fix **C-index → 0.6759**, tests → **189**. Add field-loop and Salesforce boxes to the architecture |
| **NEW** — The Verification Loop | OCR → photo hash → immutable record → label readiness (3 of 500). This is the strongest slide you are not showing |
| **NEW** — From Lead to Case | Salesforce Investigation_Case__c + 5-stage Path + Agentforce |
| 5 — Impact | Add: 10 languages · assistant that cites its sources · accessibility (glyphs, not colour alone) |
| **NEW** — Live Data Roadmap | Part 2 of this report |

---
---

# PART 2 — From a scraped snapshot to a live eSAKSHI feed

## 2.1 The honest starting position

**Today**, the system is trained and run on a **static historical extract** — roughly 210,993
works scraped from public MPLADS/eSAKSHI sources, frozen at a snapshot date of **2026-05-26**.

**In the real deployment**, MoSPI would connect eSAKSHI directly and the data would arrive
continuously. The deck's architecture diagram already draws "DATA SOURCES (Govt, public)" at
the top — but everything below it currently assumes one big file, loaded once.

**This part explains what changes, and why the change makes the product dramatically better.**

## 2.2 The whole idea in plain language

> **Today we have a photograph. Live data gives us a video.**
>
> Right now we study one photograph of every public work in India, taken on one day. We can
> say *"this work looks stalled."* But the photograph was taken months ago — by the time an
> officer reads it, the work has been stuck for a long time already.
>
> With a live feed, the same system watches the works **as they move**. And that changes the
> most important thing about it:
>
> **We stop reporting works that already failed. We start warning about works that are about
> to.**

Here is the concrete version of that idea, and it is the single best sentence in this report:

> Every kind of work has a normal rhythm. Most community halls in Bihar finish in about
> fourteen months. Our model learned that rhythm from 210,000 works.
>
> With a live feed, **on the day a particular community hall passes the point where most of
> its peers had already finished**, the system can raise its hand — automatically, that
> morning, before anyone has complained about it.
>
> That is a fundamentally different product from a report. That is an early-warning system.

## 2.3 What actually has to change

Four things. Everything else in the pipeline stays as it is.

### Change 1 — Ingestion becomes incremental, not "reload everything"

**Today:** we read the whole dataset and rebuild every artifact. Takes about four minutes.

**Live:** four minutes every time a single record changes is wasteful and, at national scale,
impossible. So we switch to **only processing what changed** — new works, and works whose
stage moved.

*In plain terms:* instead of re-reading the whole ledger every morning, we read only
yesterday's new entries and the lines that were edited.

### Change 2 — The clock has to move

This is subtle and it is the thing most teams would get wrong.

Our entire survival model is anchored to a **snapshot date**. "How long has this work been
open?" is measured against 2026-05-26. In a live system that anchor **moves every single
day** — which means every open work quietly gets older overnight, and its risk goes up on its
own, without any new data arriving.

*In plain terms:* it is not enough to add new records. **Yesterday's unfinished works are
today's slightly-more-worrying works**, even if nothing about them changed. The system has to
re-age the whole open portfolio nightly. That daily re-ageing is exactly what produces the
"about to stall" alert in §2.2.

### Change 3 — Models need a retraining cadence

Not everything needs retraining at the same speed:

| Component | How often | Why |
|---|---|---|
| **Peer comparison / percentiles** | **Nightly** | Cheap, and peers shift as works complete |
| **Completion-risk (Cox)** | **Monthly** | Needs enough new completions to be worth refitting |
| **Archetypes (clustering)** | **Quarterly**, or on drift alert | Work *types* change slowly; re-clustering constantly would make yesterday's archetype IDs meaningless |
| **Fusion weights** | **On evidence**, not on a schedule | Only when field verifications cross the 500 threshold (§3.1) |

*In plain terms:* the fast-moving parts update every night; the deep learning-what-normal-looks-like
part updates a few times a year, because "what a community hall is" does not change weekly.

### Change 4 — Alerts get pushed, not pulled

**Today:** an officer opens the dashboard and looks.
**Live:** the system emails/notifies the right officer when something crosses a line — scoped
to their jurisdiction by the RBAC we already have.

## 2.4 The architecture for live data

```
┌──────────────────────────────────────────────────────────────────────┐
│  eSAKSHI  (MoSPI system of record)                                   │
│  Tier 0 today: public scrape · Tier 1: scheduled export ·            │
│  Tier 2 target: authorised API / change-data-capture                 │
└───────────────────────────┬──────────────────────────────────────────┘
                            v
┌──────────────────────────────────────────────────────────────────────┐
│  1 · LANDING ZONE            every batch stored raw, immutable,      │
│                              timestamped. Never overwritten.         │
└───────────────────────────┬──────────────────────────────────────────┘
                            v
┌──────────────────────────────────────────────────────────────────────┐
│  2 · RECONCILIATION GATE  ★ innovation                               │
│     Check the batch against the MP-level totals that ship with it.   │
│     Does not balance -> QUARANTINE, alert a human, do not ingest.    │
└───────────────────────────┬──────────────────────────────────────────┘
                            v
┌──────────────────────────────────────────────────────────────────────┐
│  3 · CHANGE DETECTION        what is new? what moved stage?          │
│                              only those rows go downstream           │
└───────────────────────────┬──────────────────────────────────────────┘
                            v
┌──────────────────────────────────────────────────────────────────────┐
│  4 · NIGHTLY RE-AGEING    ★ the anchor moves; every open work ages   │
└───────────────────────────┬──────────────────────────────────────────┘
                            v
┌──────────────────────────────────────────────────────────────────────┐
│  5 · SCORING (unchanged)     peers · completion risk · outlier ·     │
│                              duplicates · compliance · fusion        │
└───────────────────────────┬──────────────────────────────────────────┘
                            v
┌──────────────────────────────────────────────────────────────────────┐
│  6 · STALL-CLOCK WATCHER  ★ did any work cross its peer curve today? │
└───────────────────────────┬──────────────────────────────────────────┘
                            v
┌──────────────────────────────────────────────────────────────────────┐
│  7 · SERVE + NOTIFY          dashboard · assistant · Salesforce case │
│                              · scoped push alert to the right officer│
└───────────────────────────┬──────────────────────────────────────────┘
                            v
┌──────────────────────────────────────────────────────────────────────┐
│  8 · FIELD LOOP              officer verifies -> immutable record    │
│                              -> feeds the weights (★ flywheel)       │
└──────────────────────────────────────────────────────────────────────┘

   Running alongside, always:
   MONITORS   archetype drift · schema drift · reconciliation failures
   GOVERNANCE hash-chained audit log · RBAC scope · as-of replay (★)
```

★ = an innovation described in Part 3.

## 2.5 How we actually get the data — three honest tiers

**eSAKSHI does not publish a public API.** Any claim that we can stream from it today would be
false. So we design for three tiers and say plainly which one we are on.

| Tier | Mechanism | Latency | What it needs | Status |
|---|---|---|---|---|
| **0 — today** | Public extract, loaded as a file | Snapshot | Nothing | ✅ **This is what we run** |
| **1 — realistic first deployment** | MoSPI drops a scheduled export (SFTP / object store), we poll for it | Daily / hourly | An MoU and a delivery location. **No eSAKSHI code changes** | 🔜 Designed, not built |
| **2 — target** | Authorised API or change-data-capture; eSAKSHI notifies us on change | Minutes | MoSPI engineering + access approval | 🔮 Designed |

**Why Tier 1 is the honest pitch.** It requires nothing from eSAKSHI's engineering team except
a nightly file in an agreed location — a very low ask — and it delivers **almost all** of the
value, because MPLADS works move on a scale of weeks and months, not seconds. **Daily is
genuinely real-time for this domain.**

> **Say this to a judge:** *"We do not need sub-second streaming. A road does not stall
> between 2pm and 3pm. One reliable nightly delivery gives us everything, and asks almost
> nothing of MoSPI's systems. We designed for the ask they would actually approve."*

## 2.6 What breaks with live data, and how we handle it

Being ready for these is what separates a design from a wish.

| Problem | Plain English | Our handling |
|---|---|---|
| **Late-arriving records** | A completion recorded in March arrives in June | Ingestion is append-only and event-timestamped; re-score affected works, never overwrite history |
| **Schema drift** | eSAKSHI adds/renames a column | Schema contract test on every batch; unknown columns are carried, not dropped; a *removed* required column halts ingest loudly |
| **Duplicate delivery** | The same batch arrives twice | Deterministic dedup key already exists: `(recommendation_date, work_ref, source_file, raw_row_index)` |
| **A bad batch** | Upstream export is truncated or corrupt | **Reconciliation gate** (§3.3) quarantines it before it can poison the models |
| **Model staleness** | The world moves; the model does not | Scheduled retraining cadence (§2.3) + drift monitor (§3.5) |
| **Alert fatigue** | Too many notifications and officers stop reading | Alerts are scoped by RBAC, ranked by Audit-ROI, and rate-limited per officer per day |
| **The anchor problem** | Everything silently ages | Explicit nightly re-ageing job, and the snapshot date is shown on every screen |

---
---

# PART 3 — Innovations that live data unlocks

Seven ideas. Each is listed with **what it is in plain language**, **why it matters in real
life**, and **why it lands in a pitch**. They are ranked by impact.

## 3.1 ★ The Verification Flywheel — *the system gets better the more it is used*

**Plain English.** Every time an officer visits a site and records what they found, the system
gains one piece of real ground truth. Today those weights — how much an unusual amount matters
versus an unusual delay — are **sensible numbers we chose and published**. Once about 500
verifications exist, they stop being our judgement and start being **fitted to what officers
actually confirmed on the ground**.

**Why it matters in real life.** Every other anomaly system is frozen at the moment it ships.
This one has a mechanism to improve, and the improvement comes from the officers' own work —
not from us. The longer MoSPI runs it, the more it is tuned to Indian public works
specifically.

**Why it lands in a pitch.** Slide 4 of the deck lists *"No fraud ground truth"* as challenge
number one. **This is the answer to that challenge**, and it is half-built already. It turns
the project's biggest honest weakness into its strongest long-term story.

> **Say:** *"Everyone else's model is as good on day 1000 as it was on day one. Ours is
> designed to get better, and the Transparency screen shows exactly how far along that is —
> we are at 3 of 500, and we say 3."*

**Needs:** live data + officers using it. **Already built:** the record store, the counter, the
honesty. **Not built:** the refit itself (correctly gated until there is data to refit on).

## 3.2 ★ As-Of Replay — *audit defensibility through time*

**Plain English.** Because every batch is stored immutably and the audit log is hash-chained,
the system can answer: **"What did you know on 14 March, and what did you tell the officer
that day?"**

**Why it matters in real life.** This is the difference between a tool that helps and a tool a
government can defend. When an officer's decision is questioned two years later — by CAG, by a
court, by a parliamentary committee — the fair question is *"was that reasonable with the
information available at the time?"*, not *"does it look right with hindsight?"* Almost no
analytics system can answer that. Ours can, because we never overwrite.

**Why it lands in a pitch.** It reframes the audit log from a compliance checkbox into a
**decision-defence mechanism**. It is unusual, it is deeply "government-grade," and it costs
nothing extra because append-only ingestion and the hash chain already exist.

> **Say:** *"We can reconstruct exactly what this system knew on any past date. An officer's
> judgement gets assessed on what was knowable then — not on hindsight. That protects the
> officer, and it protects the institution."*

## 3.3 ★ The Reconciliation Gate — *refuse bad data instead of absorbing it*

**Plain English.** The MPLADS data ships with MP-level totals that are **independent** of the
individual work rows — we already use them as a cross-check, and the median ratio comes out at
exactly 1.0000. In a live feed, every incoming batch gets balanced against those totals
**before** it is allowed in. A batch that does not balance is **quarantined**, and a human is
told — it is never silently ingested.

**Why it matters in real life.** The most dangerous failure in a monitoring system is not being
wrong loudly — it is being wrong quietly. A truncated nightly export would shift every
percentile in the country and nobody would notice for weeks. This makes silent corruption
structurally impossible.

**Why it lands in a pitch.** It is a genuinely uncommon idea, it uses a property of MPLADS data
that most teams discard as "corrupt rows," and it demonstrates engineering maturity in one
sentence.

> **Say:** *"Those 3,987 rows everyone throws away as corrupt are MP-level totals. We use them
> as a checksum. If tonight's data doesn't balance against them, it doesn't get in."*

## 3.4 ★ The Stall Clock — *from post-mortem to early warning*

**Plain English.** Every night, every open work is checked against the completion curve of its
peer group. The moment a work **crosses the point where most of its peers had already
finished**, it is flagged — that morning.

**Why it matters in real life.** This is the whole reason live data is worth having. A stalled
work caught at month 20 is a post-mortem. The same work caught the day it crosses month 14 is
**an intervention that can still save the asset**. Same model, same maths — the only difference
is that the data is arriving continuously.

**Why it lands in a pitch.** It is the clearest possible articulation of *why live data
matters*, and it converts our existing survival model from a descriptive tool into a genuinely
predictive one with no new modelling at all.

> **Say:** *"Our model already knows a community hall in Bihar normally finishes in fourteen
> months. With a live feed, on month fourteen of a hall that hasn't finished, we raise our hand
> — automatically, that morning, before anyone has complained."*

## 3.5 ★ Archetype Drift Monitor — *intelligence about the scheme, not just the works*

**Plain English.** The system learned 50 kinds of work from the descriptions. If newly arriving
works stop fitting those 50 kinds, something has changed **about the scheme itself** — new
priorities, new categories, a policy shift.

**Why it matters in real life.** Every other signal in this product is about *one work*. This
one is about **MPLADS as a whole**, and its audience is MoSPI policy staff rather than a
district auditor. It answers *"is the scheme changing shape?"* — a question nobody currently
has a tool for.

**Why it lands in a pitch.** It gives the product a **second customer** inside the same
ministry, and it shows the architecture generating insight at a level above the individual row.

> **Say:** *"When new works stop looking like anything we've seen before, that's not a
> suspicious work — that's the scheme changing. MoSPI should know that within weeks, not at
> the end of a five-year review."*

## 3.6 Calendar-Aware Baselines — *don't cry wolf every March*

**Plain English.** Public spending has a rhythm — a rush before the financial year closes, a
lull during elections. With enough live history, the system learns that rhythm and stops
treating a normal March surge as an anomaly.

**Why it matters in real life.** It directly attacks the number-one reason officers abandon
alerting tools: false alarms. An officer who gets a spike alert every March learns to ignore
March alerts — and then misses the real one.

**Why it lands in a pitch.** It shows we are thinking about **whether the tool will still be
used in year two**, which is a maturity most hackathon projects never display.

## 3.7 Offline-First Field Verification — *built for the districts that need it most*

**Plain English.** The verification app works **without a signal**. An officer at a remote site
photographs the board, records what they found, and the phone syncs when it is back in
coverage.

**Why it matters in real life.** The works most likely to be neglected are in exactly the
places with the worst connectivity. A verification tool that needs 4G at the site would be
unusable precisely where it is most needed.

**Why it lands in a pitch.** It shows the design was done for **India as it is**, not for a
conference-room demo. Judges from a government ministry notice this.

## 3.8 Innovation summary

| # | Innovation | Real-world impact | Pitch strength | Build cost |
|---|---|---|---|---|
| 1 | **Verification flywheel** | Very high — system improves with use | **Very high** — answers "no ground truth" | Low (mostly built) |
| 2 | **As-of replay** | High — decision defensibility | **High** — uniquely government-grade | Low (log exists) |
| 3 | **Reconciliation gate** | High — prevents silent corruption | **High** — uncommon, shows maturity | Low |
| 4 | **Stall clock** | Very high — intervention, not post-mortem | **Very high** — the reason for live data | Medium |
| 5 | **Archetype drift** | Medium — policy-level insight | Medium-high — a second customer | Medium |
| 6 | **Calendar baselines** | Medium — kills false alarms | Medium — shows year-two thinking | Medium |
| 7 | **Offline-first field app** | High — works where it matters | Medium-high — India-realistic | Medium |

**If you add only two slides:** the **Verification Flywheel** and the **Stall Clock**. The first
resolves the deck's own stated challenge #1; the second explains in one sentence why live data
transforms the product.

---
---

# Appendix — Verified numbers (2026-09-06)

Quote these; never estimate.

| Measure | Value |
|---|---|
| Works | **210,993** (85,773 completed · 125,220 open) |
| Recommended / exposure | **₹11,565 Cr / ₹1,302 Cr** |
| Investigation leads | **37,705** — 4,478 HIGH · 33,227 MEDIUM |
| Coverage | 36 states · 545 constituencies · 778 agencies |
| Archetypes | 50, silhouette **0.050** *(separation, never accuracy)* |
| Completion risk | Cox PH held-out C-index **0.6759** ⚠️ *(deck says 0.743 — fix)* |
| Multivariate outliers | **4,220** |
| Duplicates | 223,407 pairs → **47,709 concerning** |
| Compliance | **8 checks**, none asserting an official rule |
| Behaviour shifts | **73 of 697** agencies |
| Health Index | **62.9 / 100** |
| Synthetic validation | **69.25%** detection over **904** planted (stalled 96.1 · inflated 83.2 · break 58.0 · cloned 50.0) |
| Tests | **189 passing, 2 skipped** ⚠️ *(deck says 186)* |
| API / screens / languages | **35 endpoints · 12 screens · 10 languages** |
| Field verifications | **3** of ~500 needed to refit weights |

**Never claim:** fraud detected · a fraud percentage · **100% accurate** · cost-overrun on real
data · tamper-*proof* (it is tamper-**evident**) · that the AI decides audits · that we invented
any algorithm.
