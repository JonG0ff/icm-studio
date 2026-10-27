# Programmatic Animation

Make animated videos in code. Build approved pieces in the workshop, then make videos from those pieces on the production line.

This is a specialized production workflow using the shared Remotion runtime. Footage editing, repurposing, and mixed-media jobs belong in `../video-production/` unless they use a production recipe from this workspace. Choosing Remotion alone does not route a job here.

## Folder Map

```
programmatic-animation/
├── AGENTS.md          (you are here)
├── CONTEXT.md         (start here: workshop or production)
├── setup/             (onboarding questionnaire)
├── shared/            (rules and formats used by more than one stage)
│   └── formats/       (one recipe per video format)
├── library/           (approved pieces only)
├── input/             (files you bring, one folder per run slug)
└── stages/
    ├── workshop/      (build one piece: look, character, set, prop, voice)
    │   ├── 01-concept/
    │   ├── 02-design-sheet/
    │   ├── 03-rig/
    │   ├── 04-motion-test/
    │   └── 05-approve/
    └── production/    (make one video, or one set of variants)
        ├── 01-brief/
        ├── 02-script/
        ├── 03-voice/
        ├── 04-timing/
        ├── 05-blocking/
        ├── 06-scene/
        └── 07-render/
```

## Two Modes

- **Production:** the front door. Makes a video; output is an mp4 per variant plus a manifest.
- **Workshop:** a detour run by a subagent (or standalone) to build and test one missing piece.
- Library status values in `library/index.md`: `approved`, `workshop`, `archived`. Production may use `approved` and `workshop` pieces.

## Review Modes

- Follow Pattern 19 in `../../_core/CONVENTIONS.md` for review modes (`manual`, `plan`, `taste`, `auto`), stop kinds, and the spend guardrail.
- Workspace default: `taste` (recorded as `review: taste` in `stages/production/01-brief/output/[slug]/brief.md`, with optional `credit-cap: 5000`).
- Plan stops (`Kind` flagged `, plan`): P02 script lock and P05 cues in production; W04 test plan in the workshop.

## Character Consistency

- Each character links to one persona profile. It owns identity, dialogue, reactions, relationships, boundaries, and reference examples across looks and runs.
- Use `shared/persona-profile-format.md`. Draft at workshop 01, carry through design and testing, and publish with the character at workshop 05.
- Scriptwriting loads only the cast's profiles. Check made and brought scripts before lock and write `character-consistency.md` beside the script.
- Voice entries own sound, tested audio tags, and API settings. Persona prose guides writing and acting; it is not sent wholesale to ElevenLabs.
- Keep workshop profiles as drafts until sign-off. Existing approved traits can be consolidated with their source pointers; new traits and examples must be marked as proposals.
- Keep locked runs intact. Apply this review when starting a script or revising one, including a brought script.

## Plan Before Render

- The plan file always exists before test code, scene code, or rendering starts.
- Production: `cues.md` in stage 05. Workshop: `test-plan.md` in stage 04.
- It needs an owner approval line only in `plan` or `manual` mode.
- The beat audit is always on: every voiced line, beat, and set in the approved script plays in the render.
- Never cut a voiced line, beat, or set from an approved plan without asking.

## Show the Output

- Follow Pattern 21 in `../../_core/CONVENTIONS.md`. Reveal work in Finder before asking at a stop.
- Use absolute paths. Renders and audio live under `remotion/` at the repo root.

| Stop | Reveal |
|------|--------|
| W02 design sheet | `open` on `stages/workshop/02-design-sheet/output/[slug]/` (sheets or voice takes) |
| W03 rig | `open` on `stages/workshop/03-rig/output/[slug]/` (pose sheets) |
| W04 motion test | `open -R` on the newest mp4 in `remotion/out/programmatic-animation/test-[slug]/` |
| P03 voice | `open` on `remotion/public/audio/programmatic-animation/[slug]/` |
| P06 scene | `open` on `remotion/out/programmatic-animation/[slug]/` (contact sheets) |
| P07 render | `open -R` on `v1.mp4`, then `open -R` on `stages/production/07-render/output/[slug]/manifest.md` |
| Brought file | `open -R` on where it landed in `input/[slug]/` or the stage output |

## Make or Bring

- Every stage can make its output, or ingest a file you bring.
- Bring a file by attaching it in chat or dropping it in `input/[slug]/`.
- Steps live in `shared/bring-intake.md`.

## Triggers

| Keyword | Action |
|---------|--------|
| `setup` | Run the onboarding questionnaire |
| `status` | Show stage completion for a run slug in both lanes |
| `library` | Show `library/index.md` grouped by look |

### How `status` works

For the given slug, check each `stages/*/*/output/[slug]/` folder from files on disk. Files present means COMPLETE. Otherwise PENDING. Show the production lane and workshop lane on separate lines. Check `stages/production/07-render/output/[slug]/manifest.md` for the ship record (`## Approval`).

## Routing

| Task | Go To |
|------|-------|
| Start a video | `stages/production/01-brief/CONTEXT.md` |
| Fix a line or re-roll a voice | `stages/production/03-voice/CONTEXT.md` |
| Re-render or render variants | `stages/production/07-render/CONTEXT.md` |
| Build a new look from reference images | Save them in `../../libraries/swipes/`, then `stages/workshop/01-concept/CONTEXT.md` |
| Build a new character, set, prop or voice | `stages/workshop/01-concept/CONTEXT.md` |
| Approve or reject a piece | `stages/workshop/05-approve/CONTEXT.md` |
| Add a new video format | `shared/formats/CONTEXT.md` |

## What to Load

| Task | Load These | Do NOT Load |
|------|-----------|-------------|
| Workshop run | That stage's `CONTEXT.md` and its listed inputs | Production stages, `shared/formats/` |
| Production run | That stage's `CONTEXT.md` and its listed inputs | Workshop stages, other runs' outputs |
| Any stage with a brought file | `shared/bring-intake.md` plus the stage inputs | Unrelated `input/` folders |

- Library: load `library/index.md`, then only the entries a run names.
- Never read other runs' `output/` folders to learn patterns. Use the reference docs.

## Where Things Land Outside This Folder

| What | Where |
|------|-------|
| Engine code and look kits | `remotion/src/compositions/programmatic-animation/_kit/` |
| Unapproved piece code | `remotion/src/compositions/programmatic-animation/_workshop/[piece]/` |
| Approved piece code | `remotion/src/compositions/programmatic-animation/_library/[look]/[piece]/` |
| Approved piece art | `remotion/public/assets/programmatic-animation/_library/[look]/[piece]/` |
| One video's composition | `remotion/src/compositions/programmatic-animation/[slug]/` |
| One video's voice audio | `remotion/public/audio/programmatic-animation/[slug]/` (local only) |
| Renders | `remotion/out/programmatic-animation/[slug]/` (local only) |

## Stage Handoffs

- Each stage writes to its own `output/[slug]/` folder.
- The next stage reads from there.
- Edit an output file and the next stage picks up your edits.
