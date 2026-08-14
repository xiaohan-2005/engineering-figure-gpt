#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_ENGINEERING = {
    "system-architecture",
    "algorithm-workflow",
    "graphical-abstract",
    "mathematical-model-framework",
    "data-analysis-pipeline",
    "optimization-workflow",
    "evaluation-framework",
    "electronic-schematic",
}
REQUIRED_MODELING = {
    "problem-analysis",
    "q1-q2-q3-dependency",
    "data-preprocessing",
    "forecasting-workflow",
    "classification-workflow",
    "clustering-workflow",
    "optimization-model",
    "multi-objective-pareto",
    "spatial-model",
    "network-model",
    "evaluation-system",
    "sensitivity-analysis",
    "robustness-analysis",
    "decision-framework",
    "full-modeling-pipeline",
}
SUSPICIOUS = ["鍒涘缓", "鎶€鏈", "鐧借壊", "绯荤粺", "鏁版嵁", "缁撴瀯"]


def cjk_count(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def validate_pack(path: Path, required: set[str], failures: list[str]) -> dict:
    if not path.is_file():
        failures.append(f"Missing template pack: {path}")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"Cannot parse {path}: {exc}")
        return {}
    missing = sorted(required.difference(data))
    if missing:
        failures.append(f"{path.name}: missing required templates {missing}")
    for key, entry in data.items():
        if not isinstance(entry, dict) or not {"en", "zh"}.issubset(entry):
            failures.append(f"{path.name}:{key}: missing en/zh")
            continue
        for lang in ("en", "zh"):
            text = entry[lang]
            if not isinstance(text, str):
                failures.append(f"{path.name}:{key}:{lang}: template must be a string")
                continue
            if "{background}" not in text:
                failures.append(f"{path.name}:{key}:{lang}: missing {{background}} placeholder")
        if isinstance(entry.get("zh"), str) and cjk_count(entry["zh"]) < 18:
            failures.append(f"{path.name}:{key}: Chinese template is too short")
        zh = entry.get("zh", "") if isinstance(entry, dict) else ""
        hits = [frag for frag in SUSPICIOUS if frag in zh]
        if hits:
            failures.append(f"{path.name}:{key}: suspicious mojibake {hits}")
    return data


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    template_dir = root / "assets" / "prompt-templates"
    failures: list[str] = []
    engineering = validate_pack(template_dir / "engineering-figure-templates.json", REQUIRED_ENGINEERING, failures)
    modeling = validate_pack(template_dir / "mathematical-modeling-templates.json", REQUIRED_MODELING, failures)
    collisions = sorted(set(engineering).intersection(modeling))
    if collisions:
        failures.append(f"Template keys must be unique across domain packs: {collisions}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Prompt template validation passed ({len(engineering) + len(modeling)} templates across 2 packs).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
