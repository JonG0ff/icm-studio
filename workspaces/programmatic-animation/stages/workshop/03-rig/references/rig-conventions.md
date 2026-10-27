# Rig Conventions

How a rigged piece is laid out in code so production can drive it from cues and word times.

## Folders in `remotion/src/compositions/programmatic-animation/`

| Folder | Holds |
|---|---|
| `_kit/` | Engine code shared by every look: mouth driver, pose switcher, cue helpers, filters |
| `_kit/looks/[look].ts` | One look's shared constants: palette, line weight, step rate, filters |
| `_workshop/[slug]/` | A piece under test |
| `_library/[look]/[slug]/` | An approved piece. Never edited by production. |

- The first rig for a look also builds that look's kit file.
- Build `_kit/` pieces once. Pieces import them. Never copy them.

## Character Component

One folder per character:

```
[slug]/
  index.tsx        exports the character component
  parts/           one file or asset per part
  rig.ts           pivots, part order, pose and expression tables
```

Props the component takes:

| Prop | Type | Meaning |
|---|---|---|
| `pose` | pose name | From the rig's pose table |
| `expression` | expression name | From the rig's expression table |
| `mouth` | mouth shape | Set by the mouth driver from word times |
| `view` | `front` or `three-quarter` | No back or side views |
| `x`, `y`, `scale` | numbers | Placement on the set spot |

- Pose and expression names match the library entry exactly.
- No hardcoded colors. Import them from the look's kit.

## Mouth Set

Use these shape names so the mouth driver works for every character:

| Shape | Sounds |
|---|---|
| `rest` | Silence |
| `mbp` | M, B, P (lips closed) |
| `ee` | E, I, most consonants |
| `ah` | A, big open vowels |
| `oh` | O, rounded |
| `oo` | U, W, OO |
| `fv` | F, V (teeth on lip) |
| `l` | L, TH (tongue) |

- 6 shapes is the floor: `rest, mbp, ee, ah, oh, oo`.
- The driver picks a shape from each word's letters across its start and end time. It falls back to an open-close flap if a word is unclear.

## Pixel Art

- Sprites move in whole-pixel steps. Round every transform.
- Scale by whole numbers only.

## Paper Collage

- Parts are PNG layers with transparent edges.
- Motion steps on twos or threes. Small random jitter per step is fine.
