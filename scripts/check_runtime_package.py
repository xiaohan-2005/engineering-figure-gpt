#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from collections import defaultdict
from pathlib import Path

from sync_codex_skill import sync

TEXT_SUFFIXES = {".md", ".txt", ".json", ".py", ".ps1", ".yml", ".yaml"}


def token_counts(root: Path) -> tuple[int, dict[str, int]]:
    import tiktoken

    encoder = tiktoken.get_encoding("o200k_base")
    total = 0
    groups: dict[str, int] = defaultdict(int)
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        count = len(encoder.encode(path.read_text(encoding="utf-8")))
        total += count
        relative = path.relative_to(root)
        group = relative.parts[0] if len(relative.parts) > 1 else relative.name
        groups[group] += count
    return total, dict(groups)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token-budget", type=int, default=43000)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="efg-runtime-") as tmp:
        target = Path(tmp) / "engineering-figure-gpt"
        sync(target)
        skills = list(target.rglob("SKILL.md"))
        if len(skills) != 1 or skills[0] != target / "SKILL.md":
            raise SystemExit("Runtime must contain exactly one root SKILL.md")
        total, groups = token_counts(target)

    print(f"Runtime token total: {total} / {args.token_budget}")
    for name, count in sorted(groups.items(), key=lambda item: item[1], reverse=True):
        print(f"  {name}: {count}")

    if total > args.token_budget:
        raise SystemExit(f"Runtime token budget exceeded: {total} > {args.token_budget}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
