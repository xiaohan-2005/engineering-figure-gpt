# Reproducible Examples

This directory contains **real evidence-chain examples**. Conceptual GPT outputs and exact quantitative outputs are kept distinct so a manually drawn preview is never presented as model evidence.

## Current exact-plot examples

| Output | Brief | Source | Verification |
|---|---|---|---|
| [Benchmark SVG](benchmark-exact/output.svg) | [brief](benchmark-exact/brief.md) | [request](benchmark-exact/request.json) · [normalized spec](benchmark-exact/plot-spec.json) | [verification](benchmark-exact/verification.md) |
| [Sensitivity / robustness SVG](sensitivity-robustness/output.svg) | [brief](sensitivity-robustness/brief.md) | [request](sensitivity-robustness/request.json) · [normalized spec](sensitivity-robustness/plot-spec.json) | [verification](sensitivity-robustness/verification.md) |

Both current datasets are intentionally **synthetic/illustrative**. They demonstrate deterministic figure production and evidence preservation; they are not scientific claims.

The committed SVGs are deterministic vector snapshots of the preserved values. The canonical production regeneration path is still the repository's Plot Mode:

```bash
python scripts/efg.py plot docs/examples/<slug>/request.json \
  --spec-out docs/examples/<slug>/plot-spec.regenerated.json \
  --out-path docs/examples/<slug>/output-regenerated \
  --formats svg png pdf
```

Different Matplotlib versions may produce different SVG coordinates/metadata while preserving identical numeric semantics.

## Conceptual GPT example contract

A completed conceptual example must use:

```text
<slug>/
├── brief.md
├── prompt.txt
├── output.png          # real GPT output, not a layout mockup
├── verification.md
├── editable-handoff.md # when later editing is expected
└── manifest.json
```

Do not create the completed `manifest.json` until the real output artifact exists.

## Package a real output safely

After a real GPT run or exact render has produced its final file, use the repository packaging tool instead of manually copying evidence files:

```bash
python scripts/package_showcase_example.py \
  --slug rag-system-architecture \
  --mode image \
  --brief work/rag-brief.md \
  --source output/final-prompt.txt=prompt.txt \
  --output output/rag-figure.png \
  --verification work/rag-verification.md \
  --model gpt-image-2 \
  --quality high \
  --size 1536x1024 \
  --check "labels checked" \
  --check "arrow directions checked"
```

For an exact plot:

```bash
python scripts/package_showcase_example.py \
  --slug my-benchmark \
  --mode plot \
  --brief work/brief.md \
  --source output/request.json=request.json \
  --source output/spec.json=plot-spec.json \
  --output output/figure.svg \
  --verification work/verification.md \
  --check "source values preserved"
```

The packaging tool refuses to create a completed manifest when required evidence is missing, the output is empty, or PNG/JPEG/WebP/SVG/PDF file signatures do not match the declared extension. It also requires `prompt.txt` for image cases and both `request.json` + `plot-spec.json` for plot cases.

The packaging tool is repository maintenance tooling and is intentionally **not copied into the pruned Codex runtime**.

## Quantitative example contract

```text
<slug>/
├── brief.md
├── request.json
├── plot-spec.json
├── output.svg          # or PNG/PDF/SVG set
├── verification.md
└── manifest.json
```

## Rules

1. A conceptual `output.png` must be the real GPT output produced by the documented run.
2. Do not copy a manually drawn preview into this directory and label it as GPT output.
3. Preserve the actual final prompt or actual Plot Request/Spec used for the run.
4. Quantitative examples must disclose whether values are real research data or synthetic demonstration data.
5. Verification notes must record label, arrow, formula, Chinese-text, value, axis, legend, and uncertainty checks as relevant.
6. Exact numeric geometry must remain deterministic and must not be redrawn by the image model.
7. API keys, relay credentials, and other secrets must never be stored here.
8. Completed manifests must resolve to real non-empty artifacts and pass CI validation.

The older SVG files under `docs/showcase/` remain explicitly labeled layout previews. They should be removed from the main gallery only after real conceptual GPT outputs satisfy the contract above.
