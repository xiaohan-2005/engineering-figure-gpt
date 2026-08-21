# Edit Mode

Editing an existing research figure is a first-class workflow. Do not treat every edit request as a new generation request.

Use:

```bash
python scripts/efg.py edit <input-image> "<instruction>" --mode <mode>
```

The edit prompt is built by `scripts/build_image_edit_prompt.py` and then sent through the GPT Image edit path with an explicit preservation contract.

## GPT Image 2 model behavior

For `gpt-image-2`, **omit `input_fidelity`**. The model always processes image inputs at high fidelity and the API does not allow changing this parameter.

Canvas preservation is handled separately from semantic preservation:

- if the primary source width/height already satisfy GPT Image 2 output-size rules, use the exact source canvas by default;
- if the source aspect ratio is supported but the dimensions are not legal, derive the nearest legal size and emit an explicit warning;
- if the source cannot be mapped safely, fail or require an explicit legal `--size` instead of silently changing the canvas;
- an explicit `--size` always takes precedence.

GPT Image 2 concrete output sizes must satisfy all of these:

- each edge <= 3840 px;
- both edges are divisible by 16;
- long-edge / short-edge ratio <= 3:1;
- total pixels are between 655,360 and 8,294,400.

For other GPT Image models or relay-specific aliases, do not assume GPT Image 2-only parameters or flexible-size behavior. Use the provider/model's actual capability and make any canvas change explicit.

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

## Spatial edit masks

Use `--mask` when the requested change is localized and a spatial region can be supplied reliably:

```bash
python scripts/efg.py edit figure.png \
  "Fix only the mislabeled module" \
  --mode correct \
  --mask edit-mask.png \
  --preserve "all arrows and unaffected labels"
```

The portable edit path validates the mask before upload. It must:

- be smaller than 50 MB;
- match the primary input image dimensions exactly;
- use the same image format as the primary input image;
- contain an alpha channel.

The mask is attached as the dedicated `mask` multipart field while the primary figure remains the first `image[]` input. When `efg edit --mask` is used, the resolved prompt also adds a preservation rule for all content outside the masked region, except minimal blending needed at the boundary.

A mask is **strong spatial guidance, not a pixel-perfect guarantee**. Always compare the result against the source. Any unrelated change outside the intended region is still a failure in `correct` mode.

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

If both reference images and a mask are supplied, the mask applies to the primary edit image. Reference images may guide style or reconstruction but do not redefine the allowed scientific change region.

## Quality profile

Edit prompts receive the reusable image quality contract:

- `draft`
- `paper` (default)
- `final`

The quality profile controls prompt/rendering expectations. `--final` / `--highres` separately request the configured final model route and remain fail-closed if that model is not configured.

## Post-edit acceptance

After editing, compare the new image against the source.

For `correct`, any unrelated movement, label rewrite, arrow change, palette drift, geometry redesign, or change outside an intended mask region is a failure even if the requested correction is present.

Also verify that the returned raster matches the resolved output canvas. For all modes, run `references/visual-qa.md`; for objective raster constraints, run `efg verify-image`.
