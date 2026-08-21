# Engineering Figure GPT

[![Skill CI](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml/badge.svg)](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml)

A Codex-native research-figure skill for engineering, computer science, AI, data science, electronics, and mathematical modeling.

Engineering Figure GPT separates four workflows:

- `image`: new conceptual research figures;
- `edit`: preservation-first correction, revision, restyling, or redraw of an existing figure;
- `plot`: deterministic quantitative figures;
- `mixed`: conceptual panels plus locally rendered exact plots.

Core rule: **image generation must never silently rewrite numeric truth, scientific relationships, axes, uncertainty, formulas, or benchmark geometry.**

[中文说明](README.zh-CN.md) · [Installation](INSTALL.md) · [Showcase](docs/showcase.md)

## Image Pipeline v2

Conceptual prompts are composed from independent layers:

```text
domain/content template
+ publication image-quality contract
+ user style constraints
+ edit preservation contract (when editing)
+ optional spatial mask constraint (localized edits)
```

Quality profiles live in `assets/prompt-templates/image-quality-contracts.json`:

| Profile | Purpose | Default rendering hint |
|---|---|---|
| `draft` | fast structural exploration | `quality=low`, `1024x1024` |
| `paper` | default paper-ready conceptual figure | `quality=high`, `1536x1024` |
| `final` | strongest final-export constraints | `quality=high`, `2048x1152` |

The quality contract explicitly asks for safe margins, large readable text regions, clear reading order, crisp arrows/borders, disciplined alignment, restrained semantic colors, strong contrast, and readability around 50% native scale. It rejects micro-text, blur, ghosting, decorative pseudo-technical detail, glossy 3D, noisy textures, and unsupported scientific content.

See [Image Quality Contract](references/image-quality-contract.md) and [Visual QA](references/visual-qa.md).

## Generate a conceptual figure

```bash
python scripts/efg.py image \
  "A retrieval system with OCR, embeddings, reranking, and answer synthesis" \
  --figure-template system-architecture \
  --quality-profile paper \
  --lang en \
  --save-prompt output/final-prompt.txt \
  --dry-run
```

Remove `--dry-run` only for a live image request.

## Edit an existing figure

```bash
python scripts/efg.py edit figure.png \
  "Change Encoder to Cross-Attention Encoder only" \
  --mode correct \
  --preserve "all arrow endpoints" \
  --save-prompt output/edit-prompt.txt \
  --dry-run
```

Edit modes:

- `correct`: smallest possible localized fix;
- `revise`: requested local scientific/structural change;
- `restyle`: visual style only, scientific content locked;
- `redraw`: clean reconstruction while preserving authoritative scientific meaning and labels.

Use repeatable `--preserve` and `--allow-change` options to make the edit boundary explicit. Extra `--reference-image` files may guide style/reconstruction, but the primary source remains the scientific baseline.

### Mask-guided localized edits

For a bounded correction, add a spatial mask on top of the semantic preservation contract:

```bash
python scripts/efg.py edit figure.png \
  "Fix only the mislabeled module" \
  --mode correct \
  --mask edit-mask.png \
  --preserve "all arrows and unaffected labels"
```

Before upload, the portable path validates that the mask is smaller than 50 MB, has exactly the same dimensions and image format as the primary figure, and contains an alpha channel. The resolved edit prompt also preserves content outside the masked area except minimal blending needed at the boundary.

A mask is **strong spatial guidance, not a pixel-perfect guarantee**. Source-vs-result Visual QA is still required; unrelated changes outside the intended region fail `correct` mode.

### GPT Image 2 edit policy

For `gpt-image-2`, **omit `input_fidelity`**. GPT Image 2 always processes image inputs at high fidelity and does not allow that setting to be changed.

When no edit `--size` is given:

- legal source dimensions are preserved exactly;
- a source with a supported aspect ratio but illegal pixel dimensions is mapped to the nearest legal canvas with a visible warning;
- an unsafe/unresolvable canvas requires an explicit legal size instead of silently changing the figure.

This makes `correct` suitable for localized fixes without casually changing the whole canvas.

See [Edit Mode](references/edit-mode.md).

## Resolution and final-quality behavior

Model tier, rendering quality, and raster size are separate controls.

Routine model:

```text
OPENAI_IMAGE_MODEL -> gpt-image-2
```

Optional separate final/high-resolution model route:

```text
OPENAI_IMAGE_HIGHRES_MODEL
```

Use `--final` or `--highres` to request that route. If it is not configured and no explicit model is supplied, the request fails closed.

`--quality-profile final` does **not** automatically mean `--final`; it controls the stronger prompt/rendering contract, while model routing remains separate.

For GPT Image 2, a concrete `WIDTHxHEIGHT` must satisfy:

- each edge <= 3840 px;
- both edges divisible by 16;
- long/short ratio <= 3:1;
- total pixels between 655,360 and 8,294,400.

Verify the real artifact rather than trusting the model name:

```bash
python scripts/efg.py verify-image output/figure.png \
  --expected-size 2048x1152 \
  --require-format png
```

Live `efg image` / `efg edit` requests also verify concrete requested size/format after the provider returns the raster.

See [High-resolution Policy](references/highres-policy.md).

## Visual QA

API success is not figure success. Check:

1. scientific fidelity;
2. text integrity;
3. layout integrity;
4. arrows and line quality;
5. color and contrast;
6. clarity at native and roughly 50% scale;
7. source-vs-result preservation for edits, including unintended changes outside a supplied mask.

Route failures narrowly:

```text
typo / wrong arrow / minor clipping -> correct
scientific content change           -> revise
style-only problem                  -> restyle
globally unusable draft             -> redraw or regenerate
```

## Codex + CC Switch provider reuse

The portable image path resolves connection settings in this order:

```text
explicit CLI override
-> active Codex / CC Switch provider
-> legacy OPENAI_* environment fallback
-> official OpenAI default
```

Inspect the active provider without printing its secret:

```bash
python scripts/codex_provider_config.py
```

Probe image routes before spending image credits:

```bash
python scripts/efg.py provider-check
```

A manually supplied relay must be explicitly trusted with `--allow-third-party`. A provider that works for Codex text may still lack `/images/generations` or `/images/edits`.

## Exact Plot Mode

```bash
python scripts/efg.py plot request.json \
  --spec-out output/spec.json \
  --out-path output/figure \
  --formats png pdf svg
```

The internal deterministic chain is:

```text
Plot Request
-> build_plot_spec.py
-> Normalized Plot Spec
-> plot_publication_figure.py
-> PNG / PDF / SVG
```

Forecast curves, Pareto fronts, sensitivity indices, robustness curves, confusion matrices, benchmarks, axes, and uncertainty remain local/deterministic.

## Mathematical-modeling domain pack

`assets/prompt-templates/mathematical-modeling-templates.json` contains dedicated templates for problem analysis, Q1/Q2/Q3 dependencies, preprocessing, forecasting, classification, clustering, optimization, Pareto workflows, spatial/network modeling, evaluation, sensitivity, robustness, decision frameworks, and complete modeling pipelines.

Do not fabricate coefficients, optimal values, weights, rankings, or evaluation results.

## Installation

Windows PowerShell:

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

The installer synchronizes a **pruned execution runtime** to:

```text
~/.codex/skills/engineering-figure-gpt
```

Tests, CI validators, installer diagnostics, and the interactive wizard remain in the source checkout to protect the Runtime token budget.

Run source-side diagnostics against the installed Runtime:

```powershell
& "$HOME/engineering-figure-gpt/scripts/check_setup.ps1" `
  -SkillDir "$HOME/.codex/skills/engineering-figure-gpt"
```

Run the source-side Wizard against the Runtime:

```powershell
& "$HOME/engineering-figure-gpt/scripts/wizard.ps1" `
  -SkillDir "$HOME/.codex/skills/engineering-figure-gpt"
```

The Wizard asks separately for the visual quality profile and whether to use the `--final` model route, and Edit Mode can optionally accept a spatial mask.

The normal installer performs offline Plot/Edit/Verifier smoke tests without image API cost. A paid live image check is opt-in:

```powershell
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1" -SkipDependencies -TestLiveImage
```

## Unified CLI

```bash
python scripts/efg.py prompt --figure-template problem-analysis --quality-profile paper --lang en "modeling background"
python scripts/efg.py image "modeling background" --figure-template full-modeling-pipeline --lang en --dry-run
python scripts/efg.py edit figure.png "Fix one label only" --mode correct --dry-run
python scripts/efg.py edit figure.png "Change only the masked region" --mode correct --mask edit-mask.png --dry-run
python scripts/efg.py verify-image output/figure.png --expected-size 1536x1024 --require-format png
python scripts/efg.py provider-check
python scripts/efg.py plot request.json --spec-out output/spec.json --out-path output/figure --formats png pdf svg
python scripts/efg.py check
```

## Reproducibility

A real conceptual showcase should preserve:

```text
Figure Brief
-> Resolved Prompt
-> Real GPT Output
-> Visual QA
-> optional constrained Edit
-> Verification
```

Conceptual layout-preview SVGs are not presented as fake GPT output.

## License

See [LICENSE](LICENSE).
