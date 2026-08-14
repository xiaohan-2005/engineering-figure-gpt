#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
EXPECTED_NAME = "engineering-figure-gpt"


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    skill = root / "SKILL.md"
    if not skill.is_file():
        print("Missing SKILL.md", file=sys.stderr)
        return 1

    text = skill.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        print("SKILL.md must start with YAML frontmatter", file=sys.stderr)
        return 1

    front = match.group(1)
    name_match = re.search(r"^name:\s*(.+)$", front, re.M)
    description_match = re.search(r"^description:\s*(.+)$", front, re.M)
    if not name_match:
        print("SKILL.md frontmatter missing name", file=sys.stderr)
        return 1
    if name_match.group(1).strip() != EXPECTED_NAME:
        print(f"Unexpected skill name: {name_match.group(1).strip()}", file=sys.stderr)
        return 1
    if not description_match or not description_match.group(1).strip():
        print("SKILL.md frontmatter missing non-empty description", file=sys.stderr)
        return 1

    required = [
        "agents/openai.yaml",
        "assets/prompt-templates/engineering-figure-templates.json",
        "assets/prompt-templates/mathematical-modeling-templates.json",
        "schemas/figure-brief.schema.json",
        "schemas/plot-request.schema.json",
        "schemas/plot-spec.schema.json",
        "scripts/efg.py",
        "scripts/generate_image.py",
        "scripts/build_engineering_figure_prompt.py",
        "scripts/build_plot_spec.py",
        "scripts/plot_publication_figure.py",
        "scripts/sync_codex_skill.py",
        "scripts/check_setup.ps1",
        "scripts/wizard.ps1",
        "references/figure-brief-spec.md",
        "references/natural-language-plot-workflow.md",
        "references/publication-plot-api.md",
        "references/publication-chart-patterns.md",
        "references/mathematical-modeling.md",
        "references/chinese-labels.md",
        "references/openai-image-workflow.md",
        "references/highres-policy.md",
        "references/editable-figure-handoff.md",
        "references/reproducibility-chain.md",
    ]
    missing = [item for item in required if not (root / item).is_file()]
    if missing:
        print("Missing required files: " + ", ".join(missing), file=sys.stderr)
        return 1

    print("Skill validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
