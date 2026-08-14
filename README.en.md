# Engineering Figure GPT

[![Skill CI](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml/badge.svg)](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml)

A Codex-native research-figure skill for engineering, computer science, AI, data science, electronics, and mathematical modeling.

Engineering Figure GPT separates **conceptual composition** from **numeric truth**:

- `image` mode uses GPT image generation for conceptual/schematic content;
- `plot` mode renders exact quantitative figures locally;
- `mixed` mode keeps quantitative panels local and uses GPT only for conceptual panels.

Core rule: **never let image generation silently rewrite scientific data, axes, uncertainty, formulas, or benchmark geometry.**

[中文说明](README.zh-CN.md) · [Installation](INSTALL.md) · [Showcase](docs/showcase.md)

## One-command image workflow

Inside Codex, prefer the built-in GPT image capability. For portable/reproducible execution, the repository includes a GPT Image-compatible CLI that defaults to `gpt-image-2` and official OpenAI.

A figure template and scientific background can now be resolved and generated in one command:

```bash
python scripts/efg.py image \
  "A retrieval system with OCR, embeddings, reranking, and answer synthesis" \
  --figure-template system-architecture \
  --lang en \
  --save-prompt output/final-prompt.txt \
  --dry-run
```

Remove `--dry-run` only when a live request is intended.

## OpenAI-compatible relay support

A custom relay/base URL is supported only after explicit trust:

```bash
python scripts/efg.py image \
  "technical background" \
  --figure-template system-architecture \
  --base-url https://relay.example/v1 \
  --allow-third-party
```

Equivalent environment variables:

```text
OPENAI_BASE_URL=https://relay.example/v1
OPENAI_ALLOW_THIRD_PARTY=1
OPENAI_IMAGE_MODEL=gpt-image-2
```

The explicit trust gate exists because the relay may receive the configured API key and any images used in edit requests.

### Relay compatibility probe

Before spending image credits, probe the configured endpoint without generating an image:

```bash
python scripts/efg.py provider-check \
  --base-url https://relay.example/v1 \
  --allow-third-party
```

The probe checks basic model/route exposure for `/models`, `/images/generations`, and `/images/edits`. It cannot guarantee that every relay implements every OpenAI Images parameter identically.

## Final / high-resolution routing

Routine image generation uses `OPENAI_IMAGE_MODEL` and otherwise defaults to `gpt-image-2`.

Final-quality intent uses `OPENAI_IMAGE_HIGHRES_MODEL` or an explicit `--model`:

```bash
python scripts/efg.py image \
  "technical background" \
  --figure-template graphical-abstract \
  --final
```

If final/high-resolution output is requested but no final-quality model is configured, the CLI **fails closed**. It does not silently switch provider, reduce quality/size, or downgrade to the routine model.

See [Final / High-Resolution Policy](references/highres-policy.md).

## Exact plotting: request → spec → figure in one command

Natural language is the user-facing interface; JSON is an internal contract.

The internal chain is:

```text
concise Plot Request (`kind`)
        ↓
  build_plot_spec.py
        ↓
normalized Plot Spec (`type`)
        ↓
plot_publication_figure.py
```

The user-facing command now runs the full chain:

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

## Mathematical modeling is now a dedicated domain pack

The repository ships two prompt packs:

```text
assets/prompt-templates/engineering-figure-templates.json
assets/prompt-templates/mathematical-modeling-templates.json
```

The modeling pack includes dedicated templates for:

- problem analysis
- Q1/Q2/Q3 dependencies
- preprocessing
- forecasting
- classification
- clustering
- optimization formulation
- multi-objective / Pareto workflows
- spatial modeling
- network modeling
- evaluation systems
- sensitivity analysis
- robustness analysis
- decision frameworks
- end-to-end modeling pipelines

List every available template:

```bash
python scripts/build_engineering_figure_prompt.py --list-templates
```

Exact forecast curves, Pareto fronts, sensitivity indices, robustness curves, confusion matrices, and benchmark values remain local/deterministic.

See [Mathematical Modeling Guidance](references/mathematical-modeling.md).

## Editable handoff

Generated conceptual figures often need a final human-editable pass for labels, formulas, arrows, and journal layout.

The recommended conceptual handoff preserves:

```text
brief.md
prompt.txt
output.png
verification.md
editable-handoff.md
```

Exact plots should additionally preserve the request, normalized spec, and vector exports such as SVG/PDF.

See [Editable Figure Handoff](references/editable-figure-handoff.md).

## Quick start

### Install into Codex on Windows

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

The installer synchronizes a pruned runtime package to:

```text
~/.codex/skills/engineering-figure-gpt
```

Repository-only docs, tests, examples, and CI files are not copied into the runtime package.

Diagnostics:

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/check_setup.ps1"
```

Interactive wizard:

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/wizard.ps1"
```

The wizard supports template selection, official OpenAI or a trusted relay, provider compatibility checks, final-quality routing, and one-command exact plotting.

## Unified CLI

```bash
# prompt only
python scripts/efg.py prompt --figure-template problem-analysis --lang en "modeling background"

# template -> final prompt -> image generation/editing
python scripts/efg.py image "modeling background" --figure-template full-modeling-pipeline --lang en --dry-run

# relay compatibility check without image generation
python scripts/efg.py provider-check --base-url https://relay.example/v1 --allow-third-party

# request -> normalized spec -> exact figure
python scripts/efg.py plot request.json --spec-out output/spec.json --out-path output/figure --formats png pdf svg

# normalized spec -> exact figure
python scripts/efg.py render output/spec.json --out-path output/figure --formats png pdf svg

# offline runtime check
python scripts/efg.py check
```

## Reproducibility

Conceptual evidence chain:

```text
Figure Brief → Final Prompt → Real GPT Output → Verification
```

Quantitative evidence chain:

```text
Plot Request → Normalized Plot Spec → Renderer → Real Output → Verification
```

For final paper workflows, keep an editable handoff note where deterministic typography/composition still needs a final pass.

See [Reproducibility Chain](references/reproducibility-chain.md) and [Reproducible Examples](docs/examples/README.md).

## Validation and CI

The CI validates more than Python syntax:

- Python compilation
- Skill metadata/runtime structure
- UTF-8 and common mojibake patterns
- engineering + mathematical-modeling prompt packs
- local documentation links/images
- Figure Brief / Plot Request / Plot Spec contracts
- GPT image generation/edit request construction
- official endpoint defaults and explicit relay trust
- malformed URLs and embedded-credential rejection
- final/high-resolution fail-closed routing
- HTTP/network/timeout/malformed-response/empty-output behavior
- local plot E2E rendering
- pruned Codex runtime package
- runtime token budget
- offline CLI smoke checks

## Showcase status

The current conceptual SVGs in [docs/showcase.md](docs/showcase.md) remain explicitly labeled as **layout previews**. They are not presented as fake GPT outputs.

The remaining major product gap is a real reproducible showcase with:

```text
brief + final prompt + real GPT output + verification
```

and deterministic quantitative examples generated from their preserved Plot Request/Spec.

## Design principles

1. Scientific fidelity before decoration.
2. Numeric truth stays local and deterministic.
3. Natural language is the user-facing interface; JSON is an internal contract.
4. GPT is used where semantic composition helps.
5. Chinese academic figures and mathematical modeling are primary use cases.
6. Third-party relay usage must be explicit, never silent.
7. Final-quality requests must not silently downgrade.
8. Runtime context stays pruned and auditable.
9. Outputs should remain reproducible and editable whenever practical.

## License

See [LICENSE](LICENSE).
