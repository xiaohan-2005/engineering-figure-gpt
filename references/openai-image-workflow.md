# OpenAI Image Workflow

Use the official OpenAI Image API as the default conceptual-figure backend.

Default model: `gpt-image-2`.

Recommended defaults:

- landscape: `1536x1024`
- portrait: `1024x1536`
- final paper figure: `quality=high`
- output: PNG unless another format is requested

For new images, use the image generation endpoint. For redraws and edits, use the image edit endpoint and preserve user-provided scientific content. A non-official compatible endpoint must not receive user files or credentials unless the user explicitly approves that provider.
