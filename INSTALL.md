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

## Re-run after updating the repository

```powershell
Set-Location "$HOME/engineering-figure-gpt"
git pull
& ".\scripts\install_and_test.ps1" -SkipDependencies
```

## Optional live GPT Image test

A real GPT Image request is **not** part of the default install test because it performs a paid network request. To explicitly test the portable OpenAI fallback once:

```powershell
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1" -SkipDependencies -TestLiveImage
```

The live test uses the installed runtime and deletes its temporary output after verifying that a non-empty image file was produced.

## Image execution paths

Inside Codex, normal conceptual figure generation should prefer the installed built-in GPT image-generation capability.

For portable/reproducible CLI execution, the runtime also includes:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/generate_image.py" `
  "Create a publication-quality system architecture figure ..." `
  --quality high `
  --size 1536x1024
```

The CLI fallback is intentionally restricted to the official OpenAI endpoint and defaults to `gpt-image-2`.

## API key for the CLI fallback

The fallback accepts one of:

```text
OPENAI_API_KEY
OPENAI_API_KEY_FILE
~/.codex/secrets/openai_api_key.txt
```

Do not commit a real API key to this repository.

## Setup diagnostics

You can run the installed checker directly:

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/check_setup.ps1"
```

Possible outcomes:

- `READY`: required runtime components are present and no warnings were found.
- `READY WITH WARNINGS`: the core runtime is usable, but an optional image path or API-key fallback is not fully configured.
- `BLOCKED`: a required runtime component is missing or the offline smoke check failed.

## Verify Codex can see the skill

```powershell
Get-ChildItem "$HOME/.codex/skills/engineering-figure-gpt" -Filter "SKILL.md"
```

Then start a new Codex session or restart Codex if necessary.
