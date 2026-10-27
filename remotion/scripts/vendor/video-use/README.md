# Selected video-use helpers

Adapted from [browser-use/video-use](https://github.com/browser-use/video-use/tree/43cfc566833548093455c9d4a46bd69913b7e552), commit `43cfc566833548093455c9d4a46bd69913b7e552`. MIT attribution is retained in [LICENSE](LICENSE). [upstream.json](upstream.json) records source and local SHA-256 hashes, patches, dependency inspection, and actual test results.

These are local file tools. They do not import the upstream provider, upload audio, require API keys, or implement a CMP/Whisper cache bridge. The final Remotion renderer and edit mapping remain outside this folder.

## Dependencies

- Python 3.14.7 was used for verification.
- NumPy 2.4.6 and Pillow 12.2.0 are pinned in [requirements.txt](requirements.txt).
- FFmpeg and ffprobe 8.1.1 must be on PATH.
- All other imports are Python standard library, plus the adjacent packing validator.

The tests used packages already installed on this machine. No global package install was performed. For a fresh environment, create an isolated environment outside the repository:

```bash
python3 -m venv /tmp/cmp-video-use-venv
/tmp/cmp-video-use-venv/bin/python -m pip install -r remotion/scripts/vendor/video-use/requirements.txt
```

## Commands

From the repository root:

```bash
python3 -B remotion/scripts/vendor/video-use/pack_transcripts.py --edit-dir /absolute/path/to/edit
python3 -B remotion/scripts/vendor/video-use/timeline_view.py /absolute/path/to/video.mp4 0 2 --audio-track 0 --transcript /absolute/path/to/transcript.json -o /tmp/range.png
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s remotion/scripts/vendor/video-use -v
```

Packing reads `<edit-dir>/transcripts/*.json`. The transcript must contain an explicit `words` list. Each token needs an explicit `type` (`word`, `spacing`, or `audio_event`) and finite, ordered, nonnegative `start` and `end` times in source seconds. Spoken words need nonempty text and positive, nonoverlapping ranges. Missing word timestamps fail; they are never interpolated. An empty list is an explicit empty transcript.

The packing header reports **speech span**, from first to last retained token, including intervening gaps. It does not report media duration or summed speaking time. Source IDs and other metadata stay in the original transcript; packed Markdown is a review artifact, not an identity-preserving interchange format.

Timeline review accepts `0 <= start < end <= media duration`, 1–64 frames, and a zero-based audio ordinal (`--audio-track 1` maps to `0:a:1`). Functions accept the same `audio_track` argument. Missing tracks, decode failures, and empty decoded audio fail explicitly. Valid zero-amplitude audio produces a flat waveform. Samples cover the full decoded segment; the waveform normalizes amplitude and is not a loudness meter.

Filmstrip samples use evenly spaced bin centers in the requested exclusive-end range. FFprobe reads frame presentation timestamps and durations for that range, with necessary keyframe preroll. Each sample shows the frame covering its center, including the final displayed frame when its PTS precedes the center. FFmpeg selects the exact integer PTS. Each image labels its actual source `PTS`; it does not claim that PTS equals the bin center. Narrow ranges can repeat the same covering frame. The requested range, ruler, and waveform remain unchanged. Missing timestamp or final-frame duration evidence fails explicitly.

Pass an explicit transcript for supported range review. The upstream adjacent-file auto-discovery remains available. A supplied missing or invalid transcript fails. Only explicit word tokens produce labels. Shaded transcript gaps are not verified acoustic silence. `--edl` is deliberately unsupported and fails clearly.

## Verification and limits

Ten local unittest cases pass. They cover phrase punctuation/pause/speaker grouping, spacing/events, empty transcripts, missing/nonfinite timing, span labeling, unsupported EDL, invalid ranges/tracks/frame counts, silent and tone track selection, no audio, empty decoded PCM, and a synthetic two-second FFmpeg fixture with filmstrip pixels, waveform pixels, word labels, and track/gap labels. A one-second 30fps fixture checks final-frame selection, byte equality against independently selected frame 29, actual PTS labels, and one-frame/subframe ranges. Temporary fixture media and PNGs are removed by the test suite.

No matching upstream helper test files were found at the pinned revision. These are local regression cases, not a claim that the upstream suite passed. Synthetic image checks do not establish audiovisual playback QA or a real-clip integration proof. No full render or paid API was run. Python/package compatibility beyond the recorded environment is unverified.
