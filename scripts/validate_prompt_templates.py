#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path

EXPECTED = {
    "system-architecture",
    "algorithm-workflow",
    "graphical-abstract",
    "mathematical-model-framework",
    "data-analysis-pipeline",
    "optimization-workflow",
    "evaluation-framework",
    "electronic-schematic",
}
SUSPICIOUS = ["鍒涘缓", "鎶€鏈", "鐧借壊", "绯荤粺", "鏁版嵁", "缁撴瀯"]


def cjk_count(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    path = root / "assets" / "prompt-templates" / "engineering-figure-templates.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    failures = []
    if set(data) != EXPECTED:
        failures.append(f"Template keys mismatch: {sorted(data)}")
    for key, entry in data.items():
        if not {"en", "zh"}.issubset(entry):
            failures.append(f"{key}: missing en/zh")
            continue
        for lang in ("en", "zh"):
            if "{background}" not in entry[lang]:
                failures.append(f"{key}:{lang}: missing {{background}} placeholder")
        if cjk_count(entry["zh"]) < 18:
            failures.append(f"{key}: Chinese template is too short")
        hits = [frag for frag in SUSPICIOUS if frag in entry["zh"]]
        if hits:
            failures.append(f"{key}: suspicious mojibake {hits}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("Prompt template validation passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
