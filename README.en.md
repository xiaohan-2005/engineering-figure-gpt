# Engineering Figure GPT

[![Skill CI](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml/badge.svg)](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml)

A Codex-native research-figure skill for engineering, computer science, AI, data science, electronics, and mathematical modeling.

Engineering Figure GPT separates **conceptual composition** from **numeric truth**:

- `image` mode uses Codex built-in GPT image generation when available, with a GPT Image-compatible CLI fallback for reproducibility.
- `plot` mode renders exact quantitative figures locally from structured data.
- `mixed` mode keeps quantitative panels local and uses GPT only for conceptual panels.

The project is designed around one principle: **never let image generation silently rewrite scientific data, axes, formulas, or benchmark geometry.**

[中文说明](README.zh-CN.md) · [Installation](INSTALL.md) · [Showcase](docs/showcase.md)

## Why this skill exists

General-purpose image generation can make attractive diagrams, but research figures have stricter requirements. A useful paper figure must preserve terminology, reading order, module relationships, formulas, values, uncertainty, and publication readability.

This skill therefore uses a figure-production workflow rather than a single prompt:

```text
paper / method / data / reference
              ↓
         Figure Brief
              ↓
     image / plot / mixed
        ↓       ↓       ↓
     GPT     local    hybrid
    image     plot    workflow
        \       |       /
         verification
              ↓
      publication figure
```

## Core capabilities

### Image mode

Use for conceptual or schematic figures:

- system architecture
- algorithm workflow
- graphical abstract
- mathematical-model framework
- data-analysis pipeline
- optimization workflow
- evaluation framework
- electronics schematic
- redraws and image edits

Inside Codex, the preferred path is the installed built-in image-generation capability. For portable/reproducible execution, `scripts/generate_image.py` defaults to `gpt-image-2` and official OpenAI, while also supporting explicitly trusted OpenAI-compatible relay/base URLs.

A third-party relay must be explicitly enabled because it receives the API key and, for edit requests, the uploaded images:

```bash
OPENAI_BASE_URL=https://relay.example/v1 \
OPENAI_ALLOW_THIRD_PARTY=1 \
python scripts/generate_image.py "publication-quality system architecture"
```

or:

```bash
python scripts/generate_image.py "publication-quality system architecture" \
  --base-url https://relay.example/v1 \
  --allow-third-party
```

Official OpenAI does not require the third-party opt-in.

### Plot mode

Use when exact values, axes, scales, uncertainty, or benchmark geometry matter.

Supported panel intents include:

- grouped bar charts
- error bars and value annotations
- trend curves
- uncertainty shadows
- heatmaps
- scatter plots
- legend-only panels
- deliberate empty panels
- multi-panel layouts

Supported export formats include PNG, PDF, SVG, EPS, JPEG, and TIFF where supported by Matplotlib.

### Mixed mode

Use when one figure combines conceptual and quantitative content. Render the exact quantitative panels locally first; do not ask an image model to redraw them.

## Natural-language plotting

Natural language is the user interface. JSON is an internal execution format.

A request such as:

> Compare three methods using AUC and F1, show error bars, annotate exact values, and place the legend outside the panel.

should be converted into a concise plot request, normalized with `build_plot_spec.py`, and rendered locally.

```bash
python scripts/build_plot_spec.py request.json --out spec.json
python scripts/plot_publication_figure.py spec.json --out-path output/figure --formats png pdf svg
```

See [Natural-language Plot Workflow](references/natural-language-plot-workflow.md).

## Mathematical-modeling focus

The skill treats mathematical modeling as a first-class use case rather than a side category. Typical targets include:

- problem-analysis diagrams
- overall model frameworks
- Q1/Q2/Q3 dependency structures
- preprocessing pipelines
- prediction workflows
- optimization and Pareto workflows
- sensitivity-analysis layouts
- robustness-analysis layouts
- decision frameworks

For Chinese modeling papers, the workflow also checks label length, encoding, font fallback, formula fidelity, and mixed Chinese/English terminology.

See [Mathematical Modeling Guidance](references/mathematical-modeling.md) and [Chinese Labels](references/chinese-labels.md).

## Quick start

### Install into Codex on Windows

Clone the repository anywhere, then run:

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

The installer synchronizes a pruned runtime package to:

```text
~/.codex/skills/engineering-figure-gpt
```

Repository-only files such as tests, docs, and GitHub workflow files are not copied into the runtime package.

### Unified CLI

```bash
python scripts/efg.py prompt --figure-template mathematical-model-framework --lang en "technical background"
python scripts/efg.py image "publication-quality system architecture" --dry-run
python scripts/efg.py build-plot request.json --out spec.json
python scripts/efg.py plot spec.json --out-path output/figure --formats png pdf svg
python scripts/efg.py check
```

## GPT image fallback

Official OpenAI generation:

```bash
python scripts/generate_image.py "Create a publication-quality architecture figure ..." \
  --quality high \
  --size 1536x1024
```

Trusted relay generation:

```bash
python scripts/generate_image.py "Create a publication-quality architecture figure ..." \
  --base-url https://relay.example/v1 \
  --allow-third-party
```

Equivalent environment variables:

```text
OPENAI_BASE_URL=https://relay.example/v1
OPENAI_ALLOW_THIRD_PARTY=1
```

Editing:

```bash
python scripts/generate_image.py "Preserve structure and improve hierarchy" \
  --input-image input.png \
  --input-fidelity high
```

The CLI accepts `OPENAI_API_KEY`, `OPENAI_API_KEY_FILE`, or the local default key file at `~/.codex/secrets/openai_api_key.txt`. Never commit a real key to the repository, and only enable a third-party relay that you trust with the key and any image inputs.

## Figure Brief

A Figure Brief is the contract between scientific intent and figure production. It captures:

- figure goal
- paper claim
- figure type
- mode
- panel plan
- must-keep labels
- data/evidence
- style constraints
- output formats
- verification checklist

The schema is available at [schemas/figure-brief.schema.json](schemas/figure-brief.schema.json), with guidance in [references/figure-brief-spec.md](references/figure-brief-spec.md).

## Reproducibility

Whenever possible, preserve the chain:

```text
Figure Brief
    ↓
Prompt / Plot Request
    ↓
Rendered Output
```

For exact plots, supplied numeric values must remain unchanged. For conceptual figures, generated labels and relationships must be reviewed before paper use.

## Validation and CI

The GitHub Actions workflow validates more than Python syntax. It currently checks:

- Python compilation
- Skill metadata/package structure
- UTF-8 and common mojibake patterns
- Chinese prompt-template integrity
- local documentation links and images
- strict Figure Brief / Plot Request / Plot Spec contracts
- GPT Image generation/edit request construction
- official endpoint defaults and explicit third-party relay opt-in
- malformed URLs, invalid models, network failures, timeouts, malformed responses, and empty outputs
- unit and E2E tests
- pruned Codex runtime package
- runtime token budget
- offline CLI smoke checks

The runtime package is intentionally kept much smaller than the full GitHub repository.

## Repository layout

```text
engineering-figure-gpt/
├── SKILL.md
├── agents/
├── assets/prompt-templates/
├── references/
├── schemas/
├── scripts/
├── templates/
├── examples/
├── docs/
├── tests/
└── .github/workflows/
```

## Showcase status

The current conceptual SVGs in [docs/showcase.md](docs/showcase.md) are explicitly labeled as **layout previews**. They are not presented as fake GPT outputs.

The next showcase milestone is to replace them with real reproducible examples using the complete chain:

```text
brief + final prompt + real GPT output
```

while keeping exact quantitative examples generated by the local plot renderer.

## Design principles

1. Scientific fidelity before decoration.
2. Numeric truth stays local and deterministic.
3. Natural language is the user-facing interface.
4. GPT is used where semantic composition helps.
5. Chinese academic figures are treated as a primary use case.
6. Runtime context stays pruned and auditable.
7. Third-party relay usage must be explicit, never silent.
8. Outputs should remain reproducible whenever possible.

## License

See [LICENSE](LICENSE).
