# Stage 05: Open Items Closeout

Close every open item from the edit package before QA.

This stage is the readiness gate between an editor packet and QA delivery. It decides what is truly blocking, what can be closed as an editor note, and what must be carried as a rights or attribution note.

It also carries the human checkpoint for Stage 04. Stage 04 does not stop on its own, so present the edit package here alongside the closeout.

Do not use this stage to QA the final render. Use it to make sure the render or QA packet can exist.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Edit package | `../04-edit-package/output/` | `[slug]-edit-package.md`, especially Open Items | Items to resolve |
| Asset manifest | `../03-asset-gathering/output/` | Asset table, gaps, generation queue | Current source and rights status |
| Voiceover packet | `../03-asset-gathering/output/` | `[slug]-elevenlabs-vo.md` when present | VO generation and validation |
| Shared | `../../shared/edit-package-format.md` | Open Items guidance | Closure fields |
| Reference | `references/closeout-checklist.md` | Full file | Closeout rules |
| Skill | `../../../../skills/workflows/video-production/audio-rip/SKILL.md` | When temp, licensed, or cleared music/stems are needed | Music source path |
| Skill | `../../../../skills/workflows/video-production/elevenlabs-voiceover/SKILL.md` | When VO is not generated or validated | Voiceover closure |
| Skill | `../../../../skills/workflows/video-production/sound-effects-mix/SKILL.md` | When SFX are required for the edit | SFX source and mix notes |
| Skill | `../../../../skills/workflows/video-production/media-sourcing/SKILL.md` | When footage, stills, b-roll, or reference clips are unresolved | Visual source path |

## Process

1. Read the edit package open items.
2. Cross-check the asset manifest gaps and generation queue.
3. Classify each item as blocker, decision required, editor-selectable, rights note, attribution note, or optional polish.
4. Assign a resolver path to every blocker or decision-required item.
5. Load the smallest matching skill when the resolver path requires one.
6. Close non-blockers with a clear reason.
7. For each blocker, add the exact next action, owner, skill, artifact needed, and closure signal.
8. Replace optional missing assets with an approved fallback or mark them out of scope.
9. Run audit checks. Revise if any fail.
10. Save the closeout artifact to output.
11. **[Checkpoint]** Present the edit package and the closeout together: edit decision list, sound, color, export, blockers, resolver plan, and readiness state. This is the last stop before render and QA.

## Resolver Map

| Missing thing | Use this skill or path | Close when |
|---------------|------------------------|------------|
| Voiceover file | `../../../../skills/workflows/video-production/elevenlabs-voiceover/SKILL.md` | VO packet is current, chosen voice is validated or accepted, and exported WAV path is recorded |
| Music bed, temp music, licensed audio, or stems | `../../../../skills/workflows/video-production/audio-rip/SKILL.md` for downloads/stems, or a manual licensed-library source note | Music file path and rights note are recorded, or no-music/VO-only is approved |
| SFX map, SFX source terms, or SFX mix notes | `../../../../skills/workflows/video-production/sound-effects-mix/SKILL.md` | SFX source path/license and placement notes are recorded, or no-SFX is approved |
| Footage, stills, b-roll, reference clips, or manual visual source options | `../../../../skills/workflows/video-production/media-sourcing/SKILL.md` | Asset row has path/URL, status, rights note, and fallback |
| MotionVFX template, film grain, LUT, manual animation, NLE plugin choice | Editor choice inside the edit tool | Item is marked editor-selectable with any style constraints |
| Rights or attribution issue | Rights note, fallback choice, or human approval | Use condition, fallback, or attribution carry-forward is explicit |

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 11 | Edit decision list, sound/color/export plan, blockers, resolver plan, closed notes, use/skip decisions, rights carry-forward, readiness state | Approve the edit package and closure, supply missing assets, pick fallbacks, run a resolver skill, revise the edit, or keep blocked |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Blocker clarity | Every true blocker has an owner, action, and closure signal |
| Resolver clarity | Every blocker or decision-required item names the skill/path that can close it |
| VO readiness | Required VO has a generated/recorded file path or a chosen fallback |
| Music decision | Music has a cleared source or is explicitly marked VO-only/no-music |
| SFX decision | SFX have sources or are explicitly dropped |
| Editor-selectable items | MotionVFX, grain, LUTs, and similar editor choices are not treated as blockers |
| Rights carry-forward | Usage limits and attribution notes are preserved without blocking the edit when a fallback exists |
| QA gate | Closeout status is ready before Stage 06 starts |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Open items closeout | `output/[slug]-open-items-closeout.md` | Markdown |
