# Engineering Figure GPT

A Codex-native skill for publication-oriented research figures.

![Codex Skill](https://img.shields.io/badge/Codex-skill-111827)
![Modes](https://img.shields.io/badge/modes-image%20%7C%20plot%20%7C%20mixed-2563eb)
![Focus](https://img.shields.io/badge/focus-research%20figures-16a34a)

## Preview

| Mathematical modeling | Exact benchmark plot |
|---|---|
| ![Modeling framework](docs/showcase/model-framework.svg) | ![Benchmark plot](docs/showcase/benchmark-plot.svg) |

See the full [Showcase](docs/showcase.md).

## Three modes

- **Image mode:** architecture diagrams, workflows, graphical abstracts, modeling frameworks, redraws, and edits.
- **Plot mode:** exact quantitative charts rendered locally from supplied values.
- **Mixed mode:** exact local quantitative panels plus GPT-generated conceptual panels.

Core rule: exact values, axes, error bars, and benchmark geometry must remain exact and should not be redrawn by an image model.

## First-class scenarios

Computer science, AI, engineering, electronics, data science, mathematical modeling, and Chinese/bilingual academic figures.

## Included figure templates

`system-architecture` · `algorithm-workflow` · `graphical-abstract` · `mathematical-model-framework` · `data-analysis-pipeline` · `optimization-workflow` · `evaluation-framework` · `electronic-schematic`

## Quick start

Install to Codex:

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/.codex/skills/engineering-figure-gpt"
```

Build a figure prompt locally:

```bash
python scripts/efg.py prompt --figure-template mathematical-model-framework --lang en "Forecast demand, optimize allocation, validate robustness, and produce the final decision."
```

Render an exact quantitative example:

```bash
python scripts/efg.py plot examples/benchmark-plot-request.json --out-path output/benchmark
```

See [README.zh-CN.md](README.zh-CN.md) for the Chinese guide and [INSTALL.md](INSTALL.md) for installation details.
