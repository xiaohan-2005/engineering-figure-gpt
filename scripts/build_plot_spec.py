#!/usr/bin/env python3
"""Build a normalized publication-plot spec from a concise request JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_STYLE = {
    "font_size": 13,
    "axes_linewidth": 1.6,
    "font_family": ["Noto Sans CJK SC", "Microsoft YaHei", "SimHei", "DejaVu Sans", "sans-serif"],
}


def load_request(args: argparse.Namespace) -> dict:
    if args.stdin:
        return json.loads(sys.stdin.read())
    if not args.request_file:
        raise SystemExit("Provide a request file or use --stdin.")
    path = Path(args.request_file)
    if not path.is_file():
        raise SystemExit(f"Request file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_bar(panel: dict) -> dict:
    data = panel["data"]
    series_map = data["series"]
    labels = list(series_map)
    out = {
        "type": "bar",
        "title": panel.get("title"),
        "categories": data["categories"],
        "series": [series_map[label] for label in labels],
        "labels": labels,
        "colors": [panel.get("colors", {}).get(label) for label in labels] if panel.get("colors") else None,
        "yerr": [data.get("error", {}).get(label) for label in labels] if data.get("error") else None,
        "xlabel": panel.get("xlabel"),
        "ylabel": panel.get("ylabel", "Value"),
        "annotate": panel.get("annotate", False),
        "annotate_fmt": panel.get("annotate_fmt", "{:.2f}"),
        "legend": panel.get("legend", True),
        "legend_outside": panel.get("legend_outside", False),
        "legend_loc": panel.get("legend_loc", "best"),
        "legend_ncol": panel.get("legend_ncol", min(max(len(labels), 1), 3)),
        "grid": panel.get("grid", False),
        "xtick_rotation": panel.get("xtick_rotation", 0),
        "hatches": panel.get("hatches"),
    }
    return out


def normalize_trend(panel: dict) -> dict:
    data = panel["data"]
    series_map = data["series"]
    labels = list(series_map)
    return {
        "type": "trend",
        "title": panel.get("title"),
        "x": data["x"],
        "y_series": [series_map[label] for label in labels],
        "labels": labels,
        "colors": [panel.get("colors", {}).get(label) for label in labels] if panel.get("colors") else None,
        "shadow": [data.get("shadow", {}).get(label) for label in labels] if data.get("shadow") else None,
        "xlabel": panel.get("xlabel"),
        "ylabel": panel.get("ylabel", "Value"),
        "legend": panel.get("legend", True),
        "legend_outside": panel.get("legend_outside", False),
        "legend_loc": panel.get("legend_loc", "best"),
        "legend_ncol": panel.get("legend_ncol", min(max(len(labels), 1), 3)),
        "grid": panel.get("grid", False),
    }


def normalize_heatmap(panel: dict) -> dict:
    data = panel["data"]
    return {
        "type": "heatmap",
        "title": panel.get("title"),
        "matrix": data["matrix"],
        "x_labels": data.get("x_labels"),
        "y_labels": data.get("y_labels"),
        "xlabel": panel.get("xlabel"),
        "ylabel": panel.get("ylabel"),
        "cmap": panel.get("cmap", "viridis"),
        "colorbar": panel.get("colorbar", True),
        "colorbar_label": panel.get("colorbar_label"),
        "annotate": panel.get("annotate", False),
        "annotate_fmt": panel.get("annotate_fmt", "{:.2f}"),
        "xtick_rotation": panel.get("xtick_rotation", 45),
    }


def normalize_scatter(panel: dict) -> dict:
    data = panel["data"]
    out = {
        "type": "scatter",
        "title": panel.get("title"),
        "xlabel": panel.get("xlabel"),
        "ylabel": panel.get("ylabel"),
        "legend": panel.get("legend", "series" in data),
        "legend_outside": panel.get("legend_outside", False),
        "legend_loc": panel.get("legend_loc", "best"),
        "grid": panel.get("grid", False),
    }
    if "series" in data:
        out["series"] = data["series"]
    else:
        out.update({"x": data["x"], "y": data["y"], "label": data.get("label"), "color": data.get("color")})
    return out


def normalize_panel(panel: dict) -> dict:
    kind = panel["kind"]
    builders = {
        "bar": normalize_bar,
        "trend": normalize_trend,
        "heatmap": normalize_heatmap,
        "scatter": normalize_scatter,
        "legend": lambda p: {"type": "legend", "source_panel": p["source_panel"], "legend_ncol": p.get("legend_ncol", 1)},
        "empty": lambda p: {"type": "empty"},
    }
    if kind not in builders:
        raise SystemExit(f"Unsupported panel kind: {kind}")
    out = builders[kind](panel)
    for key in ("xlim", "ylim", "xticks", "yticks", "xticklabels", "yticklabels", "hide_xticks", "hide_yticks"):
        if key in panel:
            out[key] = panel[key]
    return {k: v for k, v in out.items() if v is not None}


def build_spec(request: dict) -> dict:
    panels = [normalize_panel(panel) for panel in request["panels"]]
    layout = {"nrows": 1, "ncols": max(len(panels), 1), "figsize": [6 * max(len(panels), 1), 4.8], "tight_layout_pad": 1.4}
    layout.update(request.get("layout", {}))
    spec = {
        "style": {**DEFAULT_STYLE, **request.get("style", {})},
        "layout": layout,
        "panels": panels,
    }
    if request.get("suptitle"):
        spec["suptitle"] = request["suptitle"]
    return spec


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a full publication plot spec.")
    parser.add_argument("request_file", nargs="?")
    parser.add_argument("--stdin", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()
    text = json.dumps(build_spec(load_request(args)), ensure_ascii=False, indent=2) + "\n"
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(out)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
