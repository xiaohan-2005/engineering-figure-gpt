# Final / High-Resolution Policy

Use this reference when the user explicitly asks for final export, high resolution, 2K/4K-like output, or another concrete raster-quality target.

## Model tier, rendering quality, and raster size are separate

Do not equate a high-resolution model route with a guaranteed pixel size.

Routine conceptual generation uses:

```text
OPENAI_IMAGE_MODEL
```

and otherwise defaults to `gpt-image-2`.

Final/high-resolution model routing uses:

```text
OPENAI_IMAGE_HIGHRES_MODEL
```

or an explicit image `--model` supplied by the user.

Rendering quality is controlled separately with `--quality`, and the requested provider canvas is controlled separately with:

```text
--size WIDTHxHEIGHT
```

The returned raster must be checked when an exact pixel target matters.

## Quality profiles

When the unified `efg image` path is used and no runtime override/environment value is supplied:

- `draft` → `quality=low`, `size=1024x1024`;
- `paper` → `quality=high`, `size=1536x1024`;
- `final` quality profile → `quality=high`, `size=2048x1152`.

The `final` quality profile does **not** by itself force a different model. Use `--final` / `--highres` when a separate final model route is intended.

## GPT Image 2 concrete size rules

`gpt-image-2` accepts flexible concrete resolutions when all constraints are satisfied:

- maximum edge length <= 3840 px;
- both edges are multiples of 16 px;
- long-edge / short-edge ratio <= 3:1;
- total pixels are at least 655,360 and at most 8,294,400.

Common valid examples include:

```text
1024x1024
1536x1024
2048x2048
2048x1152
3840x2160
2160x3840
```

Do not apply these GPT Image 2-specific assumptions to older image models or relay-specific aliases unless that provider documents equivalent behavior.

## Triggering final-model routing

Treat these as final-model intent:

- `--highres`
- `--final`
- prompt text containing high-resolution/final-export phrases such as `2K`, `high resolution`, `final export`, `final quality`, `高分辨率`, or `最终导出`.

The final route should also use the `final` image quality contract unless the user explicitly selects another profile.

## Fail-closed rule

If final-model output is requested but no explicit model and no `OPENAI_IMAGE_HIGHRES_MODEL` are configured, stop immediately.

Do **not** silently:

- fall back to the routine model;
- lower image quality;
- shrink the requested size;
- switch providers or relay hosts;
- alter the requested figure type;
- claim that a smaller raster is equivalent to a requested 2K/4K target.

The user must explicitly choose a final-quality model or explicitly retry without final-model intent.

## Exact pixel targets

If the user explicitly requests a concrete pixel dimension:

1. validate it against the selected model/provider's real constraints;
2. request that size explicitly;
3. verify the returned raster dimensions;
4. fail/report the mismatch if the provider returns a different size.

Example objective verification:

```bash
python scripts/efg.py verify-image output/figure.png \
  --expected-size 2048x1152 \
  --require-format png
```

A provider route that only returns a smaller native canvas cannot be called 2K/4K simply because the model name contains `final`, `pro`, or `highres`.

## Edit canvas preservation

For GPT Image 2 edits, the source canvas and final-model routing are independent.

If `--size` is omitted:

- preserve the exact source dimensions when they are legal GPT Image 2 output dimensions;
- otherwise choose the nearest legal canvas while keeping the aspect ratio as close as possible and emit a warning;
- never silently convert a localized correction to an unrelated default aspect ratio.

For a `correct` edit on a non-GPT-Image-2 model, prefer an explicit supported `--size` if exact canvas preservation matters.

## Visual clarity still requires inspection

Pixel dimensions do not prove readability. After metadata verification, inspect the image using `references/visual-qa.md`.

Final output should have:

- readable essential labels at intended paper width;
- no micro-text used to simulate detail;
- sharp text regions and module boundaries;
- clear arrowheads and consistent line weights;
- no clipping, ghosting, or visible blur;
- stable scientific content.

## Trusted relay example

A relay may expose provider-specific image model names while following an OpenAI Images-compatible shape:

```powershell
$env:OPENAI_BASE_URL = "https://relay.example/v1"
$env:OPENAI_ALLOW_THIRD_PARTY = "1"
$env:OPENAI_IMAGE_MODEL = "gpt-image-2"
$env:OPENAI_IMAGE_HIGHRES_MODEL = "<provider-final-image-model>"
```

Never invent a model alias that the relay does not expose.

Before spending credits, use:

```bash
python scripts/efg.py provider-check
```

A provider check can confirm route/model exposure but cannot guarantee every size/quality/edit parameter behaves identically. Verify the returned artifact when the output contract matters.
