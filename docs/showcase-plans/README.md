# Real Conceptual Showcase Queue

This directory contains **ready-to-run conceptual showcase plans**, not completed outputs.

A plan becomes a completed example only after a real image-generation run produces a valid image and the result is packaged into `docs/examples/<slug>/` with its evidence chain.

## Planned cases

| Slug | Purpose | Language | Prompt |
|---|---|---|---|
| `zh-mathematical-modeling-framework` | Chinese end-to-end mathematical-modeling framework | zh | [prompt](zh-mathematical-modeling-framework/prompt.txt) |
| `rag-system-architecture` | dense but readable RAG system architecture | en | [prompt](rag-system-architecture/prompt.txt) |
| `genetic-algorithm-workflow` | algorithm loop / termination workflow | zh | [prompt](genetic-algorithm-workflow/prompt.txt) |
| `multisource-fusion-graphical-abstract` | graphical abstract for multi-source data fusion | en | [prompt](multisource-fusion-graphical-abstract/prompt.txt) |

Every case also has a `brief.md` describing the intended claim, reading order, must-keep labels, and verification targets.

## 1. Configure the image endpoint

Official OpenAI works without a custom base URL. For a trusted relay:

```powershell
$env:OPENAI_BASE_URL = "https://YOUR-TRUSTED-RELAY/v1"
$env:OPENAI_ALLOW_THIRD_PARTY = "1"
$env:OPENAI_IMAGE_MODEL = "gpt-image-2"
$env:OPENAI_API_KEY_FILE = "$HOME/.codex/secrets/openai_api_key.txt"
```

Do not put a real API key in this repository.

Optional compatibility probe before spending image credits:

```powershell
python scripts/efg.py provider-check
```

## 2. Generate a real output

Example for the Chinese mathematical-modeling case:

```powershell
python scripts/efg.py image `
  --background-file "docs/showcase-plans/zh-mathematical-modeling-framework/prompt.txt" `
  --out-dir "output/showcase/zh-mathematical-modeling-framework" `
  --prefix "zh-mathematical-modeling-framework"
```

Expected routine output path:

```text
output/showcase/zh-mathematical-modeling-framework/zh-mathematical-modeling-framework-1.png
```

Run the other cases by replacing the slug in the prompt path, output directory, and prefix.

Use `--final` only when `OPENAI_IMAGE_HIGHRES_MODEL` or an explicit final-quality `--model` is actually configured.

## 3. Verify the image

Copy the common template:

```powershell
Copy-Item `
  "docs/showcase-plans/verification-template.md" `
  "output/showcase/<slug>/verification.md"
```

Then edit the copied file after visually checking the real output. Do not mark a check as passed without inspecting the generated image.

## 4. Package the evidence chain

```powershell
python scripts/package_showcase_example.py `
  --slug <slug> `
  --mode image `
  --brief "docs/showcase-plans/<slug>/brief.md" `
  --source "docs/showcase-plans/<slug>/prompt.txt=prompt.txt" `
  --output "output/showcase/<slug>/<slug>-1.png" `
  --verification "output/showcase/<slug>/verification.md" `
  --quality high `
  --size 1536x1024 `
  --check "labels checked" `
  --check "relationships checked" `
  --check "no unsupported scientific claim added"
```

If you used a known explicit model, add:

```text
--model <actual-model-name>
```

The packaging tool rejects missing evidence, empty output files, and fake/mismatched PNG/JPEG/WebP/SVG/PDF signatures.

## 5. Commit only after packaging succeeds

A completed conceptual case should then exist as:

```text
docs/examples/<slug>/
├── brief.md
├── prompt.txt
├── output.png
├── verification.md
└── manifest.json
```

For paper-quality handoff, optionally add `editable-handoff.md` following `references/editable-figure-handoff.md`.

## Important

- Files in this directory are **plans**, not generation evidence.
- Do not rename a layout preview to `output.png`.
- Do not create a completed manifest before a real output exists.
- Do not commit relay credentials, API keys, or secret headers.
- If generated text is malformed, regenerate/edit the image before packaging it as a showcase example.
