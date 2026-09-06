# Hugging Face Space (Docker SDK) — the WHOLE product in one container.
#
# React frontend + FastAPI + pre-built artifacts. One service, one URL, one deploy:
#   - no CORS, because the browser never makes a cross-origin request;
#   - no build-time API base to get wrong — the frontend uses same-origin relative paths,
#     exactly as it does in local development.
#
# Artifacts are BAKED IN rather than generated during the build. That drops the push from
# ~546 MB to ~171 MB, removes ~3 minutes of build compute, and guarantees the image serves
# exactly the artifacts that were tested. No Dataset/, no scikit-learn, no lifelines, no
# torch: the pipeline already ran, and nothing in the API import chain loads a model.

# ---------------------------------------------------------------- stage 1: frontend
FROM node:20-slim AS frontend

WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ---------------------------------------------------------------- stage 2: runtime
# Spaces run as uid 1000. Create the user before anything is copied, so the audit log and
# field verification records can actually be written at run time.
FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8

WORKDIR $HOME/app

COPY --chown=user requirements-serve.txt ./
RUN pip install --no-cache-dir --user -r requirements-serve.txt

COPY --chown=user pyproject.toml ./
COPY --chown=user src/ ./src/
RUN pip install --no-cache-dir --user --no-deps -e .

# Pre-built artifacts. config resolves these relative to the repo root, which is this dir.
COPY --chown=user data/ ./data/

# The built React app. app.py mounts /assets and serves index.html for client-side routes
# when this directory exists, and serves the API alone when it does not.
COPY --from=frontend --chown=user /build/dist ./frontend/dist

# App Runner defaults to 8080 and injects $PORT; Hugging Face uses 7860 via app_port.
# Respecting $PORT means the same image runs on either without a rebuild.
EXPOSE 8080

# One worker: the corpus is held in memory and the SQLite audit chain is append-only, so a
# second worker would double the memory and could interleave writes into the chain.
CMD ["sh", "-c", "uvicorn mplads.api.app:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]
