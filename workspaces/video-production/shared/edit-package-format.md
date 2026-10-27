# Edit Package Format

Use this format for `stages/04-edit-package/output/[slug]-edit-package.md`.

```markdown
# Edit Package: [title]

- slug: [slug]
- target_runtime:
- aspect_ratio:
- editor:

## Source Files

List scripts, scene plan, asset manifest, and any final render path.

## Edit Decision List

| Time | Scene | Asset ID | Cut / transition | On-screen text | Audio / SFX | Notes |
|------|-------|----------|------------------|----------------|-------------|-------|

## Captions And Text

Caption style, overlay text, safe-zone notes, and type direction.

## Recorded-Footage Map And Build

For recorded footage, link the selected recipe's source-to-output map or include it here. Identify original files, source in/out, output in/out, verified speech, omissions, units, frame rates, and any speed/rounding changes. Keep original-file and output time separate. Identify authored text or narration separately from recorded speech.

For a Remotion build, link the shared runtime composition, props, and media paths. Link the scene-plan storyboard and actual composition previews separately. Record preview frames inspected, findings, fixes, and remaining issues before a full render. A synthetic fixture checks implementation behavior; label it and leave real-speech validation pending.

For other routes, mark this section not applicable.

## Motion / VFX

MotionVFX templates, transitions, overlays, logo animation, or manual motion notes.

## Sound

Music bed, SFX, risers, silence, ducking, and voiceover mix notes.

## Color

Color grade, contrast, grain, temperature, and brand color use.

## Export

Resolution, frame rate, codec, loudness target, filename, and platform notes.

## Chapters And Continuity

For long form: chapter timecodes, transitions, continuity notes, version/change list, and delivery set (master, encodes, captions, metadata, thumbnail, credits, project handoff as requested). For short form, mark not applicable.

## Open Items

Anything still needed before final render or QA.

Use this table:

| Item | Class | Blocks QA? | Owner | Next action | Closure signal |
|------|-------|------------|-------|-------------|----------------|

Classes: blocker, decision required, editor-selectable, rights note, attribution note, optional polish.

Stage 05 closes this list before QA starts.
```

## Split Test Cells

For a split test, write one edit package for the whole cell, named `[cell-id]-edit-package.md`.

The sections above describe the **spine**: the body, CTA, VO, captions, and grade that every package inherits. Add these two sections.

```markdown
## Package Exports

| Package | Visual hook asset | Text overlay | Music bed | Cover frame | Caption | Export filename | utm_content |
|---------|-------------------|--------------|-----------|-------------|---------|-----------------|-------------|

## Differentiation Check

| Package | Opening visual | Opening text | Cover | Audio | Caption | B-roll order | Pass |
|---------|----------------|--------------|-------|-------|---------|--------------|------|
```

Rules:

- The edit decision list covers the spine only. Do not duplicate it per package.
- Every package must differ on opening visual, opening text, cover, audio, and caption. Caption-only or audio-only differences do not count as differentiation.
- Music and cover assignments come from the variant matrix and were set by rotation. Do not reassign them here based on which package looks strongest.
- One export per package. Filenames and tracking values come from `variant-matrix-format.md`.
