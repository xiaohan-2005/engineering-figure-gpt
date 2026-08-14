---
name: engineering-figure-gpt
description: Use when the user needs publication-style engineering, computer-science, data-science, AI, electronics, or mathematical-modeling figures. Prefer this skill for system architectures, algorithm workflows, graphical abstracts, modeling frameworks, benchmark/ablation/sensitivity plots, figure redraws, and image edits. Use Codex built-in GPT image generation for conceptual figures when available, a GPT Image-compatible CLI with official OpenAI or explicitly approved relay URLs for reproducibility, and local plotting for exact quantitative figures.
---

# Engineering Figure GPT

Use this skill once the figure goal is reasonably clear.

## Core decision

- `image`: conceptual architecture, workflow, graphical abstract, modeling framework, mechanism/schematic, redraw, image edit
- `plot`: exact bar, trend, heatmap, scatter, ablation, benchmark, sensitivity/robustness, and multi-panel quantitative figures
- `mixed`: locally rendered exact panels plus GPT-generated conceptual panels

Never use image generation for exact numeric geometry, axes, uncertainty bars, benchmark values, measured coordinates, or formulas that must remain exact.

## Default workflow

1. Inspect the user's paper text, figure brief, numeric data, reference image, or request.
2. Structure the task with `references/figure-brief-spec.md` when needed.
3. Choose `image`, `plot`, or `mixed`.
4. For conceptual figures, choose the closest template from the engineering or mathematical-modeling prompt packs.
5. Inside Codex, prefer the built-in image-generation capability for normal conceptual work.
6. For a portable/reproducible image path, use `scripts/efg.py image` or `scripts/generate_image.py`.
7. Official OpenAI works by default. A custom OpenAI-compatible relay requires explicit trust via `--allow-third-party` or `OPENAI_ALLOW_THIRD_PARTY=1`.
8. If relay compatibility is uncertain, use `scripts/efg.py provider-check` before spending image credits.
9. For final/high-resolution intent, follow `references/highres-policy.md`; never silently downgrade model/quality/provider.
10. For exact plots, treat natural language as the user interface and JSON as internal execution data.
11. Prefer the one-command plot path `scripts/efg.py plot request.json`; use `render` only for an already normalized spec.
12. In mixed mode, render quantitative panels first and never ask the image model to redraw them.
13. Verify labels, units, reading order, legends, values, axes, uncertainty, and scientific fidelity.
14. For reusable/showcase work, preserve the evidence chain from `references/reproducibility-chain.md` and use editable handoff when appropriate.

## Prompt template packs

Engineering/general templates live in:

```text
assets/prompt-templates/engineering-figure-templates.json
```

The mathematical-modeling domain pack lives in:

```text
assets/prompt-templates/mathematical-modeling-templates.json
```

It includes dedicated templates for:

- problem analysis
- Q1/Q2/Q3 dependency
- preprocessing
- forecasting
- classification
- clustering
- optimization formulation
- multi-objective/Pareto workflow
- spatial modeling
- network modeling
- evaluation systems
- sensitivity analysis
- robustness analysis
- decision frameworks
- end-to-end modeling pipelines

Use `python scripts/build_engineering_figure_prompt.py --list-templates` when template choice is unclear.

## Image mode

Use image generation when conceptual composition matters more than exact numeric geometry.

Rules:

- preserve user-supplied terminology, module relationships, variables, units, mathematical notation, and standard abbreviations
- prefer white backgrounds, short labels, clear arrows, disciplined spacing, and explicit reading order
- do not invent measurements, formulas, benchmark values, causal claims, model components, thresholds, or hardware specifications
- for Chinese figures, keep labels concise and preserve established English abbreviations when useful
- inspect all generated text before final paper use

### One-command template generation

```bash
python scripts/efg.py image \
  "A retrieval system with OCR, embedding, reranking, and answer synthesis" \
  --figure-template system-architecture \
  --lang en \
  --save-prompt output/final-prompt.txt \
  --dry-run
```

Remove `--dry-run` only when a live request is intended.

### Trusted relay

```bash
python scripts/efg.py image \
  "technical background" \
  --figure-template system-architecture \
  --base-url https://relay.example/v1 \
  --allow-third-party
```

Never trust a relay implicitly. It may receive the configured API key and any input images used for edits.

### Provider compatibility probe

```bash
python scripts/efg.py provider-check \
  --base-url https://relay.example/v1 \
  --allow-third-party
```

This is a non-generation compatibility probe. It can check basic route/model exposure but cannot guarantee that every relay implements every OpenAI image parameter correctly.

### Final/high-resolution route

```bash
python scripts/efg.py image \
  "technical background" \
  --figure-template graphical-abstract \
  --final
```

`--final` / `--highres` uses `OPENAI_IMAGE_HIGHRES_MODEL` unless an explicit `--model` is supplied. If no final-quality model is configured, stop instead of silently falling back.

## Plot mode

Numeric truth overrides aesthetics.

Supported panel intents include:

- grouped bars with optional error bars and annotations
- trend curves with optional uncertainty shadows
- heatmaps with exact matrices and colorbars
- scatter plots with one or multiple labeled series
- dedicated legend-only panels
- empty panels for deliberate multi-panel layout

Preferred one-command path:

```bash
python scripts/efg.py plot request.json \
  --spec-out output/spec.json \
  --out-path output/figure \
  --formats png pdf svg
```

If a normalized spec already exists:

```bash
python scripts/efg.py render output/spec.json --out-path output/figure --formats png pdf svg
```

Use `references/publication-plot-api.md` and `references/publication-chart-patterns.md` for complex layouts. Never alter supplied values to make a figure look better.

## Mixed mode

For figures containing conceptual and quantitative content:

1. render exact plots locally;
2. generate conceptual panels independently;
3. compose them after generation;
4. keep exact plot files untouched;
5. use `references/editable-figure-handoff.md` for the final editable composition.

## Mathematical modeling

Load `references/mathematical-modeling.md` for modeling tasks.

Important rules:

- make Q1/Q2/Q3 information handoffs explicit only when they actually exist
- preserve model names, variables, symbols, units, constraints, and standard abbreviations
- do not let the image model typeset long formulas that must be exact
- use local plots for forecast curves, residuals, Pareto fronts, sensitivity indices, robustness curves, heatmaps, confusion matrices, and benchmarks
- never fabricate coefficients, optimal values, weights, sensitivity rankings, or evaluation results

## Unified CLI

```bash
python scripts/efg.py prompt --figure-template problem-analysis --lang zh "建模背景"
python scripts/efg.py image "建模背景" --figure-template full-modeling-pipeline --lang zh --dry-run
python scripts/efg.py provider-check --base-url https://relay.example/v1 --allow-third-party
python scripts/efg.py plot request.json --spec-out output/spec.json --out-path output/figure --formats png pdf svg
python scripts/efg.py render output/spec.json --out-path output/figure --formats png pdf svg
python scripts/efg.py check
```

## Reference loading

Read only what the current task needs. Start from `references/README.md`.

Common references:

- `figure-brief-spec.md`
- `image-mode.md`
- `plot-mode.md`
- `mixed-mode.md`
- `natural-language-plot-workflow.md`
- `publication-plot-api.md`
- `publication-chart-patterns.md`
- `publication-figure-design.md`
- `mathematical-modeling.md`
- `chinese-labels.md`
- `openai-image-workflow.md`
- `image-execution-reliability.md`
- `highres-policy.md`
- `editable-figure-handoff.md`
- `reproducibility-chain.md`

## Quality rules

- do not fabricate scientific facts or numeric results
- keep exact plots local and deterministic
- keep formulas and mathematical symbols source-faithful
- inspect Chinese labels for encoding, font fallback, clipping, and excessive length
- prefer concise visual hierarchy over decorative complexity
- preserve prompts/specs/output paths when files are produced so results remain reproducible
- do not claim a showcase image is GPT-generated unless the real output and its evidence chain are actually preserved
