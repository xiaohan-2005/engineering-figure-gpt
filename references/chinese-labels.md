# Chinese Academic Figure Labels

Chinese and bilingual research figures are a first-class scenario.

## Label rules

- Keep Chinese labels short; prefer noun phrases over full sentences.
- Preserve standard English abbreviations when they are clearer than forced translations.
- Preserve mathematical symbols, subscripts, units, and model names exactly.
- Avoid mixing multiple font families inside one figure unless necessary for formulas.
- Before final use, check every generated Chinese label for missing characters, duplicated characters, malformed punctuation, and encoding problems.

## Layout rules

Chinese labels are often wider than equivalent English abbreviations. Allow extra horizontal space and avoid narrow boxes.

For flowcharts and architecture figures:

- use fewer words per node
- increase module width before shrinking font size
- avoid long vertical text
- keep arrows away from label bounding boxes

## Plot rules

For exact local plots, prefer a font fallback chain that includes common CJK fonts. Keep SVG text editable when possible.

Check:

- minus signs
- Greek letters
- subscripts and superscripts
- Chinese punctuation
- units in parentheses
- legend clipping
- rotated tick-label overlap

## Formula safety

Do not ask an image model to reproduce a long formula exactly. Reserve a placeholder or compose a locally rendered formula afterward.
