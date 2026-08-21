# Install Engineering Figure GPT in Codex

## Recommended Windows PowerShell flow

Clone the source repository outside the Codex Runtime directory:

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

The installer:

1. installs Python dependencies unless `-SkipDependencies` is used;
2. synchronizes a **pruned execution Runtime** into `~/.codex/skills/engineering-figure-gpt`;
3. runs source-side setup diagnostics against that installed Runtime;
4. performs offline CLI checks;
5. runs a real local Plot Request → Spec → PNG smoke test;
6. runs a preservation-first Edit dry-run;
7. runs a raster size/format verification smoke test.

The default test path does **not** call the image API and does not spend image credits.

## Runtime vs source checkout

Installed Runtime:

```text
~/.codex/skills/engineering-figure-gpt
```

It contains the actual Skill, prompt assets, core execution references, and Python runtime scripts.

The following stay in the source checkout to protect the Codex Runtime token budget:

- tests and CI validators;
- showcase/development files;
- installation helpers;
- `check_setup.ps1`;
- `wizard.ps1`.

Therefore diagnostics and the Wizard should be launched from the cloned source repository while pointing at the installed Runtime.

## Re-run after updating

```powershell
Set-Location "$HOME/engineering-figure-gpt"
git pull
& ".\scripts\install_and_test.ps1" -SkipDependencies
```

## Diagnose the installed Runtime

```powershell
& "$HOME/engineering-figure-gpt/scripts/check_setup.ps1" `
  -SkillDir "$HOME/.codex/skills/engineering-figure-gpt"
```

The checker verifies, among other things:

- `SKILL.md` and prompt assets;
- `efg.py`;
- `generate_image.py`;
- `image_model_policy.py`;
- edit prompt builder;
- raster verifier;
- exact plot renderer;
- Pillow availability;
- Codex / CC Switch provider discovery;
- offline runtime smoke checks.

## Interactive Wizard

```powershell
& "$HOME/engineering-figure-gpt/scripts/wizard.ps1" `
  -SkillDir "$HOME/.codex/skills/engineering-figure-gpt"
```

The Wizard can:

- build publication-constrained prompts;
- generate conceptual figures;
- edit existing figures with `correct / revise / restyle / redraw`;
- verify raster size/format/aspect;
- probe the active image provider;
- build exact plots;
- run offline Runtime checks.

For image generation/editing it asks separately for:

1. `draft / paper / final` **visual quality profile**;
2. whether to use the separate `--final` / high-resolution **model route**;
3. whether to make a paid live image request;
4. whether to reuse the active Codex/CC Switch provider or manually override a trusted relay.

## Codex + CC Switch provider reuse

If CC Switch already configured the provider used by command-line Codex, the image CLI attempts to reuse:

```text
~/.codex/config.toml
~/.codex/auth.json
```

Resolution priority:

```text
explicit CLI override
-> active Codex / CC Switch provider
-> OPENAI_* environment fallback
-> official OpenAI default
```

Inspect sanitized provider information:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/codex_provider_config.py"
```

Probe image API compatibility before spending credits:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" provider-check
```

A provider that works for Codex text may still lack `/images/generations` or `/images/edits`.

## Manual OpenAI-compatible relay

When deliberately overriding the active provider:

```powershell
$env:OPENAI_BASE_URL = "https://relay.example/v1"
$env:OPENAI_ALLOW_THIRD_PARTY = "1"
$env:OPENAI_IMAGE_MODEL = "gpt-image-2"
$env:OPENAI_API_KEY_FILE = "$HOME/.codex/secrets/openai_api_key.txt"
```

Or pass `--base-url ... --allow-third-party` per command.

Do not trust an unknown relay: an image-edit relay may receive both the configured API credential and uploaded figures.

## Image quality profiles

Normal unified-CLI defaults when no explicit runtime override/environment value exists:

```text
draft -> quality=low  -> 1024x1024
paper -> quality=high -> 1536x1024
final -> quality=high -> 2048x1152
```

The `final` quality profile strengthens prompt/rendering constraints. It does **not** automatically request a different model.

Separate final/high-resolution model routing uses:

```text
OPENAI_IMAGE_HIGHRES_MODEL
```

and is requested by:

```text
--final
--highres
```

If that route is requested but no final model is configured (and no explicit image model is supplied), the CLI fails closed instead of silently downgrading.

## GPT Image 2 edit behavior

For `gpt-image-2`:

- do **not** pass `input_fidelity`; input images are always processed at high fidelity;
- concrete output sizes must have both edges divisible by 16;
- maximum edge is 3840 px;
- long/short ratio must be <= 3:1;
- total pixels must be between 655,360 and 8,294,400.

For edits without an explicit `--size`, the primary source canvas is preserved exactly when legal. Otherwise the nearest legal GPT Image 2 size is chosen with a visible warning. Unsafe cases fail instead of silently changing the canvas.

Example preservation-first dry-run:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" edit `
  "C:\path\figure.png" `
  "Change one label only; keep everything else unchanged" `
  --mode correct `
  --dry-run
```

## Objective raster verification

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" verify-image `
  "output\figure.png" `
  --expected-size 2048x1152 `
  --require-format png
```

Pixel verification does not replace Visual QA for text clarity, arrows, scientific meaning, clipping, or unrelated edit changes.

## Exact Plot Mode

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/efg.py" plot request.json `
  --spec-out output/spec.json `
  --out-path output/figure `
  --formats png pdf svg
```

Exact numeric geometry stays deterministic and is never redrawn by the image model.

## Optional paid live GPT image test

A real image request is opt-in:

```powershell
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1" `
  -SkipDependencies `
  -TestLiveImage
```

The live test requests a concrete PNG size and verifies the returned raster instead of merely checking that a file exists.

## After installation

Start a new Codex session or restart Codex if the Skill is not discovered immediately.
