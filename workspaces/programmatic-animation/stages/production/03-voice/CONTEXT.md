# Production 03: Voice

Get one audio file per script line, made with ElevenLabs, brought, or a mix. Stitch one track per variant.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../02-script/output/[slug]/script.md` | Full | The lines to voice |
| Previous stage | `../02-script/output/[slug]/character-consistency.md` | Sources and accepted performance deviations | Which persona revisions the locked script uses |
| Previous stage | `../01-brief/output/[slug]/brief.md` | "cast" | Speaker to voice slug |
| User | `../../../input/[slug]/` | Audio files, only if brought | Brought lines or a full track |
| Shared | `../../../shared/bring-intake.md` | Full, only if a file was brought | Ingest steps |
| Library | `../../../library/entries/voice/[slug].md` | ElevenLabs fields, for the brief's voices only | Voice IDs and settings |
| Library | Persona paths from `character-consistency.md` | "Performance Link" and "Reactions", speaking cast only | Acting intent; use the revision recorded at script lock |
| Shared | `../../../shared/tool-setup.md` | "ElevenLabs Key" | How to pass the key |
| Skill | `../../../../../skills/workflows/video-production/elevenlabs-voice-generation/SKILL.md` | Full | Commands and re-roll flow |

## Process

0. For brought audio, follow bring intake. Per-line files are named by line ID. One full track is saved as `full-track.wav` and split in timing.
1. Read the locked script's persona source record and acting intent. Build `output/[slug]/cast-voices.json` from the voice entries. Persona prose stays local; only supported fields and inline audio tags go to the API. Do not rewrite locked dialogue or add unapproved acting tags. If a profile has changed since lock, recover the recorded revision from Git or the cited source before using its direction. For legacy locked runs without a consistency file, retain the existing approved script and voice settings; the next script revision gets the review.
2. Run the dry run before any paid call. Confirm every speaker has a voice and check the estimate against the spend limits in Pattern 19 of `../../../../../_core/CONVENTIONS.md`.
3. Generate the remaining lines into `remotion/public/audio/programmatic-animation/[slug]/`. Skip brought lines.
4. Stitch one track per variant.
5. Write the voice manifest. Mark each line `made` or `brought`. End `voice-manifest.md` with a `## Spend` section (`| Call | Lines | Credits |` followed by `Credits used: N of M`; brought audio writes `Credits used: 0 of 5000`).
6. Re-roll single lines on request and log the call in `## Spend`. Three re-rolls of one line, then stop and ask. Re-stitch after.

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|------------|---------------|---------------|------|
| 2 | Dry run: lines and characters per speaker | Spend the credits, or fix the script | Spend |
| 5 | Stitched tracks and manifest | Timing and delivery, or which lines to re-roll | Taste |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Coverage | Every script line has audio, or is covered by a brought full track |
| Files | Every file plays and is not silent |
| Manifest | Matches the script line for line |
| Voices | No voice outside the library |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Line audio | `remotion/public/audio/programmatic-animation/[slug]/` | One file per line ID, plus alignment files, local only |
| Variant tracks | Same folder | `variant-v[N].mp3` |
| Cast voices | `output/[slug]/cast-voices.json` | Speaker to voice ID and settings |
| Voice manifest | `output/[slug]/voice-manifest.md` | Line ID, speaker, file, source, characters, plus `## Spend` ledger |
