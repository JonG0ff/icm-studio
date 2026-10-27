# Contact Sheets

A grid of stills so Claude can check its own frames before a person watches. Used by workshop 04 and production 06.

## Make One

Run from the repo's `remotion/` folder.

1. Render a half-size draft:
   ```
   npx remotion render src/index.ts [composition-id] out/programmatic-animation/[slug]/draft.mp4 --scale=0.5
   ```
2. Pull one frame per second into a grid:
   ```
   ffmpeg -i out/programmatic-animation/[slug]/draft.mp4 -vf "fps=1,scale=360:-1,tile=4x4" -frames:v 1 out/programmatic-animation/[slug]/contact-sheet-01.png
   ```
3. Videos longer than 16 seconds make several sheets. Use `-frames:v N` and `contact-sheet-%02d.png`.
4. For a beat that matters, render one exact frame:
   ```
   npx remotion still src/index.ts [composition-id] out/programmatic-animation/[slug]/beat-[name].png --frame=[n]
   ```

## Review It

Open every sheet with the image viewer. The files are gitignored but readable.

Check for:
- Parts that detach or overlap wrongly (arm in front of face, floating mouth).
- Characters off their spot or cut off by the frame edge.
- Text outside the safe area for the platform.
- Wrong expression or pose for the cue.
- Empty or black frames.

## Record It

- List each problem with the second it appears and the fix.
- Fix and re-sheet before the person check.
- Write the sheet paths and the result in the stage output.
