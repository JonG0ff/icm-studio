# Production 05: Blocking

Write the storyboard as cues: set, who's on screen, pose, camera, SFX and holds, each tied to a quote in the voice. Or bring a storyboard.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../02-script/output/[slug]/script.md` | Full | Lines and stage directions |
| Previous stage | `../04-timing/output/[slug]/words-v1.json` | Full | Quote times |
| Previous stage | `../01-brief/output/[slug]/brief.md` | "cast", "set", "props" | What's available |
| User | `../../../input/[slug]/` | Storyboard, only if brought | A brought storyboard |
| Shared | `../../../shared/bring-intake.md` | Full, only if a file was brought | Ingest steps |
| Shared | `../../../shared/cue-grammar.md` | Full | How cues are written |
| Shared | `../../../shared/formats/[format].md` | "Structure" | Sections |
| Shared | `../../../shared/staging-limits.md` | Full | What code can and can't do |
| Shared | `../../../shared/rights-rules.md` | "Music and SFX" | Rights notes |
| Library | `../../../library/entries/[type]/[slug].md` | Poses, expressions, spots, graphics, for the brief's pieces only | What each piece can do |
| Skill | `../../../../../skills/workflows/video-production/sound-effects-mix/SKILL.md` | Index | SFX map and mix notes |
| Skill | `../../../../../skills/workflows/video-production/media-sourcing/SKILL.md` | Pixabay music and SFX | Sourcing |

## Process

0. If a storyboard was brought, follow bring intake: convert it to cue grammar.
1. Split the script into the format's sections.
2. Write one beat per 3-8 seconds. Each beat quotes 3-6 words from the voice.
3. Set who's on, pose, expression, camera and effects per beat.
4. Add holds and the button beat.
5. Pick SFX and music. Write the SFX map with rights notes.
6. Match every quote to `words-v1.json`. Hook beats are matched per variant in the scene stage. `cues.md` gets an approval line only in `plan` or `manual` mode (see Pattern 19 in `../../../../../_core/CONVENTIONS.md`).

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|------------|---------------|---------------|------|
| 4 | The cues, read as a storyboard | Shots and timing work, or change beats | Spend, plan |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Quotes resolve | Every quote matches words in `words-v1.json` (hook beats: in their variant) |
| Library only | Every pose, expression, spot, set and prop exists in its entry |
| Pace | A beat change every 3-8 seconds |
| No look names | Cues never name a look, a component or a frame |
| Rights | Every SFX and music file has a rights note |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Cues | `output/[slug]/cues.md` | Per `cue-grammar.md` |
| SFX map | `output/[slug]/sfx-map.md` | Per cue: sound, file, source, license, level |
