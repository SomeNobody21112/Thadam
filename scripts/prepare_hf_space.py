"""Assemble a Hugging Face Space directory from this repository.

Hugging Face's Docker SDK looks for a file named exactly `Dockerfile` at the root of the
Space repo, and a `README.md` carrying YAML frontmatter. Neither matches what this repo
calls those files, so copying by hand means renaming two things correctly under time
pressure. This script does it, and refuses to produce a Space that would fail to build.

It copies only what the build actually needs:

    Dockerfile.hf              -> Dockerfile
    README_HF.md               -> README.md          (frontmatter tells HF it is Docker)
    requirements-serve.txt     -> requirements-serve.txt
    requirements-build.txt     -> requirements-build.txt
    pyproject.toml             -> pyproject.toml
    src/                       -> src/
    Dataset/raw/*.csv          -> Dataset/raw/       (245 MB, the only real inputs)
    Dataset/models/archetype/  -> Dataset/models/archetype/   (293 MB cached embeddings)

Everything else under `Dataset/` is a previous team's derived output and is never read by
our pipeline, so it is deliberately left behind.

Usage:
    python scripts/prepare_hf_space.py ../mplads-space
    cd ../mplads-space && git init && git lfs install
    git lfs track "*.csv" "*.npz"
    git add -A && git commit -m "MPLADS API" && git push
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: (source, destination-in-space). Renames are the whole point of this script.
FILES: list[tuple[str, str]] = [
    ("Dockerfile.hf", "Dockerfile"),
    ("README_HF.md", "README.md"),
    ("requirements-serve.txt", "requirements-serve.txt"),
    ("requirements-build.txt", "requirements-build.txt"),
    ("pyproject.toml", "pyproject.toml"),
]

DIRECTORIES: list[tuple[str, str]] = [
    ("src", "src"),
    ("Dataset/raw", "Dataset/raw"),
    ("Dataset/models/archetype", "Dataset/models/archetype"),
]

#: Written into the Space so the two large input types go through git-lfs. Pushing a 293 MB
#: .npz without it is rejected by the Hub.
GITATTRIBUTES = """*.csv filter=lfs diff=lfs merge=lfs -text
*.npz filter=lfs diff=lfs merge=lfs -text
*.parquet filter=lfs diff=lfs merge=lfs -text
*.joblib filter=lfs diff=lfs merge=lfs -text
"""


def _megabytes(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size // 1_048_576
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) // 1_048_576


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="directory to build the Space in")
    parser.add_argument("--force", action="store_true",
                        help="overwrite the target if it already has contents")
    args = parser.parse_args()

    target: Path = args.target.expanduser().resolve()
    if target.exists() and any(target.iterdir()) and not args.force:
        print(f"refusing to write into non-empty {target} (pass --force)", file=sys.stderr)
        return 1

    # Verify every input exists before copying anything, so a missing 293 MB embeddings
    # cache fails here in a second rather than after a long partial copy.
    missing = [s for s, _ in FILES + DIRECTORIES if not (REPO / s).exists()]
    if missing:
        print("missing required inputs:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        if any(m.startswith("Dataset") for m in missing):
            print("\n`Dataset/` is gitignored. It must be present locally to build a Space "
                  "that generates its own artifacts.", file=sys.stderr)
        return 1

    target.mkdir(parents=True, exist_ok=True)
    total = 0

    for source, destination in FILES:
        src = REPO / source
        dst = target / destination
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        size = _megabytes(src)
        total += size
        note = f"  (renamed from {source})" if Path(source).name != destination else ""
        print(f"  {destination:<34} {size:>4} MB{note}")

    for source, destination in DIRECTORIES:
        src = REPO / source
        dst = target / destination
        if dst.exists():
            shutil.rmtree(dst)
        # __pycache__ and the editable-install egg-info are local build noise: they bloat the
        # image and bust the Docker layer cache on every rebuild for no reason.
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.egg-info"))
        size = _megabytes(src)
        total += size
        print(f"  {destination + '/':<34} {size:>4} MB")

    (target / ".gitattributes").write_text(GITATTRIBUTES, encoding="utf-8")
    print(f"  {'.gitattributes':<34}    0 MB  (git-lfs for csv/npz/parquet/joblib)")

    print(f"\nSpace assembled at {target}")
    print(f"Total to push: ~{total} MB — git-lfs is required, not optional.\n")
    print("Next:")
    print(f"  cd {target}")
    print("  git init && git lfs install")
    print('  git remote add origin https://huggingface.co/spaces/<user>/<space>')
    print('  git add -A && git commit -m "MPLADS API" && git push -u origin main')
    print("\nThen set ANTHROPIC_API_KEY as a Space secret (optional — without it,")
    print("briefings fall back to deterministic templates and say so).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
