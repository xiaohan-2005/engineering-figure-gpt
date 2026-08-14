# Publication Chart Patterns

Use these patterns when translating a natural-language request into a concise Plot Request. The goal is not to impose one aesthetic, but to choose a layout that makes the scientific comparison easy to read while preserving exact data.

## 1. Benchmark comparison

Use grouped bars when the user compares multiple methods across the same metrics.

Recommended structure:

```text
Panel A: primary metrics (Accuracy / F1 / AUC)
Panel B: efficiency metrics (Latency / Memory / Parameters)
Shared legend or legend-only panel
```

Do not mix metrics with incompatible units on the same axis.

## 2. Ablation study

Use grouped bars or a compact trend when model components are removed/added in a defined order.

Good ordering:

```text
Base
+ component A
+ component B
Full model
```

Preserve the actual experimental order if supplied. Do not imply causality from an unordered ablation table.

## 3. Training / validation curves

Use paired trend panels when training and validation scales or semantics differ.

```text
Panel A: training objective / metric
Panel B: validation objective / metric
```

If uncertainty bands are supplied, use them consistently across series. Do not invent them.

## 4. Forecasting paper figure

Common multi-panel pattern:

```text
Panel A: observed vs predicted time series
Panel B: residuals or absolute error
Panel C: metric comparison across models
```

If the user only supplies predictions and no residual data, compute residuals only when the observed series is also supplied and the requested transformation is unambiguous.

## 5. Sensitivity analysis

Two common patterns:

### Local / one-at-a-time

```text
Panel A: parameter perturbation curves
Panel B: ranked sensitivity magnitude
```

### Global sensitivity

```text
Panel A: first-order indices
Panel B: total-order indices
```

Never fabricate Sobol indices, confidence intervals, or parameter ranges.

## 6. Robustness analysis

Use trend curves when outputs are evaluated under progressively stronger disturbance/noise/scenario changes.

Recommended:

```text
x-axis: perturbation / noise / scenario intensity
y-axis: exact performance or objective value
one series per method/scenario
```

Mark the baseline only if its value is known.

## 7. Pareto front

Use scatter plots for exact Pareto solutions.

```text
x: objective 1
y: objective 2
optional marker/category: candidate family
```

Do not connect Pareto points with lines unless the user requests it and the ordering has a real interpretation.

## 8. Confusion matrix

Use an annotated heatmap with exact counts or normalized values.

Always preserve row/column meaning:

```text
actual × predicted
```

or the user's supplied convention. Explicitly label axes to avoid ambiguity.

## 9. Correlation matrix

Use a square heatmap with consistent variable ordering. Prefer a diverging colormap only when positive/negative values are meaningful.

Do not reorder variables by clustering unless requested.

## 10. Evaluation framework results

When a modeling paper compares alternatives across several criteria:

- use grouped bars for a small number of criteria;
- use a heatmap when methods × criteria is dense;
- use radar charts only if the renderer explicitly supports them and the user accepts the interpretability tradeoff.

The current deterministic renderer does not use radar by default.

## 11. Multi-panel efficiency benchmark

A strong engineering benchmark layout may use:

```text
A  Accuracy / quality
B  F1 / task metric
C  Latency
D  Parameters
E  Memory
F  Energy / throughput
```

Keep units visible and consistent. Use a shared method color across all panels.

## 12. Spatial / network analysis

If the figure requires exact geographic shapes, graph topology, or map coordinates beyond simple scatter points, use a dedicated local plotting/geospatial workflow rather than an image model. Do not redraw measured geometry through GPT image generation.

## Legend placement

Prefer:

- inside legend for sparse panels;
- outside legend for dense annotations;
- dedicated legend panel for multi-panel figures with many repeated methods.

Avoid covering bars, lines, or labels.

## Typography

For Chinese or bilingual figures:

- use a CJK-capable font fallback;
- keep axis labels short;
- use standard model abbreviations consistently;
- check minus signs, superscripts, subscripts, Greek symbols, and units after export.

## Final verification

Before delivery verify:

- supplied values are unchanged;
- axes use the intended units/scales;
- legends map correctly to every panel;
- no labels are clipped;
- error bars/uncertainty correspond to supplied data;
- panel order matches the paper narrative;
- vector exports remain editable when requested.
