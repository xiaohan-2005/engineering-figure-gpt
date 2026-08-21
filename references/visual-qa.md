# Visual QA for Generated Research Figures

A successful API response is not a successful research figure. Inspect every final conceptual image or edit before paper use.

## Acceptance order

Check in this order so cosmetic polish never hides a scientific failure.

### 1. Scientific fidelity

- every required module is present;
- no unsupported module, metric, formula, value, interface, or causal claim was invented;
- arrows represent real data/control/causal relationships;
- direction and loopbacks are correct;
- canonical labels, model names, symbols, units, and abbreviations are source-faithful;
- exact quantitative content has not been visually hallucinated.

Any failure here requires correction before style review.

### 2. Text integrity

Inspect every important label.

- no missing characters;
- no duplicated characters;
- no malformed Chinese;
- no corrupted punctuation;
- no hallucinated fine print;
- no clipped text;
- no label extending outside its module;
- no essential text rendered so small that it is hard to read at approximately 50% native scale;
- standard English abbreviations and formula symbols remain intact where appropriate.

If the image model repeatedly fails on a long formula or dense exact text, remove it from the raster generation path and add it later through an editable/deterministic handoff.

### 3. Layout integrity

- clear primary reading direction;
- safe outer margin on every side;
- no cropped modules or arrowheads;
- no unintended overlap;
- repeated modules aligned consistently;
- enough whitespace between functional groups;
- main path visually dominant;
- secondary branches visually secondary;
- no large accidental empty region caused by poor composition.

### 4. Arrow and line quality

- arrowheads are visible;
- line weights are consistent;
- arrows do not cross labels unless unavoidable and explicitly meaningful;
- arrows do not terminate ambiguously between modules;
- no broken, doubled, ghosted, or decorative arrows;
- feedback loops are visually unambiguous.

### 5. Color and contrast

- text/background contrast is strong;
- the same semantic color means the same thing throughout the figure;
- palette is restrained and not infographic-neon unless requested;
- no important small text sits on dark or saturated fills;
- no gradient/noise effect reduces legibility.

### 6. Raster clarity

Visually inspect at native scale and approximately 50% scale.

Reject or revise if there is:

- visible blur around text;
- ghosting/double edges;
- compression-like artifacts;
- smeared thin lines;
- unreadable micro-text;
- inconsistent sharpness between panels;
- obviously soft output compared with the requested final quality.

Then run objective metadata verification when a pixel/format requirement exists:

```bash
python scripts/efg.py verify-image output/figure.png --expected-size 1536x1024 --require-format png
```

### 7. Edit preservation check

For an edited figure, compare source and result.

`correct` mode fails if anything outside the requested correction changes materially.

Check specifically:

- unrelated module positions;
- unaffected labels;
- arrow endpoints;
- palette;
- typography;
- canvas/aspect ratio;
- icon/shape style;
- scientific relationships.

For `revise`, `restyle`, and `redraw`, use the explicit `--preserve` and `--allow-change` sets as the acceptance contract.

## Failure response

Do not simply regenerate from scratch for every failure.

- isolated typo / wrong arrow / minor clipping -> `edit --mode correct`
- requested content change -> `edit --mode revise`
- style-only problem -> `edit --mode restyle`
- globally poor layout or unusable draft -> `edit --mode redraw` or regenerate with a revised brief

When only one region is wrong, preserve everything else.

## Final acceptance

A final conceptual research figure is ready only when:

1. scientific fidelity passes;
2. text integrity passes;
3. layout and arrow checks pass;
4. the image remains understandable and labels remain readable at the intended paper scale;
5. explicit pixel/format/aspect requirements pass metadata verification;
6. edits preserve everything outside the allowed change set.
