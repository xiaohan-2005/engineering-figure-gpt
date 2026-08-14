#!/usr/bin/env python3
"""Build publication-oriented research figure prompts without network calls."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT / "assets" / "prompt-templates"
TEMPLATE_PATHS = (
    TEMPLATE_DIR / "engineering-figure-templates.json",
    TEMPLATE_DIR / "mathematical-modeling-templates.json",
)


def contains_chinese(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))


def load_templates() -> dict:
    merged: dict = {}
    for path in TEMPLATE_PATHS:
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        collisions = sorted(set(merged).intersection(data))
        if collisions:
            raise SystemExit(f"Duplicate figure template keys across domain packs: {collisions}")
        merged.update(data)
    if not merged:
        raise SystemExit(f"No prompt template packs found in {TEMPLATE_DIR}")
    return merged


def build_prompt(template_name: str, background: str, lang: str | None, style_note: str | None) -> str:
    templates = load_templates()
    if template_name not in templates:
        raise SystemExit(f"Unknown figure template: {template_name}")
    resolved_lang = lang or ("zh" if contains_chinese(background) else "en")
    prompt = templates[template_name][resolved_lang].format(background=background.strip())
    if style_note:
        heading = "附加风格要求" if resolved_lang == "zh" else "Additional style requirements"
        prompt = f"{prompt}\n\n{heading}:\n{style_note.strip()}"
    return prompt


def main() -> int:
    templates = load_templates()
    parser = argparse.ArgumentParser(description="Build an Engineering Figure GPT prompt.")
    parser.add_argument("background", nargs="?", help="Paper or technical background.")
    parser.add_argument("--background-file", help="Read paper or technical background from a UTF-8 file.")
    parser.add_argument("--figure-template", choices=tuple(sorted(templates.keys())))
    parser.add_argument("--lang", choices=("en", "zh"), default=None)
    parser.add_argument("--style-note")
    parser.add_argument("--out", help="Optional prompt output path.")
    parser.add_argument("--list-templates", action="store_true", help="Print all available template keys and exit.")
    args = parser.parse_args()

    if args.list_templates:
        for name in sorted(templates):
            print(name)
        return 0
    if not args.figure_template:
        raise SystemExit("Provide --figure-template, or use --list-templates to inspect available templates.")

    background = args.background
    if args.background_file:
        background = Path(args.background_file).read_text(encoding="utf-8")
    if not background:
        raise SystemExit("Provide background text or --background-file.")

    prompt = build_prompt(args.figure_template, background, args.lang, args.style_note)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(prompt, encoding="utf-8")
        print(out)
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
