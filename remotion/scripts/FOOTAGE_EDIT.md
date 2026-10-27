# Selected-Footage Adapter

Experimental Phase 2 implementation. Live workspace routing stays unchanged.
The real talking-clip/revision proof and complete audiovisual QA are pending.
Use the existing job's brief, plan, review mode, rights record, and handoff.

Run these commands from `remotion/`. Contracts live in
[contracts.ts](../src/lib/video-production/contracts.ts).

## Inspect and transcribe

Place the permitted source in an ignored local directory. The runtime copy must
have identical bytes under `public/assets/`. Do not commit media or cache files.
The adapter does not copy, download, normalize, or clear media rights.

```bash
node scripts/footage-edit.mjs inspect \
  --source public/assets/.cache/example/source.mp4 \
  --runtime-path assets/.cache/example/source.mp4 \
  --job-id example --source-id talk-01 --rights-ref rights.md \
  --out out/example/sources.json --energy-out out/example/energy.json

node scripts/footage-edit.mjs transcribe \
  --sources out/example/sources.json --out out/example/transcript.json \
  --cache-dir .cache/footage-whisper --model medium.en --language en \
  --bridge-out out/example/source-words.json --packed-out out/example/transcript.md
```

Create `out/example/rights.md` before inspection with `--energy-out` or validation.
It points to permission,
attribution, and use limits. A file's existence does not establish clearance.
Keep canonical small artifacts in the job's current stage; `out/` here is a local
example. Artifact references resolve relative to their containing file.

Inspection hashes the source and saves FFprobe stream/frame evidence. It checks
actual presentation timestamps, final-frame duration, and decoded audio origins
and gaps. It refuses unknown/VFR timing and nonzero origins. Select ambiguous
tracks with `--video-stream-index` / `--audio-stream-index` using absolute FFprobe
indexes. `--no-audio` explicitly mutes/declines source audio. `--energy-out` adds
the adopted PCM analysis with actual sample duration and source offset. Energy
candidates require listening; they never authorize cuts.

Whisper discovery uses PATH, then `~/.local/bin/whisper`, or `--whisper-bin`.
The executable's Python environment supplies engine metadata. System Python
does not need Whisper installed. Weights must already exist in
`~/.cache/whisper` (or `--model-dir`). No download or hosted fallback runs.
English uses explicit `--model medium.en --language en`; another language needs
a compatible installed model. Full-source analysis only is supported.

The cache identity includes source/model hashes, engine version, language,
selected audio, bounds, extraction settings, and effective decoding defaults.
Local loading retains the installed named model's alignment-head mask; the mask
and runner hashes are part of the identity.
Raw JSON stays byte-for-byte unchanged, including rejected recognition. Malformed
or missing word timestamps block normalization. A recognized word with
zero-length, overlapping, or out-of-source times keeps its ID with `null` times
and a `timingIssue`; no time is invented. A selection that could contain it fails
until a listening correction supplies both bounds. Cache hits check raw/PCM
hashes. Null CLI defaults are omitted, not passed as the string `None`. Caption and edit revisions do not rerun Whisper. Rerunning
recognition refuses to overwrite reviewed transcripts or corrections. Reuse the
existing transcript or choose a new output path.

## Lock and compile selections

Author `edit-decisions.json` from the job's editorial/visual plan. Hash the exact
source/transcript files referenced there. Record listening evidence for every
selected word and explicit corrections before selection lock. The compiler
rejects automatic-only recognition. Do not fabricate listening evidence to pass.

For a deliberate no-speech branch, use `noSpeech: true`, empty `transcriptRefs`,
and empty `wordIds` for every segment. Missing recognition does not imply silence.

```bash
node scripts/footage-edit.mjs validate \
  --decisions /absolute/job/edit-decisions.json --out-dir out/example/build
```

Validation checks versions/jobs, artifact and raw-result hashes, original/runtime
media bytes, source-frame timestamps, selected tracks, corrections, and listening
coverage. It snaps source bounds once, preserves repeated selections by segment
ID, then calls `validateEditMap` and `mapSourceCaptions`. Partial-word cuts fail.
Grouping uses the adopted helper within each output segment. SRT uses the same
cues and rejects millisecond collisions. Original text and IDs remain in the
caption word records; corrections retain their evidence.

Build outputs: `edit-map.json`, `captions.json`, `captions.srt`, `props.json`,
`output-timeline-words.json`, and `build-notes.md`. Map bytes use two-space JSON
plus a final newline; the caption artifact binds its hash. A caption mode of
`srt`, `fcp-subtitles`, or `none` renders clean picture. SRT remains a derived
sidecar; deliver it only when requested. Optional emphasis is authored text.

First-release limits: one recorded source; normal-speed cuts; matching CFR source
and output rates; first video stream; at most one selected audio stream; framing,
basic captions, and simple text emphasis. Rotated media, proxies, inserted cards,
mixed-rate sources, transitions, and retiming need an explicit later route.
The renderer converts the absolute audio stream index to an audio ordinal.

## Preview and render

```bash
node scripts/footage-edit.mjs preview \
  --decisions /absolute/job/edit-decisions.json --out-dir out/example/build \
  --frames 0,30,59 --scale 0.5 --timeline

node scripts/footage-edit.mjs render \
  --decisions /absolute/job/edit-decisions.json --out-dir out/example/build \
  --plan /absolute/job/plan.md --reviewer 'Named reviewer' \
  --playback-method 'Agreed local whole-file playback method'
```

Choose in-range frames around each cut. Inspect the actual PNGs under the job's
review mode. `--timeline` adds the adopted viewer's filmstrip, waveform, and
effective word labels for the first selected source range; it needs audio.
`output-timeline-words.json` supplies output-time labels for later rendered-cut
inspection. Stills and a source filmstrip do not demonstrate output audiovisual
continuity.

The reusable composition is `video-production-selected-footage`. Its placeholder
registration requires real compiled props. `calculateMetadata` resolves duration,
size, and fps from the validated map. Existing prototype/proof definitions stay
reproducible.

Rendering requires hash-matched previews of the exact props, a plan, and the
named playback method/reviewer. Remotion renders picture only (`muted`). FFmpeg
then cuts the original audio at the same compiled frames, sample-exact, and
muxes it. The attempt record's `audioMux` stores the sample ranges, signaled and
decoded sample counts, stream origins, and per-segment cross-correlation delay
against the source. The render fails if picture frames, signaled audio length,
origins, or delay (over 1 ms) disagree. Remotion's own audio step added 2048
samples (42.7 ms) of leading silence and ran 60 ms past picture. The MP4 movie
timescale equals the sample rate so NTSC lengths are not rounded to milliseconds.
Stills and renders allow 120 s per `delayRender`: other registered compositions'
font loads outlasted the 30 s default during full-length 4K extraction. A failed
attempt records its reason and still counts against the budget. It records each full-render attempt, including
failed attempts. The same output directory is one run's render budget across
revisions: stop at three attempts and follow the job's Spend review before
another run. Do not use a new directory to bypass that review.

The render record marks playback QA pending. Watch and listen to the exact
export through the agreed method, record its hash and observations in the job's
delivery manifest, then apply the owner's acceptance decision. If full playback
is unavailable, record QA as blocked. Any export change invalidates old QA.
These commands never publish or create owner approval.

## Verification

From repository root:

```bash
python3 -B -m unittest discover -s remotion/scripts -p 'test_footage_analysis.py' -v
python3 -B -m unittest discover -s remotion/scripts/vendor/video-use -p 'test_*.py' -v
node --test remotion/scripts/footage-edit.test.mjs remotion/scripts/footage-audio.test.mjs remotion/src/lib/video-production/compile-edit.test.mjs
python3 scripts/check_repository_foundation.py
```

From `remotion/`:

```bash
npm run typecheck
npx eslint src/lib/video-production src/compositions/video-production/selected-footage src/compositions/types.ts
npm run compositions
```

Tests use real synthetic media inspection/PCM, real FFmpeg audio muxing, and
mocked recognition. One test checks the installed Whisper CLI accepts the
setting arguments. They do not establish installed-model accuracy, talking-clip editing quality, whole-video
render/audio behavior, playback QA, or a manual-edit speed comparison.
