# Render Checklist

Pre-flight and post-render checks. Run all of them on a final render. Skip them on a draft.

## Pre-Flight

- [ ] `npm run typecheck` and `npm run compositions` pass in `remotion/`
- [ ] Every variant's composition is registered
- [ ] Studio preview plays end to end with no console errors
- [ ] No black frames between sections
- [ ] Each variant's audio mounts once and plays the whole way
- [ ] Fonts load
- [ ] Size and fps match the format's platform row
- [ ] Faces and text sit inside the platform's safe areas

## Render

From `remotion/`:

```
npx remotion render src/index.ts programmatic-animation-[slug]-v[N] out/programmatic-animation/[slug]/v[N].mp4
```

Phone copy:

```
ffmpeg -i out/programmatic-animation/[slug]/v[N].mp4 -c:v libx264 -crf 28 -c:a aac -b:a 128k out/programmatic-animation/[slug]/v[N]-phone.mp4
```

- Long videos: add `--concurrency` set to cores minus 2.
- The first render of a session is slower.

## Post-Render

- [ ] Plays in a browser and in VLC
- [ ] Watch the first 5 seconds and last 10 seconds closely
- [ ] Skim the middle at 2x for glitches
- [ ] Runtime within 5% of the timing report
- [ ] Mouths still match words at the end (no drift)
- [ ] File size makes sense (1080x1920, 30 s: about 5-20 MB)

## Ship-Ready

- Every pre-flight item checked.
- Exit code 0 for every variant.
- Post-render checks pass.
- A person has watched every variant once and approved.

## Loop Back

| Symptom | Go back to |
|---------|-----------|
| A beat lands off the word | Production 06 (rebuild `timing.ts`) |
| Wrong shot, pose or SFX | Production 05 |
| Word times wrong | Production 04 |
| A line sounds wrong | Production 03 (re-roll the line, then 04-07) |
| A line reads wrong | Production 02 (then 03-07) |
| A piece looks broken | Workshop, for that piece |
