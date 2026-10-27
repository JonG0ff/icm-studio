# Stage 02: Extract

Pull structured visual, copy, layout, and media-timeline fields from a saved intake record.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-save/output/` | `[slug]-intake.md` for current reference | What to extract from |
| Previous stage | `../01-save/output/assets/[slug]/manifest.json` | Primary context and acquired files | Local source of truth for extraction |
| Reference | `references/extraction-fields.md` | Full file | Fields to capture |
| Reference | `references/extraction-rules.md` | Full file | How to extract without inventing |
| Shared | `../../shared/stage-handoff-format.md` | Full file | Required terminal checkpoint and handoff format |

## Process

1. Read the intake file from stage 01 output.
2. Read `asset-manifest` and stop unless `workflow_state: save-approved` and `ready_for_stage_02: true`. Access `primary-context` plus relevant persistent artifacts. Do not refetch the original URL.
3. Extract visual fields: colors (hex if visible), typography, layout structure, imagery style.
4. Extract copy fields: hook, body patterns, offer, CTA, tone.
5. For audio, video, and social-video references, inspect all media artifacts in the manifest: media analysis, media timeline, frame index, scene index, motion index, audio profile, transcript, OCR text, sampled frames, and contact sheet when present. Use the local image viewer for `primary_context`, the contact sheet, and representative sampled frames. Raw package assets may be gitignored, but they remain locally viewable.
6. Record the inspected image paths in the extraction or handoff. If the image viewer is unavailable, mark visual fields `(uncertain)` and report the exact viewer/tool blocker; do not say the files are inaccessible because they are gitignored.
7. Note layout patterns: hero structure, social proof placement, form patterns, etc.
8. Note media patterns: visual beats, audio hooks, music/tone, spoken CTAs, on-screen text, motion peaks, and combined audio/visual timing.
9. Flag anything uncertain with `(uncertain)` rather than guessing.
10. Run audit checks. Revise if any fail.
11. Save extraction to output.
12. Write `[slug]-handoff.md` using `../../shared/stage-handoff-format.md` with the IDE file tool or `apply_patch`. State whether the extraction is `ready-for-review` or `blocked`, list all artifacts and uncertainties, then return the checkpoint and end the turn. Do not continue silently into Stage 03.

## Audit

| Check | Pass Condition |
|-------|---------------|
| Source fidelity | Every extracted field traces to visible content in the source |
| Local handoff | Manifest and primary-context paths resolve inside the repository |
| Stage gate | Manifest says `workflow_state: save-approved` and `ready_for_stage_02: true` |
| No invention | Uncertain fields marked `(uncertain)`, not stated as fact |
| Visual inspection | Contact sheet and representative sampled frames were opened with the local image viewer, or the exact viewer blocker is recorded |
| Section coverage | Visual, Copy, Layout, media, and Visual inspection sections all present when relevant (use "none observed" if empty) |
| Slug match | Output slug matches intake slug |
| Terminal handoff | Handoff artifact exists and the user-facing checkpoint names artifacts, uncertainties, next action, and exact reply |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Extraction | `output/[slug]-extraction.md` | Markdown per `references/extraction-fields.md` |

Stage 03 reads from `output/`. Human may edit extraction before curation.
