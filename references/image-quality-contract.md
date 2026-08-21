# Image Quality Contract

Use this reference for every conceptual research figure. The domain template decides **what** to show; this contract decides **how clearly and robustly it must render**.

## Profiles

The prompt builder injects one of three reusable contracts from:

```text
assets/prompt-templates/image-quality-contracts.json
```

- `draft`: fast structural exploration; still forbids clipping, unreadable labels, and obvious overlap.
- `paper`: default. Designed for paper-ready conceptual figures and single-column readability.
- `final`: strongest rendering constraints for final export; use with an explicit final/high-resolution model route when appropriate.

`--final` and `--highres` should use the `final` prompt contract unless the user explicitly selects another profile.

## Non-negotiable visual constraints

For `paper` and `final` output:

- use a white or near-white background unless the user asks otherwise;
- keep one explicit reading direction;
- maintain a safe outer margin so labels, arrowheads, and modules never touch the canvas edge;
- keep all important modules fully inside the canvas;
- prefer fewer larger labels over many tiny annotations;
- use large clean text regions and strong text/background contrast;
- keep titles/panel labels visually strongest, primary module labels next, and secondary notes smallest;
- keep repeated modules aligned and spacing systematic;
- use crisp, uniform arrows and borders;
- keep arrowheads obvious and prevent arrows from crossing text;
- use restrained scientific colors with stable semantic meaning;
- avoid decorative pseudo-technical microtext, noisy textures, glossy 3D, cinematic lighting, poster gradients, blur, and ghosting unless explicitly requested.

## Readability acceptance rule

A paper-profile conceptual figure is not complete merely because the API returned an image.

Before final handoff, visually inspect the figure at approximately 50% of native size or at the intended paper width. Essential labels, module hierarchy, reading order, and arrow meaning must remain clear. If they do not, reduce density, enlarge labels/modules, or regenerate/edit the figure.

Do not solve unreadable density by shrinking font-like text further.

## Pixel-size and format contract

Model tier and raster dimensions are separate concerns.

- `--final` / `--highres` selects the configured final-quality model route.
- `--size` controls the requested provider canvas.
- `efg verify-image` checks the actual returned raster dimensions, format, megapixels, and aspect ratio.

Never claim that a result is 2K/4K/final-size merely because a high-resolution model name was used. If the user gives an explicit pixel target and the provider cannot produce or return it, report that limitation instead of silently treating a smaller raster as equivalent.

Example:

```bash
python scripts/efg.py verify-image output/figure-1.png \
  --expected-size 1536x1024 \
  --require-format png
```

For a minimum-size acceptance gate:

```bash
python scripts/efg.py verify-image output/figure-1.png \
  --min-width 1500 \
  --min-height 1000 \
  --min-megapixels 1.5
```

## What metadata verification cannot prove

Pixel dimensions alone do not prove that the image is visually sharp or scientifically correct. After metadata verification, visually check:

- text clarity;
- malformed or hallucinated labels;
- clipped labels/modules;
- overlaps;
- wrong/missing arrows;
- inconsistent colors;
- unreadable micro-text;
- blur/ghosting;
- scientific fidelity.

Use `references/visual-qa.md` for the full acceptance checklist.
