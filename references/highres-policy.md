# Final / High-Resolution Policy

Use this reference when the user explicitly asks for a final export, high-resolution figure, 2K-quality output, or another final-quality path.

## Routine versus final-quality generation

Routine conceptual generation uses:

```text
OPENAI_IMAGE_MODEL
```

and falls back to `gpt-image-2` when no routine model is configured.

Final/high-resolution generation uses:

```text
OPENAI_IMAGE_HIGHRES_MODEL
```

or an explicit `--model` supplied by the user.

## Triggering final-quality routing

The CLI treats the following as final-quality intent:

- `--highres`
- `--final`
- prompt text containing common high-resolution/final-export phrases such as `2K`, `high resolution`, `final export`, `final quality`, `高分辨率`, or `最终导出`

## Fail-closed rule

If final-quality output is requested but no explicit model and no `OPENAI_IMAGE_HIGHRES_MODEL` are configured, stop immediately.

Do **not** silently:

- fall back to the routine model;
- lower image quality;
- shrink the requested size;
- switch providers or relay hosts;
- alter the requested figure type.

The user must explicitly choose a final-quality model or explicitly retry without final-quality intent.

## Trusted relay example

A relay may expose a provider-specific final model name while still following the OpenAI Images API shape:

```powershell
$env:OPENAI_BASE_URL = "https://relay.example/v1"
$env:OPENAI_ALLOW_THIRD_PARTY = "1"
$env:OPENAI_IMAGE_MODEL = "gpt-image-2"
$env:OPENAI_IMAGE_HIGHRES_MODEL = "gpt-image-2-final"
```

The exact model name is provider-specific. Never invent a model alias that the relay does not actually expose.

## Recommended command

```powershell
python scripts/efg.py image `
  "technical background" `
  --figure-template system-architecture `
  --final `
  --save-prompt output/final-prompt.txt
```

For a relay, first run `efg provider-check` to verify the configured base URL is reachable and appears to expose an image-generation route.
