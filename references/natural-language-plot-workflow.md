# Natural-Language Plot Workflow

Natural language is the user-facing interface. JSON is an internal execution format.

When the user asks for an exact scientific plot in ordinary language, the skill should not require them to write a JSON spec.

## Decision

Use `plot` mode when exact values, axes, uncertainty, or benchmark geometry matter.

Use `image` mode when the request is conceptual or schematic and numeric geometry is not the point.

If the user wants both, use `mixed` mode and keep the quantitative panels local.

## Internal path

1. Extract the intended plot type, panels, labels, units, values, uncertainty, and export needs.
2. If required numeric values are missing, ask for them instead of inventing data.
3. Write a concise internal request JSON.
4. Normalize it with:

```bash
python scripts/build_plot_spec.py request.json --out spec.json
```

5. Render it with:

```bash
python scripts/plot_publication_figure.py spec.json --out-path output/figure --formats png pdf svg
```

6. Inspect the output once for clipped labels, legend collisions, bad tick rotation, and incorrect units.

## Supported panel intents

- `bar`: grouped comparison bars, optional error bars, annotations, hatches
- `trend`: one or more curves, optional uncertainty shadows
- `heatmap`: exact matrices with labels, annotations, colorbar
- `scatter`: one series or multiple labeled method series
- `legend`: a dedicated legend-only panel
- `empty`: intentional whitespace in a multi-panel layout

## Extraction checklist

Infer or preserve:

- plot type and panel count
- title / suptitle
- x and y labels with units
- categories or x coordinates
- series labels and exact numeric values
- uncertainty arrays when present
- requested semantic colors
- axis limits and ticks when scientifically meaningful
- legend placement
- output formats

For Chinese figures, keep Chinese labels short and preserve standard mathematical notation and abbreviations.

## Example

User request:

> 画一个方法对比柱状图，横轴是 AUC、F1、Recall，Ours 用蓝色，Baseline 用红色，把数值标在柱子上。

Internal request:

```json
{
  "layout": {"nrows": 1, "ncols": 2, "figsize": [11, 4.5], "width_ratios": [1, 0.22]},
  "panels": [
    {
      "kind": "bar",
      "title": "Method Comparison",
      "ylabel": "Score",
      "annotate": true,
      "legend": false,
      "data": {
        "categories": ["AUC", "F1", "Recall"],
        "series": {
          "Ours": [0.92, 0.88, 0.85],
          "Baseline": [0.85, 0.82, 0.80]
        }
      },
      "colors": {"Ours": "blue_main", "Baseline": "red"}
    },
    {"kind": "legend", "source_panel": 0}
  ]
}
```

The numbers above are illustrative only. Never reuse them as real experimental results.
