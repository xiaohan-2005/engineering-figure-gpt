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
QUALITY_CONTRACT_PATH = TEMPLATE_DIR / "image-quality-contracts.json"


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


def load_quality_contracts() -> dict:
    if not QUALITY_CONTRACT_PATH.is_file():
        raise SystemExit(f"Missing image quality contract pack: {QUALITY_CONTRACT_PATH}")
    data = json.loads(QUALITY_CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise SystemExit("Image quality contract pack is empty or invalid.")
    return data


def resolve_lang(background: str, lang: str | None) -> str:
    return lang or ("zh" if contains_chinese(background) else "en")


def quality_contract(profile: str, lang: str) -> str:
    contracts = load_quality_contracts()
    if profile not in contracts:
        raise SystemExit(f"Unknown image quality profile: {profile}")
    value = contracts[profile].get(lang)
    if not value:
        raise SystemExit(f"Image quality profile '{profile}' has no '{lang}' contract.")
    return str(value).strip()


def build_prompt(
    template_name: str,
    background: str,
    lang: str | None,
    style_note: str | None,
    quality_profile: str = "paper",
) -> str:
    templates = load_templates()
    if template_name not in templates:
        raise SystemExit(f"Unknown figure template: {template_name}")
    resolved_lang = resolve_lang(background, lang)
    prompt = templates[template_name][resolved_lang].format(background=background.strip())

    heading = "论文图像质量约束" if resolved_lang == "zh" else "Publication Image Quality Contract"
    prompt = f"{prompt}\n\n{heading}:\n{quality_contract(quality_profile, resolved_lang)}"

    if style_note:
        style_heading = "附加风格要求" if resolved_lang == "zh" else "Additional style requirements"
        prompt = f"{prompt}\n\n{style_heading}:\n{style_note.strip()}"
    return prompt


def main() -> int:
    templates = load_templates()
    quality_profiles = tuple(sorted(load_quality_contracts()))
    parser = argparse.ArgumentParser(description="Build an Engineering Figure GPT prompt.")
    parser.add_argument("background", nargs="?", help="Paper or technical background.")
    parser.add_argument("--background-file", help="Read paper or technical background from a UTF-8 file.")
    parser.add_argument("--figure-template", choices=tuple(sorted(templates.keys())))
    parser.add_argument("--lang", choices=("en", "zh"), default=None)
    parser.add_argument("--style-note")
    parser.add_argument(
        "--quality-profile",
        choices=quality_profiles,
        default="paper",
        help="Append a reusable image-quality contract. Use final for final-export intent.",
    )
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

    prompt = build_prompt(
        args.figure_template,
        background,
        args.lang,
        args.style_note,
        args.quality_profile,
    )
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
