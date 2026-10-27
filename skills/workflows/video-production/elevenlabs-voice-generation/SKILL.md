---
name: elevenlabs-voice-generation
description: Generate multi-character voice lines through the ElevenLabs API. One take per script line with character alignment, single-line re-rolls, per-variant stitching, and a voice manifest. Use after the script and cast voices are locked.
metadata:
  tags: elevenlabs, tts, voice, multi-character, animation, alignment
---

# ElevenLabs Voice Generation

Turn a locked multi-character `script.md` into one mp3 per line, one alignment file per line, and one stitched mp3 per variant.

This skill does the API work. Tag rules and voice picking live in `skills/workflows/video-production/elevenlabs-voiceover/SKILL.md`. Read that skill to write tags or choose voices. Do not repeat its rules here.

## When to Use

- The script is locked in the `[id] SPEAKER: text` format.
- Every speaker has a voice in `cast-voices.json`.
- You need audio plus timing data for animation.
- One line sounds wrong and you want to re-roll only that line.

## Inputs

`script.md`. One spoken line per line:

```
[h1-01] HOST: [excited] Three ways to build faster.
[h2-01] HOST: Nobody tells you this.
[b-01] HOST: First, ship small.
[b-02] GUEST: [laughs] Then ship again.
```

- Ids are `h<variant>-<nn>` for hooks and `b-<nn>` for body lines.
- Speakers are UPPER_SNAKE cast names.
- v3 audio tags in square brackets are sent as written.
- Headings, notes, and blank lines are ignored.
- A line that starts like an id but breaks the format stops the run.
- Variant N is hook lines `hN-*` then every `b-*` line. No hooks means one variant, v1.

`cast-voices.json`:

```json
{"HOST": {"voice_id": "...", "model_id": "eleven_v3",
          "settings": {"stability": 0.5, "similarity_boost": 0.75, "speed": 1.0}}}
```

`model_id` defaults to `eleven_v3`. `settings` is optional.

## Outputs

In `--out-audio`:

- `<id>.mp3` for every line.
- `<id>.alignment.json` with the character alignment from the API.
- `variant-v<N>.mp3` for every variant.

In `--out-manifest`:

- `voice-manifest.md` with `id | speaker | file | source | chars` rows and the stitched files.

## Commands

Check the script and cast first. No key needed. No API calls.

```bash
python3 skills/workflows/video-production/elevenlabs-voice-generation/scripts/generate_lines.py \
  --script script.md --voices cast-voices.json \
  --out-audio audio/ --out-manifest . --dry-run
```

Generate for real. The key comes from the environment. Never read or print `.env`.

```bash
env $(grep -h '^ELEVENLABS_API_KEY=' .env) \
  python3 skills/workflows/video-production/elevenlabs-voice-generation/scripts/generate_lines.py \
  --script script.md --voices cast-voices.json \
  --out-audio audio/ --out-manifest .
```

Options:

- `--gap-ms 150` sets the silence between stitched lines.
- `--output-format mp3_44100_128` sets the API format. Only mp3 formats are allowed.
- `ELEVEN_API_KEY` also works as the key name.

## Re-roll Flow

1. Listen to the variant mp3.
2. Note the bad line ids.
3. Run again with `--lines b-03,h2-01`.
4. Listed lines are always regenerated.
5. Other lines are made only if their mp3 or alignment is missing.
6. Every variant is restitched and the manifest is rewritten.
7. Run `word-timing` again after any re-roll.

## Gotchas

- Lines with existing audio are skipped. Delete the file or use `--lines` to replace it.
- Keep `--gap-ms` the same in `word-timing`. The offsets depend on it.
- 429 and 5xx responses retry 3 times with backoff. Other errors stop the run with the status and body.
- A variant with a missing line is skipped with a warning, not stitched.
- ffmpeg must be on PATH for stitching.
- Never commit API keys. Keep generated audio out of git unless the workspace says otherwise.

## Text-to-Dialogue

ElevenLabs also has a Text-to-Dialogue API that renders many speakers in one take. It can sound more natural between speakers. This skill does not use it. Per-line takes allow single-line re-rolls and give clean per-line timing.

## Related Skills

- `skills/workflows/video-production/elevenlabs-voiceover/SKILL.md` for tags and voice criteria.
- `skills/workflows/video-production/word-timing/SKILL.md` for `words.json` from these files.

## Source

Promoted from the Jake Van Clief voice-driven-animation archive (MIT). Rewritten for per-line, multi-character generation.
