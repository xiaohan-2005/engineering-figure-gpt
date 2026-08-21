---
name: engineering-figure-gpt
description: Use when the user needs publication-style engineering, computer-science, data-science, AI, electronics, or mathematical-modeling figures. Prefer this skill for system architectures, algorithm workflows, graphical abstracts, modeling frameworks, figure correction/revision/restyling/redrawing, benchmark/ablation/sensitivity plots, and mixed conceptual-plus-quantitative figures. Conceptual figures use GPT image generation with explicit publication-quality contracts; exact quantitative figures stay local and deterministic. The portable image path can reuse the active Codex/CC Switch provider and supports explicitly trusted OpenAI-compatible relays.
---

# Engineering Figure GPT

Use this skill once the figure goal is reasonably clear.

## Core decision

- `image`: new conceptual architecture, workflow, graphical abstract, modeling framework, mechanism/schematic
- `edit`: modify an existing figure through preservation-first `correct`, `revise`, `restyle`, or `redraw` workflows
- `plot`: exact bar, trend, heatmap, scatter, ablation, benchmark, sensitivity/robustness, and multi-panel quantitative figures
- `mixed`: locally rendered exact panels plus GPT-generated conceptual panels

Never use image generation for exact numeric geometry, axes, uncertainty bars, benchmark values, measured coordinates, or formulas that must remain exact.

## Non-negotiable image-quality rule

A successful image API response is not automatically a successful research figure.

Every conceptual generation/edit must separate:

```text
domain/content contract
        +
publication image-quality contract
        +
user style constraints
        +
edit preservation contract (when editing)
```

The reusable quality contracts live in:

```text
assets/prompt-templates/image-quality-contracts.json
```

Profiles:

- `draft`: structural exploration
- `paper`: default paper-ready conceptual figure
- `final`: strongest final-export rendering constraints

For `paper` and `final` output:

- white or near-white background unless explicitly overridden
- one explicit reading direction
- safe outer margins; no clipped modules, labels, or arrowheads
- large clean text regions and strong text/background contrast
- essential labels readable at approximately 50% native size / intended paper width
- prefer fewer larger labels over many tiny annotations
- crisp consistent borders/arrows with clear arrowheads
- no arrows through text unless unavoidable and meaningful
- disciplined alignment and spacing
- stable low-to-medium-saturation semantic colors
- no unreadable micro-text, blur, ghosting, decorative pseudo-technical fine print, glossy 3D, cinematic lighting, noisy textures, or poster gradients unless requested

Read `references/image-quality-contract.md` and `references/publication-figure-design.md` when visual quality matters.

## Default workflow

1. Inspect the user's paper text, figure brief, numeric data, reference image, or request.
2. Structure the task with `references/figure-brief-spec.md` when needed.
3. Choose `image`, `edit`, `plot`, or `mixed`.
4. For a new conceptual figure, choose the closest engineering or mathematical-modeling template.
5. Build the final prompt with the reusable image-quality contract; use `paper` by default and `final` for explicit final/high-resolution intent.
6. For an existing figure, choose the narrowest edit mode and define what must remain unchanged.
7. Inside Codex, use the installed GPT image path when appropriate; for reproducible execution use `scripts/efg.py`.
8. When Codex is launched from the command line and its provider is managed by CC Switch, the portable image path should reuse the active `~/.codex/config.toml` + `~/.codex/auth.json` provider automatically. Read `references/codex-cc-switch.md` when provider behavior matters.
9. A non-OpenAI endpoint selected by the active Codex provider is already user-selected and does not require a second trust flag. A custom URL supplied independently through `--base-url` or `OPENAI_BASE_URL` still requires `--allow-third-party` or `OPENAI_ALLOW_THIRD_PARTY=1`.
10. If image compatibility is uncertain, use `scripts/efg.py provider-check` before spending image credits. A provider that works for Codex text requests may still lack `/images/generations` or `/images/edits`.
11. For final/high-resolution intent, follow `references/highres-policy.md`; never silently downgrade model, requested size, quality, or provider.
12. After generation/editing, run the visual QA checks in `references/visual-qa.md`.
13. When explicit raster dimensions/format/aspect matter, run `scripts/efg.py verify-image` on the actual returned file.
14. Correct localized problems with `edit --mode correct` rather than blindly regenerating the whole image.
15. For exact plots, treat natural language as the user interface and JSON as internal execution data.
16. In mixed mode, render quantitative panels first and never ask the image model to redraw them.
17. For reusable/showcase work, preserve the evidence chain from `references/reproducibility-chain.md` and use editable handoff when appropriate.

## Prompt template packs

Engineering/general templates:

```text
assets/prompt-templates/engineering-figure-templates.json
```

Mathematical-modeling domain pack:

```text
assets/prompt-templates/mathematical-modeling-templates.json
```

The modeling pack includes problem analysis, Q1/Q2/Q3 dependency, preprocessing, forecasting, classification, clustering, optimization, Pareto workflows, spatial/network modeling, evaluation, sensitivity/robustness, decision frameworks, and end-to-end modeling pipelines.

List templates with:

```bash
python scripts/build_engineering_figure_prompt.py --list-templates
```

## Image mode: new conceptual figure

Use image generation when conceptual composition matters more than exact numeric geometry.

Rules:

- preserve user terminology, module relationships, variables, units, mathematical notation, and standard abbreviations
- do not invent measurements, formulas, benchmark values, causal claims, model components, thresholds, or hardware specifications
- keep Chinese labels concise and preserve established English abbreviations when useful
- do not generate long exact formulas inside raster conceptual art
- inspect all generated text before final paper use

One-command generation with a paper-quality contract:

```bash
python scripts/efg.py image \
  "A retrieval system with OCR, embedding, reranking, and answer synthesis" \
  --figure-template system-architecture \
  --lang en \
  --quality-profile paper \
  --save-prompt output/final-prompt.txt \
  --dry-run
```

Remove `--dry-run` only when a live request is intended.

A raw prompt without a template also receives the selected quality contract through `efg image`.

## Edit mode: existing figure

Editing is a first-class workflow. Do not treat a small correction as a from-scratch generation.

Use:

```bash
python scripts/efg.py edit figure.png \
  "Change Encoder to Cross-Attention Encoder only" \
  --mode correct \
  --preserve "all arrow endpoints" \
  --save-prompt output/edit-prompt.txt
```

Edit modes:

- `correct`: smallest possible correction; preserve canvas, layout, unaffected labels, arrows, palette, typography, and style
- `revise`: requested local content/structural change; preserve unaffected content and established visual language
- `restyle`: change visual style only; lock scientific content, labels, relationships, and supported claims
- `redraw`: reconstruct cleanly from the reference; layout may improve, but scientific meaning, canonical labels, and supported relationships remain authoritative

Use repeated `--preserve` and `--allow-change` flags to define the change boundary explicitly.

The primary input image is the scientific/content baseline. Extra `--reference-image` files may guide style or reconstruction but must not silently override the scientific content.

Edit mode uses `input_fidelity=high` by default unless explicitly overridden.

Read `references/edit-mode.md`.

## Visual QA and correction loop

Before final handoff, check in this order:

1. scientific fidelity
2. text integrity
3. layout integrity
4. arrows/line quality
5. color/contrast
6. raster clarity at native and approximately 50% size
7. edit preservation against the source image when applicable

Reject or correct malformed labels, clipping, overlap, wrong arrows, hallucinated detail, blur/ghosting, unreadable micro-text, or unrelated changes.

Failure routing:

- isolated typo/wrong arrow/minor clipping -> `edit --mode correct`
- requested scientific content change -> `edit --mode revise`
- style-only issue -> `edit --mode restyle`
- globally unusable layout -> `edit --mode redraw` or regenerate from a revised brief

Read `references/visual-qa.md`.

## Final/high-resolution and raster-size verification

High-resolution model routing and actual raster dimensions are separate concerns.

Routine image model resolution:

```text
--model -> OPENAI_IMAGE_MODEL -> gpt-image-2
```

Final/high-resolution intent:

```text
--model -> OPENAI_IMAGE_HIGHRES_MODEL
```

If final-quality intent has no explicit image model and no configured `OPENAI_IMAGE_HIGHRES_MODEL`, stop instead of silently falling back.

The provider canvas is controlled separately with `--size`.

Never claim 2K/4K/final-size output only because a model name suggests high resolution. When the user gives an explicit pixel target, verify the returned artifact.

Example:

```bash
python scripts/efg.py verify-image output/figure.png \
  --expected-size 1536x1024 \
  --require-format png
```

Minimum-size gate:

```bash
python scripts/efg.py verify-image output/figure.png \
  --min-width 1500 \
  --min-height 1000 \
  --min-megapixels 1.5
```

Metadata verification does not replace visual QA; pixel dimensions cannot prove text clarity or scientific correctness.

Read `references/highres-policy.md` and `references/image-quality-contract.md`.

## Command-line Codex + CC Switch

If the user starts Codex from the command line and CC Switch already selected the Codex API provider, do not ask the user to duplicate the same Base URL and key in environment variables.

Connection resolution:

```text
explicit CLI override
        ↓
active Codex provider (~/.codex/config.toml + auth.json)
        ↓
legacy OPENAI_* fallback
        ↓
official OpenAI default
```

Inspect the sanitized active provider with:

```bash
python scripts/codex_provider_config.py
```

Check provider image routes with:

```bash
python scripts/efg.py provider-check
```

Never print or copy the provider token into prompts or repository files.

### Manual trusted relay override

Only when deliberately overriding the active Codex provider:

```bash
python scripts/efg.py image \
  "technical background" \
  --figure-template system-architecture \
  --base-url https://relay.example/v1 \
  --allow-third-party
```

A manually supplied relay may receive the configured API key and input images used for edits, so explicit trust remains required.

A provider check can confirm basic route/model exposure but cannot guarantee that every OpenAI image parameter is implemented identically. Verify real outputs when size/format/edit fidelity matters.

## Plot mode

Numeric truth overrides aesthetics.

Supported panel intents include:

- grouped bars with optional error bars and annotations
- trend curves with optional uncertainty shadows
- heatmaps with exact matrices and colorbars
- scatter plots with one or multiple labeled series
- dedicated legend-only panels
- empty panels for deliberate multi-panel layout

Preferred path:

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
# build prompt only
python scripts/efg.py prompt --figure-template problem-analysis --quality-profile paper --lang zh "建模背景"

# generate a conceptual figure
python scripts/efg.py image "建模背景" --figure-template full-modeling-pipeline --lang zh --dry-run

# preservation-first image correction
python scripts/efg.py edit figure.png "只修正第二个模块的错别字" --mode correct --dry-run

# provider compatibility
python scripts/efg.py provider-check

# objective raster verification
python scripts/efg.py verify-image output/figure.png --expected-size 1536x1024 --require-format png

# exact quantitative figure
python scripts/efg.py plot request.json --spec-out output/spec.json --out-path output/figure --formats png pdf svg
python scripts/efg.py render output/spec.json --out-path output/figure --formats png pdf svg

# offline runtime smoke check
python scripts/efg.py check
```

## Reference loading

Read only what the current task needs. Start from `references/README.md`.

Common references:

- `figure-brief-spec.md`
- `image-mode.md`
- `image-quality-contract.md`
- `edit-mode.md`
- `visual-qa.md`
- `publication-figure-design.md`
- `highres-policy.md`
- `plot-mode.md`
- `mixed-mode.md`
- `natural-language-plot-workflow.md`
- `publication-plot-api.md`
- `publication-chart-patterns.md`
- `mathematical-modeling.md`
- `chinese-labels.md`
- `openai-image-workflow.md`
- `codex-cc-switch.md`
- `image-execution-reliability.md`
- `editable-figure-handoff.md`
- `reproducibility-chain.md`
