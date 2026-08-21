# Publication Figure Design

Use these defaults for journal-style conceptual figures unless the user provides a different venue/style reference.

## Core visual style

- white or near-white background;
- minimalist, publication-oriented composition rather than poster/marketing art;
- clean panel/module structure;
- explicit reading order;
- short professional labels;
- restrained low-to-medium-saturation colors;
- no decorative 3D, cinematic lighting, glossy rendering, noisy textures, or poster gradients unless explicitly requested.

## Typography and label hierarchy

Aim for a clean sans-serif academic look similar to Helvetica/Arial-style typography.

Use a simple hierarchy:

1. panel letters/titles: strongest emphasis;
2. primary module labels: medium emphasis;
3. secondary notes: smallest emphasis.

Do not create a fourth layer of tiny pseudo-technical text merely to make the figure look detailed.

For raster conceptual figures:

- use large clean text regions;
- prefer fewer larger labels over many tiny labels;
- keep text centered or deliberately aligned within containers;
- preserve strong text/background contrast;
- avoid long paragraphs inside the image;
- enlarge modules before shrinking essential label text.

A paper-profile figure should remain understandable and its essential labels should remain readable at approximately 50% native scale or at intended single-column paper width.

## Layout logic

- choose one primary left-to-right or top-to-bottom narrative;
- keep the main pathway visually dominant;
- keep side branches secondary;
- group related modules consistently;
- use repeated alignment and regular spacing;
- keep a safe outer margin on all sides;
- do not allow text, arrowheads, or modules to touch/cross the canvas edge;
- avoid accidental overlaps and unnecessary line crossings;
- prefer balanced multi-panel composition over one overcrowded canvas when information density is high.

## Arrows and borders

- arrows must have technical meaning rather than decorative purpose;
- keep line weights visually consistent;
- use crisp arrowheads;
- avoid arrows crossing text;
- avoid ambiguous endpoints between two modules;
- make loopbacks clearly distinct from forward flow;
- keep repeated borders/shapes consistent.

## Semantic palette

Use color semantically, not decoratively.

Recommended meaning when the user has not supplied a palette:

- blue: primary method, key pathway, or central mechanism;
- green: validated output, favorable state, or successful result;
- red/warm accent: baseline, failure route, bottleneck, risk, or contrast;
- gray: infrastructure, context, non-focal modules;
- at most one additional accent for a targeted highlight.

Keep the same semantic meaning for the same color across the figure.

Prefer low-to-medium saturation and light fills behind dark text.

## Mathematical-modeling figures

Show the reasoning chain only when supported by the source:

```text
problem/data
-> assumptions
-> preprocessing
-> model construction
-> estimation/forecast/optimization
-> validation
-> sensitivity/robustness
-> decision/output
```

Preserve supplied symbols, variables, units, constraints, and model names. If a formula must remain exact, reserve an editable placeholder or compose it deterministically instead of asking the image model to typeset it from memory.

## Exact quantitative figures

Exact plots must preserve supplied scales, values, uncertainty, and geometry. Do not change numbers to improve appearance and do not ask the image model to redraw exact plots.

## Final readability rule

Do not accept an image merely because it looks attractive at full screen.

Before final use:

- inspect at native scale;
- inspect at approximately 50% scale/intended paper width;
- confirm essential labels remain readable;
- confirm module hierarchy and arrows remain obvious;
- confirm there is no clipping, blur, ghosting, micro-text, or accidental overlap.

Use `references/image-quality-contract.md` and `references/visual-qa.md` for acceptance gates.
