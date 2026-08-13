# Install in Codex

## Recommended Windows PowerShell path

Keep the GitHub repository as a source checkout, then install a pruned runtime copy into Codex.

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

The runtime skill is synchronized to:

```text
~/.codex/skills/engineering-figure-gpt
```

The runtime is intentionally smaller than the GitHub repository. Repository-only items such as `docs/`, `examples/`, `tests/`, `.github/`, and README files stay out of the Codex runtime context.

## Setup check

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/check_setup.ps1"
```

The check verifies Python, required runtime files, the Codex built-in image-generation skill when present, the offline CLI path, and optional OpenAI API-key availability for the portable image fallback.

## Image generation

Normal in-agent use should prefer Codex's built-in image-generation capability.

The portable CLI fallback requires an OpenAI API key. You can set `OPENAI_API_KEY` in the environment or store a key in:

```text
~/.codex/secrets/openai_api_key.txt
```

Do not commit real keys to this repository.

## Updating

Update the source checkout and rerun the installer:

```powershell
Set-Location "$HOME/engineering-figure-gpt"
git pull
& .\scripts\install_and_test.ps1 -SkipDependencies
```

## Direct clone into the skills directory

A direct clone into `~/.codex/skills/engineering-figure-gpt` can work for development, but it also places docs, examples, tests, and CI files inside the runtime directory. The pruned installer path above is preferred.
