# Open Items Closeout Checklist

Use this checklist after the edit package names open items.

## Classify

| Class | Means | Examples |
|-------|-------|----------|
| Blocker | The edit or QA packet cannot continue until this is done | Missing required VO WAV, missing hero footage with no fallback, unresolved must-use rights issue |
| Decision required | The edit can continue after a use/skip choice | Source music or mark VO-only, source launch SFX or drop SFX |
| Editor-selectable | The editor can choose it inside the NLE/plugin during the build | MotionVFX template, film grain, LUT, manual keyframe style |
| Rights note | Usage constraint to carry forward | Instagram-only use accepted, YouTube clips internal reference only |
| Attribution note | Public delivery needs credit or share-alike review | CC BY, CC BY-SA, GFDL assets |
| Optional polish | Nice if available, not required | Extra generated texture, alternate visual, bonus SFX layer |

## Closeout Rules

- Do not advance to QA with unresolved blockers.
- Every blocker or decision-required item must name the skill or path that can close it.
- A resolver skill is complete only when it returns a file path, URL, rights note, source terms, mix note, validation result, fallback, or approved skip decision.
- A missing optional asset is closed only when the edit package names the fallback or says to omit it.
- A rights issue is a blocker only when the risky asset must be used and no approved fallback exists.
- MotionVFX templates, plugin choices, film grain, color LUTs, and manual animation choices are editor-selectable unless the user says a specific asset is required.
- YouTube reference clips stay internal reference only unless a public-domain, CC, paid, or written license is confirmed.
- Instagram-only usage must stay tied to the approved platform and use case.
- Attribution notes do not block editing, but they must carry into QA and delivery notes.

## Resolver Skills

| Need | Resolver | Artifact that closes it |
|------|----------|-------------------------|
| VO script, voice criteria, voice validation, or exported TTS path | `elevenlabs-voiceover` | Updated VO packet plus generated/recorded WAV path |
| Music download, licensed audio, temp track, or stems | `audio-rip` or manual licensed-library note | Music file path, license/source note, and any stem paths |
| SFX timing, search terms, source list, or mix levels | `sound-effects-mix` | SFX timeline, download/source checklist, file paths, and license notes |
| Footage, stills, b-roll, or reference clips | `media-sourcing` | Asset manifest row with path/URL, rights status, and fallback |
| Plugin, grain, LUT, end-card reveal, or manual NLE choice | Editor choice | Mark editor-selectable and carry style constraints into the edit package |
| Rights, usage, or attribution issue | Human approval, fallback, or delivery note | Approved use condition, fallback decision, or attribution note |

## Readiness States

| State | Use when |
|-------|----------|
| `blocked` | One or more blockers remain open |
| `ready-for-edit` | The editor can build the timeline, but no final render exists yet |
| `ready-for-qa-packet` | The packet is complete enough for Stage 06 packet QA |
| `ready-for-render-qa` | A render path exists and Stage 06 can inspect it |
