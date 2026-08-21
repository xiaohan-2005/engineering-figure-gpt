# Engineering Figure GPT

[![Skill CI](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml/badge.svg)](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml)

A Codex-native research-figure skill for engineering, computer science, AI, data science, electronics, and mathematical modeling.

Engineering Figure GPT separates **scientific content**, **image quality**, **editing scope**, and **numeric truth**:

- `image`: generate new conceptual/schematic research figures with a reusable publication-quality contract;
- `edit`: correct, revise, restyle, or redraw an existing research figure with explicit preservation rules;
- `plot`: render exact quantitative figures locally;
- `mixed`: keep quantitative panels local and use GPT only for conceptual panels.

Core rule: **never let image generation silently rewrite scientific data, axes, uncertainty, formulas, benchmark geometry, or unrelated parts of an existing figure.** A successful image API response is not automatically a paper-ready figure.

[中文说明](README.zh-CN.md) · [Installation](INSTALL.md) · [Showcase](docs/showcase.md)

## Image Pipeline v2: content contract + quality contract

A domain template determines what the figure should communicate. A separate reusable image-quality contract determines how clearly and robustly it must render.

```text
domain/content template
        +
publication image-quality contract
        +
user style note
        +
edit preservation contract (when editing)
```

Quality profiles live in:

```text
assets/prompt-templates/image-quality-contracts.json
```

Profiles:

- `draft`: structural exploration;
- `paper`: default paper-ready constraints;
- `final`: strongest final-export constraints.

The `paper` and `final` profiles explicitly require safe outer margins, large readable label regions, strong contrast, disciplined alignment/spacing, crisp arrows and borders, restrained semantic colors, and essential labels that remain readable at roughly 50% native size / intended paper width. They reject unreadable micro-text, clipping, blur/ghosting, decorative pseudo-technical fine print, and unrelated scientific invention.

See [Image Quality Contract](references/image-quality-contract.md), [Publication Figure Design](references/publication-figure-design.md), and [Visual QA](references/visual-qa.md).

## Image mode: generate a new conceptual figure

For portable/reproducible execution, route image requests through `efg image` so the selected quality contract is injected into the resolved prompt.

```bash
python scripts/efg.py image \
  "A retrieval system with OCR, embeddings, reranking, and answer synthesis" \
  --figure-template system-architecture \
  --quality-profile paper \
  --lang en \
  --save-prompt output/final-prompt.txt \
  --dry-run
```

Remove `--dry-run` only when a live request is intended.

Raw prompts without a figure template also receive the selected quality contract when routed through `efg image`.

## Edit mode: preserve what should not change

Image editing is a first-class workflow rather than a hidden `--input-image` option.

```bash
python scripts/efg.py edit figure.png \
  "Change Encoder to Cross-Attention Encoder only" \
  --mode correct \
  --preserve "all arrow endpoints" \
  --save-prompt output/edit-prompt.txt \
  --dry-run
```

Four modes define the permitted scope:

| Mode | Behavior |
|---|---|
| `correct` | smallest possible localized correction; preserve everything unrelated |
| `revise` | requested local content/structure change; keep unaffected content stable |
| `restyle` | visual-style change only; lock scientific content and relationships |
| `redraw` | clean reconstruction while preserving scientific meaning and canonical labels |

Repeat `--preserve` and `--allow-change` to make the edit boundary explicit:

```bash
--preserve "module positions"
--preserve "all labels except the requested one"
--allow-change "Encoder label text"
```

Additional style/visual references may be supplied with repeatable `--reference-image`. The primary input image remains the scientific/content baseline.

Edit mode defaults to `input_fidelity=high` unless explicitly overridden.

See [Edit Mode](references/edit-mode.md).

## Visual QA: API success is not figure success

Before paper use, inspect conceptual figures in this order:

1. scientific fidelity;
2. text integrity;
3. layout integrity;
4. arrows and line quality;
5. color and contrast;
6. raster clarity at native and approximately 50% scale;
7. source-vs-result preservation for edited figures.

Do not regenerate the entire image for every localized problem:

```text
typo / wrong arrow / minor clipping -> edit --mode correct
requested content change            -> edit --mode revise
style-only problem                  -> edit --mode restyle
globally unusable layout            -> edit --mode redraw or regenerate
```

See [Visual QA](references/visual-qa.md).

## Final/high-resolution: model tier is not raster size

Routine image generation uses `OPENAI_IMAGE_MODEL` and otherwise defaults to `gpt-image-2`.

Final-quality intent uses `OPENAI_IMAGE_HIGHRES_MODEL` or an explicit image `--model`:

```bash
python scripts/efg.py image \
  "technical background" \
  --figure-template graphical-abstract \
  --final
```

If final/high-resolution output is requested but no final-quality image model is configured, the CLI fails closed rather than silently downgrading.

However, a high-resolution model route does **not** guarantee a particular raster dimension. Provider canvas size is requested separately with `--size`, and the actual returned artifact can be checked objectively:

```bash
python scripts/efg.py verify-image output/figure.png \
  --expected-size 1536x1024 \
  --require-format png
```

Minimum acceptance gate:

```bash
python scripts/efg.py verify-image output/figure.png \
  --min-width 1500 \
  --min-height 1000 \
  --min-megapixels 1.5
```

Live image/edit requests routed through `efg image` or `efg edit` now automatically verify that returned raster files are readable and that concrete requested size/format settings were honored. This catches compatible relays that silently ignore `--size`.

Pixel dimensions still do not prove text clarity or scientific correctness, so visual QA remains required.

See [Final / High-Resolution Policy](references/highres-policy.md).

## Codex CLI + CC Switch provider reuse

For command-line Codex users, the portable image path can reuse the active provider from:

```text
~/.codex/config.toml
~/.codex/auth.json
```

Connection resolution:

```text
explicit CLI override
        ↓
active Codex / CC Switch provider
        ↓
legacy OPENAI_* fallback
        ↓
official OpenAI default
```

Inspect the sanitized active provider:

```bash
python scripts/codex_provider_config.py
```

Probe image routes before spending credits:

```bash
python scripts/efg.py provider-check
```

A non-OpenAI endpoint already selected by the active Codex provider is treated as user-selected. A manually supplied relay still requires explicit trust:

```bash
python scripts/efg.py image \
  "technical background" \
  --figure-template system-architecture \
  --base-url https://relay.example/v1 \
  --allow-third-party
```

The relay may receive the configured API key and any input images used for editing. Provider checks can confirm basic route/model exposure, but not perfect compatibility for every image parameter.

## Exact plotting: request → spec → figure

Natural language is the user-facing interface; JSON is an internal contract.

```text
concise Plot Request (`kind`)
        ↓
build_plot_spec.py
        ↓
normalized Plot Spec (`type`)
        ↓
plot_publication_figure.py
```

One-command route:

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

Supported deterministic panel intents include grouped bars, error bars, annotations, trend curves, uncertainty shadows, heatmaps, scatter plots, legend-only panels, and multi-panel layouts.

See [Publication Plot API](references/publication-plot-api.md) and [Publication Chart Patterns](references/publication-chart-patterns.md).

## Mathematical modeling domain pack

The repository ships:

```text
assets/prompt-templates/engineering-figure-templates.json
assets/prompt-templates/mathematical-modeling-templates.json
```

The modeling pack includes problem analysis, Q1/Q2/Q3 dependencies, preprocessing, forecasting, classification, clustering, optimization formulation, multi-objective/Pareto workflows, spatial/network modeling, evaluation systems, sensitivity/robustness analysis, decision frameworks, and end-to-end modeling pipelines.

List all templates:

```bash
python scripts/build_engineering_figure_prompt.py --list-templates
```

Exact forecast curves, Pareto fronts, sensitivity indices, robustness curves, confusion matrices, and benchmark values remain local/deterministic.

See [Mathematical Modeling Guidance](references/mathematical-modeling.md).

## Editable handoff

Generated conceptual figures may still need a deterministic human-editable pass for typography, formulas, panel letters, or final composition.

Recommended conceptual package:

```text
brief.md
prompt.txt
output.png
verification.md
editable-handoff.md
```

Exact plots should additionally preserve the request, normalized spec, and vector exports such as SVG/PDF.

See [Editable Figure Handoff](references/editable-figure-handoff.md).

## Install into Codex on Windows

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

The installer synchronizes a pruned runtime package to:

```text
~/.codex/skills/engineering-figure-gpt
```

The default install test now runs three offline chains without image API cost:

```text
Plot Request -> Spec -> Renderer -> PNG
Edit Contract -> preservation-first dry-run prompt
Raster Fixture -> verify-image size/format gate
```

Optional paid live image test:

```powershell
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1" -TestLiveImage
```

The live test routes through the quality-constrained `efg image` workflow and verifies the actual returned raster size/format.

Diagnostics:

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/check_setup.ps1"
```

Interactive wizard:

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/wizard.ps1"
```

The wizard covers prompt building, image generation, constrained editing, raster verification, active Codex/CC Switch provider reuse, manual trusted relay override, provider probing, exact plots, and offline runtime checks.

## Unified CLI

```bash
# prompt only + paper quality contract
python scripts/efg.py prompt --figure-template problem-analysis --quality-profile paper --lang en "modeling background"

# conceptual generation dry-run
python scripts/efg.py image "modeling background" --figure-template full-modeling-pipeline --lang en --dry-run

# localized image correction dry-run
python scripts/efg.py edit figure.png "Fix the second label only" --mode correct --dry-run

# objective raster verification
python scripts/efg.py verify-image output/figure.png --expected-size 1536x1024 --require-format png

# provider compatibility without image generation
python scripts/efg.py provider-check

# request -> normalized spec -> exact figure
python scripts/efg.py plot request.json --spec-out output/spec.json --out-path output/figure --formats png pdf svg

# normalized spec -> exact figure
python scripts/efg.py render output/spec.json --out-path output/figure --formats png pdf svg

# offline runtime checks
python scripts/efg.py check
```

## Reproducibility

Conceptual evidence chain:

```text
Figure Brief
-> Domain Prompt + Quality Contract
-> Real GPT Output
-> Visual QA
-> optional constrained Edit
-> Verification
```

Quantitative evidence chain:

```text
Plot Request -> Normalized Plot Spec -> Renderer -> Real Output -> Verification
```

## Validation and CI

CI validates:

- Python compilation;
- Skill metadata/runtime structure;
- UTF-8 and common mojibake patterns;
- engineering + mathematical-modeling prompt packs;
- reusable image-quality contract pack;
- quality-contract prompt injection;
- preservation-first edit behavior;
- objective raster verification success/failure paths;
- local documentation links/images;
- Figure Brief / Plot Request / Plot Spec contracts;
- GPT image generation/edit request construction;
- Codex/CC Switch provider resolution and explicit relay trust;
- final/high-resolution fail-closed routing;
- HTTP/network/timeout/malformed-response/empty-output behavior;
- local plot E2E rendering;
- pruned runtime package/token budget;
- offline CLI checks.

## Showcase status

Current conceptual SVGs in [docs/showcase.md](docs/showcase.md) remain explicitly labeled as **layout previews** rather than fake GPT outputs.

Real GPT conceptual showcase cases should be added only after the quality/edit/verification pipeline is stable and each case preserves a real:

```text
brief + resolved prompt + output + visual verification
```

## Design principles

1. Scientific fidelity before decoration.
2. Image-quality constraints are separate from domain-content templates.
3. API success is not final figure acceptance.
4. Localized errors should be corrected locally rather than forcing a full redraw.
5. High-resolution model routing and actual raster dimensions are separate acceptance concerns.
6. Numeric truth stays local and deterministic.
7. GPT is used where semantic composition helps.
8. Chinese academic figures and mathematical modeling are primary use cases.
9. Active Codex/CC Switch providers can be reused; manual relay overrides require explicit trust.
10. Final-quality requests must not silently downgrade.
11. Runtime context stays pruned and auditable.
12. Outputs should remain reproducible and editable whenever practical.

## License

See [LICENSE](LICENSE).
