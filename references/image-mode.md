# Image Mode

Use image mode for conceptual research figures rather than exact numeric charts.

Recommended targets:

- system architecture
- algorithm workflow
- graphical abstract
- mathematical-model framework
- mechanism or process diagram
- reference-inspired redraw
- image correction/revision/restyling

## Preferred execution path

Inside Codex, use the installed GPT image-generation/editing capability when it can satisfy the task and preserve the required inputs. For reproducible command-line execution, use the bundled GPT Image-compatible CLI.

The portable path reuses the active Codex/CC Switch provider when available. Resolution order is:

```text
explicit CLI override
    -> active Codex/CC Switch provider
    -> legacy OPENAI_* settings
    -> official OpenAI default
```

A custom URL supplied independently through `--base-url` or `OPENAI_BASE_URL` requires explicit third-party trust. An already selected non-OpenAI Codex provider is treated as user-selected.

## Generation workflow

1. Extract scientific entities, relationships, labels, and reading order.
2. Select the closest domain template.
3. Build the prompt with the reusable image quality contract.
4. Preserve source-grounded terminology and relationships.
5. Generate through GPT Image.
6. Inspect labels, arrows, hierarchy, symbols, clipping, overlaps, and accidental invented content.
7. Verify objective raster constraints when pixel/format/aspect requirements exist.
8. Correct localized problems with edit mode instead of blindly regenerating the whole figure.

The prompt builder injects:

```text
assets/prompt-templates/image-quality-contracts.json
```

Use `paper` by default and `final` for final-export intent.

Example:

```bash
python scripts/efg.py image \
  "A retrieval system with OCR, embedding, reranking, and answer synthesis" \
  --figure-template system-architecture \
  --quality-profile paper \
  --save-prompt output/final-prompt.txt \
  --dry-run
```

## Editing workflow

Do not treat every edit as a new generation.

Use:

```bash
python scripts/efg.py edit figure.png \
  "Fix the misspelled label only" \
  --mode correct
```

Modes:

- `correct`: smallest possible localized correction;
- `revise`: requested content/structural revision while preserving unaffected content;
- `restyle`: visual-style change with scientific content locked;
- `redraw`: clean reconstruction with scientific meaning and canonical labels preserved.

See `references/edit-mode.md` for preservation rules.

## Final/high-resolution intent

High-resolution routing and actual raster size are separate.

- `--final` / `--highres`: select the configured final-quality model route and fail closed if unavailable;
- `--size`: request the provider canvas;
- `efg verify-image`: verify what dimensions/format/aspect the provider actually returned.

Do not claim 2K/4K/final-size quality merely because a high-resolution model was selected.

## Visual acceptance

Before paper use, inspect every final conceptual image at native size and approximately 50% size. Essential labels and the main scientific story must remain clear.

Reject or correct:

- unreadable micro-text;
- malformed Chinese or hallucinated labels;
- clipped modules/labels;
- ambiguous arrows;
- accidental overlaps;
- blur/ghosting;
- inconsistent semantic colors;
- unsupported scientific detail.

Use `references/image-quality-contract.md` and `references/visual-qa.md`.

Do not ask image generation to reproduce exact benchmark geometry, long formulas, exact measured values, axes, or error bars. Keep those deterministic or editable.
