#!/usr/bin/env python3
"""Validate the pruned Codex runtime without conflating code size with model context.

Two independent budgets are enforced:
1. agent-facing context tokens: SKILL.md + agents + references;
2. total installed runtime bytes: executable code + prompt assets + guidance.

Python execution files are not automatically injected into the model context, so counting
all .py source as context tokens makes an execution-capable Skill look artificially bloated.
"""

from __future__ import annotations

import argparse
import tempfile
from collections import defaultdict
from pathlib import Path

from sync_codex_skill import sync

CONTEXT_SUFFIXES = {".md", ".txt", ".json", ".yml", ".yaml"}
CONTEXT_ROOTS = {"agents", "references"}


def is_context_file(root: Path, path: Path) -> bool:
    relative = path.relative_to(root)
    if relative == Path("SKILL.md"):
        return True
    return bool(relative.parts and relative.parts[0] in CONTEXT_ROOTS and path.suffix.lower() in CONTEXT_SUFFIXES)


def context_token_counts(root: Path) -> tuple[int, dict[str, int]]:
    import tiktoken

    encoder = tiktoken.get_encoding("o200k_base")
    total = 0
    groups: dict[str, int] = defaultdict(int)
    for path in root.rglob("*"):
        if not path.is_file() or not is_context_file(root, path):
            continue
        count = len(encoder.encode(path.read_text(encoding="utf-8")))
        total += count
        relative = path.relative_to(root)
        group = relative.parts[0] if len(relative.parts) > 1 else relative.name
        groups[group] += count
    return total, dict(groups)


def prompt_asset_tokens(root: Path) -> int:
    import tiktoken

    encoder = tiktoken.get_encoding("o200k_base")
    assets = root / "assets" / "prompt-templates"
    if not assets.is_dir():
        return 0
    total = 0
    for path in assets.glob("*.json"):
        total += len(encoder.encode(path.read_text(encoding="utf-8")))
    return total


def runtime_bytes(root: Path) -> tuple[int, dict[str, int]]:
    total = 0
    groups: dict[str, int] = defaultdict(int)
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        size = path.stat().st_size
        total += size
        relative = path.relative_to(root)
        group = relative.parts[0] if len(relative.parts) > 1 else relative.name
        groups[group] += size
    return total, dict(groups)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context-token-budget", "--token-budget", dest="context_token_budget", type=int, default=43000)
    parser.add_argument("--runtime-byte-budget", type=int, default=300000)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="efg-runtime-") as tmp:
        target = Path(tmp) / "engineering-figure-gpt"
        sync(target)
        skills = list(target.rglob("SKILL.md"))
        if len(skills) != 1 or skills[0] != target / "SKILL.md":
            raise SystemExit("Runtime must contain exactly one root SKILL.md")
        context_total, context_groups = context_token_counts(target)
        prompt_tokens = prompt_asset_tokens(target)
        byte_total, byte_groups = runtime_bytes(target)

    print(f"Agent context tokens: {context_total} / {args.context_token_budget}")
    for name, count in sorted(context_groups.items(), key=lambda item: item[1], reverse=True):
        print(f"  context/{name}: {count}")
    print(f"Prompt-asset tokens (diagnostic, not implicit Codex context): {prompt_tokens}")
    print(f"Installed runtime bytes: {byte_total} / {args.runtime_byte_budget}")
    for name, size in sorted(byte_groups.items(), key=lambda item: item[1], reverse=True):
        print(f"  bytes/{name}: {size}")

    failures: list[str] = []
    if context_total > args.context_token_budget:
        failures.append(
            f"Agent context token budget exceeded: {context_total} > {args.context_token_budget}"
        )
    if byte_total > args.runtime_byte_budget:
        failures.append(f"Runtime byte budget exceeded: {byte_total} > {args.runtime_byte_budget}")
    if failures:
        raise SystemExit("\n".join(failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
