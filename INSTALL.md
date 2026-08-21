# Install in Codex

## Recommended Windows PowerShell flow

Clone the repository outside the Codex runtime directory, then run the installer/test wrapper:

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

The installer:

1. installs Python dependencies unless `-SkipDependencies` is used, including Pillow for raster verification;
2. synchronizes a **pruned runtime package** into `~/.codex/skills/engineering-figure-gpt`;
3. runs setup diagnostics;
4. runs offline CLI checks;
5. renders a real temporary Plot Mode PNG;
6. builds a preservation-first Edit Mode prompt in dry-run mode;
7. creates a local raster fixture and verifies exact dimensions/format;
8. removes temporary smoke-test files.

The default install path makes **no paid image API request**.

Repository-only docs, examples, tests, CI validators, and GitHub workflow files are not copied into the Codex runtime.

## Re-run after updating

```powershell
Set-Location "$HOME/engineering-figure-gpt"
git pull
& ".\scripts\install_and_test.ps1" -SkipDependencies
```

If dependencies changed, omit `-SkipDependencies`.

## Verify the installed runtime

```powershell
Get-ChildItem "$HOME/.codex/skills/engineering-figure-gpt" -Filter "SKILL.md"
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/check_setup.ps1"
```

The runtime should include:

```text
assets/prompt-templates/engineering-figure-templates.json
assets/prompt-templates/mathematical-modeling-templates.json
assets/prompt-templates/image-quality-contracts.json
scripts/build_image_edit_prompt.py
scripts/verify_image_output.py
references/image-quality-contract.md
references/edit-mode.md
references/visual-qa.md
```

## Recommended command-line workflow with CC Switch

If CC Switch already configured the active Codex provider, do not duplicate the same Base URL and key for this Skill.

Resolution order:

```text
explicit CLI override
        ↓
active Codex / CC Switch provider
        ↓
legacy OPENAI_* fallback
        ↓
official OpenAI default
```

Inspect the sanitized provider configuration:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/codex_provider_config.py"
```

Probe image compatibility without generating an image:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" provider-check
```

A Codex text provider may work perfectly while exposing no compatible `/images/generations` or `/images/edits` route.

## Interactive wizard

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/wizard.ps1"
```

The wizard now supports:

- engineering and mathematical-modeling template selection;
- `draft / paper / final` image-quality profiles;
- conceptual image generation;
- `correct / revise / restyle / redraw` image editing;
- preservation and allowed-change constraints;
- raster size/format verification;
- active Codex / CC Switch provider reuse by default;
- optional trusted relay override;
- provider compatibility probe;
- exact Plot Request → Spec → Figure workflows;
- offline runtime checks.

## New conceptual image workflow

For portable/reproducible CLI execution, use `efg image` rather than calling the low-level generator directly. This ensures the reusable publication image-quality contract is injected.

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" image `
  "A retrieval system with OCR, embeddings, reranking, and answer synthesis" `
  --figure-template system-architecture `
  --quality-profile paper `
  --lang en `
  --save-prompt output/final-prompt.txt `
  --dry-run
```

Remove `--dry-run` only when a live request is intended.

The quality contract constrains safe margins, text-region size, paper-width readability, alignment, arrows, color contrast, micro-text, clipping, blur/ghosting, and decorative pseudo-technical detail independently from the domain template.

## Existing-image editing

Editing is a first-class workflow:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" edit figure.png `
  "Change Encoder to Cross-Attention Encoder only" `
  --mode correct `
  --preserve "all arrow endpoints" `
  --save-prompt output/edit-prompt.txt `
  --dry-run
```

Modes:

- `correct`: smallest possible local correction;
- `revise`: requested local scientific/structural change while preserving unaffected content;
- `restyle`: visual style only; scientific content remains locked;
- `redraw`: clean reconstruction while preserving scientific meaning and canonical labels.

Use repeatable `--preserve` and `--allow-change` flags to define the edit boundary. Additional references may be supplied with `--reference-image`.

Edit mode defaults to `input_fidelity=high` unless explicitly overridden.

## Raster verification

High-resolution model routing and actual raster dimensions are separate concerns.

Verify an exact requested output:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" verify-image output/figure.png `
  --expected-size 1536x1024 `
  --require-format png
```

Or enforce minimum constraints:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" verify-image output/figure.png `
  --min-width 1500 `
  --min-height 1000 `
  --min-megapixels 1.5
```

Live requests routed through `efg image` and `efg edit` automatically perform basic raster verification on returned files. When a concrete size is requested, a relay that silently returns a different size causes the unified workflow to fail instead of presenting the smaller result as equivalent.

Raster metadata cannot prove label sharpness or scientific correctness. Final images must still pass `references/visual-qa.md`.

## Manual custom OpenAI-compatible relay / 中转站

A custom relay can be supplied manually. Because it may receive the API key and input images, a manually supplied non-OpenAI URL requires explicit opt-in.

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" image `
  "technical background" `
  --figure-template system-architecture `
  --base-url "https://relay.example/v1" `
  --allow-third-party `
  --dry-run
```

Environment fallback/override example:

```powershell
$env:OPENAI_BASE_URL = "https://relay.example/v1"
$env:OPENAI_ALLOW_THIRD_PARTY = "1"
$env:OPENAI_IMAGE_MODEL = "gpt-image-2"
$env:OPENAI_API_KEY_FILE = "$HOME/.codex/secrets/openai_api_key.txt"
```

Do not enable third-party trust for a service you do not trust. Credentials embedded directly in the URL are rejected.

### Relay compatibility probe

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" provider-check `
  --base-url "https://relay.example/v1" `
  --allow-third-party
```

The probe does **not** generate an image. It checks basic signals for:

```text
GET     <base-url>/models
OPTIONS <base-url>/images/generations
OPTIONS <base-url>/images/edits
```

A successful probe does not guarantee support for every `size`, `quality`, `background`, `input_fidelity`, or edit parameter. Verify actual outputs when the contract matters.

## API key

The portable image path can reuse the active Codex provider credential. Legacy/manual fallback sources include:

```text
OPENAI_API_KEY
OPENAI_API_KEY_FILE
~/.codex/secrets/openai_api_key.txt
```

Do not commit real credentials to the repository or paste them into figure prompts.

## Final / high-resolution routing

Routine requests use:

```text
OPENAI_IMAGE_MODEL
```

and otherwise default to `gpt-image-2`.

Final/high-resolution requests use:

```text
OPENAI_IMAGE_HIGHRES_MODEL
```

or an explicit image `--model`.

Example:

```powershell
$env:OPENAI_IMAGE_HIGHRES_MODEL = "<final-quality-image-model-exposed-by-your-endpoint>"

python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" image `
  "technical background" `
  --figure-template graphical-abstract `
  --final
```

If `--final` / `--highres` is requested and no final-quality image model is configured, the CLI stops instead of silently downgrading.

Do not assume a model called `highres`, `final`, or `pro` returned a specific 2K/4K canvas. Request and verify actual pixel dimensions separately. See `references/highres-policy.md`.

## One-command exact plotting

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" plot request.json `
  --spec-out output/spec.json `
  --out-path output/figure `
  --formats png pdf svg
```

This runs:

```text
Plot Request
    ↓
build_plot_spec.py
    ↓
Normalized Plot Spec
    ↓
plot_publication_figure.py
    ↓
Figure
```

If you already have a normalized spec:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" render output/spec.json `
  --out-path output/figure `
  --formats png pdf svg
```

## Optional live GPT Image test

A real image request is **not** part of the default install test because it incurs API usage.

To test the configured image endpoint once:

```powershell
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1" -SkipDependencies -TestLiveImage
```

The live test:

1. routes through the same quality-constrained `efg image` path;
2. requests a concrete PNG canvas;
3. confirms a non-empty output was returned;
4. checks that the returned PNG actually matches the requested dimensions/format;
5. removes the temporary output afterward.

If a relay is configured manually, set the appropriate relay/trust environment first. If the active CC Switch provider is compatible, it can be reused directly.

## Setup diagnostics outcomes

`check_setup.ps1` reports:

- `READY`: required runtime components and Pillow are present with no warnings;
- `READY WITH WARNINGS`: the runtime is usable but an optional built-in image path, final-quality model, API credential, or provider setting is not fully configured;
- `BLOCKED`: a required runtime component/dependency is missing or the offline smoke check failed.

After installation or update, start a new Codex session or restart Codex if necessary so the refreshed Skill runtime is loaded.
