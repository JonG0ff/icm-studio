# Format: Music Visual

A song section drawn in code. No voice, no script. The music drives every move.

## Settings

| Field | Value |
|-------|-------|
| Platform | Instagram Reels, 9:16 |
| Length | Whole bars. Usually 8 bars from a drop. |
| Speakers | None |
| Variants | 1 |
| Captions | Off. Optional small title and artist credit. |

## Structure

| Section | Length | Job |
|---------|--------|-----|
| drop | frame 0 | Start on the downbeat. The first frame moves. |
| body | bars 1-6 | One look, reacting to the bands and hits. Add one layer at bar 5. |
| rush | bars 7-8 | Speed up or get denser. |
| loop | last beat | Return to the frame-0 state so the reel loops. |

## Stage Changes

- 02 script and 03 voice: skip. Write "n/a: music visual" in the brief.
- 04 timing: run `skills/workflows/video-production/audio-rip/scripts/beat_map.py`. It writes `beat-map.ts` and cuts the clip.
- 05 blocking: `cues.md` is a bar-by-bar plan: what each band and hit drives.

## Hook Rules

- Frame 0 is the drop. No silent lead-in.
- The look must read in under 1 second.

## Music Rights

- Songs you don't own stay local-only (gitignored temp audio).
- Render a silent copy. Post it and add the song with the platform's music picker.
- Write the rights note in the brief: song, artist, source link, date, use.

## Ending

- Loop back onto the drop. No end card.

## Render

- `v1.mp4` with the song, for review.
- `v1-silent.mp4` for posting.
