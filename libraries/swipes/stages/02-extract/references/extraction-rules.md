# Extraction Rules

How to extract without inventing or over-interpreting.

## Do

- Quote visible copy verbatim when extracting hooks and CTAs
- Describe colors as seen (hex if readable, otherwise "dark blue background")
- Note layout structure ("hero left text, right image")
- Flag `(uncertain)` when source is low resolution or partial
- Separate observation from interpretation
- Classify `hook-type` using only the vocabulary in `extraction-fields.md`. Use "none observed" when the opening does not fit a listed type; do not stretch a type to make it fit
- Measure `reset cadence` from the frame and scene indexes, not from impression

## Do not

- Invent offers or pricing not visible in the source
- Assume brand fonts without evidence
- Copy competitor brand names into "patterns worth reusing" as recommendations
- Fill empty sections with generic marketing advice
- Treat generated `media-analysis.md` as final truth. It is a draft handoff; verify against frames, transcript, audio profile, and timeline.
- Gitignored does not mean inaccessible. Git status controls versioning, not local file access. Use the local image viewer on `primary_context` (usually `context/contact-sheet.jpg`) and then open representative sampled frames from the manifest before making visual claims.
- For video/social-video, inspect the contact sheet first, then use the frame index and image viewer to inspect the opening frame, major scene-change frames, and closing frame. Record which visual artifacts were actually inspected in the extraction or handoff.

## Source types

| Type | Approach |
|------|----------|
| Webpage | Inspect the acquired full-page screenshot from the manifest |
| Image/screenshot | Inspect the acquired image; describe visible elements only |
| PDF | Inspect rendered page images and extracted text from the manifest |
| Audio | Inspect media analysis, media timeline, audio profile, and transcript when present |
| Video/social video | Inspect media analysis, media timeline, frame index, scene index, motion index, contact sheet, sampled frames with the local image viewer, audio profile, OCR text, probe, and transcript when present |
| Pasted copy | Structure what was pasted; no external inference |

Do not refetch a URL during extraction. If the local image viewer is available, failure to use it is an agent error, not an acquisition blocker. If the viewer itself is unavailable or an artifact is missing, return to Stage 01 acquisition or report the exact tool/file blocker; do not claim to have visually inspected the source.
