#!/usr/bin/env python3
"""Build preservation-first prompts for editing existing research figures."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUALITY_PATH = ROOT / "assets" / "prompt-templates" / "image-quality-contracts.json"

MODE_RULES = {
    "correct": {
        "en": [
            "Make the smallest possible correction that satisfies the instruction.",
            "Preserve the canvas, layout, module positions, arrows, palette, typography, icon style, and every unaffected label.",
            "Do not redesign unrelated regions or add new visual elements.",
        ],
        "zh": [
            "只进行满足指令所必需的最小范围修正。",
            "保持画布、布局、模块位置、箭头、配色、字体风格、图标风格以及所有未涉及标签不变。",
            "不得重设计无关区域，也不得新增无关视觉元素。",
        ],
    },
    "revise": {
        "en": [
            "Apply the requested content or structural revision while preserving the established visual language.",
            "Keep unaffected modules, labels, relationships, palette, typography, and reading order unchanged unless the instruction makes a local move necessary.",
            "Do not use the revision as an excuse to redesign the whole figure.",
        ],
        "zh": [
            "按要求修改内容或局部结构，同时保持原有视觉语言。",
            "除非指令要求局部移动，否则未涉及模块、标签、关系、配色、字体和阅读顺序必须保持不变。",
            "不得借局部修改之名重画整张图。",
        ],
    },
    "restyle": {
        "en": [
            "Change visual style only. Preserve scientific content, canonical labels, module relationships, arrow meaning, and overall information architecture.",
            "Do not add or remove scientific modules, values, formulas, or claims.",
            "Keep geometry as stable as practical while applying the requested palette/typography/rendering style.",
        ],
        "zh": [
            "只改变视觉风格。科学内容、标准标签、模块关系、箭头含义和整体信息架构必须保持不变。",
            "不得新增或删除科学模块、数值、公式或结论。",
            "在应用指定配色、字体或渲染风格时，尽量保持原有几何结构稳定。",
        ],
    },
    "redraw": {
        "en": [
            "Reconstruct the figure cleanly from the reference while preserving its scientific meaning, canonical labels, and supported relationships.",
            "Layout may be improved when necessary, but no scientific content may be invented, dropped, or silently changed.",
            "Use the reference as the authoritative source for what must remain present.",
        ],
        "zh": [
            "基于参考图重新构建更干净的版本，但必须保留其科学含义、标准标签和有依据的关系。",
            "必要时可以优化布局，但不得虚构、遗漏或静默改变科学内容。",
            "参考图中有依据的内容应视为必须保留的权威来源。",
        ],
    },
}


def contains_chinese(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))


def load_quality(profile: str, lang: str) -> str:
    data = json.loads(QUALITY_PATH.read_text(encoding="utf-8"))
    if profile not in data or lang not in data[profile]:
        raise SystemExit(f"Missing quality contract: {profile}/{lang}")
    return str(data[profile][lang]).strip()


def build_edit_prompt(
    instruction: str,
    mode: str,
    lang: str | None = None,
    preserve: list[str] | None = None,
    allow_change: list[str] | None = None,
    quality_profile: str = "paper",
) -> str:
    if mode not in MODE_RULES:
        raise SystemExit(f"Unsupported edit mode: {mode}")
    resolved_lang = lang or ("zh" if contains_chinese(instruction) else "en")
    preserve = [item.strip() for item in (preserve or []) if item.strip()]
    allow_change = [item.strip() for item in (allow_change or []) if item.strip()]

    if resolved_lang == "zh":
        sections = [
            "你正在修改一张已有科研图。参考图是视觉与结构基准，不要把这项任务当成从零生成。",
            f"\n修改模式：{mode}",
            "\n修改目标：\n" + instruction.strip(),
            "\n模式规则：\n- " + "\n- ".join(MODE_RULES[mode]["zh"]),
        ]
        if preserve:
            sections.append("\n额外必须保持：\n- " + "\n- ".join(preserve))
        if allow_change:
            sections.append("\n明确允许改变：\n- " + "\n- ".join(allow_change))
        sections.append("\n论文图像质量约束：\n" + load_quality(quality_profile, "zh"))
        sections.append(
            "\n完成前自检：除明确允许改变的内容外，比较原图与修改图，确认未出现无关模块移动、标签改写、箭头关系变化、颜色漂移、裁切、重叠或清晰度下降。"
        )
        return "".join(sections)

    sections = [
        "You are editing an existing research figure. Treat the supplied image as the visual and structural baseline; do not treat this as a from-scratch generation task.",
        f"\n\nEdit mode: {mode}",
        "\n\nEdit goal:\n" + instruction.strip(),
        "\n\nMode rules:\n- " + "\n- ".join(MODE_RULES[mode]["en"]),
    ]
    if preserve:
        sections.append("\n\nAdditional must-preserve constraints:\n- " + "\n- ".join(preserve))
    if allow_change:
        sections.append("\n\nExplicitly allowed changes:\n- " + "\n- ".join(allow_change))
    sections.append("\n\nPublication Image Quality Contract:\n" + load_quality(quality_profile, "en"))
    sections.append(
        "\n\nBefore finalizing, compare the edited result with the reference and confirm that everything outside the explicitly allowed change set remains stable: no unrelated module movement, label rewriting, arrow relationship changes, palette drift, clipping, overlap, or loss of clarity."
    )
    return "".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a preservation-first image edit prompt.")
    parser.add_argument("instruction")
    parser.add_argument("--mode", choices=tuple(MODE_RULES), default="correct")
    parser.add_argument("--lang", choices=("en", "zh"))
    parser.add_argument("--preserve", action="append", default=[])
    parser.add_argument("--allow-change", action="append", default=[])
    parser.add_argument("--quality-profile", choices=("draft", "paper", "final"), default="paper")
    parser.add_argument("--out")
    args = parser.parse_args()

    prompt = build_edit_prompt(
        args.instruction,
        args.mode,
        args.lang,
        args.preserve,
        args.allow_change,
        args.quality_profile,
    )
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(prompt + "\n", encoding="utf-8")
        print(path)
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
