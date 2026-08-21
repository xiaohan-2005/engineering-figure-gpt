# Edit Mode

Editing an existing research figure is a first-class workflow. Do not treat every edit request as a new generation request.

Use:

```bash
python scripts/efg.py edit <input-image> "<instruction>" --mode <mode>
```

The edit prompt is built by `scripts/build_image_edit_prompt.py` and then sent through the normal GPT Image edit path with `input_fidelity=high` by default.

## Four edit modes

### `correct`

Use for typo fixes, one wrong arrow, one missing label, a small alignment problem, or another localized defect.

Default rule: **smallest possible change**.

Preserve unless explicitly allowed to change:

- canvas and aspect ratio;
- layout and module positions;
- arrows and scientific relationships;
- palette and typography;
- icon/shape language;
- every unaffected label.

Example:

```bash
python scripts/efg.py edit figure.png \
  "Change the label Encoder to Cross-Attention Encoder; change nothing else" \
  --mode correct \
  --preserve "all arrow endpoints" \
  --save-prompt output/edit-prompt.txt
```

### `revise`

Use when the requested scientific/structural content genuinely changes, for example adding one module, replacing one stage, or updating a local relationship.

Keep unaffected content stable and do not redesign the whole figure.

### `restyle`

Use when content should remain scientifically identical but the visual treatment changes, for example journal palette, typography, border style, or overall visual language.

Do not add/remove scientific modules, values, formulas, or claims.

### `redraw`

Use when a reference figure should be reconstructed more cleanly. Layout may improve, but scientific meaning, canonical labels, and supported relationships remain authoritative.

## Explicit preservation controls

Repeat `--preserve` for anything that must stay fixed:

```bash
--preserve "module positions"
--preserve "all labels except the requested one"
--preserve "blue/gray palette"
--preserve "Q1 -> Q2 dependency arrow"
```

Repeat `--allow-change` to define the permitted change set:

```bash
--allow-change "the preprocessing block width"
--allow-change "palette only"
```

The smaller and clearer the allowed change set, the less likely a localized edit becomes a full redraw.

## Multiple reference images

Use `--reference-image` for extra visual references:

```bash
python scripts/efg.py edit current.png \
  "Keep the structure, but adopt the typography and palette of the style reference" \
  --mode restyle \
  --reference-image style-reference.png
```

The primary input remains the scientific/content baseline. Additional references must not silently override scientific content.

## Quality profile

Edit prompts also receive the reusable image quality contract:

- `draft`
- `paper` (default)
- `final`

`--final` / `--highres` should use the final-quality contract and final model route unless explicitly overridden.

## Post-edit acceptance

After editing, compare the new image against the source.

For `correct`, any unrelated movement, label rewrite, arrow change, palette drift, or geometry redesign is a failure even if the requested correction is present.

For all modes, run the visual QA checklist in `references/visual-qa.md`. For objective raster-size requirements, run `efg verify-image`.
