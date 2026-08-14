#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "README.zh-CN.md",
    "README.en.md",
    "INSTALL.md",
    "docs/showcase.md",
    "references/figure-brief-spec.md",
    "references/natural-language-plot-workflow.md",
    "references/chinese-labels.md",
]
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_LINK_RE = re.compile(r"(?:src|href)=[\"']([^\"']+)[\"']", re.IGNORECASE)
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data"}


def markdown_files() -> list[Path]:
    roots = [
        ROOT / "README.md",
        ROOT / "README.en.md",
        ROOT / "README.zh-CN.md",
        ROOT / "INSTALL.md",
        ROOT / "docs",
        ROOT / "examples",
        ROOT / "references",
    ]
    result: list[Path] = []
    for item in roots:
        if item.is_file():
            result.append(item)
        elif item.is_dir():
            result.extend(sorted(item.rglob("*.md")))
    return result


def clean_target(raw: str) -> str | None:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if " " in target and not target.startswith(("http://", "https://")):
        target = target.split(None, 1)[0]
    if target.startswith("#") or not target:
        return None
    parsed = urlparse(target)
    if parsed.scheme.lower() in EXTERNAL_SCHEMES or target.startswith("//"):
        return None
    path = unquote(parsed.path)
    return path or None


def resolve_local(source: Path, target: str) -> Path:
    if target.startswith("/"):
        return ROOT / target.lstrip("/")
    return source.parent / target


def find_local_targets(text: str) -> list[str]:
    values = MARKDOWN_LINK_RE.findall(text)
    values.extend(HTML_LINK_RE.findall(text))
    return values


def main() -> int:
    failures: list[str] = []
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            failures.append(f"Missing required documentation file: {name}")

    for source in markdown_files():
        text = source.read_text(encoding="utf-8")
        for raw in find_local_targets(text):
            target = clean_target(raw)
            if target is None:
                continue
            resolved = resolve_local(source, target)
            if not resolved.exists():
                failures.append(
                    f"{source.relative_to(ROOT)}: broken local link/image '{raw}' -> {resolved.relative_to(ROOT) if resolved.is_relative_to(ROOT) else resolved}"
                )

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("Documentation links/images validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
