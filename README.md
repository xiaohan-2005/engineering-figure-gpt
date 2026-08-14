# Engineering Figure GPT

<div align="center">

![License](https://img.shields.io/badge/license-MIT-2563eb)
![Codex Skill](https://img.shields.io/badge/Codex-skill-111827)
![Modes](https://img.shields.io/badge/modes-image%20%7C%20plot%20%7C%20mixed-2563eb)
![Image](https://img.shields.io/badge/image-GPT--only-7c3aed)
![Focus](https://img.shields.io/badge/focus-research%20figures-16a34a)

**GPT-native research-figure production for engineering, AI, data science, and mathematical modeling.**

Conceptual figures use GPT image generation. Exact quantitative figures stay local and deterministic.

[中文说明](README.zh-CN.md) · [English Guide](README.en.md) · [Showcase](docs/showcase.md) · [Install](INSTALL.md)

</div>

## Reproducible outputs + conceptual preview

| Exact benchmark output | Sensitivity / robustness output |
|---|---|
| ![Exact benchmark](docs/examples/benchmark-exact/output.svg) | ![Sensitivity and robustness](docs/examples/sensitivity-robustness/output.svg) |
| [brief](docs/examples/benchmark-exact/brief.md) · [request](docs/examples/benchmark-exact/request.json) · [spec](docs/examples/benchmark-exact/plot-spec.json) · [verification](docs/examples/benchmark-exact/verification.md) | [brief](docs/examples/sensitivity-robustness/brief.md) · [request](docs/examples/sensitivity-robustness/request.json) · [spec](docs/examples/sensitivity-robustness/plot-spec.json) · [verification](docs/examples/sensitivity-robustness/verification.md) |

Both datasets are intentionally **synthetic/illustrative**. They demonstrate the exact Plot Mode evidence chain and are not scientific claims.

Conceptual SVGs under `docs/showcase/` are still **layout previews**, not claims that GPT generated them. A conceptual case only becomes a real showcase example after its actual `brief + prompt + output + verification` chain is committed.

## Why this skill exists

Research figures are not one-prompt problems.

| Figure need | Better path |
|---|---|
| Architecture, workflow, graphical abstract, modeling framework | `image` mode |
| Benchmark bars, trends, heatmaps, scatter, sensitivity/robustness | `plot` mode |
| Conceptual + quantitative panels | `mixed` mode |
| Exact formulas or measured geometry | local rendering / editable handoff |

Core rule: **numeric truth overrides aesthetics**. Exact values, axes, uncertainty, benchmark geometry, and long formulas should not be redrawn by an image model.

## Three modes

### Image mode

Use GPT image generation for conceptual composition, redraws, and edits.

Inside Codex, prefer the installed built-in image-generation path. For reproducibility or environments without that path, the repository includes a GPT Image-compatible CLI fallback.

The fallback defaults to `gpt-image-2` and official OpenAI. A custom OpenAI-compatible relay is supported only after explicit trust, so a key or input image is never silently sent to an unexpected host.

One-command template flow:

```bash
python scripts/efg.py image \
  "A retrieval system with OCR, embeddings, reranking, and answer synthesis" \
  --figure-template system-architecture \
  --lang en \
  --save-prompt output/final-prompt.txt \
  --dry-run
```

Remove `--dry-run` only when a live request is intended.

Trusted relay:

```bash
python scripts/efg.py image \
  "technical background" \
  --figure-template system-architecture \
  --base-url https://relay.example/v1 \
  --allow-third-party
```

Before spending image credits, a relay can be probed without generating an image:

```bash
python scripts/efg.py provider-check \
  --base-url https://relay.example/v1 \
  --allow-third-party
```

The compatibility probe checks basic route/model exposure. It cannot guarantee that every relay implements every OpenAI Images parameter identically.

### Final / high-resolution routing

Routine image generation uses `OPENAI_IMAGE_MODEL` and otherwise defaults to `gpt-image-2`.

Final-quality intent uses `OPENAI_IMAGE_HIGHRES_MODEL` or an explicit `--model`:

```bash
python scripts/efg.py image \
  "technical background" \
  --figure-template graphical-abstract \
  --final
```

If a final/high-resolution request has no configured final model, the CLI stops instead of silently downgrading. See [Final / High-Resolution Policy](references/highres-policy.md).

### Plot mode

Natural language is the user interface; JSON is internal execution data.

Supported panel intents include grouped bars, error bars, trend curves, uncertainty shadows, heatmaps, scatter plots, legend-only panels, and multi-panel layouts.

The internal contracts are:

```text
concise Plot Request (`kind`)
        ↓
  build_plot_spec.py
        ↓
normalized Plot Spec (`type`)
        ↓
plot_publication_figure.py
```

The user-facing one-command route is:

```bash
python scripts/efg.py plot examples/multi-panel-plot-request.json \
  --spec-out output/spec.json \
  --out-path output/figure \
  --formats png pdf svg
```

If a normalized spec already exists:

```bash
python scripts/efg.py render output/spec.json --out-path output/figure --formats png pdf svg
```

See [Publication Plot API](references/publication-plot-api.md) and [Chart Patterns](references/publication-chart-patterns.md).

### Mixed mode

Render exact quantitative panels locally first. Generate conceptual panels separately. Compose them after generation and never ask the image model to redraw exact plots. See [Editable Figure Handoff](references/editable-figure-handoff.md).

## Mathematical modeling is a dedicated domain pack

The project includes two prompt packs:

```text
assets/prompt-templates/engineering-figure-templates.json
assets/prompt-templates/mathematical-modeling-templates.json
```

The mathematical-modeling pack adds dedicated templates for:

- problem analysis
- Q1/Q2/Q3 dependency
- data preprocessing
- forecasting
- classification
- clustering
- optimization formulation
- multi-objective / Pareto workflow
- spatial modeling
- network modeling
- evaluation systems
- sensitivity analysis
- robustness analysis
- decision frameworks
- full end-to-end modeling pipelines

List all available templates:

```bash
python scripts/build_engineering_figure_prompt.py --list-templates
```

Chinese and bilingual academic labels are first-class workflows. Exact forecast curves, Pareto fronts, sensitivity indices, robustness curves, confusion matrices, and benchmark values remain local/deterministic.

## Install for Codex

Recommended Windows development/source install:

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

The installer syncs a **pruned runtime package** to:

```text
~/.codex/skills/engineering-figure-gpt
```

Repository-only docs, examples, tests, and CI files are not copied into the Codex runtime.

The default installer test performs a real local Plot Mode E2E chain:

```text
request → normalized spec → renderer → non-empty PNG
```

This has no image API cost. A live GPT image request remains opt-in.

Setup diagnostics:

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/check_setup.ps1"
```

Interactive wizard:

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/wizard.ps1"
```

The wizard can select templates, use official OpenAI or a trusted relay, run provider compatibility checks, request final/high-resolution routing, and execute one-command Plot Mode.

## Relay configuration

Example PowerShell environment:

```powershell
$env:OPENAI_BASE_URL = "https://relay.example/v1"
$env:OPENAI_ALLOW_THIRD_PARTY = "1"
$env:OPENAI_IMAGE_MODEL = "gpt-image-2"
$env:OPENAI_API_KEY_FILE = "$HOME/.codex/secrets/openai_api_key.txt"
```

Optional final-quality model exposed by the relay:

```powershell
$env:OPENAI_IMAGE_HIGHRES_MODEL = "<relay-final-quality-model>"
```

Do not invent a model alias that the relay does not actually expose.

## Unified CLI

```bash
# prompt only
python scripts/efg.py prompt --figure-template problem-analysis --lang zh "建模背景"

# prompt + image generation/editing in one command
python scripts/efg.py image "建模背景" --figure-template full-modeling-pipeline --lang zh --dry-run

# relay compatibility check without image generation
python scripts/efg.py provider-check --base-url https://relay.example/v1 --allow-third-party

# request -> normalized spec -> exact figure in one command
python scripts/efg.py plot request.json --spec-out output/spec.json --out-path output/figure --formats png pdf svg

# normalized spec -> exact figure
python scripts/efg.py render output/spec.json --out-path output/figure --formats png pdf svg

# offline runtime smoke check
python scripts/efg.py check
```

## Reproducibility contract

Conceptual example:

```text
Figure Brief → Final Prompt → Real GPT Output → Verification
```

Quantitative example:

```text
Plot Request → Normalized Plot Spec → Renderer → Real Output → Verification
```

For final paper workflows, add an editable handoff note where labels/formulas/composition may need a deterministic human-editable pass.

See [Reproducibility Chain](references/reproducibility-chain.md) and [Reproducible Examples](docs/examples/README.md).

## Validation

CI checks include:

- Python compilation
- `SKILL.md` package validation
- UTF-8 / common Chinese mojibake regressions
- engineering + mathematical-modeling prompt packs
- local Markdown links and image paths
- Figure Brief schema behavior
- Plot Request → normalized Plot Spec contracts
- completed showcase manifest/artifact resolution
- completed plot showcase Request/Spec schema validation
- image generation/edit request construction
- official endpoint defaults plus explicit trusted-relay opt-in
- malformed base URL and embedded-credential rejection
- final/high-resolution fail-closed model routing
- HTTP error, timeout, malformed-response, and empty-output failure paths
- real local plot rendering smoke tests
- pruned runtime token budget
- offline CLI smoke checks

## Repository map

| Path | Purpose |
|---|---|
| `SKILL.md` | Codex routing/workflow |
| `assets/prompt-templates/` | engineering + mathematical-modeling prompt packs |
| `references/` | mode, plotting, Chinese, modeling, relay, final-quality, reproducibility, handoff guidance |
| `scripts/efg.py` | unified user-facing CLI |
| `scripts/generate_image.py` | GPT Image-compatible official/relay fallback |
| `scripts/build_plot_spec.py` | concise request → normalized exact-plot spec |
| `scripts/plot_publication_figure.py` | multi-panel deterministic renderer |
| `scripts/sync_codex_skill.py` | pruned runtime sync |
| `scripts/check_setup.ps1` | Windows/Codex diagnostics |
| `scripts/wizard.ps1` | guided interactive setup/run flow |
| `schemas/` | Figure Brief, Plot Request, normalized Plot Spec contracts |
| `examples/` | reusable plot/brief inputs |
| `docs/examples/` | completed reproducible showcase evidence |
| `tests/` | offline unit, contract, safety, and E2E tests |

## Showcase status

**Exact Plot Mode now has real reproducible showcase evidence.** The remaining major showcase gap is **real GPT conceptual output**. Conceptual SVGs stay labeled as layout previews until actual GPT runs are committed with their brief, prompt, output, verification, and manifest.

## What it is not

- not a full paper-writing system
- not permission to fabricate missing numeric data
- not a replacement for checking generated labels and scientific fidelity
- not a guarantee that every third-party relay implements every OpenAI image parameter identically
- not a single image prompt that treats diagrams and exact plots as the same problem

## License

MIT.
