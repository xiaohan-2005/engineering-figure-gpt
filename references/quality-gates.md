# Release Quality Gates

Before describing the repository as release-ready, require all of the following:

1. Skill metadata validation passes.
2. Python scripts compile.
3. UTF-8 and Chinese-template validation pass.
4. Engineering + mathematical-modeling prompt packs validate.
5. The reusable `draft / paper / final` image-quality contract pack validates.
6. Documentation local links/images resolve.
7. Unit tests pass.
8. Figure Brief / Plot Request / Plot Spec schema tests pass.
9. GPT image fallback tests pass without real network calls.
10. Prompt-builder tests confirm that conceptual prompts actually receive the publication image-quality contract.
11. Edit tests confirm that `correct` is preservation-first and uses high input fidelity by default through the unified workflow.
12. Raster verification tests prove both success and failure paths for explicit dimensions/format requirements.
13. Plot renderer E2E smoke test produces a non-empty image.
14. Install smoke tests cover Plot Mode, preservation-first Edit Mode dry-run, and raster-size/format verification without API cost.
15. Runtime pruning check passes and remains within the token budget.
16. `efg.py check` passes offline.

## Live image integration gate

Real GPT image generation remains a separate opt-in integration test because it incurs API usage.

When the live test is run, it should:

1. route through `efg image` so the quality contract is included;
2. request a concrete raster size/format;
3. save a non-empty returned image;
4. verify that the returned image can be opened;
5. verify that the provider honored the requested concrete dimensions/format;
6. fail if the relay silently returns a different raster size.

A live test failure must not trigger silent model, provider, quality, or size downgrade.

## Visual acceptance gate

Automated tests cannot prove that generated scientific text and arrows are visually correct. A real conceptual showcase/final output must additionally pass `references/visual-qa.md`:

- scientific fidelity;
- text integrity;
- layout integrity;
- arrow/line quality;
- color/contrast;
- raster clarity at native and approximately 50% scale;
- edit preservation when an existing figure was modified.

Do not call a conceptual image paper-ready solely because the API returned HTTP 200 or because its pixel dimensions passed metadata verification.

## Runtime pruning

The Codex runtime should contain only files required for actual figure production. Repository-only CI validators, tests, showcase assets, and development documentation should remain outside the runtime unless the Skill needs them at execution time.

## Plot renderer E2E

At least one local deterministic request must run through:

```text
Plot Request -> normalized Plot Spec -> renderer -> non-empty raster
```

without a network request.

## GPT image fallback

Offline tests must cover request construction, edit multipart behavior, provider/relay trust, model resolution, error handling, and dry-run behavior. Paid network generation is opt-in only.
