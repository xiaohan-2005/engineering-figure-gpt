# GPT Image 2 Guidance

Use Codex built-in image generation for normal conceptual-figure creation and editing when it is available.

For portable CLI/API work, default to `gpt-image-2`. The project intentionally uses OpenAI's official image path and does not silently fall back to older image models.

Use high quality for dense diagrams and final paper figures when appropriate. Landscape output is usually a good fit for architectures and model frameworks; other aspect ratios may fit graphical abstracts or journal layouts better.

GPT Image 2 supports generation, editing, flexible image sizes, and high-fidelity image inputs. Exact API parameters can evolve, so verify current official OpenAI documentation when a model-specific option fails.

The CLI leaves `input_fidelity` unset by default and only sends it when explicitly requested.

Do not use an image model to reproduce exact benchmark geometry, long formulas, measured values, axes, error bars, or uncertainty regions. Keep those elements local and deterministic.
