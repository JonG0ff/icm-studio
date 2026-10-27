import {createContext, useContext, type ReactNode} from "react";
import {FLASH_BOIL, FLASH_LINE, FLASH_PALETTE} from "./looks/flash-cutout";

/**
 * Prefix for clip-path ids, so several copies of a character can share one
 * SVG document (design sheets, crowds) without id collisions.
 */
const ShadeScopeContext = createContext("s");

export function ShadeScope({prefix, children}: {prefix: string; children: ReactNode}) {
  return <ShadeScopeContext.Provider value={prefix.replace(/[^a-zA-Z0-9_-]/g, "")}>{children}</ShadeScopeContext.Provider>;
}

/** Scoped id for a clip path or filter inside the current ShadeScope. */
export const useScopedId = (id: string): string => `${useContext(ShadeScopeContext)}-${id}`;

type ShadedProps = {
  /** Unique within the current ShadeScope; used for the clip path. */
  id: string;
  d: string;
  fill: string;
  /** Shadow tone, clipped to the shape. */
  shade?: string;
  shadeD?: string;
  line?: number;
  children?: ReactNode;
};

/**
 * A flat-filled part with one clipped shadow tone and its outline drawn on
 * top, so the shadow never spills past the line.
 */
export function Shaded({id, d, fill, shade, shadeD, line = FLASH_LINE.outer, children}: ShadedProps) {
  const clipId = useScopedId(`clip-${id}`);
  return (
    <g>
      <clipPath id={clipId}>
        <path d={d} />
      </clipPath>
      <path d={d} fill={fill} />
      <g clipPath={`url(#${clipId})`}>
        {shade && shadeD ? <path d={shadeD} fill={shade} /> : null}
        {children}
      </g>
      <path d={d} fill="none" stroke={FLASH_PALETTE.ink} strokeWidth={line} strokeLinejoin="round" strokeLinecap="round" />
    </g>
  );
}

/** Thin inner line: folds, creases, contours. */
export function Crease({d, width = FLASH_LINE.inner}: {d: string; width?: number}) {
  return <path d={d} fill="none" stroke={FLASH_PALETTE.ink} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" />;
}

/** Line-boil filter definition. `seed` changes per held drawing. */
export function LineBoilFilter({id, seed, scale = FLASH_BOIL.scale}: {id: string; seed: number; scale?: number}) {
  return (
    <filter id={id}>
      <feTurbulence type="fractalNoise" baseFrequency={FLASH_BOIL.frequency} numOctaves={2} seed={seed} />
      <feDisplacementMap in="SourceGraphic" scale={scale} />
    </filter>
  );
}

/** Solid-black silhouette filter for the "reads at phone size" check. */
export function SilhouetteFilter({id}: {id: string}) {
  return (
    <filter id={id}>
      <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" />
    </filter>
  );
}

/** Render children mirrored around a vertical axis (for symmetric limbs). */
export function Mirror({axis, children}: {axis: number; children: ReactNode}) {
  return <g transform={`translate(${axis * 2} 0) scale(-1 1)`}>{children}</g>;
}
