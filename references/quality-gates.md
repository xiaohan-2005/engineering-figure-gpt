# Release Quality Gates

Before describing the repository as release-ready, require all of the following:

1. Skill metadata validation passes.
2. Python scripts compile.
3. UTF-8 and Chinese-template validation pass.
4. Documentation local links/images resolve.
5. Unit tests pass.
6. Figure Brief schema tests pass.
7. GPT image fallback tests pass without real network calls.
8. Plot renderer E2E smoke test produces a non-empty image.
9. Runtime pruning check passes and remains within the token budget.
10. `efg.py check` passes offline.

Real GPT image generation is a separate opt-in integration test because it incurs API usage. A live test failure must not trigger silent model, provider, quality, or size downgrade.
