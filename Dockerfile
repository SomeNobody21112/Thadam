# The API only. It serves pre-computed artifacts and runs no models, so this image needs
# neither scikit-learn nor lifelines nor torch — see requirements-serve.txt.
#
# Artifacts are NOT baked in. They are ~146 MB, gitignored, and regenerated from the raw
# dataset; a deployment mounts them at /app/data (see docs/DEPLOYMENT.md). Baking them in
# would make the image unreproducible and stale the moment the pipeline reruns.

FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /app

# Dependencies first, so a source edit does not invalidate the dependency layer.
COPY requirements-serve.txt ./
RUN pip install --no-cache-dir -r requirements-serve.txt

COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --no-cache-dir --no-deps -e .

# Writable state: the hash-chained audit log and field verification records. Mount a
# persistent volume here — on an ephemeral filesystem the chain restarts every deploy and
# every verification an officer recorded is lost.
VOLUME ["/app/data"]

EXPOSE 8000

# Single worker on purpose. The corpus is held in memory (~66 MB after categoricals) and
# the SQLite audit chain is append-only; two workers would double the memory and could
# interleave writes into the chain.
CMD ["sh", "-c", "uvicorn mplads.api.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
