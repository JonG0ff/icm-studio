# QA Checklist

Check the final render or the delivery packet.

## Gate

- Stage 05 closeout says `ready-for-qa-packet` or `ready-for-render-qa`.
- No required VO, music, SFX, footage, or rights blocker remains unresolved.
- Any skipped optional asset has an approved fallback or omit decision.
- Before presenting a render for review or delivery, complete full audiovisual playback of the actual final export. If playback cannot be performed, final-video QA is `blocked`; state the limitation and next action. Technical checks and sampled frames cannot establish readiness.
- For footage-led shorts, load the approved [quality SOP](../../../../../libraries/business-memory/sops/footage-short-quality.md).

## Visual

- Aspect ratio, runtime, resolution, safe zones, and versions match the brief.
- Important text avoids top and bottom platform UI zones.
- Opening text follows the selected format recipe and is legible.
- The opening promise reads as intended for the selected format.
- The payoff the hook promised is delivered.
- Pacing and holds fit the selected recipe; rapid short-form resets are not imposed on long-form scenes.
- Cuts match the approved scene plan.
- Logo or end card appears only where approved.
- Footage-led shorts have a concrete hook and delivered payoff. Graphics carry meaning; generic headers, repeated names, progress rows, and footer explanations do not crowd the speaker or captions.
- Subtitle words and timing are checked against audio. Highlight boxes fit the active word, with interword spaces outside the box. Inspect word changes and line wraps.
- No unintended frozen video, stalls, missing motion, or abrupt visual ending remains.

## Audio

- Voice is clear.
- Music and SFX do not cover the voice.
- Silence is intentional.
- Final line is not clipped.
- No unintended audio gap, repeated syllable, audio/video drift, or mismatched audio/video ending remains. Check suspicious moments against the source.

## Brand

- Voice rules are respected.
- Brand colors and type direction match Business Memory.
- No unapproved offer, product claim, price, or division language appears.

## Chapters And Continuity

- For long form, every chapter has a purpose, takeaway, and working transition.
- People, props, location, screen state, grade, and ambience stay consistent across sequences.
- Review the complete video, not only a few samples.
- Record the exact final export/version watched and heard, findings, and fixes. Replay the changed result after final encoding or audio processing.

## Delivery

- Export settings are stated.
- Filenames and versions are clear.
- Requested caption files, chapter metadata, thumbnails, credits, and project handoff are present.
- Packet-only review establishes packet readiness only; unperformed final-export playback remains blocked.
- A render is not ready for review or delivery until full playback QA is complete; disclose a blocked playback check honestly rather than treating metrics as a pass.
- Open asset or rights risks are named and match the Stage 05 closeout notes.

## Split Test Cells

Skip this section for a normal single-reel run. For a cell, run every check on every package. A cell ships whole or not at all.

### Spine integrity

- Body, CTA, VO, and grade are identical across every package.
- Runtime matches across packages, allowing only for hook-length differences.
- If any spine element differs, the cell is invalid. Stop and rebuild, do not publish.

### Differentiation gate

Every package must pass every row. See `../../../../../libraries/business-memory/sops/instagram-publishing-safety.md`.

- Opening 3 seconds use a different visual hook clip, not a recrop of another package.
- Text hook is different wording, not moved or restyled.
- Cover frame is unique per package.
- Music bed differs across packages.
- Caption is written per package, not copy-pasted.
- B-roll order varies where the beat map allows it.

A package differing only by caption, cover, or audio has not been differentiated. Send it back.

### Interleave check

- No two publish slots from this cell fall on consecutive days.
- Slots alternate with the other live cell.
- No slot is empty in the queue window.

### Rotation check

- No visual/text pairing in this cell repeats an earlier cell.
- `used_in_cells` and `paired_text_hooks` are updated on every hook record used.

### Tracking

- Each package has a unique `utm_content`.
- Export filenames match the variant matrix.
- Primary metric, view floor, and close condition are recorded on the cell ledger before the first package publishes.

### Publishing

- Every package is set to publish as a trial reel, not a normal post.
- No package is scheduled to share with everyone before its read.
