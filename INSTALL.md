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

## Image execution paths

Inside Codex, normal conceptual figure generation should prefer the installed built-in GPT image-generation capability.

For portable/reproducible CLI execution, the runtime also includes:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/generate_image.py" `
  "Create a publication-quality system architecture figure ..." `
  --quality high `
  --size 1536x1024
```

The CLI defaults to `gpt-image-2` and the official OpenAI base URL.

## Custom OpenAI-compatible relay / 中转站

A custom relay is supported. Because a relay receives the configured API key and, for image-edit requests, uploaded image files, non-OpenAI URLs require explicit opt-in.

PowerShell environment configuration:

```powershell
$env:OPENAI_BASE_URL = "https://relay.example/v1"
$env:OPENAI_ALLOW_THIRD_PARTY = "1"
$env:OPENAI_API_KEY_FILE = "$HOME/.codex/secrets/openai_api_key.txt"
```

Then validate the configuration without making a paid request:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/generate_image.py" `
  "test research figure" `
  --dry-run
```

The dry-run output should contain:

```text
"third_party": true
```

You can also configure the relay per command instead of using environment variables:

```powershell
python "$HOME/.codex/skills/engineering-figure-gpt/scripts/generate_image.py" `
  "Create a publication-quality system architecture figure ..." `
  --base-url "https://relay.example/v1" `
  --allow-third-party
```

The configured base URL should expose OpenAI-compatible routes such as:

```text
POST <base-url>/images/generations
POST <base-url>/images/edits
```

Do not enable `OPENAI_ALLOW_THIRD_PARTY=1` for a service you do not trust. Credentials embedded directly in the URL are rejected.

## API key for the CLI fallback

The fallback accepts one of:

```text
OPENAI_API_KEY
OPENAI_API_KEY_FILE
~/.codex/secrets/openai_api_key.txt
```

The key only needs to be valid for the selected endpoint. Do not commit a real API key to this repository.

## Optional live GPT Image test

A real GPT Image request is **not** part of the default install test because it performs a paid network request. To explicitly test the configured image endpoint once:

```powershell
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1" -SkipDependencies -TestLiveImage
```

If a relay is configured, set `OPENAI_BASE_URL` and `OPENAI_ALLOW_THIRD_PARTY=1` first. The live test uses the installed runtime and deletes its temporary output after verifying that a non-empty image file was produced.

## Setup diagnostics

You can run the installed checker directly:

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/check_setup.ps1"
```

The checker reports whether the image path uses official OpenAI, an explicitly trusted relay, or a custom URL that has not yet been approved.

Possible outcomes:

- `READY`: required runtime components are present and no warnings were found.
- `READY WITH WARNINGS`: the core runtime is usable, but an optional image path, relay trust setting, or API-key fallback is not fully configured.
- `BLOCKED`: a required runtime component is missing or the offline smoke check failed.

## Verify Codex can see the skill

```powershell
Get-ChildItem "$HOME/.codex/skills/engineering-figure-gpt" -Filter "SKILL.md"
```

Then start a new Codex session or restart Codex if necessary.
