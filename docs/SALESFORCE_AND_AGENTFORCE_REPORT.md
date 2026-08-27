# Salesforce & Agentforce — what was built, what it adds, and what it is worth

**Status report · SIH 2026 · PS 26102 · Team Morior Invictus**

Written to be checked. Every number below came from a live query against the running
system, not from a plan.

---

## 1. The one-paragraph answer

> Our engine reads 2,10,993 works and decides **where a government officer should look**.
> Salesforce decides **what happens after they decide to look** — assignment, approval,
> a mobile app at the site, an audit trail. Agentforce connects an officer to both, in
> their own language. The models stay in Python because there is no Cox regression in
> Apex, and Salesforce holds the 500 cases that need a human rather than the two lakh
> works that do not. **That split is the design, not a limitation.**

---

## 2. What is actually running

### In the live Salesforce org

Org `00DAJ0000143KQ5EAI`, connected as `ropheangel1312...@agentforce.com`.

| | |
|---|---|
| Custom objects | **2** — Investigation Case, Evidence |
| Fields | **31**, correct types, picklists pre-populated |
| Investigation cases loaded | **500** (highest Audit-ROI, ₹97.5 Cr exposure) |
| Evidence records loaded | **1,586**, every one linked to its case |
| Path | **5 stages**, deployed with per-stage officer guidance |
| List views | All Cases · Open HIGH Priority · My Cases |
| Compact layout | deployed |
| Permission set | deployed and assigned |

All of it deployed from source (`salesforce_package/`) rather than clicked, so it is
reproducible: one command rebuilds the org from scratch.

### In the application

| Feature | Where |
|---|---|
| Salesforce casework hub | `/salesforce` |
| Audit plan under a budget | `/audit-plan` |
| Casework strip on every case file | `/case/:ref` |
| PDF case report | button on every case file |
| Agentforce assistant | floating, on every screen |
| Agentforce in 10 languages | follows the site language picker |
| Findings feed back as labels | `field.py`, immutable and attributed |

---

## 3. What Salesforce actually adds

This is the question worth answering carefully, because "we added Salesforce" is not an
answer.

### It adds the half of the problem we had not solved

Before: the system produced 37,705 leads and stopped.

```
ML  ->  37,705 leads  ->  ???
```

A lead nobody owns, with no due date and no record of what happened, is not monitoring.
It is a longer list.

After:

```
ML  ->  lead  ->  case  ->  officer  ->  site visit  ->  finding  ->  label  ->  better weights
```

### Concretely, five things we would otherwise have had to build

| What Salesforce gives | What it would have cost us |
|---|---|
| **Assignment and ownership** | a user model, queues, routing rules |
| **Approval before closure** | an approval engine |
| **Mobile app at the site** | an entire second frontend |
| **Field history — who changed what, when** | audit tables and triggers |
| **Reports and dashboards** | a charting and export layer |

The mobile app is the clearest case. An officer standing at a work site opens Salesforce on
their phone and the case is there, because every object we deployed is automatically
available on mobile. **We did not build a mobile app. We did not need to.**

### And one thing it adds that we could not have built at all

Credibility with the buyer. MoSPI does not procure bespoke case management. Government
departments already run Salesforce. "This is a Salesforce app your officers already know
how to use" is a deployment story; "we built our own workflow engine" is a maintenance
liability.

### What Salesforce is deliberately *not* doing

It is not the analytical warehouse. A free Developer Edition org holds roughly 2,500
records; the portfolio is 210,993 works. Even with unlimited storage it would be the wrong
place — there is no survival model, no clustering, no perceptual hashing in Apex.

**Say this before a judge asks it:** *"We loaded the 4,478 that need a human, not the two
lakh that do not."*

---

## 4. What Agentforce adds

An officer should not have to know which of eleven screens holds the answer.

### Six topics, all answering from real data

| Topic | Example question | What it does |
|---|---|---|
| Investigation Lookup | *"Tell me about MP3018356-W86316"* | full brief: evidence, stage, tier, next step |
| State Brief | *"Show me HIGH priority cases in Bihar"* | that state's casework and exposure |
| Escalation Tier | *"What does escalation tier mean?"* | how the 500 cases are routed |
| Top Exposure | *"Which case has the highest exposure?"* | ranked by money at risk |
| **Audit Planning** | *"What should I investigate first?"* | a live plan from the optimiser |
| **Casework Status** | *"How many cases are open?"* | the 500 across the five Path stages |

The last two are new. Before, both fell through to a generic reply.

Audit Planning parses a budget out of the question — *"plan 100 auditor-days"* returns a
100-day plan — and calls the same engine the Audit Plan screen uses. One source of truth.

### Multilingual, and honestly so

All **10 languages** at 100% of the phrase set.

The answers are templates, so the *structure* is translated from committed strings while
the data poured in is not:

- **Translated:** headings, field labels, and above all the non-fraud contract
- **Never translated:** work references, agency names, MP names, rupee figures

A work reference is an identifier, not a word. An agency's name is how it appears on its
own letterhead. Translating either produces something an officer cannot search for or
quote back to anyone.

Nothing is machine-translated at runtime. That would need the live model, and with no API
credits the fallback would silently be English — which is the failure this design exists to
avoid. A Tamil reader shown a list of flagged works and an English disclaimer has, in
practice, been shown a list of flagged works.

---

## 5. Which of the nine functionalities were implemented

| # | Functionality | Priority given | Status |
|---|---|---|---|
| 1 | AI audit prioritisation | 🔴 Core | ✅ already the core |
| 2 | Explainable case files | 🔴 Must | ✅ + **PDF export added** |
| 3 | Investigation workflow | 🔴 Must | ✅ **built** |
| 4 | **Audit-ROI optimisation** | 🔴 Must | ✅ **built — was missing entirely** |
| 5 | Salesforce case management | 🟠 Strong | ✅ **built and deployed** |
| 6 | **Evidence + resolution loop** | 🟠 Strong | ✅ **built** |
| 7 | Behaviour / change-point | 🟠 Strong | 🟡 pre-existing, not extended |
| 8 | Semantic duplication | 🟠 Strong | ✅ pre-existing |
| 9 | Agentforce copilot | 🟡 Enhancement | ✅ **extended + multilingual** |

**The four built from scratch this session: 4, 3, 6, 2 (PDF).** Plus 9 extended.

Nothing from the ❌ list was touched — no HDBSCAN, no GNN, no LLM anomaly detection, no
blockchain, no deep tabular models.

---

## 6. The audit plan — the strongest new thing

This did not exist and your own audit marked it ❌.

Ranking answers *"what is worst?"*. An official asks *"I have twenty auditor-days, where do
I send them?"* — a different question, because cases do not cost the same to check.

- first work at an implementing agency: **1.0 auditor-day** (travel, visit, write-up)
- every further work there: **0.35** — the auditor is already standing there

At 50 auditor-days, on real data:

| Strategy | Works | Agency visits | Exposure covered |
|---|---|---|---|
| **Optimised plan** | **100** | **23** | **₹47.1 Cr** |
| Audit-ROI ranking | 74 | 37 | ₹42.4 Cr (90%) |
| Biggest cheques first | 72 | 38 | ₹28.1 Cr (60%) |
| Highest risk first | 94 | 26 | ₹3.7 Cr (8%) |
| Random selection | 55 | 47 | ₹0.5 Cr (1%) |

The plan reaches **more works across fewer trips**. That is the entire mechanism, and it is
visible in the table.

**It is a heuristic and the tests say so.** Ratio-greedy is not optimal —
`test_the_planner_is_greedy_and_does_not_pretend_otherwise` pins a case where it trails the
clustered optimum. The comparison table is built to be able to report that we lost; a table
hard-wired to crown our own strategy would be decoration, not evidence.

---

## 7. The loop that makes it worth having

An officer records a finding in the casework hub. That finding writes an **immutable,
attributed** record into the same store the in-app field verification uses.

Three rules hold it together:

- **Stage moves are workflow.** They go back and forth; they are mutable state.
- **Findings are evidence.** They are not editable. A correction is a new record.
- **A finding needs a name.** An unattributed one raises rather than writing "anonymous"
  into the label set.

And one decision worth defending out loud: **"False Positive" maps to
`VERIFIED_COMPLETE`**, not to an outcome of its own. An officer saying *"we looked, nothing
wrong"* is a **negative label**, and negatives are half of what makes a label set usable.
Giving them their own name is how they quietly stop being counted.

This is the answer to the project's central limitation. There are no fraud labels in the
source data. These records are those labels, accumulating one site visit at a time. The
Data Transparency screen reports how far off the threshold still is rather than implying it
has been reached.

---

## 8. Honest gaps

**The agent inside the Salesforce org is not built.** What runs in the app is our own
Agentforce-branded topic router over the same data. Building the real one is about fifteen
minutes of clicking — `salesforce_package/SETUP.md` §7 — and the org is Agentforce-enabled.

**Ministry view is thinner than the auditor view.** Reports and dashboard metadata exist in
`salesforce_package/`; whether they deployed cleanly is unverified.

**Public Sector Solutions is not used.** Inspections, Data 360 and the public-sector case
management features are a licensed managed package, not available in a Developer Edition
org. Plain custom objects tell the same story and actually run.

**The cost model is an assumption.** One day per agency visit, 0.35 per follow-up. It is
stated on the screen and in the API response so a reviewer can disagree with it. Real
auditor-day figures from MoSPI would replace it without changing any code.

---

## 9. If a judge asks

**"Is the Salesforce real or a mock-up?"**
> Real org, real deployment, 500 cases with 1,586 linked evidence records. Deployed from
> source, so one command rebuilds it.

**"Why only 500 of 210,993?"**
> A Developer Edition org holds about 2,500 records, and Salesforce is a workflow platform
> rather than an analytical one. We loaded the ones that need a human.

**"Does Agentforce decide anything?"**
> No. It looks things up and shows which lookups it ran. There is no tool in it that can
> write, rank or move a threshold.

**"Is the multilingual real or Google Translate?"**
> Committed strings, ten languages, works with no internet. And the figures are deliberately
> not translated — a work reference is an identifier, not a word.

**"Your optimiser — is it optimal?"**
> No, and we have a test that documents where it loses. It is a greedy heuristic chosen
> because it is explainable: at every step it took the case buying the most exposure per
> auditor-day, and you can read the plan and check that.

---

## 10. Numbers to quote

| | |
|---|---|
| Works analysed | **2,10,993** |
| Salesforce cases | **500** · evidence records **1,586** |
| Exposure in the loaded cases | **₹97.5 Cr** |
| Audit plan @ 50 days | **100 works / 23 visits / ₹47.1 Cr** |
| Same budget, ranking top-down | 74 works / 37 visits / ₹42.4 Cr |
| Agentforce topics | **6** |
| Assistant languages | **10**, all at 100% |
| Tests passing | **210** |

**Quote these exactly or say "let me check".**
