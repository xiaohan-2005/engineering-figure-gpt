# Plot Mode

Use plot mode when numeric values, axes, scales, geometry, or uncertainty must stay exact.

Typical figures:

- grouped benchmark bars
- ablation plots
- training / validation trends
- sensitivity curves
- scatter comparisons
- heatmaps
- uncertainty bands
- multi-panel quantitative figures

## User interface

The user should normally describe the desired figure in natural language. JSON is an internal execution contract.

Follow `natural-language-plot-workflow.md` to extract the numeric data, labels, units, panel structure, uncertainty, colors, and export needs.

## Internal execution

```bash
python scripts/build_plot_spec.py request.json --out spec.json
python scripts/plot_publication_figure.py spec.json --out-path output/figure --formats png pdf svg
```

## Exactness rules

Preserve:

- every supplied value
- category and series order
- units
- uncertainty arrays
- axis meaning
- legend semantics
- tick labels
- scientific notation

Never alter values or scales just to improve appearance.

## Layout rules

The renderer supports multiple panels, dedicated legend panels, width/height ratios, bar annotations, error bars, trend uncertainty shadows, heatmaps, and multi-series scatter plots.

Prefer vector export for editable paper figures. For PNG, use sufficient DPI for the final document size.

Before finishing, inspect clipping, long Chinese labels, rotated tick overlap, legends, minus signs, mathematical symbols, and units.

Do not redraw exact plots with an image-generation model.
