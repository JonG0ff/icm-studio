# Style Feasibility

How the agent says, honestly, how well it can animate a reference style in code. Written in workshop 01 for every new look. Checked against the look test render.

## Trait Grades

Break the style into traits. Grade each one.

| Grade | Meaning | Example |
|---|---|---|
| Native | Code draws this as well as the reference | Flat fills, bold even outlines, hard cuts, on-twos timing |
| Close | A known technique gets most of the way. Name the technique. | Line boil for hand-drawn wobble, a grain shader for film texture |
| Workaround | Possible only by changing it. Say what changes. | Painterly shading becomes two flat tones plus a texture overlay |
| Out of reach | Code can't do it convincingly | Fluid hand-drawn full-body acting, painted frames that change every frame |

Traits to check, at minimum:

- Line: weight, variation, wobble, color, presence.
- Fill and shading: flat, cel, gradient, painted, hatched.
- Texture: paper, grain, brush, halftone, none.
- Palette: count, saturation, limits.
- Construction: shapes, proportions, how faces and hands are built.
- Motion: puppet, morphing, full redraw, frame rate (ones, twos, threes).
- Camera and depth: flat, parallax, 3D.

## Overall Grade

| Grade | Expected Match score | Means |
|---|---|---|
| A | 5 | Reads as the same style. All traits Native or Close. |
| B | 4 | Clearly the same family. One or two Workarounds, none on a defining trait. |
| C | 3 | An adaptation. A defining trait is a Workaround. Say what it will look like instead. |
| D | 1-2 | Not this style. A defining trait is Out of reach. Recommend adapting or dropping. |

A defining trait is one the person would name first when describing the style.

## Honesty Rules

- Grade from the references, not from what would be fun to build.
- Lead with the hardest trait, not the easiest.
- Never say "fully achievable" for a C or D. Say what the person will actually see.
- Every Close and Workaround names its technique family from `looks.md`.
- If one trait drags the grade down, offer the adapted version and its grade side by side.
- If the grade depends on generated or hand-made art, say so. That is a cost, not code.
- If unsure, grade lower and say why. The look test settles it.

## Feasibility Read Format

Saved in the concept for a look.

```
## Feasibility
Overall: [A-D], expected Match [1-5]
Hardest trait: [trait], [grade], [why]

| Trait | What the references show | Grade | Technique or change |
|---|---|---|---|

What you'll see: [2-3 sentences, plain words, including what's lost]
Adapted option: [the version that drops a grade's worth of risk, and its grade], or none
Needs non-code art: yes / no, and what
```

## Calibration

One row per look test. Read this before grading a new style. If predictions keep missing in one direction, adjust.

| Look | Date | Predicted | Match scored | Miss | What fooled the prediction |
|---|---|---|---|---|---|
| sitcom-toon | 2026-10-19 | B, Match 4 | 4 | 0 | Nothing missed on the grade. The gaps were construction detail (arm thickness, hands, set detail), not a trait the grade covered; grade those under construction next time. |
