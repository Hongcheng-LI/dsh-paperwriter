#!/usr/bin/env python3
"""Sync the paperwriter skill source into the DSH plugin bundle (assets/paperwriter/).

The skill's source of truth is the paperwriter repository (Hongcheng-LI/paperwriter).
This script copies SKILL.md / references / scripts / assets from a local
paperwriter checkout into assets/paperwriter/ so the plugin ships an
up-to-date snapshot of the skill.

Usage:
  python scripts/sync_dsh.py [--from PATH_TO_PAPERWRITER_CHECKOUT] [--check]

--check compares bytes without writing (CI drift check) and exits 1 on drift.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "assets" / "paperwriter"
SOURCE_ITEMS = ("SKILL.md", "references", "scripts", "assets")
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")


def resolve_source(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).resolve()
    else:
        path = REPO_ROOT.parent / "paperwriter"
    if not (path / "SKILL.md").is_file():
        sys.exit(f"error: paperwriter checkout not found at {path} (use --from)")
    return path


def snapshot(source: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for item in SOURCE_ITEMS:
        src = source / item
        if not src.exists():
            sys.exit(f"error: missing required item in source: {item}")
        if src.is_dir():
            shutil.copytree(src, dest / item, ignore=IGNORE)
        else:
            shutil.copy2(src, dest / item)


def tree_files(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from", dest="source", default=None,
        help="path to a paperwriter checkout (default: sibling ../paperwriter)",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="verify assets are in sync without writing",
    )
    args = parser.parse_args()

    source = resolve_source(args.source)

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            fresh = Path(tmp) / "paperwriter"
            snapshot(source, fresh)
            current, expected = tree_files(TARGET), tree_files(fresh)
        missing = sorted(set(expected) - set(current))
        extra = sorted(set(current) - set(expected))
        changed = sorted(k for k in set(current) & set(expected) if current[k] != expected[k])
        if missing or extra or changed:
            for label, keys in (("missing", missing), ("extra", extra), ("changed", changed)):
                for key in keys:
                    print(f"{label}: {key}")
            sys.exit(1)
        print(f"in sync: {len(current)} files match {source}")
        return

    snapshot(source, TARGET)
    print(f"synced {len(tree_files(TARGET))} files -> {TARGET.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
