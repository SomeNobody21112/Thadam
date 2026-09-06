# Deployment

**Audited and configured 2026-09-06 · 191 tests passing · frontend build verified**

---

## The short answer

**Frontend on Vercel. Backend on Hugging Face Spaces.**

Vercel hosts the React app perfectly. It cannot host the FastAPI backend — not a preference,
three hard blockers documented below, so nobody re-litigates it under time pressure. The
backend runs as a Docker Space instead: free, public HTTPS, and it builds its own artifacts.

```
   ┌────────────────────────┐         ┌──────────────────────────────┐
   │  VERCEL                │  HTTPS  │  HUGGING FACE SPACE (Docker) │
   │  React static build    │ ──────► │  FastAPI + self-built        │
   │  (frontend/dist)       │  CORS   │  artifacts (mplads.api.app)  │
   └────────────────────────┘         └──────────────────────────────┘
   VITE_API_BASE ──────────────► https://<user>-<space>.hf.space

   Part 2 keeps Render/Railway/Fly/VM as the option with a persistent disk.
```

---

## Why the backend cannot run on Vercel

Three independent blockers. Any one of them alone would be fatal.

### 1. Size — over the function limit before any of our code

Vercel's serverless functions cap at **250 MB unzipped**, including dependencies.

| Item | Size |
|---|---|
| pandas + pyarrow + numpy | ~120–150 MB |
| `data/artifacts/` | **146 MB** — `case_files.json` alone is **83 MB** |
| `data/interim/works.parquet` (corpus the assistant searches) | 15 MB |

That is comfortably over the limit before FastAPI is added.

### 2. Writes — the audit chain would be a fiction

Vercel's filesystem is **read-only** except `/tmp`, and `/tmp` is **ephemeral per
invocation**. Two things in this product are SQLite writes:

- the **append-only, hash-chained audit log**
- **field verification records** — the officer's own observations

On Vercel, both would be silently discarded between requests. A tamper-evident chain that
resets on every invocation is worse than no chain at all, and losing a verification an
officer walked to a site to record is unacceptable. **This alone rules Vercel out**, size
notwithstanding.

### 3. Cold starts — the 10s limit

A cold invocation would parse an 83 MB JSON file and a 23 MB parquet before answering. That
exceeds the Hobby 10-second limit and would be painfully slow even on Pro.

> **If a judge asks "why not all on Vercel?"** — *"Serverless functions are stateless and
> capped at 250 MB. Our audit log is append-only and our artifacts are 146 MB. Putting it
> there would mean throwing away every field verification between requests. We split the
> deployment instead: static frontend on Vercel, stateful API on a host with a disk."*

---

## Part 1 — Frontend on Vercel

Already configured in [`vercel.json`](../vercel.json).

### Steps

1. Push the repo to GitHub.
2. In Vercel: **New Project → import the repo**.
3. Leave the framework preset as **Other** — `vercel.json` supplies the build.
4. Add one environment variable:

   | Name | Value |
   |---|---|
   | `VITE_API_BASE` | `https://your-api-host.onrender.com` *(no trailing slash)* |

5. **Deploy.**

### What the config does

- Builds `frontend/` and serves `frontend/dist`.
- **SPA rewrite** — every path that is not `/assets/*` returns `index.html`, so deep links
  like `/case/MP3018356-W86316` work on refresh instead of 404ing.
- Immutable caching on hashed assets; `nosniff`, `DENY` framing and a referrer policy on
  everything else.

### ⚠️ `VITE_API_BASE` is baked in at build time

Vite inlines it into the bundle. **Changing it requires a redeploy**, not just an env edit.
Verified: building with a value produces a bundle containing that origin; building without
one produces same-origin relative paths for local development.

---

## Part 2 — Backend on Render (or equivalent)

Configured in [`Dockerfile`](../Dockerfile) and [`render.yaml`](../render.yaml).

### Steps

1. In Render: **New → Blueprint**, point it at the repo. `render.yaml` is detected.
2. Confirm the **1 GB persistent disk** mounted at `/app/data`. **Do not skip this** — see
   blocker 2 above.
3. Set `ANTHROPIC_API_KEY` in the dashboard (optional — without it, briefings use
   deterministic templates and say so).
4. Deploy, then **upload the artifacts** (next section).
5. Copy the service URL into Vercel's `VITE_API_BASE` and redeploy the frontend.

### Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `MPLADS_DATA_DIR` | Where artifacts and writable state live | `<repo>/data` |
| `MPLADS_REQUIRE_AUTH` | `1` requires a token to **write**; reads stay open | `0` |
| `MPLADS_JWT_SECRET` | Token signing key | dev value — **must be overridden** |
| `ANTHROPIC_API_KEY` | Written briefings | unset → templates |
| `PORT` | Listen port | 8000 |

### Why one worker

The corpus is held in memory (~66 MB after categorical compression) and the SQLite audit
chain is append-only. A second worker would double the memory and could interleave writes
into the chain. Scale by adding instances behind a load balancer with shared storage, not by
adding workers to one box.

### The image is deliberately slim

[`requirements-serve.txt`](../requirements-serve.txt) is much smaller than `pyproject.toml`.
**The API runs no models** — the pipeline already produced every artifact, so serving needs a
dataframe library and a web server and nothing else.

Verified 2026-09-06: no module in the API import chain references `sklearn`, `lifelines`,
`joblib` or `torch`. Excluding them takes the image from well over a gigabyte to roughly
200 MB. `anthropic`, `Pillow` and `rapidocr` are imported lazily and each degrades to a
documented fallback if missing.

---

## Part 2b — Backend on Hugging Face Spaces (free)

The chosen deployment. Spaces are Docker-native, give a public HTTPS URL, and the free CPU
tier has 16 GB RAM — far more than the ~400 MB this needs.

Unlike Part 2, this variant **generates the artifacts during the image build**, so the Space
is self-contained and there is nothing to upload afterwards.

### Steps

```bash
# 1. Assemble the Space directory (renames Dockerfile.hf -> Dockerfile, README_HF.md -> README.md)
python scripts/prepare_hf_space.py ../mplads-space

# 2. Create a Space at huggingface.co/new-space  (SDK: Docker, hardware: CPU basic - free)

# 3. Push it
cd ../mplads-space
git init && git lfs install
git remote add origin https://huggingface.co/spaces/<user>/<space>
git add -A && git commit -m "MPLADS API" && git push -u origin main
```

Then set `ANTHROPIC_API_KEY` as a Space **secret** (optional — without it briefings fall back
to deterministic templates and say so), and point Vercel's `VITE_API_BASE` at
`https://<user>-<space>.hf.space`.

### What gets pushed

| Item | Size |
|---|---|
| `Dataset/raw/` — the three eSAKSHI CSVs | 244 MB |
| `Dataset/models/archetype/` — cached MiniLM vectors | 301 MB |
| `src/` + config files | ~1 MB |
| **Total** | **~546 MB** |

**git-lfs is required, not optional** — the Hub rejects a 293 MB `.npz` pushed without it.
`prepare_hf_space.py` writes the `.gitattributes` for you.

### What the build does

`ingest` → `train` → `pipeline`, roughly 3 minutes of compute, then **deletes the 546 MB of
inputs** because serving never reads them again. Final image ~1.1 GB.

The generation step is **idempotent**: if artifacts are already present it skips them, so this
same Dockerfile still works if you later switch to baking artifacts in. It also **fails the
build loudly** if the pipeline produced no `stats.json`, rather than shipping an image that
serves zeros.

No torch and no sentence-transformers: the MiniLM vectors are pre-computed, so the
45-minute embedding step is already paid for.

### Free-tier trade-offs — know these

| | Behaviour |
|---|---|
| **Storage** | Not persistent. The audit log and field verifications (~1.1 MB combined) reset when the Space restarts. Everything else is read-only and rebuilt from the image |
| **Sleep** | Free Spaces sleep after inactivity; the first request afterwards is slow |
| **Rebuild cost** | Every rebuild redoes the 3-minute pipeline |

For a hackathon demo these are all acceptable. For a real deployment, use Part 2 (persistent
disk) or Part 3 Option C (object storage).

⚠️ **Before you push:** the Space is public. `Dataset/` contents become publicly downloadable,
and the seeded demo credentials are listed at `/api/auth/accounts`. Both are fine for
evaluation on public MPLADS data — just be deliberate about it.

---

## Part 3 — The artifacts problem

**This is the step people forget, and the symptom is every screen showing zeros.**

`Dataset/` (878 MB) and `data/` (167 MB) are **gitignored**. The repository is only 3.9 MB.
So a fresh deployment has **no artifacts at all** until you put them there.

Three options:

### Option A — Generate on the host *(most reproducible)*

Requires `Dataset/` (878 MB) on the host and the full dependency set.

```bash
python -m mplads.cli ingest     # ~40s
python -m mplads.cli train      # ~90s
python -m mplads.cli pipeline   # ~50s
```

### Option B — Upload the artifacts *(fastest)*

Build locally, then copy `data/artifacts/` and `data/interim/` to the mounted disk. On
Render, use a one-off shell; on a VM, `rsync`.

### Option C — Object storage *(best for a real deployment)*

Push artifacts to S3/Azure Blob from CI whenever the pipeline reruns; the container syncs
them on boot. Keeps the image immutable and makes rebuilds routine.

### Sanity check after deploying

```bash
curl https://your-api-host/api/health
curl https://your-api-host/api/stats
```

`/api/stats` must report `total_works: 210993`. **If it returns zeros, the artifacts are not
mounted** — the API starts fine without them and serves empty results rather than crashing,
which is friendly locally and confusing in production.

---

## Part 4 — Before going public

The evaluation build makes deliberate trade-offs that are wrong for a public deployment.

| Item | Now | For production |
|---|---|---|
| **Demo accounts** | Listed openly at `/api/auth/accounts`, shared password | Remove the endpoint; connect an identity provider |
| **`MPLADS_REQUIRE_AUTH`** | `0` locally | **`1`** |
| **`MPLADS_JWT_SECRET`** | Dev default | Generated secret (`render.yaml` does this) |
| **CORS** | `allow_origins=["*"]` | Restrict to the Vercel domain |
| **Audit log** | Tamper-**evident** | Publish the head hash somewhere the writer does not control |
| **`ANTHROPIC_API_KEY`** | Pasted in chat during development | **Rotate it** |

⚠️ **The key currently in `.env` was pasted in plaintext in a chat transcript. Rotate it
before any deployment**, public or not.

---

## Quick reference

```bash
# Local development (unchanged)
.venv\Scripts\python.exe -m uvicorn mplads.api.app:app --port 8000
cd frontend; npm.cmd run dev

# Build the frontend for a split deployment
cd frontend
VITE_API_BASE=https://your-api-host.onrender.com npm.cmd run build

# Build and run the API container
docker build -t mplads-api .
docker run -p 8000:8000 -v "$PWD/data:/app/data" -e MPLADS_DATA_DIR=/app/data mplads-api
```

## Files added for deployment

| File | Purpose |
|---|---|
| `vercel.json` | Frontend build, SPA rewrite, cache and security headers |
| `Dockerfile` | Slim API image, no ML dependencies |
| `.dockerignore` | Keeps `Dataset/` (878 MB) and `data/` out of the build context |
| `render.yaml` | One-click backend with a persistent disk |
| `requirements-serve.txt` | Runtime-only dependencies |
| `config.MPLADS_DATA_DIR` | Lets the container mount artifacts on a volume |
| `Dockerfile.hf` | Hugging Face variant — generates artifacts at build time |
| `README_HF.md` | Space README with the YAML frontmatter HF requires |
| `requirements-build.txt` | Adds sklearn + lifelines for build-time generation |
| `scripts/prepare_hf_space.py` | Assembles and validates the Space directory |
