#!/usr/bin/env python3
from pathlib import Path

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


def main() -> int:
    root = Path(".")
    missing = [name for name in REQUIRED if not (root / name).is_file()]
    if missing:
        raise SystemExit("Missing documentation files: " + ", ".join(missing))
    print("Documentation smoke check passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
