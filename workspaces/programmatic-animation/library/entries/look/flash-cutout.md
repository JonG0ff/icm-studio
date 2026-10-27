# flash-cutout
type: look
look: flash-cutout
status: approved
approved: 2026-10-16
code: remotion/src/compositions/programmatic-animation/_kit/looks/flash-cutout.ts
art: none

- **References:** your own reference sheets. Save them in the Swipe Engine and tag them `style-flash-cutout`.
- **Technique:** Vector rig (`FLASH_LINE`, `FLASH_PALETTE`, `Shaded`, `FLASH_STEP = 2` on twos, 8-mouth lip-sync via `remotion/src/compositions/programmatic-animation/_kit/mouth-driver.ts`) plus Procedural line finishing (`LineBoilFilter` at `FLASH_BOIL` settings).
- **Kit:** `remotion/src/compositions/programmatic-animation/_kit/looks/flash-cutout.ts` (with shared helpers in `remotion/src/compositions/programmatic-animation/_kit/flash-shapes.tsx`, `remotion/src/compositions/programmatic-animation/_kit/mouth-driver.ts`, and `remotion/src/compositions/programmatic-animation/_kit/shape-paths.ts`).
- **Feasibility:** Overall grade A. Hardest trait: camera and depth three-quarter view (`Workaround`; requires a separate hand-built drawing per character and a hard cut between views rather than an animated turn). Line boil on render is `Close` (SVG turbulence filter; adds render time and can shimmer small text if applied full-frame). All other traits (line, flat fill with one hard shadow tone, texture, palette, rounded puppet construction, waddle on twos, 8-mouth lip-sync) are `Native`.
- **Scores:** From four production runs and one workshop motion test (`../../../shared/looks.md` dimensions):
  - **Match:** 5/5 (`own-asset, not predictive`; kit renders match the reference sheets by construction).
  - **Appeal:** 5/5 (bold cartoon silhouettes, lidded eyes, and deadpan expression swaps landed in solo skits and a six-character ensemble).
  - **Time:** 4/5 (reusable kit primitives and `CharacterSheet` / `PoseSheetBoard` speed up rig builds; each character still needs separate front and three-quarter drawings).
  - **Range:** 4/5 (8-mouth phoneme lip-sync, 4 to 7 expressions per rig, seated/standing/walk-loop poses, and cutaway inserts read clearly; full-body acting relies on staging workarounds).
  - **Reuse:** 5/5 (`FLASH_PALETTE`, `FLASH_LINE`, `FLASH_STEP`, `MouthSet`, and `remotion/src/compositions/programmatic-animation/_kit/mouth-driver.ts` carried across four production runs and six character rigs).
  - **Cost:** 5/5 (100% code-drawn SVG in Remotion with zero paid image or video generation credits; only ElevenLabs voice credits).
  - **Reliability:** 5/5 (deterministic SVG rigs stay strictly on-model across every frame, camera zoom, and pose).
- **Rules:**
  - Always use one warm-black ink (`#1c1416`) at `FLASH_LINE` weights (`outer: 10`, `inner: 5.5`, `detail: 3`) with rounded caps and joins.
  - Always use flat fills from `FLASH_PALETTE` with at most one hard-edged left shadow tone per form via `Shaded` (light from upper right, no gradients).
  - Always pair a muted base palette with saturated accent tokens so characters pop against sets.
  - Always build characters in the shared 640x1080 rig box (feet at `y = 1012`) with rounded torso shapes, stiff tube limbs, lidded oval eyes, and the 8-shape mouth set (`rest`, `mbp`, `ee`, `ah`, `oh`, `oo`, `fv`, `l`).
  - Always step character and mouth animation on twos (`FLASH_STEP = 2`) and drive mouths from word-level alignment with zero mouth movement during silent beats.
  - Never hardcode hex colors or stroke widths inside a piece; import all tokens from `remotion/src/compositions/programmatic-animation/_kit/looks/flash-cutout.ts`.
- **Can't do:**
  - No animated turns between front and three-quarter views (hard cut only; no side or back views).
  - No foreshortening or 3D perspective.
  - No bending bodies, elbows, or fluid full-body acting such as running, dancing, or fighting (use short waddle/shuffle loops, squash dips, or cutaway gags per `../../../shared/staging-limits.md`).
  - No complex hand manipulation beyond fixed grip poses (`holding`, `walker`, `underArm`, or pose-specific hand points).
  - No small on-screen text on monitors, phones, or signs that must be read at 9:16 phone scale (use large pop-up toast cards or full-frame cutaway inserts).
