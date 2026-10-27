# Workshop 04: Motion Test

Prove the piece feels alive in a short test render. Plan it on paper first, then build it. Voices get test lines instead. Looks run the look test.

**Optional for characters, sets and props.** The owner can skip this stage when the piece goes straight into a production run. The first production render is the test (see `../05-approve/CONTEXT.md`). Note the skip, with its date, in `output/[slug]/motion-test.md`. Looks always run the look test.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../03-rig/output/[slug]/rig.md` | Full | What to test (not used for voices) |
| Previous stage | `../02-design-sheet/output/[slug]/design-sheet.md` | Voice design section, voices only | Voice ID and settings |
| Previous stage | `../01-concept/output/[slug]/concept.md` | Must-do list, first-use story, needs table | What must be shown, and where |
| Previous stage | `../02-design-sheet/output/[slug]-voice/design-previews.json` | `text`, characters only, if a voice was designed for this piece | The approved voiceover lines |
| Reference | `references/test-plan-format.md` | Full | Shape of the test plan |
| Shared | `../../../shared/contact-sheets.md` | Full | Self-review of frames |
| Shared | `../../../shared/staging-limits.md` | Full | What code can and can't do |
| Shared | `../../../shared/looks.md` | "Look Test" and "Look Test Scoring", looks only | The news-desk test |
| Shared | `../../../shared/style-feasibility.md` | "Overall Grade" and "Calibration", looks only | Check the prediction |
| Library | `../../../library/entries/set/` and `../../../library/entries/prop/` | Only the entries the needs table marks `library` | Approved sets and props to use |
| Skill | the `remotion-best-practices` skill (install: `remotion/README.md`) | Index, then rules as needed | Remotion APIs |
| Skill | `../../../../../skills/workflows/video-production/elevenlabs-voice-generation/SKILL.md` | Full, characters, voices and looks | Make test lines |

## Process

1. Pick the test for the type:
   - character: act out the first-use story from the concept, in its sets. Talk, gesture, react, enter, exit. Length is whatever the story needs; 15-45 s is typical.
   - set: a pan or hold with a stand-in character on each spot.
   - prop: a hold and a toss.
   - voice: 5-8 lines in character, using varied audio tags.
   - look: the 20-second news-desk scene from `looks.md`.
2. Write the test plan per `references/test-plan-format.md`. Save to `output/[slug]/test-plan.md`. No code, audio or renders yet.
3. **Stop for approval (`plan` and `manual` modes).** In `plan` or `manual` mode, present the test plan, wait for the person to approve it or mark it up, apply every markup, and write the approval line in `test-plan.md` (see Pattern 19 in `../../../../../_core/CONVENTIONS.md`). In `taste` or `auto` mode, do not write an approval line.
4. Make the voice lines exactly as the script in `test-plan.md` lists them.
5. Build the test composition under `remotion/src/compositions/programmatic-animation/_workshop/[slug]/test/`, with stand-in sets and props under `remotion/src/compositions/programmatic-animation/_workshop/[slug]/test/sets/` and `remotion/src/compositions/programmatic-animation/_workshop/[slug]/test/props/`. Register it as `programmatic-animation-test-[slug]`.
6. Make a contact sheet and review it against the test plan, beat by beat. Fix and re-sheet.
7. Render the test mp4 (or the voice lines).
8. Looks only: make the side-by-side sheet, score the seven look test questions, compare Match with the predicted grade, and add a row to "Calibration" in `style-feasibility.md`. If Match is 2+ below the prediction, say so first.
9. Save to `output/[slug]/motion-test.md`.

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|------------|---------------|---------------|------|
| 3 | Test plan: full script, sets, beat table, coverage | Approve, or mark up. Nothing is built until approved. | Spend, plan |
| 7 | Test render (or lines), contact sheet, issues | Feels alive, or back to rig or test plan | Taste |

## Revisions

After the step 7 checkpoint the person gives notes as timestamps plus what feels wrong ("37-40, mouth moves with no sound"). Find the beat from the frame ranges in `motion-test.md`.

| Note size | Examples | What happens |
|---|---|---|
| Small fix | A weird sound, a stiff pose, a hold too long, text too small | Fix it, render the next version (`-v3`, `-v4`), keep older renders. Log it in the "Revisions" table in `motion-test.md`: version, date, the person's note, the fix. No re-approval. |
| Story or script change | A line added or cut, a new beat, a different ending, a new set | Mark up `test-plan.md` and get it approved again before rebuilding. The plan must always match the render. |

- Several notes can come in one message. Fix them all in one version.
- Re-check only the changed span unless the person asks for a full re-watch.

## Audit

| Check | Pass Condition |
|-------|---------------|
| Plan | `test-plan.md` written before any test code; has an approval line with the date in `plan` or `manual` mode |
| Full script | Every line in the script is voiced and plays in the render. No line cut unless the plan says so. |
| Story covered | Every first-use story beat appears in the render, in order |
| Environment | Every beat plays in its planned set. No blank or placeholder background unless the plan says so. |
| Must-do shown | Every must-do item appears in the render, or the plan lists it as skipped with a reason |
| Contact sheet | Reviewed against the plan, no open problems |
| Clean parts | No detached, clipped or floating parts |
| Voice lines | Voices only: every line plays, no artifacts, fits the character |
| Look scored | Looks only: side-by-side sheet made, seven scores, calibration row added |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Test plan | `output/[slug]/test-plan.md` | Per `references/test-plan-format.md` (approval line only in `plan` or `manual` mode) |
| Test notes | `output/[slug]/motion-test.md` | What was tested, plan deviations, issues, scores (looks), file paths |
| Test render | `remotion/out/programmatic-animation/test-[slug]/` | mp4 or voice files, local only |
