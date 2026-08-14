# OpenAI Image Workflow

Use GPT Image for conceptual-figure generation and editing.

Default model: `gpt-image-2`.

Recommended defaults:

- landscape: `1536x1024`
- portrait: `1024x1536`
- final paper figure: `quality=high`
- output: PNG unless another format is requested

For new images, use the image generation endpoint. For redraws and edits, use the image edit endpoint and preserve user-provided scientific content.

## Base URL policy

Official OpenAI is trusted by default:

```text
OPENAI_BASE_URL=https://api.openai.com/v1
```

OpenAI-compatible relay/base URLs are supported, but they require explicit trust opt-in because the selected endpoint receives the API key and, for image edits, the uploaded image files.

Environment configuration:

```text
OPENAI_BASE_URL=https://relay.example/v1
OPENAI_ALLOW_THIRD_PARTY=1
```

Equivalent CLI configuration:

```bash
python scripts/generate_image.py "research figure prompt" \
  --base-url https://relay.example/v1 \
  --allow-third-party
```

Do not enable third-party mode for an endpoint you do not trust. Do not embed credentials inside the URL. The CLI accepts only valid `http://` or `https://` base URLs and continues to restrict the selected model to GPT Image model names.

The relay is expected to expose OpenAI-compatible image routes under the configured base URL:

```text
POST <base-url>/images/generations
POST <base-url>/images/edits
```

No automatic provider, model, quality, or size downgrade should happen after a request failure.
