# Figure Brief Spec

A figure brief is the structured contract between paper reasoning and figure production.

Required fields:

- `figure_goal`: what the figure should explain or prove.
- `paper_claim`: the claim or contribution it supports.
- `figure_type`: architecture, workflow, graphical abstract, mathematical-model framework, benchmark plot, or another explicit type.
- `mode`: `image`, `plot`, or `mixed`.
- `panels`: modules/panels in reading order.
- `must_keep_labels`: terms that must remain faithful.
- `data`: numeric data or `not_applicable`.
- `style_constraints`: language, venue, aspect ratio, density, and export constraints.
- `output_formats`: png/pdf/svg/prompt-only as needed.
- `verification_checklist`: checks before paper use.

Use `image` for conceptual figures, `plot` for exact quantitative figures, and `mixed` for figures that combine both. Never invent missing numeric data.
