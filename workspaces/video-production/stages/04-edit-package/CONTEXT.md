# Stage 04: Edit Package

Build the editor-ready packet, including timing, assets, text, sound, color, continuity, and delivery files.

## Inputs

| Source | Location | Scope | Why |
|---|---|---|---|
| Script | `../01-script-lock/output/` | This job | Words, beats, chapters, text |
| Scenes | `../02-shot-and-scene-plan/output/` | This job | Shots, cuts, continuity |
| Assets | `../03-asset-gathering/output/` | Manifest and relevant supporting packets | Sources and readiness |
| Brief | `../00-brief/output/[slug]/` | Accepted visual direction and delivery | Output constraints |
| Format | `../../shared/formats/CONTEXT.md` | Selected recipe | Pacing and delivery checks |
| Brand | `../../../../libraries/business-memory/brand-vault/CONTEXT.md` | Selected tokens | Color/type/logo rules |
| Shared | `../../shared/edit-package-format.md` | Full | Handoff fields |
| Reference | `references/edit-notes.md` | Full | Tool, sound, color, export notes |
| Setup | `../../setup/questionnaire.md` | Configured preferences only | Optional tool defaults |
| SFX skill | `../../../../skills/workflows/video-production/sound-effects-mix/SKILL.md` | Only when needed | SFX mix notes |
| Split test only | `../02-shot-and-scene-plan/output/` and `../../../../libraries/business-memory/sops/instagram-publishing-safety.md` | Variant matrix and differentiation | Package exports |

## Process

1. Read the script, scenes, manifest, and relevant asset packets.
2. Map every scene to timing, asset IDs, cuts, text, and audio cues. Keep chapter/sequence IDs when present.
3. Choose the editor and plugins from job needs and configured preferences.
4. Specify captions, overlays, platform safe zones, accessibility, brand type, and approved color treatment.
5. Specify voice, music, SFX, ambience, transitions, silence, ducking, and agreed loudness targets.
6. For long form, include continuity notes, chapter timecodes, version/change list, and requested chapter/thumbnail/caption/credit deliverables.
7. Set each export's resolution, aspect ratio, frame rate, codec, audio target, filename, and destination.
8. Classify open items as blocker, decision-required, editor-selectable, rights, attribution, or optional polish.
9. For a recorded-footage Remotion build, follow the selected recipe: save the source-to-output map, assemble from the scene plan in the shared runtime, inspect actual composition previews before a full render, and record preview paths, findings, and remaining blockers. Planning frames do not count as composition previews.
10. Audit and save, then continue to Stage 05 for the combined edit/closeout checkpoint.

## Split Test Runs

Skip for a single video. Build one spine timeline and swap only the approved hook/differentiation layer.

1. Keep body, CTA, VO, captions, and grade shared.
2. Apply each package's rotated hook, music, cover, and allowed B-roll order. Write a caption per package.
3. Export one file per package with filename and `utm_content` from the matrix.
4. Confirm differentiation for every package. Produce the cell as one batch.

## Audit

| Check | Pass Condition |
|---|---|
| Coverage | Every scene maps to a manifest asset or explicit fallback |
| Sound and color | Audio decisions explicit; brand tokens respected |
| Format | Safe zones, pacing, chapters, continuity, captions, and delivery match the brief/recipe |
| Export | Every requested version has complete settings and filename |
| Closeout | Open items classified for Stage 05 |
| Recorded-footage build | Executed source/output map and composition pointers exist; actual previews inspected before a full render; unresolved findings remain visible |
| Cell | Spine identical, differentiation rotated, package exports complete |

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Edit package | `output/[slug]-edit-package.md` | `../../shared/edit-package-format.md` |
| Cell edit package, split test only | `output/[cell-id]-edit-package.md` | Spine and all package exports |
