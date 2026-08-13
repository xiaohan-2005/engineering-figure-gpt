---
name: engineering-figure-gpt
description: Use when the user needs publication-style engineering, computer-science, data-science, AI, electronics, or mathematical-modeling figures. Prefer this skill for system architectures, algorithm workflows, graphical abstracts, model-framework diagrams, benchmark charts, ablation plots, trend/scatter/heatmap panels, figure redraws, and image edits. Use Codex built-in GPT image generation for conceptual figures and local plotting for exact quantitative figures.
---

# Engineering Figure GPT

Use this skill for research-figure production once the figure goal is reasonably clear.

## Modes

- `image`: conceptual figures, architecture diagrams, algorithm workflows, graphical abstracts, mathematical-model frameworks, mechanism diagrams, and reference-inspired redraws.
- `plot`: exact charts where numeric values, axes, error bars, or benchmark geometry must be faithful.
- `mixed`: render quantitative panels locally first, then generate only the conceptual panels.

Never use image generation for exact numeric geometry.

## Workflow

1. Inspect the paper text, figure brief, data, or requested figure.
2. If needed, structure the request with `references/figure-brief-spec.md`.
3. Choose `image`, `plot`, or `mixed` mode.
4. For conceptual figures, use the closest template in `assets/prompt-templates/engineering-figure-templates.json` and adapt it to the user's scientific content.
5. Route normal generation and editing through Codex's built-in image-generation capability. Prefer the built-in path over a custom API wrapper.
6. For exact plots, render locally with Python/Matplotlib from the user's supplied numeric data.
7. In `mixed` mode, keep quantitative panels local and exact; use image generation only for conceptual panels.
8. Verify labels, hierarchy, reading order, values, axes, legend, and claim fidelity before finishing.

## Figure Brief

When the request is under-specified, extract these fields before rendering:

- `figure_goal`
- `paper_claim`
- `figure_type`
- `mode`
- `panels`
- `must_keep_labels`
- `data`
- `style_constraints`
- `output_formats`
- `verification_checklist`

See `references/figure-brief-spec.md`.

## Image Mode Rules

- Use GPT image generation for conceptual composition, redraws, and edits.
- Preserve scientific terminology and module relationships supplied by the user.
- Prefer white backgrounds, short labels, clear arrows, explicit reading order, and restrained publication styling.
- For final figures, favor high quality and a landscape aspect ratio unless the paper layout or user request implies otherwise.
- Do not introduce unsupported formulas, measurements, causal claims, model components, or benchmark values.
- If the user explicitly asks for a CLI/API/model-specific path, follow the installed system image-generation skill's fallback rules instead of inventing a new wrapper.

## Plot Mode Rules

- Numeric truth overrides aesthetics.
- Use local plotting for exact values, scales, error bars, confidence intervals, and benchmark geometry.
- Never change supplied numbers to improve the visual.
- Prefer vector export when useful and high-resolution raster output for paper insertion.
- Keep axis labels, units, legends, and uncertainty notation faithful to the source data.

## Mixed Mode Rules

- Render quantitative panels first.
- Do not ask the image model to redraw exact plots.
- Generate only the conceptual panels, then keep the visual language compatible across panels.
- Re-check that panel labels and cross-panel references still match after composition.

## Quality Rules

- Do not fabricate measurements, benchmark values, hardware specs, model components, formulas, or unsupported causal claims.
- Preserve user-supplied terminology when scientifically meaningful.
- Favor white backgrounds, clear arrows, restrained spacing, concise labels, and publication readability.
- For Chinese figures, preserve standard mathematical notation and established technical abbreviations where useful.
