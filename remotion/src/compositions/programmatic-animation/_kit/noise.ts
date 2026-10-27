/**
 * Deterministic 3D value noise for generative looks. Same inputs give the same
 * output on every render, so frames are stable across renders and machines.
 */
const hash3 = (x: number, y: number, z: number, seed: number): number => {
  let h = (x * 374761393 + y * 668265263 + z * 2147483647 + seed * 144269504) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967295;
};

const fade = (t: number): number => t * t * (3 - 2 * t);
const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;

/** Smooth noise in 0-1. */
export const valueNoise3 = (x: number, y: number, z: number, seed = 0): number => {
  const xi = Math.floor(x);
  const yi = Math.floor(y);
  const zi = Math.floor(z);
  const u = fade(x - xi);
  const v = fade(y - yi);
  const w = fade(z - zi);
  const c = (dx: number, dy: number, dz: number) => hash3(xi + dx, yi + dy, zi + dz, seed);
  const x00 = lerp(c(0, 0, 0), c(1, 0, 0), u);
  const x10 = lerp(c(0, 1, 0), c(1, 1, 0), u);
  const x01 = lerp(c(0, 0, 1), c(1, 0, 1), u);
  const x11 = lerp(c(0, 1, 1), c(1, 1, 1), u);
  return lerp(lerp(x00, x10, v), lerp(x01, x11, v), w);
};

/** Two octaves, roughly 0-1. Softer and more organic than one octave. */
export const fbm3 = (x: number, y: number, z: number, seed = 0): number =>
  valueNoise3(x, y, z, seed) * 0.65 + valueNoise3(x * 2.1, y * 2.1, z * 1.7, seed + 7) * 0.35;
