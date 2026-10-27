# Hybrid Short: Selected Footage Prototype

Status: experimental. This recipe describes the first selected-footage build. It is not a proven production loop or a promoted reference method.

Use it for one already selected talking clip with captions, selective emphasis, and optional supporting media. Video Production owns the job. The shared `remotion/` runtime hosts its composition. Long-recording candidate ranking and automatic story selection are outside this prototype.

Load the approved [footage-short quality SOP](../../../../libraries/business-memory/sops/footage-short-quality.md). It owns the default hook/payoff, interaction goal, purposeful-graphics, accurate-caption, and full-playback standards for this route.

## Inputs And Scope

- Start at the existing brief stage. Record `format: short-form`, selected recipe `hybrid-short`, source clip, intended audience, platform, duration, aspect ratio, delivery files, and review mode. Name the recipe in the script and scene artifacts while retaining their short-form headers.
- Record whether the source is permitted for this job. A saved swipe is a reference, not cleared production footage.
- Check the media catalog before sourcing supporting assets. Keep selections, rights, timing, and placement in the job's manifest and edit package.
- Choose a look from the brief. This recipe does not imply approval of a brand, reference pattern, or reusable library piece.
- A synthetic test fixture can check runtime behavior. Label it as a fixture; it does not prove the edit works with real speech or establish production acceptance.
- Missing footage, verified words, rights, or delivery decisions stay explicit. Do not invent inputs or mark a real-video proof complete from a fixture.

## Stage 01: Select And Verify Recorded Speech

Use the existing locked-script artifact. Its recorded-speech section replaces authored narration for this route.

1. Inventory each original file with a stable source ID, local path, duration, frame rate, and audio presence. Record the verified media facts; do not infer them from a filename.
2. Transcribe or inspect the selected range and its surrounding context. Verify automatic transcript words against the recording. Preserve qualifications, cause, and the speaker's meaning.
3. Record exact selected speech and original-file in/out points. Identify omissions and cut reasons. A transcript draft remains unverified until checked.
4. Separate recorded speech from authored hooks, emphasis text, cards, narration, or CTA. Authored text must not be presented as a quotation unless it matches verified source words.
5. Identify a concrete opening hook, payoff, relevant interaction goal, and whether the excerpt stands alone. Remove recap introductions and filler that add no meaning. Keep unresolved transcript or context issues visible before locking the selection.

## Stage 02: Plan Before Assembly

Use the existing scene-plan artifact as the editorial and visual plan. Add a storyboard section for this route.

| Field | Record |
|---|---|
| Beat / scene | Stable ID shared with script and edit package |
| Source | Source ID and original-file in/out range |
| Output | Planned output in/out range |
| Speech | Verified words heard in the beat |
| Visual | Speaker crop, supporting media, card, or deliberate hold |
| Text | Phrase captions and separate authored emphasis |
| Assets / audio | Manifest IDs, placement, sound, and fallbacks |
| Planning frame | Source frame or clearly labelled placeholder |

Plan mobile-safe text, face clearance, crop changes, and readable holds. Supporting media should explain the current idea. Remove generic headers, repeated speaker names, footer explanations, progress rows, and labels that only fill space. Preserve source-required attribution through the job's documented placement decision. Do not add unsupported claims or obscure essential speech context.

Planning frames communicate intent. They are not evidence that the composition has been built or rendered. Preserve the existing script-and-scenes checkpoint under the job's review mode.

## Stage 03: Record Sources And Rights

Use the existing asset manifest. Record source IDs for brought footage and manifest IDs for supporting images, footage, graphics, music, and SFX. Keep raw media in an ignored local path. Record clear no-music or no-SFX decisions when applicable. Keep reference-only assets and unclear rights out of a ready production selection.

## Stage 04: Assemble And Preview

Use the existing edit package and the shared Remotion runtime. Do not create a workspace-local runtime.

1. Build the selected sequence from the planned source ranges. Preserve original audio and speech timing unless a different treatment is explicitly recorded.
2. Write the source-to-output edit map in the package or a linked artifact. The package points to the executable composition and props; do not duplicate their editable state in several places.
3. Add captions from words checked against audio. Verify timing rather than treating automatic timestamps as alignment. Keep authored emphasis separate. Highlight bounds fit the active word; put interword spaces outside its colored box and inspect actual rendered word changes and wraps.
4. Use explicit crop positions for the speaker. Supporting media, callouts, and full-frame cards follow the scene plan and asset manifest.
5. Render actual composition preview frames before a full render. Inspect opening, each visual treatment, every source cut, text-heavy frames, and the ending. Inspect frames around boundaries where timing or overlap is uncertain.
6. Save preview paths and findings in the edit package. Label previews as actual composition output. Record fixes and unresolved items for Stage 05.

Preserve the existing edit-package and closeout checkpoint. Preview inspection is an audit within these stages, not an additional approval gate.

## Source-To-Output Edit Map

Keep original-file time and output time in separate fields. Ranges use an inclusive start and exclusive end. State units and frame rates. If using seconds, record how they convert to frames. Record any rounding, trim, offset, or playback-speed change.

| Segment | Source ID | Source in | Source out | Output in | Output out | Recorded speech | Omission / timing note |
|---|---|---|---|---|---|---|---|

- Each output segment of recorded speech resolves to one original file and its source range.
- At normal speed, source and output durations agree within the stated frame-rounding tolerance.
- For gaps, repeated material, inserts, or transitions, state what is heard and seen. Do not silently stretch, overlap, or duplicate speech.
- Captions follow output time. Keep the original-file timing evidence available for verification.
- Authored narration or a silent card is identified as authored content. It does not acquire a fictional source quotation or source timecode.
- Keep the planned map and executed result consistent. Record changes in the edit package rather than silently changing an accepted script.

## Stages 05 And 06: Close, Render, And Verify

Close source, transcript, asset, and rights blockers through the existing closeout stage. Follow its readiness state and the job's existing review mode before rendering or delivery QA. Keep render settings and final paths in the edit package. Apply Pattern 19's spend guardrail.

Final-video QA covers the complete render with audio, not only preview stills:

- Confirm the opening, explanation, and payoff form a complete story.
- Compare every spoken segment with its source range, including cuts and nearby context. Check omissions, repeated words, clipped syllables, and meaning.
- Check caption wording, output timing, phrase breaks, and any claimed word alignment. Check authored overlays separately.
- Inspect crop, face clearance, supporting media, mobile text, and platform safe zones throughout.
- Listen for speech clarity, cut clicks, unintended silence, clipped ending, and music/SFX masking speech.
- Check export dimensions, duration, frame rate, audio presence, delivery files, rights notes, and credits against the brief.

Complete audiovisual playback of the final export is mandatory before presenting it for review or delivery. Record the actual file/version, scope, findings, and fixes in delivery notes. If playback cannot be performed, mark final-video QA `blocked`, state the limitation and needed action, and do not present the render as ready. Technical checks, sampled frames, and a fixture render cannot close that item. A packet-only review may describe packet readiness while final-video QA stays blocked. Owner acceptance and any ship decision remain explicit; this recipe grants neither.

## Existing Contracts

- [Stage routing](../../CONTEXT.md)
- [Script format](../../stages/01-script-lock/references/locked-script-format.md)
- [Scene-plan format](../../stages/02-shot-and-scene-plan/references/scene-plan-format.md)
- [Asset manifest](../asset-manifest-format.md)
- [Edit package](../edit-package-format.md)
- [Review and spend rules](../../../../_core/CONVENTIONS.md#pattern-19-files-are-the-state)
- [Shared runtime](../../../../remotion/README.md)
