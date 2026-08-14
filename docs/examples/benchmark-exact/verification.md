# Verification — Exact Benchmark Comparison

Status: **verified illustrative plot example**.

Checks:

- Source values are synthetic and explicitly labeled illustrative.
- Method A values are exactly `0.91, 0.89, 0.87`.
- Method B values are exactly `0.84, 0.82, 0.80`.
- The committed vector output uses those exact bar heights and annotations.
- Categories remain Metric A / Metric B / Metric C in the supplied order.
- Legend mapping is Method A → blue and Method B → green.
- No generated scientific claim, significance label, error bar, or missing value was added.
- No image-generation model was used for numeric geometry.

Reproduction path:

```bash
python scripts/efg.py plot docs/examples/benchmark-exact/request.json \
  --spec-out docs/examples/benchmark-exact/plot-spec.regenerated.json \
  --out-path docs/examples/benchmark-exact/output-regenerated \
  --formats svg png pdf
```

The checked-in SVG is a deterministic vector showcase of the preserved values. Exact SVG coordinates/metadata can vary slightly across Matplotlib versions, but the numeric semantics must remain unchanged.
