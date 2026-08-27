# The Full Demo Script — Every Screen, In Plain English

**Read this standing up, laptop open, judge beside you.**

Everything in **> quote blocks** is meant to be said out loud, almost word for word.
Everything else is stage direction for you.

**Total time: 8–10 minutes.** If they rush you, do only the steps marked ⭐ — that is 4 minutes.

---

## Before the judges arrive — 3 minute checklist

Run these two commands in two separate terminals. Wait for both.

```bash
.venv/Scripts/python.exe -m uvicorn mplads.api.app:app --port 8000
```

```bash
cd frontend && npm run dev
```

Then check, in order:

1. Open **http://localhost:5173** — the landing page must load.
2. Open **http://localhost:8000/api/stats** — you must see numbers, not an error.
3. Sign in once as `auditor` / `mplads2026` and sign out again. This warms everything up.
4. Have `demo/photos/` open in a file explorer window, ready to drag from.
5. **Close every other browser tab.** Nothing kills a demo like a notification popping up.

**If port 5173 is busy**, the app moves to another port and prints it. Read the terminal, use
the port it actually printed. Do not assume 5173.

**Zoom the browser to 110%.** Judges are standing behind you and the type is small.

---

## The 20 seconds before you click anything

Do not open the laptop yet. Say this first, looking at them:

> "The MPLADS scheme funds around two lakh small public works — roads, school buildings,
> solar street lights.
>
> The problem is simple to say and hard to solve: **nobody can look at two lakh works.**
> Monitoring today is manual and it is reactive. Somebody complains, and then somebody checks.
>
> We built a system that reads all 2,10,993 of them, learns what normal looks like, and
> hands an officer a short list of the ones worth checking — **with the reason attached.**
>
> It never says the word fraud. I will explain why not, and that turns out to be the most
> important thing about it."

*Now* open the laptop.

---

## ⭐ STEP 1 — The landing page (45 seconds)

**Go to `http://localhost:5173`**

Scroll down slowly. Don't talk over the whole thing — let them read one or two panels.

> "This is the front door. It explains the idea in one line: **learn, compare, predict,
> explain, prioritise.**
>
> That is the order the system actually works in, and it is the order I am going to walk you
> through."

Point at the line that says *investigation leads, not fraud verdicts*.

> "This sentence is on every screen in the product. It is not marketing. I will show you the
> automated test that fails our build if anyone ever types the word fraud into the source
> code."

---

## ⭐ STEP 2 — Login (45 seconds)

**Click Sign in, or go to `/login`**

Don't type. **Click the "CAG Audit Officer" card** — it fills the boxes for you.

> "Four roles. A ministry user sees the whole country. A state officer sees only their state.
> A constituency officer sees only their constituency.
>
> That is not a display trick — the filtering happens on the server. If a Bihar officer asks
> the API for a Kerala work, the server refuses. There is a test for that too."

**Click Sign in.**

Point at the small grey line under the top bar.

> "It now says who I am, what I can see, and that everything I do is written to an audit log.
> The log is hash-chained — like a blockchain, but boring and useful. If anyone edits an old
> entry, the chain breaks and we can prove it."

**Why this matters, if they ask:**

> "Reading this data is open — it is public expenditure. But *writing* something, like
> recording what you found at a site, needs a name attached. An anonymous finding is not
> evidence."

---

## ⭐ STEP 3 — National Overview (90 seconds)

**You land here automatically. `/overview`**

Let the numbers count up. Then point at the four boxes, one at a time.

> "**2,10,993 works.** That is every work in the dataset. Not a sample.
>
> **₹11,565 crore** recommended in total.
>
> **37,705** have been surfaced for a human to review. That is about 18% — and I want to be
> honest that 18% is still too many for one officer, which is why the next screen ranks them.
>
> **₹1,302 crore of exposure.**"

Stop on that last one. Say this carefully:

> "That word matters. **Exposure is not loss.** It is not theft, and it is not missing money.
>
> It means: we multiplied each work's recommended amount by our model's estimate of the
> chance it does not finish on time. It is money to keep an eye on. Nothing more.
>
> If I called it 'loss' I would be lying to you, and you would be right to stop listening."

**Scroll to the confidence chart.** Point at the colours.

> "Every flagged work is graded by **how many independent kinds of evidence agree** on it.
>
> One signal on its own is usually just noise. Two is worth a look. Three or more is HIGH —
> and there are **4,478** of those.
>
> Notice we count *families* of evidence, not signals. Two signals from the same source are
> one piece of evidence counted twice. That is the mistake that makes anomaly dashboards
> useless, and we deliberately don't make it."

---

## ⭐ STEP 4 — Investigation Queue (60 seconds)

**Click "Investigation Queue" in the sidebar. `/worklist`**

> "This is the screen an officer actually works from. It is a to-do list, in order."

**Click one row.** It expands in place.

> "It opens without leaving the page, because an officer skimming twenty of these does not
> want twenty page loads."

Point at the sort order.

> "It is ranked by something we call **Audit-ROI**:
>
> how unusual it is **×** how much money is involved **×** how many kinds of evidence agree.
>
> An auditor has a limited number of days. This answers: **where is one day of your time worth
> the most?**
>
> It is a queue order. It is not a measure of guilt, and the screen says so."

---

## ⭐ STEP 5 — The Case File (2 minutes — the heart of it)

**Click any row's "open case file". You land on `/case/MP...`**

> "This is what the whole system exists to produce. One work, and everything we know about it."

**Walk the evidence panel with your finger.**

> "Each row here is one piece of evidence, and each says which *family* it came from.
>
> This one — the amount is unusual **compared to its true peers**. Not compared to all two
> lakh works. Compared to the same kind of work, in the same state, at the same rough size.
>
> A ₹42 lakh community hall is invisible next to a highway. Next to other community halls in
> Bihar, it might be very visible indeed. You cannot spot an odd one out until you know what
> to compare it to."

**Point at the peer context box.**

> "It tells you the group it was compared against and how big that group was. If the group was
> too small we widen it rather than compare against five works and pretend that means
> something. And a work is never compared against itself — obvious, easy to get wrong, and it
> quietly inflates every result if you do."

**Now scroll to the bottom — "Recommended next step".**

> "Every case file ends here. Not with a verdict — with **an instruction for a human.**
>
> 'A person should check X against Y.' That is the product. The AI does not decide anything."

**The line to not skip:**

> "There is no fraud score on this screen because there cannot be one. I will explain that on
> the transparency screen in a moment."

---

## ⭐ STEP 6 — Field Verification (2 minutes — the part they remember)

**Stay on the same case file. Scroll to "Field verification".**

> "Everything I have shown you so far ends at *'someone should go and look'*.
>
> This is the only screen in the product that records **what the person found when they went.**"

### 6a. It reads the board

**Drag in `demo/photos/01-board-matches.png`.**

> "MPLADS already requires a display board at every work site. The officer photographs it.
>
> The system reads the work number and the sanctioned amount straight off the board. Nobody
> types a reference number while standing in a field in the sun."

Point at the confidence percentage.

> "It reads it at 99.8% confidence — and it also checks the amount painted on the board
> against the amount in the record. Two things agreeing is better than one thing being
> confident."

### 6b. ⭐ It catches a recycled photograph

**Now the strong one. Drag in `demo/photos/04-photo-resubmitted.jpg`.**

A red panel appears: *THIS PHOTOGRAPH HAS BEEN SUBMITTED BEFORE.*

> "That is a **completely different file**. Different name, different format, different size,
> and a totally different checksum. Re-saving an image defeats a normal checksum entirely.
>
> We use a **perceptual hash**. A normal hash asks 'is this the same *file*'. A perceptual
> hash asks 'is this the same *picture*' — and it survives resizing, re-compression and
> brightening.
>
> It matched at 94%, and it tells you which work the picture was already submitted for, by
> whom, and when.
>
> This is the one check a human genuinely cannot do at scale. Nobody remembers a photograph
> they approved eight months ago in a different district."

**Then immediately say the honest line. Do not skip it:**

> "And it is a **question, not a finding.** Two phases of the same road legitimately look
> identical from the roadside. The system asks. A human answers."

Point at the checkbox that has appeared.

> "It will not let me save until I tick that box confirming I have looked at what it flagged."

### 6c. It admits when it is unsure

**Drag in `demo/photos/05-board-weathered.png`.**

> "Faded and out of focus, the way real boards look. Now watch what it does *not* do.
>
> It reads a number at 99.6% confidence — and that confidence is genuine, but it is confidence
> in the **pixels**, not in the answer. One digit is wrong.
>
> And because MPLADS numbers run in sequence, the wrong one is **also a real work**. Two gym
> installations at two schools in the same block, same sanctioned amount. Confidence cannot
> tell them apart. Neither can the amount.
>
> So it refuses to decide. It shows every real work that differs by one character and will not
> save until a person says which board they actually photographed.
>
> A system that guessed here would be right most of the time and silently, confidently wrong
> the rest. We would rather ask."

### 6d. Why this is the most important screen

> "Here is the deepest problem with this entire problem statement.
>
> **There are no fraud labels in this data.** Nobody has ever marked a row 'this one was a
> problem'. So no honest system can be *trained* to predict fraud, and no honest team can quote
> you an accuracy percentage.
>
> These verification records are exactly those missing labels — collecting one site visit at a
> time. At around 500 of them, our scoring weights stop being reasoned judgements and start
> being fitted to what officers actually confirmed.
>
> We are nowhere near 500. And our transparency screen shows the real number instead of
> pretending otherwise."

---

## STEP 7 — Temporal Intelligence (60 seconds)

**Sidebar → Temporal. `/trends`**

> "Everything so far scores a *work*. This screen scores an *actor* — an implementing agency,
> over time.
>
> A hundred works can each look perfectly normal while the agency producing them quietly
> changes. Bigger amounts. Different kinds of work. Fewer completions.
>
> **No single work can show you that.** The change is not in any one row. It is only visible if
> you watch the same agency across years."

Point at the count.

> "**73 of 697** agencies show a measurable shift in how they behave."

**Then the honest line:**

> "A change is not a bad thing. A new officer, a new state scheme, or a flood all look exactly
> the same in the data. We show the before and after and let a human explain it. We never say
> why it changed, because we cannot know."

---

## STEP 8 — Near-Duplicates (45 seconds)

**Sidebar → Near-Duplicates. `/duplicates`**

> "We looked for works with nearly identical descriptions. We found **2,23,407** similar pairs."

Pause. Then:

> "If we had put that number on a slide and called them all suspicious, you would have been
> right to laugh at us. Government works are *supposed* to repeat. Every district builds solar
> street lights, and one MP recommending forty of them writes the same sentence forty times.
>
> So we narrowed it hard: **same implementing agency, nearly the same amount, nearly the same
> words.** That is the shape a genuinely repeated claim would take.
>
> That leaves **47,709** worth a look — and even those are questions, not accusations."

---

## STEP 9 — Compliance & Early Warning (45 seconds)

**Sidebar → Compliance. `/compliance`**

> "Simple, checkable rules. Was a work marked complete before it was even recommended? Is a
> stage missing? Is a date impossible?
>
> **5,946 works** trip at least one check."

**Point at the "authority" column. This is the bit that earns trust:**

> "Every check declares what kind of rule it is. And **none of them claims to be an official
> government rule.**
>
> We do not have the MPLADS rulebook. So we never dress up a statistical oddity as a legal
> breach. That would be inventing law, and there is an automated test that fails our build if
> anyone tries."

---

## STEP 10 — Work Archetypes (60 seconds)

**Sidebar → Work Archetypes. `/archetypes`**

> "This is the model that makes everything else possible.
>
> Every work has a written description. 'Construction of community hall.' 'Building of
> community centre.' 'Community hall construction work.' A human instantly knows those are the
> same kind of thing. A computer sees three different strings of letters.
>
> We used a language model called MiniLM to turn each description into a list of numbers, where
> similar *meanings* get similar numbers. Then we let similar ones fall into piles.
>
> **Nobody gave it these categories.** It found 50 kinds of work on its own, by reading
> 1,87,865 descriptions."

**Now say the honest part before they find it:**

> "We measure how clean the piles are with a score called **silhouette**. Ours is **0.050**.
>
> That is a low number, and I want to say it before you ask. It means the piles overlap a lot
> at the edges — real government descriptions are messy, half of them are pasted-in tables.
>
> But **silhouette is not accuracy.** It does not mean 5% correct. It measures separation, and
> we say so in the code, the docs and on this screen."

**Point at the cluster labelled "not interpretable".**

> "We named 49 of the 50. This one we could not understand, so we labelled it *uninterpretable*
> and left it. Saying 'we don't know' beats inventing a name."

---

## ⭐ STEP 11 — Data Transparency (90 seconds — the screen that wins arguments)

**Sidebar → Data Transparency. `/transparency`**

> "This screen exists to be attacked. It lists what we measure, what we calculate, and what
> the public data simply does not contain."

**Point at the "Unavailable" column.**

> "Seven fields we do **not** have. No payment records. No independent spending figures. No
> cost estimates. No vendor names. No GPS.
>
> We list them as unavailable rather than quietly filling them in with something plausible."

**Then the single strongest thing you can say all day:**

> "Look at this one — cost overruns. We *wanted* that signal badly.
>
> Then we measured it. The 'actual amount' field equals the recommended amount **exactly, on
> 98.35% of finished works.** Not approximately. Exactly.
>
> It is a completion tick-box, not a record of spending. **There is no overrun signal in this
> data.** Any team who tells you they detected cost overruns here is making it up — and you can
> check that number yourself in thirty seconds."

**Scroll to the ground-truth panel.**

> "And here is our own report card. It shows how many real site verifications exist and how far
> that is from the 500 we would need before our weights could be fitted to reality.
>
> It also excludes the sample records we seeded for this demo, so nothing on this stage inflates
> that number."

---

## STEP 12 — How It Works (30 seconds)

**Sidebar → How it works. `/how`**

> "The whole method in plain language, for anyone who has to trust this without reading code."

Scroll to the killed-signals section.

> "And here is what we tested and **threw away**.
>
> Amount bunching below approval limits — the classic fraud signal. We tested it. Amounts
> cluster at round numbers because that is how budgets are written, not because anyone is
> gaming a limit. Killed.
>
> Agency concentration. Sounds suspicious. The 'agency' is the District Collector's office — of
> course it has all the works, that is its job. Killed.
>
> A team that says 'we tried it and it failed' is telling you the truth about the rest."

---

## STEP 13 — The Assistant (60 seconds)

**Click the ◈ button, bottom right. It works on every screen.**

Type or click: **"How many leads are there?"**

> "It answers from the computed results only. Watch the small tags under the answer — those are
> the exact lookups it ran to get that number.
>
> It has no independent knowledge of this data and it **cannot do arithmetic**, so it cannot
> invent a figure. If a lookup did not return a number, it does not have one."

**Now click a work reference in its reply.**

> "Every work number it mentions is clickable and opens that case file."

**Ask it a hard one: "Can you detect cost overruns?"**

> "It says no, and explains why — the same honest answer the transparency screen gives. The
> honesty is built into the system, not bolted onto the presentation."

---

## STEP 14 — Multilingual (30 seconds)

**Use the language dropdown in the top bar. Pick हिन्दी.**

> "Ten Indian languages. The interface is fully translated — not machine-translated at runtime,
> but committed text, so it works with no internet and cannot fail live.
>
> A district officer in Bihar should not need English to monitor works in Bihar."

**Switch back to English** before you continue.

---

## The closing 30 seconds

Stop clicking. Look at them.

> "So — what did we actually build?
>
> Other teams will tell you how late the finished works were. **That number is a lie.** It
> quietly ignores every work that never finished at all — and those are the ones you care about.
>
> We corrected for that with survival analysis, the same maths hospitals use, and we turned the
> risk into a rupee figure an official can act on.
>
> We tested the obvious fraud signals and **rejected** them, in public, on the transparency
> screen.
>
> And we refuse to output a fraud score, because there are no fraud labels in this data and any
> such number would be fabricated.
>
> **It gives investigators evidence and priorities — not accusations.**
>
> An AI that knows what it does not know."

---

# If they ask something hard

**"Isn't this just an Excel pivot table?"**
> A pivot table has to throw away unfinished works, so it inherits exactly the bias we
> corrected. It cannot tell you when an agency's behaviour changed. And it cannot rank under a
> budget. Those are the three things we built.

**"How accurate is it?"**
> On problems we planted deliberately and knew the location of: 69.2% overall, 96.1% for
> stalled works. On real fraud: we do not know, and neither does anyone else, because there is
> no answer key. I would rather tell you that than show you a number I made up.

**"Why 50 groups and not 30?"**
> We tried 20, 30, 40, 50 and 60 and measured each. 50 scored best. It is not a number we
> chose because we liked it.

**"So the AI decides who gets audited?"**
> No. It puts names in an order and shows the reason for each one. A human decides. Every
> screen says so, and there is no button anywhere in this product that takes an action against
> a work.

**"What if you flag an innocent district?"**
> We never accuse anyone — there is no accusation anywhere in the system, only 'this is
> unusual, here is why, please check'. And because we show the evidence, an officer can
> disagree with us in thirty seconds. That is the point of showing our working.

**"Your silhouette score is terrible."**
> It is 0.050 and we put it on the screen ourselves. It measures how cleanly the piles
> separate, not whether they are correct. Government work descriptions genuinely overlap —
> a community hall and a community centre *should* be near each other. The clusters are
> validated by whether they make peer comparison work, and they do.

**"Where is your dataset from?"**
> Public MPLADS and eSAKSHI portal data — 4,80,768 lifecycle rows. No login needed, nothing
> restricted. The fields we would need a MoSPI data grant for are listed as unavailable rather
> than faked.

---

# If something breaks live

**Stay calm and narrate it.** Judges have watched demos crash all day.

- **A screen is blank** → refresh once. If it is still blank, move to the next screen and come
  back. Do not debug in front of them.
- **The API is down** → say *"the backend has dropped, one moment"*, restart it in the
  terminal, and keep talking about the method while it comes up.
- **The assistant does not reply** → say *"the language model needs billing credits we haven't
  added; it falls back to a deterministic engine"* — then ask it one of the suggested questions,
  which always work offline.
- **A photo upload fails** → the walkthrough in `demo/WALKTHROUGH.md` has the same evidence in
  screenshots. Show that instead.

**The one thing never to do:** do not invent a number when you cannot remember it. Say "I would
have to check that" — it costs you nothing and it is consistent with everything else you have
told them.

---

# Numbers to have on the tip of your tongue

| | |
|---|---|
| Works | **2,10,993** |
| Raw lifecycle rows | **4,80,768** |
| Finished / still open | **85,773 / 1,25,220** |
| Total recommended | **₹11,565 crore** |
| Exposure (money to watch) | **₹1,302 crore** |
| Surfaced for review | **37,705** — of which **4,478** HIGH |
| States / constituencies / agencies | **36 / 545 / 778** |
| Kinds of work learned | **50** — silhouette **0.050** |
| Prediction quality | **C-index 0.6759** |
| Second-opinion flags | **4,220** |
| Duplicate pairs → concerning | **2,23,407 → 47,709** |
| Compliance-flagged works | **5,946** |
| Agencies whose behaviour changed | **73 of 697** |
| Planted-problem detection | **69.2%** (synthetic — always say so) |
| Automatic tests passing | **189** |

**Quote these exactly or not at all.** A number you half-remember is worse than "let me check".
