# Scene Conventions

How one video's composition is laid out. The cues say what and when. This file says where code goes and how time works. Remotion API details live in the `remotion-best-practices` skill.

## Folder

```
remotion/src/compositions/programmatic-animation/[slug]/
  timing.ts           sections and beats with absolute start times, per variant
  sections/           one component per top-level cue section
  Master.tsx          assembles sections, audio and SFX for one variant
  index.ts            exports one defineComposition() per variant
```

- Import pieces from `_library/[look]/` and engine code from `_kit/`.
- Never edit `_library/` or `_kit/` for one video. If a piece needs a change, run it back through the workshop.

## timing.ts

- One source of truth for when things happen.
- Holds each variant's sections and beats with absolute start times in seconds, taken from `words-v[N].json`.
- Hook sections differ per variant. Body sections are shared, offset by the hook length.
- Never time a beat by ear. Times come from the word times.

## Section-Local Time

- Each section renders inside a `<Sequence>`. `useCurrentFrame()` there counts from the section start.
- So beat times inside a section are local: `local = absolute - section.start`.
- Write both in the section's header comment so the math is visible.

## Gap-Fill

- Each section's sequence runs until the next section starts. The last one runs to the end.
- `endFrame = next ? Math.floor(next.start * fps) : totalFrames`.
- A background `AbsoluteFill` sits under everything. No black frames.
- Use `premountFor={30}` so entrances are already moving when the cut lands.

## Audio

- Mount the variant's stitched track once at the master root.
- SFX mount per beat, at the levels in `sfx-map.md`.
- Music mounts once at the level in the cue file's `music:` line.

## Mouths

- The `_kit` mouth driver takes `words-v[N].json` and a speaker name.
- It returns the mouth shape for the current frame. Pass it to the character's `mouth` prop.
- Only the speaking character's mouth moves. Others hold `rest` or react.

## Camera and Effects

- Camera moves wrap the whole stage layer, not single characters.
- Effects (rain, speed lines) come from `_kit/` and read the look's kit for colors.

## When Audio Changes

1. Re-run timing.
2. Rebuild `timing.ts` from the new word times.
3. Re-check every beat's local times.
4. Re-sheet and re-render.

## Composition IDs

- `programmatic-animation-[slug]-v[N]`, one per variant.
- Size and fps from the format's platform row.
