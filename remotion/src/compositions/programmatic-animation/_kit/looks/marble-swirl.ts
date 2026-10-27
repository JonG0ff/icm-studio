/**
 * marble-swirl look constants. Every marble-swirl piece imports from here;
 * never hardcode colors or line weights in a piece.
 *
 * Studied from swipe entry marble-swirl-01: a circular mask full of flat,
 * overlapping flow-field ribbons, a radial spike-burst pupil, a hand-sketched
 * orange-red rim, dashed orbit arcs for spin, all on cream paper.
 */
export const MARBLE_PALETTE = {
  paper: "#e5ddc4",
  paperShade: "#d6cbb0",
  smudge: "#c9b9b4",
  irisBase: "#e8d5c0",
  irisFiber: "#8d5d55",
  ink: "#1d1717",
  sketch: "#3b302c",
  rim: "#d4462a",
  rimShade: "#a8321d",
  rimLight: "#f08a5d",
  /** A character before the color reaches him. */
  manGray: "#8b8079",
} as const;

/** Ribbon colors. Black stays in the set: it gives the swirl its depth. */
export const MARBLE_RIBBONS = [
  "#2bb3c8", // cyan
  "#e2337d", // magenta
  "#d9a92b", // mustard
  "#1f7f86", // teal
  "#f07aa7", // pink
  "#1d1717", // black
  "#e85a2f", // orange-red
  "#88aa9b", // sage
] as const;

export const MARBLE_LINE = {
  /** Fine iris fibers and spike-burst spikes. */
  fiber: 1.4,
  /** Dashed orbit arcs and rim sketch passes. */
  sketch: 2.6,
  /** Halo rim body. */
  rim: 30,
} as const;

/**
 * Landscape colors for scenes that build a world round a piece. `gloom`
 * values are the world in the storm; the others are after it clears.
 */
export const MARBLE_LAND = {
  grassGloom: "#8e9184",
  grass: "#7fb35c",
  dirtGloom: "#b2a690",
  dirt: "#c9a67a",
  stoneGloom: "#9a9ca0",
  stone: "#93b2c6",
  snow: "#f4f1ea",
  rockGloom: "#a19e97",
  rock: "#b3b0a8",
  hillGloom: "#8f9188",
  hill: "#79a86a",
  plainGloom: "#aaa797",
  plain: "#a8cf8a",
  waterGloom: "#7d858c",
  water: "#2bb3c8",
  waterLight: "#d6f3f6",
  leafGloom: "#6f756c",
  bark: "#5b4636",
  cloud: "#9b958f",
  cloudShade: "#6f6a66",
  cloudLight: "#bab4ac",
} as const;
