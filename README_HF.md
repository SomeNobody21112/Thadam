---
title: MPLADS Intelligence API
emoji: 🏛️
colorFrom: red
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Investigation leads over 2.1 lakh MPLADS public works — never fraud verdicts
---

# MPLADS AI Forensic Monitoring — API

**Team Morior Invictus · Smart India Hackathon 2026 · PS SIH26102 (MoSPI)**

This Space runs the FastAPI backend. It serves intelligence computed over **210,993** real
MPLADS/eSAKSHI public works.

## What this is

An AI-assisted monitoring layer that learns what normal public work looks like, compares each
work against its **true peers**, estimates completion risk and the rupee exposure attached to
it, and ranks what deserves a human's attention.

**It produces investigation leads with evidence. It never produces fraud verdicts.** There are
no fraud labels in this data, so any model claiming to predict fraud would be fabricated.

## Try it

| Endpoint | What it returns |
|---|---|
| `/api/health` | Liveness |
| `/api/stats` | National totals — should report `total_works: 210993` |
| `/api/worklist?limit=5` | Top investigation leads by Audit-ROI |
| `/api/case/MP3018356-W86316` | A full explainable case file |
| `/api/models` | Model metrics, with their honest caveats |
| `/api/transparency` | What this data cannot tell you |
| `/docs` | Interactive OpenAPI documentation |

## Verified numbers

| Measure | Value |
|---|---|
| Works | 210,993 (85,773 completed · 125,220 open) |
| Recommended / exposure | ₹11,565 Cr / ₹1,302 Cr |
| Investigation leads | 37,705 — 4,478 HIGH · 33,227 MEDIUM |
| Coverage | 36 states · 545 constituencies · 778 agencies |
| Archetypes | 50, silhouette **0.050** *(separation, never accuracy)* |
| Completion risk | Cox PH held-out **C-index 0.6759** |
| Synthetic validation | **69.25%** detection over 904 planted anomalies |

## Honest limitations

- **No fraud labels exist**, so nothing here is validated against a real fraud outcome.
- **`ACTUAL_AMOUNT` is not expenditure** — it equals the recommended amount on 98.35% of
  completed works. No cost-overrun signal exists in this data.
- **Silhouette 0.050 is not accuracy.** It measures cluster separation. Real-world text
  clusters overlap heavily.
- **No official rules are asserted.** No statutory threshold ships with this public data, so
  calling a statistical outlier a legal breach would be inventing law.

## Notes on this deployment

- Artifacts are generated **during the image build** from the raw dataset, so the Space is
  self-contained.
- Written briefings need an `ANTHROPIC_API_KEY` secret. Without it they fall back to
  deterministic templates and **say so** — the interface never silently degrades.
- Free-tier storage is not persistent. The audit log and field verification records
  (~1 MB combined) reset when the Space restarts. Everything else is read-only.
