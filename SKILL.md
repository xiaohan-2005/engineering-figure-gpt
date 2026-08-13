---
name: engineering-figure-gpt
description: Use when the user needs publication-style engineering, computer-science, data-science, AI, electronics, or mathematical-modeling figures. Prefer this skill for system architectures, algorithm workflows, graphical abstracts, model-framework diagrams, benchmark charts, ablation plots, trend/scatter/heatmap panels, figure redraws, and image edits. Use Codex built-in GPT image generation for conceptual figures when available, an official OpenAI GPT Image 2 CLI fallback for reproducibility, and local plotting for exact quantitative figures.
---

# Engineering Figure GPT

Use this skill for research-figure production once the figure goal is reasonably clear.

## Boundary

Good fit:

- turn a figure brief into a conceptual diagram, workflow, modeling framework, schematic, or exact plot
- choose `image`, `plot`, or `mixed` mode
- turn natural-language plot requests into internal specs
- generate/edit conceptual figures through GPT image generation
- render exact quantitative panels locally

Not the main tool for deciding from scratch what scientific claim a paper should make. If the figure claim, panel logic, or caption argument is still unclear, resolve that upstream first.

## Core Decision

- `image`: conceptual architecture, workflow, graphical abstract, modeling framework, mechanism diagram, redraw, image edit
- `plot`: exact bar, trend, heatmap, scatter, ablation, benchmark, and multi-panel quantitative figures
- `mixed`: local exact quantitative panels plus GPT-generated conceptual panels

Never use image generation for exact numeric geometry, axes, uncertainty bars, benchmark values, or formulas that must remain exact.

## Default Workflow

1. Inspect the user's paper text, figure brief, numeric data, reference image, or request.
2. If needed, structure the request with `references/figure-brief-spec.md`.
3. Choose `image`, `plot`, or `mixed`.
4. For conceptual figures, choose the closest template in `assets/prompt-templates/engineering-figure-templates.json` and adapt it to the scientific content.
5. Inside Codex, prefer the installed built-in image-generation capability for normal conceptual generation/editing.
6. When a portable or reproducible CLI path is requested, use `scripts/generate_image.py`, which is intentionally restricted to the official OpenAI endpoint and defaults to `gpt-image-2`.
7. For exact plots, treat natural language as the user interface and JSON as an internal format. Follow `references/natural-language-plot-workflow.md`.
8. Normalize concise plot requests with `scripts/build_plot_spec.py`, then render with `scripts/plot_publication_figure.py`.
9. In mixed mode, render quantitative panels first and never ask the image model to redraw them.
10. Verify labels, units, reading order, legends, values, axes, uncertainty, and scientific fidelity before finishing.

## Image Mode

Use GPT image generation when conceptual composition matters more than numeric geometry.

Rules:

- preserve user-supplied terminology, module relationships, mathematical notation, and standard abbreviations
- prefer white backgrounds, short labels, clear arrows, disciplined spacing, and explicit reading order
- do not invent measurements, formulas, benchmark values, causal claims, model components, or hardware specifications
- for Chinese figures, keep labels concise and preserve established English abbreviations when they improve readability
- for final paper use, inspect generated text carefully; regenerate or edit if labels are malformed

Portable fallback:

```bash
python scripts/generate_image.py "publication-quality architecture figure ..." --quality high --size 1536x1024
```

Edit an existing image:

```bash
python scripts/generate_image.py "keep structure, improve hierarchy and labels" --input-image input.png --input-fidelity high
```

The CLI fallback requires an OpenAI API key. Do not commit keys to the repository.

## Plot Mode

Numeric truth overrides aesthetics.

Supported panel intents:

- grouped bars with optional error bars and annotations
- trend curves with optional uncertainty shadows
- heatmaps with exact matrices and colorbars
- scatter plots with one or multiple labeled series
- dedicated legend-only panels
- empty panels for deliberate multi-panel layout

Natural-language request path:

```bash
python scripts/build_plot_spec.py request.json --out spec.json
python scripts/plot_publication_figure.py spec.json --out-path output/figure --formats png pdf svg
```

Use vector export when helpful. Never alter supplied values to make a figure look better.

## Unified CLI

```bash
python scripts/efg.py prompt --figure-template mathematical-model-framework --lang zh "technical background"
python scripts/efg.py image "research figure prompt" --dry-run
python scripts/efg.py build-plot request.json --out spec.json
python scripts/efg.py plot spec.json --out-path output/figure --formats png pdf svg
python scripts/efg.py check
```

## Reference Loading

Read only what the task needs:

- `references/figure-brief-spec.md`
- `references/publication-figure-design.md`
- `references/natural-language-plot-workflow.md`
- `references/image-mode.md`
- `references/plot-mode.md`
- `references/mixed-mode.md`
- `references/mathematical-modeling.md`
- `references/gpt-image-2-guidance.md`

## Quality Rules

- do not fabricate scientific facts or numeric results
- keep exact plots local and deterministic
- keep formulas and mathematical symbols source-faithful
- inspect Chinese labels for encoding, font fallback, clipping, and excessive length
- prefer concise visual hierarchy over decorative complexity
- save prompts/specs/output paths when files are produced so the result is reproducible
