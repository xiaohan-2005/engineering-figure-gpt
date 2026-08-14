# Publication Plot API

Use this reference for deterministic quantitative figures. Natural language remains the user-facing interface; the JSON shapes below are internal contracts used by `build_plot_spec.py` and `plot_publication_figure.py`.

## Execution chain

```text
natural-language intent
        ↓
concise Plot Request (`kind`)
        ↓
build_plot_spec.py
        ↓
normalized Plot Spec (`type`)
        ↓
plot_publication_figure.py
        ↓
PNG / PDF / SVG / other Matplotlib export
```

Use `efg plot request.json` for the complete chain. Use `efg render spec.json` only when a normalized spec already exists.

## Top-level normalized spec

A normalized spec contains layout/style information plus `panels`.

Typical structure:

```json
{
  "suptitle": "Optional figure title",
  "layout": {
    "nrows": 1,
    "ncols": 2,
    "figsize": [12, 5],
    "width_ratios": [1, 1]
  },
  "style": {
    "font_size": 11,
    "axes_linewidth": 1.2
  },
  "panels": [
    {"type": "bar"},
    {"type": "trend"}
  ]
}
```

Do not hand-author a normalized spec unless necessary. Prefer the concise request contract.

## Panel types

Supported normalized panel types:

- `bar`
- `trend`
- `heatmap`
- `scatter`
- `legend`
- `empty`

## Bar panel

Use for benchmark, ablation, method comparison, or grouped metric comparison.

Typical fields:

```json
{
  "type": "bar",
  "title": "Method Comparison",
  "categories": ["AUC", "F1", "Recall"],
  "series": [
    [0.92, 0.90, 0.88],
    [0.86, 0.84, 0.82]
  ],
  "labels": ["Ours", "Baseline"],
  "ylabel": "Score",
  "annotate": true
}
```

When values are supplied, preserve them exactly. Do not alter bar heights for aesthetics.

Useful behavior:

- grouped multi-series bars;
- optional error bars;
- exact value annotation;
- internal or outside legend;
- category tick labels;
- manual y-limits when scientifically justified.

For dense annotated bars, prefer an outside legend or a dedicated legend panel.

## Trend panel

Use for training curves, forecasting diagnostics, temporal trends, robustness curves, or sensitivity trajectories.

```json
{
  "type": "trend",
  "x": [1, 2, 3, 4],
  "y_series": [
    [0.60, 0.72, 0.79, 0.83],
    [0.57, 0.67, 0.73, 0.77]
  ],
  "labels": ["Model A", "Model B"],
  "xlabel": "Epoch",
  "ylabel": "Accuracy"
}
```

If uncertainty/shadow arrays are supplied, preserve them exactly. Never synthesize confidence bands from a single curve unless the user explicitly asks for a defined statistical transformation and supplies sufficient data.

## Heatmap panel

Use for exact matrices such as:

- correlations;
- transition matrices;
- confusion matrices;
- parameter grids;
- model-vs-dataset performance matrices.

```json
{
  "type": "heatmap",
  "matrix": [
    [1.0, 0.42],
    [0.42, 1.0]
  ],
  "x_labels": ["A", "B"],
  "y_labels": ["A", "B"],
  "annotate": true,
  "colorbar_label": "Correlation"
}
```

Do not reorder matrix rows/columns unless the user requests it.

## Scatter panel

Use for exact measured coordinate pairs, trade-off plots, latency/accuracy maps, or model/property comparisons.

Single-series example:

```json
{
  "type": "scatter",
  "x": [10, 20, 30],
  "y": [0.81, 0.87, 0.91],
  "xlabel": "Latency (ms)",
  "ylabel": "Accuracy"
}
```

For multiple methods, use multiple labeled series. Preserve x/y pairing exactly.

## Legend panel

Use a dedicated legend panel when data panels are dense or the final figure has a shared legend.

A legend panel should reuse handles from a prior panel rather than recreating semantic labels independently.

## Empty panel

Use an `empty` panel only for deliberate layout spacing or future composition. Do not use empty panels to hide missing data.

## Layout rules

For multi-panel figures:

- preserve panel reading order;
- keep related metrics adjacent;
- use consistent axis language and units;
- align panel titles and label sizes;
- avoid tiny panels created only to fit too much content;
- use width/height ratios only when one panel genuinely needs more space.

## Axis rules

Exact plotting may define:

- `xlim`, `ylim`;
- explicit ticks/tick labels;
- tick rotation;
- grid behavior;
- axis labels;
- hidden ticks for layout-only panels.

Do not truncate axes in a way that exaggerates differences unless the user explicitly requests a justified scientific scale and the figure makes that scale obvious.

## Annotation rules

Annotations are allowed only when they are derived from supplied values or supplied text.

Good annotations:

- exact bar values;
- supplied thresholds;
- known operating points;
- user-supplied significance labels.

Do not generate significance stars, p-values, confidence intervals, or optimality labels without evidence.

## Color and style

Prefer restrained publication styling. Color should encode semantic grouping rather than decoration.

For accessibility:

- do not rely on color alone when patterns/markers can help;
- keep contrast sufficient against white backgrounds;
- use consistent colors for the same method across panels;
- avoid rainbow palettes for ordinal data unless scientifically meaningful.

## Export

For paper workflows, prefer a reproducible set:

```text
PNG -> review / submission compatibility
SVG -> editable vector output
PDF -> print/vector handoff
```

Use 300 dpi or greater for raster exports when appropriate to the target venue.

## Mathematical modeling patterns

Typical exact outputs include:

- forecast and residual curves;
- Pareto fronts;
- sensitivity-index bars;
- robustness curves under parameter perturbation;
- evaluation-score comparisons;
- correlation or confusion matrices;
- model-comparison benchmarks.

See `publication-chart-patterns.md` for recommended panel composition patterns.
