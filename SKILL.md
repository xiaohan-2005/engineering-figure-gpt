---
name: engineering-figure-gpt
description: Use when the user needs publication-style engineering, computer-science, data-science, AI, electronics, or mathematical-modeling figures. Prefer this skill for system architectures, algorithm workflows, graphical abstracts, model-framework diagrams, benchmark charts, ablation plots, trend/scatter/heatmap panels, figure redraws, and image edits. Use OpenAI image models for conceptual figures and local plotting for exact quantitative figures.
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
4. For conceptual figures, select a prompt template and use `scripts/build_engineering_figure_prompt.py`.
5. Generate or edit with `scripts/generate_image.py` using the official OpenAI Image API by default.
6. For exact plots, use `scripts/plot_publication_figure.py`.
7. Verify labels, hierarchy, reading order, values, axes, legend, and claim fidelity.

## Quality rules

- Do not fabricate measurements, benchmark values, hardware specs, model components, or unsupported causal claims.
- Preserve user-supplied terminology when scientifically meaningful.
- Favor white backgrounds, clear arrows, restrained spacing, concise labels, and publication readability.
- Use GPT Image 2 as the default conceptual-image model unless the user explicitly overrides it.
- Never send API keys or user files to a non-official endpoint without explicit user approval.
- For Chinese figures, preserve standard mathematical notation and established technical abbreviations where useful.
