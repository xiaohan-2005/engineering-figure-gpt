# Install in Codex

## Recommended Windows PowerShell flow

Clone the repository outside the Codex runtime directory, then run the installer/test wrapper:

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

The installer:

1. installs Python dependencies unless `-SkipDependencies` is used;
2. synchronizes a **pruned runtime package** into `~/.codex/skills/engineering-figure-gpt`;
3. runs setup diagnostics;
4. performs an offline CLI smoke check;
5. renders a real temporary Plot Mode PNG and verifies that the output is non-empty;
6. removes temporary smoke-test files.

Repository-only docs, examples, tests, and GitHub workflow files are not copied into the Codex runtime.

## Re-run after updating

```powershell
Set-Location "$HOME/engineering-figure-gpt"
git pull
& ".\scripts\install_and_test.ps1" -SkipDependencies
```

## Verify the installed runtime

```powershell
Get-ChildItem "$HOME/.codex/skills/engineering-figure-gpt" -Filter "SKILL.md"
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/check_setup.ps1"
```

The runtime should contain both prompt packs:

```text
assets/prompt-templates/engineering-figure-templates.json
assets/prompt-templates/mathematical-modeling-templates.json
```

## Interactive wizard

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/wizard.ps1"
```

The wizard can:

- list engineering and mathematical-modeling templates;
- build prompts only;
- run one-command template → image workflows;
- select official OpenAI or a trusted relay;
- probe relay compatibility without generating an image;
- request final/high-resolution routing;
- run one-command Plot Request → Spec → Figure workflows.

## Image execution paths

Inside Codex, normal conceptual generation should prefer the built-in GPT image capability.

For portable/reproducible CLI execution:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" image `
  "A retrieval system with OCR, embeddings, reranking, and answer synthesis" `
  --figure-template system-architecture `
  --lang en `
  --save-prompt output/final-prompt.txt `
  --dry-run
```

Remove `--dry-run` only when a live request is intended.

## Custom OpenAI-compatible relay / 中转站

A custom relay is supported. Because a relay receives the configured API key and, for image-edit requests, uploaded images, non-OpenAI URLs require explicit opt-in.

PowerShell environment configuration:

```powershell
$env:OPENAI_BASE_URL = "https://relay.example/v1"
$env:OPENAI_ALLOW_THIRD_PARTY = "1"
$env:OPENAI_IMAGE_MODEL = "gpt-image-2"
$env:OPENAI_API_KEY_FILE = "$HOME/.codex/secrets/openai_api_key.txt"
```

Dry-run configuration check:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" image `
  "test research figure" `
  --dry-run
```

The output should show the selected `base_url`, model, and whether `third_party` is true.

### Relay compatibility probe

Before a paid image generation request, run:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" provider-check `
  --base-url "https://relay.example/v1" `
  --allow-third-party
```

The probe does **not** generate an image. It checks basic reachability signals for:

```text
GET     <base-url>/models
OPTIONS <base-url>/images/generations
OPTIONS <base-url>/images/edits
```

A successful probe is useful evidence that the relay follows the expected API shape, but it cannot guarantee that every OpenAI Images parameter is implemented identically.

Do not enable `OPENAI_ALLOW_THIRD_PARTY=1` for a service you do not trust. Credentials embedded directly in the URL are rejected.

## API key

The portable image path accepts one of:

```text
OPENAI_API_KEY
OPENAI_API_KEY_FILE
~/.codex/secrets/openai_api_key.txt
```

The key only needs to be valid for the selected endpoint. Do not commit a real key to this repository.

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

or an explicit `--model`.

Example:

```powershell
$env:OPENAI_IMAGE_HIGHRES_MODEL = "<final-quality-model-exposed-by-your-endpoint>"

python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" image `
  "technical background" `
  --figure-template graphical-abstract `
  --final
```

If `--final` / `--highres` is requested and no final-quality model is configured, the CLI stops instead of silently downgrading. See `references/highres-policy.md`.

## One-command exact plotting

The preferred user-facing route is:

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

A real image request is **not** part of the default install test because it performs a paid network request.

To explicitly test the configured image endpoint once:

```powershell
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1" -SkipDependencies -TestLiveImage
```

If a relay is configured, set `OPENAI_BASE_URL` and `OPENAI_ALLOW_THIRD_PARTY=1` first. The live test deletes its temporary output after confirming that a non-empty image file was produced.

## Setup diagnostics outcomes

`check_setup.ps1` can report:

- `READY`: required runtime components are present and no warnings were found;
- `READY WITH WARNINGS`: the core runtime is usable, but an optional image path, relay trust setting, final-quality model, or API-key fallback is not fully configured;
- `BLOCKED`: a required runtime component is missing or the offline smoke check failed.

After installation, start a new Codex session or restart Codex if necessary.
