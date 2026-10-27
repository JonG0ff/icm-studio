# Stage 02: Shot And Scene Plan

Turn the locked script into scenes, shots, timing, cuts, and continuity. Review the script and scene plan together.

## Inputs

| Source | Location | Scope | Why |
|---|---|---|---|
| Script | `../01-script-lock/output/` | `[slug]-locked-script.md` | Words, timing, overlays |
| Brief | `../00-brief/output/[slug]/` | Accepted direction and constraints | Visual language and delivery |
| Format | `../../shared/formats/CONTEXT.md` | Selected recipe | Pacing, chapters, continuity, safe zones |
| Motion graphics only | `../../../../skills/ai-capabilities/design/motion-graphic-design/SKILL.md` | Direction and craft | Typography, composition, and scene choreography |
| Brand | `../../../../libraries/business-memory/brand-vault/CONTEXT.md` | Selected tokens | Approved color/type |
| Reference | `references/scene-plan-format.md` | Full | Scene table |
| Split test only | `../../../../libraries/business-memory/sops/reel-split-test.md` and `../../../../libraries/business-memory/sops/instagram-publishing-safety.md` | Full | Experiment and publishing rules |
| Split test only | `../../shared/variant-matrix-format.md` | Full | Packages, rotation, slots, read plan |
| Split test only | `../../../../libraries/media/assets/index.md` and selected brand's text-hook-bank | Hook rows | Reuse and pairing history |

## Process

1. Read the script and accepted visual direction. Keep prior approvals intact.
2. Map every beat to scenes with time ranges. Long form also uses chapter/sequence IDs.
3. Specify source type, shot/crop, transition, text, motion, audio cue, and asset need per scene. For recorded footage, keep original-file ranges separate from planned output timing. Use the selected recipe's storyboard fields; label source frames and placeholders as planning evidence.
4. Set pacing and hold reasons using the selected recipe. For long form, record continuity across people, props, location, screen state, and audio.
5. List asset needs and fallbacks. Leave sourcing to Stage 03.
6. For a split test, create the variant matrix using the section below.
7. Audit, save, and present script, scenes, rhythm, continuity, missing assets, and any variant matrix together.

## Split Test Runs

Skip for a single video. The scene plan describes the locked body/CTA spine once and marks the hook slot.

1. Check visual and text hook banks. Build packages from their approved shape.
2. Reject visual/text pairings that already ran. Assign differentiation by rotation.
3. Interleave publish slots with the other live cell; no consecutive slots from one cell.
4. Set primary metric, view floor, and close condition before publishing.
5. Write `output/[cell-id]-variant-matrix.md`. Changing the spine after asset generation invalidates the cell.

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|---|---|---|---|
| 7 | Script, scenes, pacing, continuity, gaps, and test design if applicable | Approve or revise before sourcing | Taste |

## Audit

| Check | Pass Condition |
|---|---|
| Coverage and timing | Every beat has a scene and total runtime fits |
| Recorded footage | Source/output ranges, exact speech, authored text, and planning frames are distinct; storyboard exists before assembly |
| Format fit | Pacing, text safe zones, chapters, and holds follow the selected recipe and brief |
| Continuity | Long-form sequences preserve relevant visual/audio state |
| Direction traced | Mood, color, type, and locks match accepted direction |
| Assets | Every scene has an asset need or fallback |
| Cell integrity | Spine fixed, packages complete, pairings fresh, slots interleaved, read plan set |

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Scene plan | `output/[slug]-scene-plan.md` | `references/scene-plan-format.md` |
| Variant matrix, split test only | `output/[cell-id]-variant-matrix.md` | `../../shared/variant-matrix-format.md` |
