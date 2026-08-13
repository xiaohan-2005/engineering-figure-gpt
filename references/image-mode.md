# Image Mode

Use image mode for conceptual research figures rather than exact numeric charts.

Recommended targets:

- system architecture
- algorithm workflow
- graphical abstract
- mathematical-model framework
- mechanism or process diagram
- reference-inspired redraw
- image edit

## Preferred execution path

Inside Codex, use the installed built-in image-generation capability for normal generation and editing. This keeps the skill agent-native and avoids unnecessary provider wrappers.

## Portable fallback

For reproducibility, local testing, or environments without the built-in image tool, use:

```bash
python scripts/generate_image.py "figure prompt" --dry-run
```

The fallback is GPT-only, defaults to `gpt-image-2`, and rejects custom base URLs. Remove `--dry-run` only after configuring an OpenAI API key and intentionally choosing to spend image API credits.

## Workflow

1. Extract scientific entities, relationships, labels, and reading order.
2. Select the closest prompt template.
3. Preserve source-grounded terminology and relationships.
4. Generate or edit through the preferred GPT image path.
5. Inspect labels, arrows, hierarchy, symbols, and accidental invented content.
6. Regenerate or edit when scientific fidelity is inadequate.

Prefer white backgrounds, concise labels, clean arrows, restrained styling, and readability at paper width.

Do not ask image generation to reproduce exact benchmark geometry, long formulas, exact measured values, axes, or error bars.
