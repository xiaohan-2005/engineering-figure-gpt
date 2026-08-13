#!/usr/bin/env python3
"""Render exact publication-style multi-panel figures from a normalized JSON spec."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

_CACHE = Path(tempfile.gettempdir()) / "engineering_figure_gpt_mpl"
os.environ.setdefault("MPLCONFIGDIR", str(_CACHE / "mplconfig"))

import matplotlib.pyplot as plt
import numpy as np

PALETTE = {
    "blue_main": "#2563EB",
    "blue_dark": "#1D4ED8",
    "green": "#16A34A",
    "red": "#DC2626",
    "orange": "#EA580C",
    "violet": "#7C3AED",
    "teal": "#0F766E",
    "gray": "#6B7280",
    "light_gray": "#D1D5DB",
}
DEFAULT_COLORS = [PALETTE[k] for k in ("blue_main", "green", "red", "violet", "teal", "orange", "gray")]
SUPPORTED_FORMATS = {"png", "pdf", "svg", "eps", "jpg", "jpeg", "tif", "tiff"}


def color(value: str | None, index: int = 0) -> str:
    if not value:
        return DEFAULT_COLORS[index % len(DEFAULT_COLORS)]
    return PALETTE.get(value, value)


def as_1d(values, label: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise SystemExit(f"{label} must be 1D")
    return arr


def as_2d(values, label: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 2:
        raise SystemExit(f"{label} must be 2D")
    return arr


def apply_style(spec: dict) -> None:
    style = spec.get("style", {})
    families = style.get("font_family", ["Noto Sans CJK SC", "Microsoft YaHei", "SimHei", "DejaVu Sans", "sans-serif"])
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": families,
        "font.size": style.get("font_size", 13),
        "axes.linewidth": style.get("axes_linewidth", 1.6),
        "axes.spines.right": False,
        "axes.spines.top": False,
        "legend.frameon": False,
        "svg.fonttype": "none",
        "axes.unicode_minus": False,
    })


def apply_axis(ax: plt.Axes, panel: dict) -> None:
    if panel.get("title"):
        ax.set_title(panel["title"])
    if panel.get("xlabel"):
        ax.set_xlabel(panel["xlabel"])
    if panel.get("ylabel"):
        ax.set_ylabel(panel["ylabel"])
    if "xlim" in panel:
        ax.set_xlim(panel["xlim"])
    if "ylim" in panel:
        ax.set_ylim(panel["ylim"])
    if "xticks" in panel:
        ax.set_xticks(panel["xticks"])
    if "yticks" in panel:
        ax.set_yticks(panel["yticks"])
    if "xticklabels" in panel:
        ax.set_xticklabels(panel["xticklabels"], rotation=panel.get("xtick_rotation", 0))
    if "yticklabels" in panel:
        ax.set_yticklabels(panel["yticklabels"])
    if panel.get("hide_xticks"):
        ax.set_xticks([])
    if panel.get("hide_yticks"):
        ax.set_yticks([])
    if panel.get("grid"):
        ax.grid(True, alpha=0.18, linewidth=0.8)


def add_legend(ax: plt.Axes, panel: dict) -> None:
    if panel.get("legend_outside"):
        ax.legend(loc=panel.get("legend_loc", "upper center"), bbox_to_anchor=panel.get("legend_bbox_to_anchor", [0.5, 1.18]), ncol=panel.get("legend_ncol", 1))
    else:
        ax.legend(loc=panel.get("legend_loc", "best"), ncol=panel.get("legend_ncol", 1))


def render_bar(ax: plt.Axes, panel: dict) -> None:
    categories = panel["categories"]
    series = as_2d(panel["series"], "bar.series")
    labels = panel["labels"]
    if series.shape[1] != len(categories) or series.shape[0] != len(labels):
        raise SystemExit("Bar series dimensions do not match labels/categories")
    x = np.arange(len(categories), dtype=float)
    group_width = float(panel.get("bar_group_width", 0.8))
    width = group_width / max(series.shape[0], 1)
    colors = panel.get("colors") or [None] * series.shape[0]
    errors = panel.get("yerr") or [None] * series.shape[0]
    hatches = panel.get("hatches") or []
    containers = []
    for i, values in enumerate(series):
        pos = x - group_width / 2 + width * (i + 0.5)
        yerr = errors[i] if i < len(errors) else None
        bars = ax.bar(pos, values, width=width, label=labels[i], color=color(colors[i] if i < len(colors) else None, i), edgecolor="black", linewidth=0.8, yerr=yerr, capsize=3 if yerr is not None else 0, hatch=hatches[i] if i < len(hatches) else None)
        containers.append(bars)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=panel.get("xtick_rotation", 0))
    if panel.get("legend", True):
        add_legend(ax, panel)
    if panel.get("annotate"):
        fmt = panel.get("annotate_fmt", "{:.2f}")
        for bars in containers:
            for patch in bars:
                value = patch.get_height()
                ax.annotate(fmt.format(value), (patch.get_x() + patch.get_width() / 2, value), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=panel.get("annotate_fontsize", 9))


def render_trend(ax: plt.Axes, panel: dict) -> None:
    x = as_1d(panel["x"], "trend.x")
    ys = panel["y_series"]
    labels = panel["labels"]
    colors = panel.get("colors") or [None] * len(ys)
    shadows = panel.get("shadow") or [None] * len(ys)
    if len(ys) != len(labels):
        raise SystemExit("Trend labels length does not match series")
    for i, values in enumerate(ys):
        y = as_1d(values, f"trend.series[{i}]")
        if len(y) != len(x):
            raise SystemExit("Trend series length must match x")
        c = color(colors[i] if i < len(colors) else None, i)
        ax.plot(x, y, label=labels[i], color=c, linewidth=panel.get("line_width", 2.2), marker=panel.get("marker"))
        if i < len(shadows) and shadows[i] is not None:
            s = as_1d(shadows[i], f"trend.shadow[{i}]")
            if len(s) != len(x):
                raise SystemExit("Trend shadow length must match x")
            ax.fill_between(x, y - s, y + s, color=c, alpha=panel.get("shadow_alpha", 0.14))
    if panel.get("legend", True):
        add_legend(ax, panel)


def render_heatmap(ax: plt.Axes, panel: dict, fig: plt.Figure) -> None:
    matrix = as_2d(panel["matrix"], "heatmap.matrix")
    image = ax.imshow(matrix, aspect=panel.get("aspect", "auto"), cmap=panel.get("cmap", "viridis"))
    if panel.get("x_labels"):
        ax.set_xticks(np.arange(len(panel["x_labels"])))
        ax.set_xticklabels(panel["x_labels"], rotation=panel.get("xtick_rotation", 45), ha="right")
    if panel.get("y_labels"):
        ax.set_yticks(np.arange(len(panel["y_labels"])))
        ax.set_yticklabels(panel["y_labels"])
    if panel.get("annotate"):
        fmt = panel.get("annotate_fmt", "{:.2f}")
        for r in range(matrix.shape[0]):
            for c in range(matrix.shape[1]):
                ax.text(c, r, fmt.format(matrix[r, c]), ha="center", va="center", fontsize=panel.get("annotate_fontsize", 9))
    if panel.get("colorbar", True):
        cb = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
        if panel.get("colorbar_label"):
            cb.set_label(panel["colorbar_label"])


def render_scatter(ax: plt.Axes, panel: dict) -> None:
    if "series" in panel:
        for i, item in enumerate(panel["series"]):
            x = as_1d(item["x"], f"scatter.series[{i}].x")
            y = as_1d(item["y"], f"scatter.series[{i}].y")
            if len(x) != len(y):
                raise SystemExit("Scatter x/y lengths must match")
            ax.scatter(x, y, label=item.get("label"), color=color(item.get("color"), i), s=item.get("size", 48), alpha=item.get("alpha", 0.8))
        if panel.get("legend", True):
            add_legend(ax, panel)
        return
    x = as_1d(panel["x"], "scatter.x")
    y = as_1d(panel["y"], "scatter.y")
    if len(x) != len(y):
        raise SystemExit("Scatter x/y lengths must match")
    ax.scatter(x, y, label=panel.get("label"), color=color(panel.get("color")), s=panel.get("size", 48), alpha=panel.get("alpha", 0.8))
    if panel.get("legend") and panel.get("label"):
        add_legend(ax, panel)


def render_panel(ax: plt.Axes, panel: dict, fig: plt.Figure, previous_axes: list[plt.Axes]) -> None:
    kind = panel["type"]
    if kind == "bar":
        render_bar(ax, panel)
    elif kind == "trend":
        render_trend(ax, panel)
    elif kind == "heatmap":
        render_heatmap(ax, panel, fig)
    elif kind == "scatter":
        render_scatter(ax, panel)
    elif kind == "legend":
        source = int(panel["source_panel"])
        if source >= len(previous_axes):
            raise SystemExit("Legend source_panel is out of range")
        handles, labels = previous_axes[source].get_legend_handles_labels()
        ax.set_axis_off()
        ax.legend(handles, labels, loc="center", ncol=panel.get("legend_ncol", 1))
        return
    elif kind == "empty":
        ax.set_axis_off()
        return
    else:
        raise SystemExit(f"Unsupported panel type: {kind}")
    apply_axis(ax, panel)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render publication-style plots from JSON.")
    parser.add_argument("spec_file")
    parser.add_argument("--out-path", default="output/publication-figure")
    parser.add_argument("--formats", nargs="+", default=["png", "pdf", "svg"])
    parser.add_argument("--dpi", type=int, default=320)
    args = parser.parse_args()

    spec_path = Path(args.spec_file)
    if not spec_path.is_file():
        raise SystemExit(f"Spec not found: {spec_path}")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    apply_style(spec)
    layout = spec.get("layout", {})
    nrows = int(layout.get("nrows", 1))
    ncols = int(layout.get("ncols", max(len(spec["panels"]), 1)))
    gridspec_kw = {}
    if layout.get("width_ratios"):
        gridspec_kw["width_ratios"] = layout["width_ratios"]
    if layout.get("height_ratios"):
        gridspec_kw["height_ratios"] = layout["height_ratios"]
    fig, axes = plt.subplots(nrows, ncols, figsize=tuple(layout.get("figsize", [6 * ncols, 4.8 * nrows])), squeeze=False, gridspec_kw=gridspec_kw or None)
    flat = list(axes.reshape(-1))
    if len(spec["panels"]) > len(flat):
        raise SystemExit("Layout has fewer axes than panels")
    rendered = []
    for i, panel in enumerate(spec["panels"]):
        render_panel(flat[i], panel, fig, rendered)
        rendered.append(flat[i])
    for ax in flat[len(spec["panels"]):]:
        ax.set_axis_off()
    if spec.get("suptitle"):
        fig.suptitle(spec["suptitle"], y=0.995)
    fig.tight_layout(pad=float(layout.get("tight_layout_pad", 1.4)))

    base = Path(args.out_path)
    base.parent.mkdir(parents=True, exist_ok=True)
    for fmt in args.formats:
        fmt = fmt.lower()
        if fmt not in SUPPORTED_FORMATS:
            raise SystemExit(f"Unsupported format: {fmt}")
        out = base.with_suffix(f".{fmt}")
        fig.savefig(out, dpi=args.dpi, bbox_inches="tight", pad_inches=0.08, facecolor="white")
        print(out)
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
