import type {ReactNode} from "react";
import {useScopedId} from "./flash-shapes";
import {SITCOM_LINE, SITCOM_PALETTE, SITCOM_SHADE} from "./looks/sitcom-toon";

/** Soft-edge filter for shade tones. Define once per ShadeScope. */
export function SoftShadeFilter() {
  const id = useScopedId("sitcom-soft");
  return (
    <filter id={id} x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation={SITCOM_SHADE.blur} />
    </filter>
  );
}

type SoftShadedProps = {
  /** Unique within the current ShadeScope; used for the clip path. */
  id: string;
  d: string;
  fill: string;
  /** Shade tone, blurred and clipped to the shape. */
  shade?: string;
  shadeD?: string;
  line?: number;
  children?: ReactNode;
};

/**
 * A flat-filled part with one soft-edged shade tone and its outline on top,
 * so the shade never spills past the line. Needs a SoftShadeFilter in scope.
 */
export function SoftShaded({id, d, fill, shade, shadeD, line = SITCOM_LINE.outer, children}: SoftShadedProps) {
  const clipId = useScopedId(`clip-${id}`);
  const softId = useScopedId("sitcom-soft");
  return (
    <g>
      <clipPath id={clipId}>
        <path d={d} />
      </clipPath>
      <path d={d} fill={fill} />
      <g clipPath={`url(#${clipId})`}>
        {shade && shadeD ? <path d={shadeD} fill={shade} filter={`url(#${softId})`} /> : null}
        {children}
      </g>
      <path d={d} fill="none" stroke={SITCOM_PALETTE.ink} strokeWidth={line} strokeLinejoin="round" strokeLinecap="round" />
    </g>
  );
}

/** A second soft-edged tone inside a SoftShaded part (e.g. pants under a shirt). */
export function SoftTone({d, fill}: {d: string; fill: string}) {
  const softId = useScopedId("sitcom-soft");
  return <path d={d} fill={fill} filter={`url(#${softId})`} />;
}

/** Thin inner line: folds, seams, chin, ears. */
export function InkLine({d, width = SITCOM_LINE.inner}: {d: string; width?: number}) {
  return <path d={d} fill="none" stroke={SITCOM_PALETTE.ink} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" />;
}

/** Shade region for the picture-right side of a form (light from upper left). */
export const rightShadePath = (cx: number, width: number, y0: number, y1: number): string =>
  `M2000 -200 H${cx + width * 0.22} C${cx + width * 0.38} ${y0 + (y1 - y0) * 0.45} ${cx + width * 0.16} ${y1} ${cx - width * 0.02} ${y1 + 400} H2000 Z`;
