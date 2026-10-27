/**
 * Path builders for quick parametric shapes. Roughs use them to explore
 * proportions; clean rigs can use them for simple parts.
 */

/** Closed ellipse path. */
export const ellipsePath = (cx: number, cy: number, rx: number, ry: number): string =>
  `M${cx - rx} ${cy} A${rx} ${ry} 0 1 0 ${cx + rx} ${cy} A${rx} ${ry} 0 1 0 ${cx - rx} ${cy} Z`;

export type BlobSpec = {
  cx: number;
  /** Top and bottom edges. */
  y0: number;
  y1: number;
  /** Widths at the top edge, the widest middle, and the bottom edge. */
  top: number;
  mid: number;
  bot: number;
  /** 0-1: where the widest point sits between top and bottom. */
  midAt?: number;
};

/** Symmetric rounded body: torso, robe, belly. */
export const blobPath = ({cx, y0, y1, top, mid, bot, midAt = 0.5}: BlobSpec): string => {
  const h = y1 - y0;
  const c1 = y0 + h * midAt * 0.5;
  const c2 = y0 + h * (midAt + (1 - midAt) * 0.5);
  return [
    `M${cx - top / 2} ${y0}`,
    `C${cx - mid / 2} ${c1} ${cx - mid / 2} ${c2} ${cx - bot / 2} ${y1}`,
    `Q${cx} ${y1 + h * 0.07} ${cx + bot / 2} ${y1}`,
    `C${cx + mid / 2} ${c2} ${cx + mid / 2} ${c1} ${cx + top / 2} ${y0}`,
    `Q${cx} ${y0 - h * 0.05} ${cx - top / 2} ${y0}`,
    "Z",
  ].join(" ");
};

/** Shadow region for the left side of a shape (light comes from upper right). */
export const leftShadePath = (cx: number, width: number, y0: number, y1: number): string =>
  `M-200 -200 H${cx - width * 0.2} C${cx - width * 0.36} ${y0 + (y1 - y0) * 0.45} ${cx - width * 0.12} ${y1} ${cx + width * 0.05} ${y1 + 400} H-200 Z`;

/** Tapered limb from (x0,y0) to (x1,y1) with rounded ends. */
export const limbPath = (x0: number, y0: number, x1: number, y1: number, w0: number, w1: number): string => {
  const dx = x1 - x0;
  const dy = y1 - y0;
  const len = Math.hypot(dx, dy) || 1;
  const ux = dx / len;
  const uy = dy / len;
  const nx = -uy;
  const ny = ux;
  const p = (x: number, y: number, w: number, s: number) => `${x + nx * (w / 2) * s} ${y + ny * (w / 2) * s}`;
  return [
    `M${p(x0, y0, w0, 1)}`,
    `L${p(x1, y1, w1, 1)}`,
    `Q${x1 + ux * w1 * 0.75} ${y1 + uy * w1 * 0.75} ${p(x1, y1, w1, -1)}`,
    `L${p(x0, y0, w0, -1)}`,
    `Q${x0 - ux * w0 * 0.75} ${y0 - uy * w0 * 0.75} ${p(x0, y0, w0, 1)}`,
    "Z",
  ].join(" ");
};
