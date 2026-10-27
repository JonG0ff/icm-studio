# Looks

A look is any art style that can be drawn in code. There is no fixed menu. Each look starts from reference images, gets an honest feasibility read, and passes the look test before production uses it.

Looks in use: rows with type `look` in `../library/index.md`.

## Where a Look Comes From

1. **References.** The person brings 3-10 images (or clips) of the style. Each one is saved in the swipe engine with the tag `animation-style` plus a shared style tag, `style-[look-slug]`. See `../../../libraries/swipes/stages/01-save/CONTEXT.md`.
2. **Style read.** Workshop 01 breaks the references into traits: line, fill, shading, texture, palette, construction, motion and frame rate.
3. **Feasibility.** Workshop 01 grades every trait and the look as a whole per `style-feasibility.md`. The person decides to build it, adapt it or drop it.
4. **Kit and look test.** Workshop 02-04 build the look's kit and render the news-desk test. The render is scored against the references.
5. **Approve.** Workshop 05 writes the look entry. Only then can pieces be built in it.

## Rules for All Looks

- References are for studying a style, never copying. No tracing, no reused art, no named artist's characters.
- A look is a render layer. Cues don't change between looks.
- Each look has its own cast. A piece is built and approved for one look.
- Porting a piece to another look is a new workshop run.
- A look enters production only after it passes the look test.
- The feasibility read is a promise. If the render misses it, say so and log it.

## Technique Families

How code draws a style. A look can mix families. The feasibility read names which ones it uses.

| Family | Built with | Good at | Weak at |
|---|---|---|---|
| Vector rig | React + layered SVG groups, swappable parts | Bold outlines, flat fills, puppet limbs, lip-sync, recoloring | Painterly texture, organic line variation, 3D turns |
| Procedural line | SVG paths with noise, stroke width animation, line boil | Sketch, doodle, hand-drawn wobble, morphing shapes | Detailed drawings that must stay on-model |
| Sprite / pixel | Sprite sheets on canvas, whole-pixel steps | Pixel art, retro games, discrete poses | Smooth motion, small expressive faces |
| Cutout layers | Transparent PNG layers moved with transforms | Collage, paper, photo cutouts, choppy motion | Anything that must bend or deform |
| Shader / canvas | WebGL or canvas 2D, per-pixel effects | Grain, halftone, glow, watercolor bleed, paper texture, gradients | Character acting on its own |
| 3D | Three.js in Remotion | Real perspective, turns, toon-shaded 3D | Hand-drawn feel, fast build times |
| Generated art + code motion | AI or hand-made stills, animated with transforms and masks | Rich illustration, painterly frames | Consistency across poses, lip-sync |

Worked examples:

- **flash-cutout:** vector rig. Bold outlines, flat fills, puppet limbs, big reaction faces, on twos. Kit: `_kit/looks/flash-cutout.ts`. Study: Eddsworld, Homestar Runner.
- **pixel-art:** sprite / pixel. Tight palette, never scale by fractions. Study: Chrono Trigger, Stardew Valley.
- **paper-collage:** cutout layers plus a paper-texture shader. Rights matter, see `rights-rules.md`. Study: Terry Gilliam's Monty Python cutouts, early South Park.
- **sketch / storyfeeling:** procedural line plus line boil. Monochrome, morphing doodles. Study: hand-drawn explainer shorts with visible line boil.

## Finishing Filters

Work on any look. Set per look in its kit.

- Line boil: outlines wiggle a little each frame.
- Animate on twos or threes: choppy on purpose.
- VHS, CRT scanlines, film grain, halftone dots, paper texture.

## Look Test

The workshop's motion test for a new look.

1. Build one 20-second news-desk scene: the host enters, says two lines, gestures, reacts to a ridiculous clip, exits.
2. Use the same voice and cues for every look being tested.
3. The "ridiculous clip" is a re-enactment we animate, not real footage.
4. The host is a quick test piece, not cast, unless it's good enough to keep.
5. Make a side-by-side sheet: 3 render frames next to 3 reference images.

## Look Test Scoring

Score 1-5 on each. Decide from real renders, not reference pictures.

| Score | Question |
|---|---|
| Match | Next to the references, does it read as the same style? |
| Appeal | Do the characters look good and funny? |
| Time | How long did the test take to build? |
| Range | How many expressions and actions read clearly? |
| Reuse | How much carries to the next video? |
| Cost | Art, credits and render time |
| Reliability | Does it stay on-model across poses? |

Then compare Match with the predicted grade from the feasibility read. Log both in `style-feasibility.md` under "Calibration".
