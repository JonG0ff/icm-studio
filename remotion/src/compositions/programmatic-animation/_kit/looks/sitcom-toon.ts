/**
 * sitcom-toon look constants. Every sitcom-toon piece imports from here;
 * never hardcode colors or line weights in a piece.
 *
 * Studied from swipe entries sitcom-toon-01..04: thin even near-black line,
 * flat fills, one soft-edged shade tone, circle eyes with dot pupils.
 */
export const SITCOM_LINE = {
  /** Silhouette edges. Thin and even: no taper, no boil. */
  outer: 5,
  /** Folds, collar, seams, ears. */
  inner: 3.5,
  /** Hair strands, stubble edge, small marks. */
  detail: 2.5,
} as const;

/** Smooth motion: draw on ones. */
export const SITCOM_STEP = 1;

/**
 * Light comes from upper left. The shade tone sits on the picture-right side
 * of each form with a blurred edge (sitcom-toon-03).
 */
export const SITCOM_SHADE = {
  /** Gaussian blur on the shade edge, px in the 640x1080 rig box. */
  blur: 6,
} as const;

export const SITCOM_PALETTE = {
  ink: "#17120f",
  white: "#ffffff",
  eyeWhite: "#ffffff",
  skin: "#f9d3b6",
  skinShade: "#e2b293",
  stubble: "#a8826c",
  hairBrown: "#6e4428",
  hairBrownShade: "#52301b",
  poloBlue: "#4a77a8",
  poloBlueShade: "#3a6190",
  khaki: "#c9ae80",
  khakiShade: "#ab9064",
  belt: "#4a3020",
  buckle: "#c8c8c4",
  sneaker: "#f6f5f1",
  sneakerShade: "#d8d6cf",
  sole: "#9a9890",
  mouth: "#5a1d1f",
  tongue: "#e07a7a",
  teeth: "#ffffff",
  // Sheet and set neutrals (muted so characters pop, sitcom-toon-02/04)
  sheetBg: "#efe6d6",
  panel: "#fbf7ef",
  // News desk (look test)
  studioWall: "#5d6b7c",
  studioWallShade: "#4c5868",
  studioPanel: "#6f7e90",
  studioFloor: "#3e4652",
  desk: "#7a5a44",
  deskShade: "#634936",
  deskTop: "#9a7a60",
  bezel: "#24272c",
  banner: "#b8322e",
  bannerDark: "#1f2a3a",
  bannerText: "#ffffff",
  // Backyard (look test clip)
  sky: "#9cc4e4",
  skyLow: "#c4dcec",
  fence: "#b49a78",
  fenceShade: "#9a8262",
  grass: "#7fa45a",
  grassShade: "#6a8c4a",
  brick: "#a3584a",
  plank: "#c09a6a",
  poolRim: "#d2463e",
  poolRimShade: "#a8342e",
  water: "#6fb6dc",
  waterLight: "#b6e0f2",
  cartMetal: "#b4bcc4",
  cartShade: "#8c949c",
  wheel: "#2c2f34",
  recRed: "#e0352c",
} as const;
