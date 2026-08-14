# GPT Image Execution Reliability

The portable image CLI is a fallback for reproducibility and local testing. Inside Codex, prefer the installed built-in GPT image-generation path when available.

## Provider policy

- Official OpenAI is the default trusted endpoint.
- Explicitly approved OpenAI-compatible relays are supported with `--allow-third-party` or `OPENAI_ALLOW_THIRD_PARTY=1`.
- A custom base URL without explicit opt-in must fail closed before any API key or image is sent.
- GPT Image model names only.
- No silent provider switching.
- No silent downgrade of model, quality, or size after a failed request.
- Do not embed credentials in the base URL.

## Third-party relay safety

A relay receives the configured API key. For image-edit requests it also receives uploaded image inputs. Therefore:

- only enable a relay the user explicitly trusts;
- prefer HTTPS for non-local relays;
- record the base URL used for reproducibility, but never record API keys;
- treat relay compatibility as an implementation contract, not a guarantee that every OpenAI image parameter is supported identically.

Expected routes are:

```text
POST <base-url>/images/generations
POST <base-url>/images/edits
```

## Failure behavior

When a live image request fails:

- surface the HTTP status and a concise server message;
- distinguish authentication, rate-limit, timeout/network, and server-side failures when possible;
- do not retry by silently reducing quality;
- do not switch model aliases automatically;
- do not silently switch from one base URL to another;
- do not claim an output file exists unless it was actually written and is non-empty.

## Reproducibility

Record the following when a real output is intended for a showcase or paper workflow:

- model name;
- base URL host or provider label when a relay is used;
- quality;
- requested size;
- output format;
- final prompt;
- input image filenames for edits;
- output path;
- verification notes.

Do not record or commit API keys.
