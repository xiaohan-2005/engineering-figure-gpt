# Verification — Sensitivity / Robustness Analysis

Status: **verified illustrative plot example**.

Checks:

- All values are synthetic and explicitly disclosed as illustrative.
- Sensitivity indices are exactly `0.62, 0.48, 0.36, 0.25, 0.18` for x1–x5.
- Perturbation x values are exactly `-20, -10, 0, 10, 20` percent.
- All three response series equal `1.00` at zero perturbation, matching the preserved request.
- The committed vector output preserves the direction and relative geometry implied by the exact arrays.
- No confidence intervals, significance labels, Sobol claims, or real-world conclusions were invented.
- No image-generation model was used for numeric geometry.

Reproduction path:

```bash
python scripts/efg.py plot docs/examples/sensitivity-robustness/request.json \
  --spec-out docs/examples/sensitivity-robustness/plot-spec.regenerated.json \
  --out-path docs/examples/sensitivity-robustness/output-regenerated \
  --formats svg png pdf
```

The checked-in SVG is a deterministic vector showcase of the preserved values. Exact SVG coordinates/metadata may differ across Matplotlib versions; numeric semantics must not.
