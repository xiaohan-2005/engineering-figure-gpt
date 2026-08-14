# Editable Figure Handoff

Research figures often need one final human-editable pass after generation. Treat a raster image as the visual master, not always as the last editable artifact.

## When to use

Use an editable handoff when:

- Chinese or bilingual labels may still need wording or font adjustment;
- arrows, callouts, or panel letters may need small corrections;
- the journal requires exact width, type size, or vector labels;
- a generated conceptual panel must be combined with exact locally rendered plots;
- the user expects later editing in PowerPoint, Illustrator, Inkscape, Figma, or another layout tool.

## Recommended handoff package

For conceptual figures, preserve:

```text
brief.md
prompt.txt
output.png
verification.md
editable-handoff.md
```

For exact plots, preserve the request and normalized spec as well:

```text
request.json
plot-spec.json
output.svg
output.pdf
output.png
verification.md
```

## Handoff note contents

`editable-handoff.md` should record:

- final canvas orientation and approximate aspect ratio;
- reading order;
- canonical labels that must not change;
- module groups and arrow relationships;
- formulas or symbols that must remain source-faithful;
- recommended font family/fallback for Chinese text;
- which parts may be manually edited;
- which parts must be regenerated or rerendered rather than redrawn by eye.

## Mixed figures

For a figure containing conceptual and quantitative panels:

1. render quantitative panels locally to SVG/PDF;
2. keep the exact plot files untouched;
3. generate conceptual panels separately;
4. compose the panels in an editable layout tool;
5. add panel letters and final labels after composition;
6. verify that no exact plot was raster-redrawn by the image model.

## Formula rule

Long formulas, exact matrix notation, measured geometry, axes, error bars, and benchmark values should remain editable or deterministic. If an image model renders a malformed formula, replace the formula during handoff rather than accepting the generated text.

## Chinese typography

Prefer a known CJK-capable font in the final editing environment. Check:

- missing glyphs;
- punctuation width;
- excessive label length;
- clipping after export;
- inconsistent Chinese/English font metrics;
- superscripts, subscripts, and mathematical symbols.

## Export recommendation

Keep at least one publication-ready raster and one editable/vector path whenever possible:

```text
PNG  -> preview/submission compatibility
SVG  -> editable local plots and labels
PDF  -> print/vector handoff
```

Generated conceptual artwork may remain raster if no reliable vector reconstruction exists, but labels and exact quantitative elements should stay editable whenever practical.
