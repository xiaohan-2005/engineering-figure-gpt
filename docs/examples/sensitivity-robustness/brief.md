# Figure Brief — Sensitivity / Robustness Analysis

- **figure_goal:** demonstrate a mathematical-modeling exact-plot pattern using a ranked sensitivity panel plus perturbation-response curves.
- **paper_claim:** none; all values are synthetic and illustrative.
- **figure_type:** two-panel sensitivity/robustness plot.
- **mode:** plot.
- **panels:** Panel A ranks five normalized sensitivity indices; Panel B shows normalized output under several illustrative perturbation settings.
- **must_keep_labels:** x1–x5, Sensitivity Index, Parameter change (%), Normalized output.
- **data:** exact values are preserved in `request.json` and `plot-spec.json`.
- **style_constraints:** publication-style white background, restrained semantic colors, exact values only, no invented confidence intervals or significance marks.
- **output_formats:** committed SVG; the normal renderer can also export PNG/PDF.
- **verification_checklist:** source values unchanged; x coordinates unchanged; series identity consistent; baseline at zero perturbation remains 1.00 for all three illustrative series.

> This case demonstrates workflow structure only. It is not a Sobol result or a claim about any real model.
