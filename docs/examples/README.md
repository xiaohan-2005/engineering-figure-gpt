# Reproducible Examples

This directory is reserved for **real, reproducible outputs**.

Conceptual examples should use this structure:

```text
<slug>/
├── brief.md
├── prompt.txt
├── output.png
└── verification.md
```

Quantitative examples should use:

```text
<slug>/
├── plot-request.json
├── plot-spec.json
├── output.png
└── verification.md
```

Rules:

1. `output.png` must be the real output produced by the documented workflow.
2. Do not copy a manually drawn preview into this directory and label it as GPT output.
3. Preserve the actual final prompt or actual plot request/spec used for the run.
4. Verification notes should record label, arrow, formula, Chinese-text, value, axis, legend, and uncertainty checks as relevant.
5. API keys and other secrets must never be stored here.

The existing SVG files under `docs/showcase/` remain layout previews until they are replaced by real outputs that satisfy this contract.
