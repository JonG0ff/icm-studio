# Bring Intake

How a stage ingests a file you made somewhere else. Every stage points here.

## When It Applies

- You attached a file in chat for this stage.
- Or a file for this stage is in `input/[slug]/`.
- A run can mix: bring some stages, make others.

## Steps

1. Name the file and the stage it's for. Ask if that's unclear.
2. Copy it into the stage's `output/[slug]/` folder under the standard name for that stage.
3. Keep the original in `input/[slug]/` untouched.
4. Map it onto the stage's output format. Keep your words as written. Only add structure: IDs, headers, field labels.
5. Run the stage audit.
6. List the gaps, one per bullet. Example: "line b-07 has no speaker".
7. Wait. You fill the gaps or reply "fine as is".
8. Run the stage's normal person check.

## Rules

- Never rewrite brought content to "improve" it. Flag, don't fix.
- Brought files are run assets, not library pieces. They skip workshop approval.
- Brought files still pass `rights-rules.md`.
- Mark the source as `brought` wherever the stage records sources (for example, the voice manifest).
- Bulky files (wav, mp3, mp4, png, psd) stay gitignored in `input/`. Markdown is tracked.

## Standard Names by Stage

| Stage | Standard name |
|---|---|
| workshop 01 concept | `concept.md` |
| workshop 02 design sheet | `design-sheet.md` plus art files |
| production 01 brief | `brief.md` |
| production 02 script | `script.md` |
| production 03 voice | `[line-id].wav` or `full-track.wav` |
| production 05 blocking | `cues.md` |
| production 06 scene | Music, SFX or art, logged in `sfx-map.md` or `build.md` |
