# Stage 06: QA Delivery

Review the complete render or closed production packet against the accepted brief and selected format.

## Inputs

| Source | Location | Scope | Why |
|---|---|---|---|
| Closeout | `../05-open-items-closeout/output/` | This job | Readiness gate |
| Edit packet | `../04-edit-package/output/` | This job | Delivery decisions |
| Brief | `../00-brief/output/[slug]/` | Accepted direction and constraints | Required outcome |
| Format | `../../shared/formats/CONTEXT.md` | Selected recipe | Format-specific QA |
| Render | User-provided or edit-packet path | Complete video, if available | Visual/audio review |
| Reference | `references/qa-checklist.md` | Full | QA gates |
| Footage short only | `../../../../libraries/business-memory/sops/footage-short-quality.md` | Full | Approved editorial, subtitle, and playback quality |
| Handoff | `../../../../_core/handoff-checkpoint.md` | Full | Delivery response |
| Split test only | `../02-shot-and-scene-plan/output/` | Variant matrix | Packages and read plan |
| Split test only | `../../publishing/split-tests/queue.md` and `../../publishing/split-test-cell-template.md` | Current slots and ledger format | Queue continuity |

## Process

1. Read closeout first. If any blocker remains, return to Stage 05.
2. Read the brief, selected recipe, and edit packet. Inspect the complete render when supplied.
3. If there is no render, review packet readiness and explicitly state that final-video QA remains open.
4. Check format, story, continuity, captions, audio, claims, rights, and exports. For recorded footage, verify source/output mapping, speech meaning, caption wording/timing and highlight bounds, crop, and face clearance. Complete full audiovisual playback of the final export before presenting it. Check stalls, freezes, gaps, drift, and endings. If playback cannot be performed, mark final-video QA `blocked` and state the needed action; do not call the render ready. Long-form QA covers all chapters and transitions.
5. Record required fixes separately from optional polish.
6. For a split test, check every package: spine integrity, differentiation, rotation, interleave, tracking, and publishing. Write the ledger/read plan before first publication and preserve queue continuity. A cell ships whole.
7. Audit and save delivery notes with `ready`, `ready-after-fixes`, or `blocked`, review scope, artifacts, and pending human decisions. Render readiness requires completed playback QA; packet readiness does not establish final-video readiness.
8. Present the delivery checkpoint under the job's review mode. Acceptance and publishing decisions remain explicit in job artifacts; no tracking card is required.

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|---|---|---|---|
| 8 | Review scope, artifacts, fixes/blockers, next action, and exact reply; cell gates when applicable | Accept delivery or request fixes | Ship |

## Audit

| Check | Pass Condition |
|---|---|
| Closeout | No unresolved blockers |
| Scope honest | Packet readiness and final-render QA clearly distinguished |
| Recorded footage | Quote integrity, caption timing, and highlight bounds checked against sources; complete audiovisual review recorded; unperformed playback blocks final-video readiness |
| Format | Aspect ratio, runtime, safe zones, chapters/continuity, export targets match brief |
| Audio and text | Voice clear, text legible, caption/credit files complete |
| Rights and claims | Use limits, attribution, and approved business claims preserved |
| State | Delivery status, fixes, pending decisions, next action explicit |
| Cell | All packages pass, ledger/read plan exists, queue remains discoverable |

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Delivery notes | `output/[slug]-delivery-notes.md` | Markdown with scope, findings, state, pending approval |
| Cell ledger, split test only | `../../publishing/split-tests/[cell-id].md` | `../../publishing/split-test-cell-template.md` |
