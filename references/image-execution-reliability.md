# GPT Image Execution Reliability

The portable image CLI is a fallback for reproducibility and local testing. Inside Codex, prefer the installed built-in GPT image-generation path when available.

## Provider policy

- Official OpenAI endpoint only.
- GPT Image models only.
- No silent fallback to third-party relays.
- No silent downgrade of model, quality, or size after a failed request.

## Failure behavior

When a live image request fails:

- surface the HTTP status and a concise server message;
- distinguish authentication, rate-limit, timeout/network, and server-side failures when possible;
- do not retry by silently reducing quality;
- do not switch model aliases automatically;
- do not claim an output file exists unless it was actually written and is non-empty.

## Reproducibility

Record the following when a real output is intended for a showcase or paper workflow:

- model name;
- quality;
- requested size;
- output format;
- final prompt;
- input image filenames for edits;
- output path;
- verification notes.

Do not record or commit API keys.
