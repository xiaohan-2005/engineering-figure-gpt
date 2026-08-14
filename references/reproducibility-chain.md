# Reproducibility Chain

A mature research-figure example should preserve enough evidence for another user to understand and reproduce how the figure was made.

## Conceptual figure

Keep these three artifacts together:

```text
Figure Brief
    ↓
Final Prompt
    ↓
Real GPT Output
```

Recommended gallery files:

```text
docs/examples/<slug>/brief.md
docs/examples/<slug>/prompt.txt
docs/examples/<slug>/output.png
```

The brief should record the scientific goal, claim, panel/module structure, must-keep terminology, language, style constraints, and verification checklist.

The final prompt should be the actual prompt used for the run, not a cleaned-up prompt written afterward.

The output must be the actual generated image. Do not label a manually drawn preview as a model output.

## Quantitative figure

Keep:

```text
Plot Request
    ↓
Normalized Plot Spec
    ↓
Renderer
    ↓
Real Output
```

Recommended gallery files:

```text
docs/examples/<slug>/plot-request.json
docs/examples/<slug>/plot-spec.json
docs/examples/<slug>/output.png
```

Exact values must remain unchanged from the request/spec to the rendered figure.

## Verification note

For publication-facing examples, add a short `verification.md` that records checks such as:

- labels match the source terminology;
- arrows and reading order are correct;
- no unsupported modules or claims were introduced;
- formulas and symbols are source-faithful;
- Chinese labels do not show mojibake or clipping;
- plot values, axes, legends, and uncertainty match the supplied data.
