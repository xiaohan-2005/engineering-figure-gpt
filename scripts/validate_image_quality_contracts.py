#!/usr/bin/env python3
"""Validate the reusable image-quality contract pack."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_PROFILES = {"draft", "paper", "final"}
REQUIRED_LANGS = {"en", "zh"}


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    path = root / "assets" / "prompt-templates" / "image-quality-contracts.json"
    failures: list[str] = []

    if not path.is_file():
        print(f"Missing image quality contract pack: {path}", file=sys.stderr)
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Cannot parse {path}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print("Image quality contract pack must be a JSON object.", file=sys.stderr)
        return 1

    missing = sorted(REQUIRED_PROFILES.difference(data))
    if missing:
        failures.append(f"Missing quality profiles: {missing}")

    for profile in REQUIRED_PROFILES.intersection(data):
        entry = data[profile]
        if not isinstance(entry, dict):
            failures.append(f"{profile}: contract must be an object")
            continue
        missing_langs = sorted(REQUIRED_LANGS.difference(entry))
        if missing_langs:
            failures.append(f"{profile}: missing languages {missing_langs}")
            continue
        for lang in REQUIRED_LANGS:
            text = entry[lang]
            if not isinstance(text, str) or len(text.strip()) < 80:
                failures.append(f"{profile}/{lang}: contract is missing or too short")

    paper_en = str((data.get("paper") or {}).get("en") or "")
    final_en = str((data.get("final") or {}).get("en") or "")
    for phrase in ("safe outer margin", "micro-text", "50%", "crisp"):
        if phrase not in paper_en:
            failures.append(f"paper/en missing critical rendering constraint: {phrase}")
    for phrase in ("blur", "clipped", "pixel-size", "silently downgrading"):
        if phrase not in final_en:
            failures.append(f"final/en missing critical final-export constraint: {phrase}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("Image quality contract validation passed (draft, paper, final; en + zh).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
