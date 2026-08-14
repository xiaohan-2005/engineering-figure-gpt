# Conceptual Showcase Verification Template

Copy this file next to a **real generated output**, then fill it out after visual inspection.

## Run metadata

- Date/time:
- Endpoint profile: `official-openai` / `trusted-relay`
- Model:
- Quality:
- Requested size:
- Output file:
- Prompt source:

Do not record API keys, authorization headers, or secret query parameters.

## Visual verification

- [ ] The output file is a real image produced by the documented run.
- [ ] The final prompt used for generation is preserved exactly.
- [ ] All must-keep labels from the Figure Brief are present or intentionally omitted with explanation.
- [ ] Text is readable at likely paper/README display size.
- [ ] Arrow direction and module relationships match the Brief.
- [ ] No unsupported module, method, variable, formula, numeric result, or scientific claim was introduced.
- [ ] No exact plot, measured geometry, benchmark value, or long formula was redrawn conceptually when it should remain deterministic.
- [ ] Spelling and standard abbreviations are correct.
- [ ] Chinese text, when present, has no mojibake, missing glyphs, clipping, or broken punctuation.
- [ ] Mathematical symbols, when present, remain source-faithful.
- [ ] The reading order is clear without relying on decorative arrows.
- [ ] Color is restrained and semantically consistent.
- [ ] Background, margins, and whitespace are suitable for a research-paper figure.
- [ ] No watermark, unrelated logo, fake citation, or fabricated source marker appears.

## Corrections made

Record any regeneration/edit pass here. If none, write `None`.

- 

## Remaining limitations

Record anything a downstream user should still edit or verify before publication.

- 

## Final status

Choose one:

- [ ] PASS — suitable for repository showcase after packaging.
- [ ] NEEDS EDIT — do not package yet.
- [ ] REJECT — regenerate from the preserved prompt/brief.
