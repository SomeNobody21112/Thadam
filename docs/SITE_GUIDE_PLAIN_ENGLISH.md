# The whole system, in plain English

**MPLADS Intelligence · SIH 2026 · PS 26102 (MoSPI) · Team Morior Invictus**

No jargon. If you read only this file you will be able to explain every screen, every
Salesforce feature, and all nine functionalities to anyone.

---

## Part 1 — What is this thing, in one page?

### The problem

Members of Parliament each get money to spend on local public works — roads, school rooms,
community halls, streetlights, outdoor gyms. That's the **MPLADS** scheme. Every work gets
recommended, sanctioned, built, and (eventually) marked complete. All of that is recorded
in a government system called eSAKSHI.

We have **2,10,993 works** worth **₹11,565 crore** in front of us.

Here is the problem in one sentence:

> **Nobody can look at two lakh works. So which ones should a government auditor actually
> go and inspect?**

Today that decision is made by hand, by hunch, or by complaint. Most works are fine. A few
are not. There is no way to tell which is which without visiting — and you cannot visit two
lakh sites.

### What we built

A system that reads all 2,10,993 works and **tells an officer where to look first, and
why.**

Think of it like a doctor's triage desk in a busy hospital. Triage doesn't diagnose anyone.
It doesn't say "this person has pneumonia." It says *"see this one before that one, and
here is what worried me."* A doctor still examines the patient.

That is exactly what this is. It produces **investigation leads with evidence** — never
accusations.

### The one rule that shapes everything

> **We never say a work is fraudulent. Not once. Anywhere.**

Why not? Because **the data contains no examples of fraud**. Nobody has ever labelled a
single one of these 2,10,993 works as "this one was a problem." Without examples, no
computer can learn to spot fraud — it can only *pretend* to, and a system that pretends is
worse than no system, because someone will believe it.

So we say what is honestly true instead: *"This work is unusual compared to works like it,
here are the four independent reasons why, and a human should go and check."*

There is even an automated test that searches our entire codebase for words like
`fraud_score` and **fails the build** if it finds one. It has caught real mistakes twice.

### How it decides — four steps, in plain words

| Step | Plain English |
|---|---|
| **1. Learn what normal looks like** | Group the 2,10,993 works into 50 families of similar things — "village roads", "school toilets", "outdoor gyms". A ₹65 lakh road is normal; a ₹65 lakh gym is not. You can only judge a work against works *like it*. |
| **2. Compare each work to its true peers** | Is this one unusually expensive? Taking unusually long? Suspiciously identical to another one? Compared only against its own family, in its own state. |
| **3. Predict what will happen** | Of the works still unfinished, which ones look likely to stall? This uses **survival analysis** — the same maths hospitals use to estimate patient outcomes. |
| **4. Turn it into money and rank it** | "Risk" is abstract. **₹28 lakh at risk** is not. Every work gets a rupee figure for how much money is genuinely uncertain, and the list is ranked by that. |

Out of 2,10,993 works, **37,705** were surfaced as worth a look. **4,478** of those are
HIGH confidence, meaning **four or more completely separate signals agreed**. One signal on
its own is usually noise. Four independent ones agreeing is a reason to drive out there.

### The honest bits we say out loud

Most demos hide their weaknesses. We print ours on the screen:

- **Our grouping quality score is 0.050 out of 1.0.** That's low. We say so, on the page.
  It means "roughly useful families", not "perfect categories."
- **The cost of an audit visit (1 day per agency) is our assumption, not a measured fact.**
  Printed on the screen and in the PDF so anyone can disagree with it.
- **We tested the obvious fraud signals and publicly rejected them.** The famous one:
  everyone assumes you can catch overspending by comparing the actual spend to the
  sanctioned amount. We checked. In this data, **98.35% of completed works have those two
  numbers exactly equal.** The field is a copy, not a measurement. There is no overspending
  signal here, and any team claiming one is reading a column that doesn't mean what they
  think.

---

## Part 2 — Every tab on the site, and what it actually does

The site has **16 screens**. Here is each one in one paragraph, plus what you'd say about
it in a demo.

### The way in

#### 🏠 Landing page (`/`)
The front door. Explains the project and its promise in a sentence. No data — it exists so
a first-time visitor knows what they're looking at before the numbers hit them.

#### 🔑 Login (`/login`)
Four demo accounts, each seeing a different slice of the country:

| Account | Password | Sees |
|---|---|---|
| `ministry` | `mplads2026` | Everything, all 36 states |
| `auditor` | `mplads2026` | Everything (CAG audit officer) |
| `bihar` | `mplads2026` | **Only Bihar** |
| `saran` | `mplads2026` | **Only the Saran constituency** |

**The important part:** the Bihar account cannot see Kerala's data *even if it asks the
server directly*. The restriction is enforced on the server, not hidden in the browser.
There's a test that proves it. You do not need to log in to read — but you **must** be
signed in to record a site inspection, because a finding without a name on it is not
evidence.

---

### 📊 MONITOR — the working screens

#### ▤ Overview (`/overview`)
The national picture on one page. Total works, total money, how many are open versus
complete, how many leads were surfaced, and a **Health Index of 62.9 / 100** for the scheme
overall. This is the ministry's morning screen — "is the country broadly OK?"

#### ▦ Investigation Queue (`/worklist`)
**The core list.** All 37,705 surfaced works, ranked by how much money is at risk per day
of audit effort. Filter by state, confidence band, or signal type. Click any row to open
its full case file.

This is the screen that answers *"what should I look at?"*

#### ◷ Audit Plan (`/audit-plan`)
**The single strongest idea in this project.**

The queue answers *"what is worst?"*. A real officer asks something different: **"I have
50 auditor-days this quarter. Where do I send them?"**

Those are not the same question, because **cases don't cost the same to check**. Five works
inside one district office is one trip. Five works in five districts is five trips. An
auditor who blindly follows a ranked list spends the quarter in a car.

So we price it honestly:
- First work at an agency: **1 full day** (travel, the visit, the write-up)
- Every further work at that same agency: **0.35 of a day** — the auditor is already there

Then we plan under that budget. And here's the result on real data at 50 auditor-days:

| Strategy | Works reached | Trips | Money covered |
|---|---|---|---|
| **Our optimised plan** | **100** | **23** | **₹47.1 Cr** (100%) |
| Just working our own ranking top-down | 74 | 37 | ₹42.4 Cr (90%) |
| Biggest cheques first | 72 | 38 | ₹28.1 Cr (60%) |
| Highest risk score first | 94 | 26 | ₹3.7 Cr (8%) |
| Picking at random | 55 | 47 | ₹0.5 Cr (1%) |

**More works, fewer trips, more money covered.** The whole gain is travel.

And the honest part: **that comparison table is built so it can report that we lost.** A
table hard-wired to always crown our own method would be decoration, not evidence. There is
a test that pins a case where our method comes second.

#### ◫ Field Rota (`/rota`) — *new*
The plan says where the days go. A supervisor can't hand a plan to anyone — they hand out a
**rota**: names, agencies, days.

One rule makes this interesting:

> **An agency is never split between two auditors.**

Why? The entire saving above depends on the second work at an agency being cheap *because
somebody is already standing there*. Send two people and you pay for that journey twice
while only earning it once — and every number on the Audit Plan screen quietly stops being
true.

At **50 days across 4 auditors** the system produces: 23 trips, 100 works, 49.95 of the 50
days used, and the workload spread between the busiest and quietest auditor is **0.4 of a
day**. Nearly perfectly even.

We also print the honest caveat: this kind of scheduling is a famously hard problem
(NP-hard), so our method is a well-known shortcut called LPT — but LPT has a *mathematically
proved* guarantee that its longest round is within 1.25× the best rota that could possibly
exist. **We print both the guarantee and the spread we actually achieved.**

If you ask for more auditors than there are trips, somebody is idle — and the screen
**says so** rather than splitting an agency to make everyone look busy.

**📄 Field Day Pack:** click a button and any auditor's round becomes a **PDF they carry** —
where to be on which day, a tick box against every work, what to record (including "nothing
wrong"), and the cost assumptions printed on the page so an officer who finds them wrong in
the field can say so.

#### ⌂ Agency Dossier (`/agency`) — *new*
An auditor doesn't travel to a *work*. They travel to a **body** — a district planning
office, a municipal corporation. This is the briefing they read on the journey: what this
agency holds, what it builds, what was found here last time.

**This screen carries the biggest safety risk in the whole product, and it's designed
around that risk.** A district office with four thousand works will naturally surface more
leads than one with forty. Reading the raw count as a signal is the single most likely way
a system like this gets somebody unfairly investigated.

So **every number is printed beside the national rate**, and where an agency is ordinary,
the page says so in words:

> *"6.6% of this agency's works were surfaced, against 17.9% nationally — below the
> ordinary rate."*

and where it isn't:

> *"31.0% … about 1.7 times the national rate. **That is a reason to look, not a finding.**"*

Under 20 works, no rate is calculated at all — the arithmetic would be meaningless.

What officers actually found on site sits **above** the model's reasoning on the page,
because a real visit outranks any calculation. Demo records are shown but clearly marked.

---

### ⚡ CASEWORK & CRM

#### ⚡ Salesforce & Agentforce (`/salesforce`)
The hand-off screen. See Part 3 below — this one needs its own section.

Includes the new **"What has gone quiet"** strip at the top: which cases are past their
review date, and how much money is sitting in them.

---

### 🔍 INTELLIGENCE — the "why" screens

#### ◪ Temporal (`/trends`)
Behaviour over time. Did an agency's pattern of recommendations suddenly shift? **73 of 697
agencies** changed measurably. A change is not wrongdoing — a new officer, a new scheme
round, or a genuine policy shift all look identical from here. It's a question, not an
answer.

#### ⧉ Near-Duplicates (`/duplicates`)
Two works that describe the same thing. We found **223,407 similar pairs**, narrowed to
**47,709 genuinely concerning** ones.

The honesty here matters: **repeated descriptions are completely normal in this scheme.** A
road built in three phases legitimately has three near-identical entries. So we report the
pair, show both descriptions side by side, and ask a human to confirm whether they're
genuinely separate works. We never conclude.

#### § Compliance (`/compliance`)
Rule checks against the scheme's own guidelines — **5,946 works flagged**. Things like "this
work completed but has no sanction record" (70 cases) or "this date is before the
recommendation date" (1,194 cases). Some of these are data-entry errors and some are real
process failures; the screen doesn't pretend to know which.

#### ◈ Work Archetypes (`/archetypes`)
The 50 families the system learned. **49 got a human-readable name**; one is honestly
labelled *"uninterpretable"* because we couldn't work out what it was, and inventing a name
for it would have been a lie.

This screen also prints the grouping quality score of **0.050** and explains it is low.

---

### ✓ TRUST — the screens that hold us to account

#### ◉ Data Transparency (`/transparency`)
Every known weakness in the data, listed openly: 695 orphan records, no real sanction date,
no district column, the `ACTUAL_AMOUNT` problem. Also tracks how far we are from having
enough real site visits to improve the system's own weights.

#### ◎ Field Scoreboard (`/scoreboard`) — *new*
**The one screen this system is allowed to lose on.**

The question: *when an officer actually went to look, did the works we called HIGH turn out
worse than the ones we called MEDIUM?*

Three rules, each of which costs us a number we'd rather show:

1. **No percentage below 10 visits.** Three visits and two problems found is *three visits*,
   not "67% accuracy". And the bar on the chart is left **completely empty**, never drawn
   short — a short bar reads as a low rate.
2. **Every percentage carries an error range.** Where two bands' ranges overlap, we
   explicitly **do not claim** one ranks above the other, however different the bars look.
3. **The sample is biased and always will be.** Officers go where this model sends them, so
   the works we *never* flagged barely get visited. That's stated with the result, not in a
   footnote.

Right now it reports **3 site visits and refuses to score any of them.** That is the correct
answer, and it's the one a judge should be shown.

#### ? How it works (`/how`)
A walkthrough of the whole pipeline for a non-technical reader.

---

### 📁 Case File (`/case/:ref`) — reachable from any list

The detailed page for one work. Contains:

- **What it is** — description, state, agency, MP, amount, dates
- **Why it was surfaced** — every signal, in plain sentences, grouped into families
- **How it compares to its peers** — "at the 100th percentile of 144 similar works"
- **Rule check results and early warnings**
- **A recommended next step**, always phrased as *"a human should verify X"*
- **The casework strip** — is anyone actually working this case, and how far along?
- **Field verification** — record what you found, upload a photo of the work board
- **📄 PDF export** — the whole thing as a document you can email or carry

Two details worth knowing:

**Works we never flagged still get a case file.** They return a "clear record" page instead
of a 404. This isn't cosmetic: if only flagged works can be inspected, then every label we
ever collect is a positive, and the system can never learn it was wrong about anything.

**The PDF has the "this is not a fraud finding" disclaimer on every single page.** A PDF
outlives the screen it came from — it gets emailed, printed, and read months later by
someone who never saw the caveat.

---

### 📷 The camera feature (inside any case file)

Photograph a work board at a site. The system:

1. **Reads the text off the board** (OCR) and matches it against all 2,10,993 works
2. **Refuses to settle an ambiguous match by itself.** A weathered board can read one digit
   wrong at 99.6% confidence and land on a *different real work*, because MPLADS reference
   numbers run in sequence. So it shows every reference one character away, cross-checks the
   rupee amount painted on the board, and **will not save until a human ticks a box.**
3. **Fingerprints the photo** against every photo ever submitted — catching a resized,
   re-compressed, brightened copy that a simple file check would miss.
4. **Reports a re-used photo as a question, never a finding.** Two phases of one road
   genuinely look identical from the roadside.

What the officer concluded and what the camera saw are stored in **separate columns on
purpose** — the two disagreeing is the single most useful thing a photograph can tell you,
and storing only the resolved answer throws that away.

---

### 💬 The assistant (floating button, every screen)

Ask questions in plain language across all 2,10,993 works. **15 tools, all of them
read-only** — there is a test that reads the assistant's own source code and fails if it
finds anything capable of writing, ranking, or moving a threshold.

Available in **10 languages**: English, Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati,
Kannada, Malayalam, Punjabi.

---

## Part 3 — Salesforce and Agentforce, in plain English

### The one-sentence version

> **Our engine decides where an officer should look. Salesforce handles everything that
> happens after they decide to look.**

### Why we needed it

Before Salesforce, the system did this:

```
2,10,993 works  →  37,705 leads  →  ??? 
```

A lead nobody owns, with no due date and no record of what happened, **is not monitoring.
It's a longer list.**

After:

```
works → lead → case → officer → site visit → finding → label → better system
```

### What Salesforce gives us that we'd otherwise have to build

| We get for free | It would have cost us |
|---|---|
| **Assignment and ownership** — who owns this case | building a user system, queues, routing rules |
| **Approval before a case closes** | building an approval engine |
| **A mobile app at the site** | building an entire second application |
| **Full history — who changed what, when** | building audit tables and database triggers |
| **Reports and dashboards** | building a charting and export layer |

The mobile one is the clearest. **An officer standing at a work site opens Salesforce on
their phone and the case is there** — because every object we deployed is automatically
available on mobile. We did not build a mobile app. We did not need to.

And one thing we could never have built: **credibility with the buyer.** Government
departments already run Salesforce. *"This is a Salesforce app your officers already know
how to use"* is a deployment story. *"We built our own workflow engine"* is a maintenance
liability.

### What's actually in the live Salesforce org

Real org, real deployment, connected as `ropheangel1312...@agentforce.com`.

| Thing | Count | What it is |
|---|---|---|
| **Investigation Case** | **500** records | The 500 highest-value leads, ₹97.5 crore of exposure |
| **Evidence** | **1,586** records | Every reason each case was surfaced, linked to its case |
| **Site Verification** | **4** records | What an officer *and* the camera found |
| **Audit Assignment** | *built, not yet loaded* | The rota: who visits what, on which day |
| **The 5-stage Path** | deployed | New → Assigned → In Progress → Verified → Closed |
| Custom fields | **65** | correct types, picklists filled in |
| List views, tabs, app, permission set | deployed | including one called *"Camera Raised A Question"* |

**Everything is deployed from source code, not clicked together.** One command rebuilds the
entire org from scratch. That is the difference between a demo and a product.

### "Why only 500 of 2,10,993?"

Two reasons, and the second is the real one:

1. A free Salesforce Developer Edition org holds about 2,500 records. Two lakh works would
   be roughly 420 MB.
2. **More importantly, it would be the wrong place.** Salesforce is a workflow platform, not
   an analytical one. There is no survival model, no clustering, and no image fingerprinting
   in Apex. **We loaded the 500 that need a human, not the two lakh that don't.**

That split is the design, not a limitation.

### Agentforce — the assistant, in ten languages

An officer shouldn't need to know which of sixteen screens holds the answer. **Ten topics,
every one of them answering from real data:**

| Ask it | It tells you |
|---|---|
| *"Tell me about MP3018356-W86316"* | The full brief on one case: evidence, stage, next step |
| *"Show me HIGH priority cases in Bihar"* | That state's casework and money at risk |
| *"What does escalation tier mean?"* | How the 500 cases are routed |
| *"Which case has the highest exposure?"* | Ranked by money at risk |
| *"Plan 100 auditor-days"* | A live plan from the same optimiser the screen uses |
| *"How many cases are open?"* | The 500 across the five stages |
| ⭐ *"What has gone quiet?"* | Cases past their review date, and the money in them |
| ⭐ *"Split 50 days across 4 auditors"* | Who goes where, on which day |
| ⭐ *"Has the model been right so far?"* | What site visits actually said back |
| ⭐ *"Brief me on SARAN before I visit"* | The agency, not the work |

⭐ = new.

**Crucially, Agentforce decides nothing.** It looks things up and shows you which lookups
it ran. There is no tool inside it that can write, rank, or move a threshold.

### The multilingual part — and why it's honest

All **10 languages at 100%** of the phrase set (47 phrases).

The answers are **templates**, so the *structure* is translated from committed text while
the data poured into it is not:

- **Always translated:** headings, field labels, and above all **the "this is not a fraud
  finding" line**
- **Never translated:** work reference numbers, agency names, MP names, rupee figures

Why? **A work reference is an identifier, not a word.** An agency's name is how it appears
on its own letterhead. Translate either and you've given an officer something they cannot
search for or quote back to anyone.

**Nothing is machine-translated at run time.** That would need a live AI connection, and
with no API credits the fallback would silently be English — which is the exact failure this
design exists to prevent. *A Tamil reader shown a list of flagged works and an English
disclaimer has, in practice, been shown a list of flagged works.*

> This actually caught a real bug while building the four new topics: they were written to
> end on an English disclaimer built in code, which produced a Tamil answer ending in
> English. Every topic now closes on the committed translated line.

### The "what has gone quiet" feature — the failure nobody screens for

A lead that was surfaced, assigned, and then left alone for four months **has not been
monitored. It has been filed** — and the money is still out there.

Two different silences, deliberately counted apart:

- **Late** — somebody committed to a date and the date passed
- **Never picked up** — the case is still sitting on the stage it was loaded on. A different
  failure, and usually a supervisor's rather than an officer's

Merging them into one "overdue" number hides whichever is smaller.

> Building this found a real bug: the review deadline was set by confidence band alone — and
> since all 500 loaded cases are HIGH, **every single one got the same date.** An ageing
> report that can't tell a slipping ₹5-crore ministry case from a routine district one is
> useless. The clock is now set by who has to review it, and stretched by how sure we are.

### The loop that makes all of this worth having

An officer records what they found. That writes an **immutable, attributed** record — it
cannot be edited, only superseded by a new one, and it must carry a name.

And one decision worth defending out loud: **"False Positive" is recorded as "Verified
Complete"**, not as its own outcome. An officer saying *"we looked, nothing was wrong"* is a
**negative example** — and negatives are half of what makes a data set usable for learning
anything. Giving them their own name is how they quietly stop being counted.

**This is the answer to the project's central limitation.** There are no fraud labels in the
source data. These records *are* those labels, accumulating one site visit at a time.

---

## Part 4 — The nine functionalities, in layman's terms

These were the nine things the project set out to build.

| # | Name | What it means in plain English | Status |
|---|---|---|---|
| **1** | AI audit prioritisation | *"Which works should we look at first?"* Reads all 2,10,993 works and ranks them by how much money is genuinely at risk. | ✅ **This is the core** |
| **2** | Explainable case files | *"Why is this one on the list?"* Every flagged work gets a page listing every reason in plain sentences — never a black-box score. Now also exports as a **PDF** you can email or carry to a site. | ✅ **+ PDF added** |
| **3** | Investigation workflow | *"Who owns this, and what happened to it?"* A lead becomes a case with an owner, a due date, five stages, and a history. This is the Salesforce half. | ✅ **Built** |
| **4** | Audit-ROI optimisation | *"I have 50 auditor-days — where do I send them?"* Plans a real budget accounting for travel. Reaches **100 works in 23 trips** where working the ranking top-down reaches 74 works in 37 trips. | ✅ **Built — was completely missing before** |
| **5** | Salesforce case management | The government-grade workflow platform officers already know, holding the 500 cases that need a human. Includes the mobile app we didn't have to build. | ✅ **Built and deployed live** |
| **6** | Evidence + resolution loop | *"What did the officer actually find?"* Site findings are recorded permanently, with a name attached, and feed back as the only real ground truth this system will ever have. | ✅ **Built** |
| **7** | Behaviour / change-point | *"Did this agency's pattern suddenly shift?"* 73 of 697 agencies changed measurably. | 🟡 **Partly built** (about 30% — volume only) |
| **8** | Semantic duplication | *"Are these two works actually the same work claimed twice?"* Found 223,407 similar pairs, narrowed to 47,709 worth asking about. | ✅ **Built** |
| **9** | Agentforce copilot | *"Just tell me the answer."* Ask questions in plain language, in ten languages, and get answers from real data. | ✅ **Built + extended to 10 topics** |

### And six things built on top that weren't in the original nine

| What | Plain English |
|---|---|
| **Field rota** | The plan turned into named people and specific days |
| **Field day pack** | One auditor's round as a PDF they carry, with tick boxes |
| **Agency dossier** | The briefing you read on the way to a visit — comparing rates, not counts |
| **Field scoreboard** | *"Has our model actually been right?"* — the screen we're allowed to lose on |
| **Case ageing** | Which cases have gone quiet, and how much money is sitting in them |
| **Audit Assignment object** | The rota as Salesforce records, so it's on an auditor's phone |

### What we deliberately did NOT build

No blockchain. No deep neural networks on tabular data. No graph neural networks. No AI
model deciding whether something is fraud.

Every one of those would have been a longer slide and a weaker product. The honest answer to
"why no fraud classifier?" is that **there is nothing to train it on**, and building one
anyway would mean fabricating the very thing the system is supposed to detect.

---

## Part 5 — The numbers to quote

Quote these exactly, or say "let me check."

| | |
|---|---|
| Works analysed | **2,10,993** |
| Total sanctioned | **₹11,565 crore** |
| Money genuinely at risk | **₹1,302 crore** |
| Completed / still open | 85,773 / 1,25,220 |
| Leads surfaced | **37,705** (4,478 HIGH, 33,227 MEDIUM) |
| States / constituencies / agencies | 36 / 545 / 778 |
| Work families learned | 50 (49 named, 1 honestly "uninterpretable") |
| Grouping quality score | **0.050** — low, and we say so |
| Prediction accuracy (held-out test) | **0.676** C-index |
| Near-duplicate pairs | 223,407 → **47,709 concerning** |
| Rule-check flags | 5,946 works |
| Agencies whose behaviour shifted | 73 of 697 |
| Scheme Health Index | **62.9 / 100** |
| Self-test detection rate | **69.2%** on planted problems |
| **Salesforce cases** | **500** · evidence records **1,586** |
| **Salesforce objects / fields** | **4** / **65** |
| Exposure in loaded cases | **₹97.5 crore** |
| **Audit plan @ 50 days** | **100 works / 23 trips / ₹47.1 Cr** |
| Same budget, working the ranking | 74 works / 37 trips / ₹42.4 Cr |
| **Rota @ 50 days, 4 auditors** | **23 trips, 0.4-day spread** |
| Agentforce topics | **10** |
| Languages | **10**, all at 100% |
| **Automated tests passing** | **245** |
| API endpoints | **44** |

---

## Part 6 — The closing line

> *"Other teams will tell you how late the finished works were. That number is a lie — it
> ignores every work that never finished. We corrected it with survival analysis, turned the
> risk into a rupee figure, tested the obvious fraud signals and **rejected them in public**,
> and we refuse to output a fraud score because there are no fraud labels in this data.*
>
> *It gives investigators evidence and priorities — not accusations. An AI that knows what
> it doesn't know."*
