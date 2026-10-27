# Content Type: Split Test Cell

Template for a set of reel variants that share one body and CTA.

A cell is not a deliverable. It is several deliverables that exist to answer one question.

## Format Constants

Each package in the cell is a short-form video. Inherit every constant from `short-form-video.md`:

- Aspect ratio: 9:16.
- Resolution: 1080x1920.
- Length: 15 to 60 seconds.
- Safe zones: top 20 percent and bottom 15 percent reserved for platform UI.

Cell constants:

- Packages per screening cell: 3 to 5.
- Packages per decomposition cell: exactly 3.
- Publish rate: one package per day, on non-consecutive days.
- Distribution: trial reel, until a winner is promoted.

## Required Sections

1. **Cell header.** Cell id, stage, hypothesis in one line, and what a win would prove.
2. **Locked spine.** The body beat map and the CTA. Identical across every package. See `../sops/reel-retention-progression.md`.
3. **Package table.** One row per package. See the field list below.
4. **Read plan.** Primary metric, view floor, close condition, decision rule.
5. **Publish slots.** Assigned dates on the interleave, with the other live cell named.

## Package Fields

| Field | Notes |
|---|---|
| `package_id` | `P-A`, `P-B`, `P-C` within the cell |
| `visual_hook_id` | `VH-###` from the media library |
| `text_hook_id` | `TH-###` from the brand text-hook bank |
| `visual_hook_type` | Scroll stopper or head scratcher |
| `text_hook_type` | Emotion-striking, curiosity-building, or withheld-secret |
| `differentiation_delta` | Music, cover, B-roll order, caption. Assigned by rotation. |
| `publish_slot` | Date |
| `utm_content` | Unique per package |
| `result` | Filled after the 24-hour read |

## Cell Fields

- cell_id
- brand slug
- stage: `screening` or `decomposition`
- hypothesis
- audience
- locked spine: body beat map and CTA
- packages
- primary metric
- view floor
- close condition
- interleaved with
- source references

## Voice Notes

- Load the selected brand's `voice-rules.md`.
- Every text hook clears the brand claims boundary before it enters the cell.
- Text hooks are short. One line, readable in the first 3 seconds at a glance.

## Pair With

- `../sops/reel-split-test.md` for the test design.
- `../sops/instagram-publishing-safety.md` for slots and differentiation.
- `../sops/reel-hook-design.md` for drafting and typing each hook pair.
