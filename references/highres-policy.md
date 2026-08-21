# Final / High-Resolution Policy

Use this reference when the user explicitly asks for final export, high resolution, 2K/4K-like output, or another concrete raster-quality target.

## Model tier and raster size are separate

Do not equate a high-resolution model route with a guaranteed pixel size.

Routine conceptual generation uses:

```text
OPENAI_IMAGE_MODEL
```

and otherwise defaults to `gpt-image-2`.

Final/high-resolution intent uses:

```text
OPENAI_IMAGE_HIGHRES_MODEL
```

or an explicit image `--model` supplied by the user.

The requested provider canvas is controlled separately with:

```text
--size WIDTHxHEIGHT
```

The returned raster must be checked when an exact pixel target matters.

## Triggering final-quality routing

Treat these as final-quality intent:

- `--highres`
- `--final`
- prompt text containing high-resolution/final-export phrases such as `2K`, `high resolution`, `final export`, `final quality`, `高分辨率`, or `最终导出`.

The final route should also use the `final` image quality contract unless the user explicitly selects another profile.

## Fail-closed rule

If final-quality output is requested but no explicit model and no `OPENAI_IMAGE_HIGHRES_MODEL` are configured, stop immediately.

Do **not** silently:

- fall back to the routine model;
- lower image quality;
- shrink the requested size;
- switch providers or relay hosts;
- alter the requested figure type;
- claim that a smaller raster is equivalent to a requested 2K/4K target.

The user must explicitly choose a final-quality model or explicitly retry without final-quality intent.

## Exact pixel targets

Provider/model support for raster sizes varies. Do not invent a supported size.

If the user explicitly requests a concrete pixel dimension or a provider-specific 2K/4K mode:

1. use an actual size/model option supported by that provider, if known;
2. request that size explicitly;
3. verify the returned raster dimensions;
4. fail/report the mismatch if the provider returns a different size.

Example objective verification:

```bash
python scripts/efg.py verify-image output/figure.png \
  --expected-size 1536x1024 \
  --require-format png
```

A provider route that only returns a smaller native canvas cannot be called 2K/4K simply because the model name contains words such as `final`, `pro`, or `highres`.

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

A provider check can confirm route/model exposure but cannot guarantee that every size/quality/edit parameter is implemented correctly. Verify the returned artifact when the output contract matters.
