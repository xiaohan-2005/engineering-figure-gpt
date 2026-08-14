# Codex CLI + CC Switch Integration

Engineering Figure GPT is designed to work naturally when the user launches **Codex from the command line** and manages Codex API providers with **CC Switch**.

## Expected user flow

```text
CC Switch
   ↓
~/.codex/config.toml + ~/.codex/auth.json
   ↓
codex
   ↓
Engineering Figure GPT skill
```

The user should not need to maintain a second copy of the same relay URL and API key just for this skill.

## Connection resolution order

The portable image fallback resolves its connection in this order:

1. explicit command-line overrides such as `--base-url` / `--api-key-file`;
2. the active Codex provider from `~/.codex/config.toml` plus `~/.codex/auth.json`;
3. legacy `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and `OPENAI_API_KEY_FILE` settings;
4. official OpenAI defaults.

For the active Codex provider, the resolver supports common CC Switch layouts:

```toml
model_provider = "custom"

[model_providers.custom]
base_url = "https://example.com/v1"
wire_api = "responses"
experimental_bearer_token = "..."
```

and the auth-file layout:

```json
{
  "OPENAI_API_KEY": "..."
}
```

Secrets are used only in memory and must never be printed in diagnostics, committed to the repository, or copied into prompts.

## Trust behavior

A non-OpenAI endpoint that comes from the **currently active Codex provider** is treated as already selected by the user. It does not require a second `--allow-third-party` flag.

A custom URL supplied independently with `--base-url` or `OPENAI_BASE_URL` still requires explicit trust through `--allow-third-party` or `OPENAI_ALLOW_THIRD_PARTY=1`.

This distinction prevents accidental credential forwarding while avoiding duplicate configuration for normal CC Switch users.

## Image model is separate from the Codex text model

Do **not** reuse the text model from `model = ...` as the image model.

For example, an active Codex provider may use a coding/text model while the image endpoint exposes a different model. Routine image generation therefore resolves independently:

```text
--model
  ↓
OPENAI_IMAGE_MODEL
  ↓
gpt-image-2
```

Final/high-resolution routing remains independent through `OPENAI_IMAGE_HIGHRES_MODEL` or an explicit image-model override.

## Check the currently selected provider

From the installed skill directory:

```powershell
python scripts/codex_provider_config.py
```

The output is sanitized. It reports the provider name, base URL, wire API, config/auth file locations, and whether a key was found, but never prints the key itself.

## Check whether the provider actually supports Images

A provider that works for Codex text requests does **not automatically** guarantee support for `/images/generations` or `/images/edits`.

Run:

```powershell
python scripts/efg.py provider-check
```

No `--base-url` is needed when CC Switch already selected the provider. The command reuses the active Codex provider and probes its model/image routes without generating an image.

If the selected provider does not expose an image-generation route, Plot Mode still works locally, but the portable GPT Image fallback cannot generate conceptual images through that provider.

## Typical command-line Codex workflow

After switching a provider in CC Switch, launch/relaunch Codex normally:

```powershell
codex
```

Then ask Codex to use `$engineering-figure-gpt` for the figure task. For direct reproducible CLI execution inside the repository or installed skill:

```powershell
python scripts/efg.py image `
  "一个包含数据预处理、模型训练、验证和决策输出的数学建模框架" `
  --figure-template full-modeling-pipeline `
  --lang zh `
  --dry-run
```

The dry run should report:

```text
connection_source: codex-config
codex_provider: <the currently active provider>
```

Remove `--dry-run` only when a live image request is intended.
