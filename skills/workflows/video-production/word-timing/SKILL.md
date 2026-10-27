---
name: word-timing
description: Build word-level timing (words.json) for one script variant, with speaker and line on every word. Mode A uses ElevenLabs per-line alignment. Mode B runs Whisper on brought audio and aligns it to the script. Use before animating to the voice track.
metadata:
  tags: whisper, alignment, word-timing, animation, captions, multi-character
---

# Word Timing

Make `words.json` and `timing-report.md` for one variant of a multi-character script. Every word has a start, an end, a speaker, and a line id.

## When to Use

- Voice lines exist and the animation needs word or line timing.
- Mode A: lines came from `elevenlabs-voice-generation`.
- Mode B: someone brought one full recording instead.
- After any re-roll. Old timing goes stale.

## Inputs

- `script.md` in the `[id] SPEAKER: text` format. See `elevenlabs-voice-generation/SKILL.md`.
- Mode A: a folder with `<id>.mp3` and `<id>.alignment.json` per line.
- Mode B: one full track, wav or mp3.
- `--variant N`. Default 1. Variant N is hook lines `hN-*` then every body line.

## Outputs

`words.json`:

```json
{"variant": 1, "duration": 12.43,
 "lines": [{"id": "b-01", "speaker": "HOST", "found": true, "start": 0.0, "end": 2.1}],
 "words": [{"word": "First,", "start": 0.0, "end": 0.31, "speaker": "HOST", "line": "b-01"}]}
```

- Times are seconds on the variant timeline.
- Words are spelled as in the script. Audio tags are removed.
- Lines not found have `found: false` and no words.

`timing-report.md` sits next to `words.json` unless `--report` says otherwise. It lists each line as found or NOT FOUND, misheard words, words per minute, and total duration.

## Commands

Mode A, made audio. Use the same `--gap-ms` as generation.

```bash
python3 skills/workflows/video-production/word-timing/scripts/build_words.py \
  --script script.md --audio-dir audio/ --variant 1 --gap-ms 150 --out words.json
```

Mode B, brought audio.

```bash
python3 skills/workflows/video-production/word-timing/scripts/build_words.py \
  --script script.md --track full.wav --variant 1 --out words.json \
  --split-lines lines/
```

- `--split-lines` cuts `<id>.wav` per found line, with 50 ms of padding.
- `--whisper-model` defaults to `medium.en`. See [`rules/cpu-fallback.md`](rules/cpu-fallback.md).
- `--whisper-bin` points at the CLI. Default is PATH, then `~/.local/bin/whisper`.

## How It Works

- Mode A offsets each line by the real ffprobe durations of the lines before it, plus the gap. This matches the stitched `variant-v<N>.mp3`.
- Mode B aligns the whole transcript to the script in order. See [`rules/line-matching.md`](rules/line-matching.md).

## Gotchas

- Mode A needs every mp3. A missing mp3 stops the run because later offsets would be wrong.
- A missing alignment file marks that line NOT FOUND. Offsets stay right.
- Never animate past a NOT FOUND line. Fix the audio or the script first.
- Whisper writes numbers as digits. A script that says "ten" may show a mismatch note. The timing is still used.
- The first `medium.en` run downloads the model, about 1.5 GB.

## Related Skills

- `skills/workflows/video-production/elevenlabs-voice-generation/SKILL.md` makes the Mode A files.
- the `remotion-best-practices` skill (install: `remotion/README.md`) for using the timing in Remotion.

## Source

Promoted from the Jake Van Clief voice-driven-animation archive (MIT). Rewritten from beat-phrase finding to per-word, per-speaker timing.
