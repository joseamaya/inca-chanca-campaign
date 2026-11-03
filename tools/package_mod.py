#!/usr/bin/env python3
"""Build a .zip/.pyromod from the mod root."""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {".git", ".github", "dist", "__pycache__"}
EXCLUDE_FILES = {".gitignore", ".gitattributes"}


def main() -> int:
    version = json.loads((ROOT / "mod.json").read_text(encoding="utf-8"))["version"]
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / f"dist/inca-chanca-{version}.zip")
    args = parser.parse_args()
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            if set(rel.parts) & EXCLUDE_DIRS or rel.name in EXCLUDE_FILES:
                continue
            if path.suffix in {".pyc", ".pyromod", ".zip"}:
                continue
            archive.write(path, rel.as_posix())

    print(output)
    print(f"{output.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
