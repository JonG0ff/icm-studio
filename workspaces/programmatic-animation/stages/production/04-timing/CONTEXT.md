# Production 04: Timing

Turn the voice audio into word times per speaker. This is the exposure sheet every later stage times against.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../03-voice/output/[slug]/voice-manifest.md` | Full | Which lines are made or brought |
| Previous stage | `../02-script/output/[slug]/script.md` | Full | The words and speakers to match |
| Audio | `remotion/public/audio/programmatic-animation/[slug]/` | Line files, alignment files, variant tracks | The source audio |
| Shared | `../../../shared/tool-setup.md` | Whisper row, only for brought audio | Whisper setup |
| Skill | `../../../../../skills/workflows/video-production/word-timing/SKILL.md` | Full | Commands for both modes |

## Process

1. Pick the mode per variant:
   - Made lines: use their ElevenLabs alignment. Default engine: ElevenLabs alignment, Whisper only for brought audio.
   - Brought full track: run Whisper and match words to the script in order.
2. Brought full track: split it into per-line files.
3. Build `output/[slug]/words-v[N].json` for each variant.
4. Re-spell words against the script. Flag every mismatch.
5. Write the timing report.

## Checkpoints

No stops. See Audit.

## Audit

| Check | Pass Condition |
|-------|---------------|
| All lines found | Every script line is found, in order; names and lines match the script |
| No mismatches | Words re-spelled against the script with no unresolved mismatches |
| Speakers | Every word has the speaker from its script line |
| No overlaps | Lines don't overlap unless the script says so |
| Pace | Words per minute recorded and within the format's pace |
| Length | Each variant fits the format's length range |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Word times | `output/[slug]/words-v[N].json` | Words with start, end, speaker, line ID. One file per variant. |
| Timing report | `output/[slug]/timing-report-v[N].md` | One per variant. Found or missing per line, mismatches, words per minute, length |
| Split lines | `remotion/public/audio/programmatic-animation/[slug]/` | Per-line files, brought full track only |
