#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import matplotlib.pyplot as plt


def main():
    p = argparse.ArgumentParser()
    p.add_argument("spec_file")
    p.add_argument("--out-path", default="output/publication-figure")
    p.add_argument("--formats", nargs="+", default=["png", "pdf", "svg"])
    args = p.parse_args()

    spec = json.loads(Path(args.spec_file).read_text(encoding="utf-8"))
    kind = spec.get("kind", "bar")
    data = spec["data"]

    fig, ax = plt.subplots(figsize=tuple(spec.get("figsize", [8, 5])))
    if kind == "bar":
        ax.bar(data["labels"], data["values"])
    elif kind == "line":
        ax.plot(data["x"], data["y"], marker="o")
    elif kind == "scatter":
        ax.scatter(data["x"], data["y"])
    else:
        raise SystemExit(f"Unsupported plot kind: {kind}")

    ax.set_title(spec.get("title", ""))
    ax.set_xlabel(spec.get("xlabel", ""))
    ax.set_ylabel(spec.get("ylabel", ""))
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()

    base = Path(args.out_path)
    base.parent.mkdir(parents=True, exist_ok=True)
    for fmt in args.formats:
        out = base.with_suffix(f".{fmt}")
        fig.savefig(out, dpi=300, bbox_inches="tight")
        print(out)
    plt.close(fig)


if __name__ == "__main__":
    main()
