#!/usr/bin/env python3
from __future__ import annotations
import re
import sys
from pathlib import Path

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    skill = root / "SKILL.md"
    if not skill.is_file():
        print("Missing SKILL.md", file=sys.stderr); return 1
    text = skill.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        print("SKILL.md must start with YAML frontmatter", file=sys.stderr); return 1
    front = match.group(1)
    for key in ("name:", "description:"):
        if key not in front:
            print(f"SKILL.md frontmatter missing {key}", file=sys.stderr); return 1
    required = [
        "agents/openai.yaml",
        "assets/prompt-templates/engineering-figure-templates.json",
        "scripts/efg.py",
        "scripts/generate_image.py",
        "scripts/build_plot_spec.py",
        "scripts/plot_publication_figure.py",
    ]
    missing = [item for item in required if not (root / item).is_file()]
    if missing:
        print("Missing required files: " + ", ".join(missing), file=sys.stderr); return 1
    print("Skill validation passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
