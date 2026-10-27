import type {ReactNode} from "react";
import {Crease, useScopedId} from "./flash-shapes";
import {FLASH_LINE, FLASH_PALETTE as C} from "./looks/flash-cutout";
import type {MouthShape} from "./mouth-driver";

export type MouthSetProps = {
  shape: MouthShape;
  /** Mouth center in the character's box. */
  x: number;
  y: number;
  /** 1 = full-size rig head. Small heads use less. */
  scale?: number;
  /** Curve of the resting mouth; positive smiles. */
  restBend?: number;
  /** Lift on the picture-right corner of the resting mouth (smirk). */
  restSmirk?: number;
  /** Lip color for the `oo` pucker. */
  lip?: string;
};

/** An open mouth: dark cavity, contents clipped inside, outline on top. */
function Cavity({id, d, children}: {id: string; d: string; children?: ReactNode}) {
  const clipId = useScopedId(`mouthset-${id}`);
  return (
    <g>
      <clipPath id={clipId}>
        <path d={d} />
      </clipPath>
      <path d={d} fill={C.mouth} />
      <g clipPath={`url(#${clipId})`}>{children}</g>
      <path d={d} fill="none" stroke={C.ink} strokeWidth={FLASH_LINE.inner} strokeLinejoin="round" />
    </g>
  );
}

const TopTeeth = ({y, w}: {y: number; w: number}) => <rect x={-w} y={y} width={w * 2} height={11} fill={C.white} />;

const shapeFor = (shape: MouthShape, restBend: number, restSmirk: number, lip: string): ReactNode => {
  switch (shape) {
    case "rest":
      return <Crease d={`M-26 ${-restBend * 0.4} Q0 ${restBend * 1.6} 26 ${-restBend * 0.4 - restSmirk}`} />;
    case "mbp":
      return (
        <g>
          <Crease d="M-24 0 Q0 4 24 0" width={FLASH_LINE.inner + 1.5} />
          <Crease d="M-12 9 Q0 14 12 9" width={FLASH_LINE.detail} />
        </g>
      );
    case "ee":
      return (
        <Cavity id="ee" d="M-34 -6 Q0 -10 34 -6 Q30 16 0 18 Q-30 16 -34 -6 Z">
          <TopTeeth y={-12} w={36} />
        </Cavity>
      );
    case "ah":
      return (
        <Cavity id="ah" d="M-32 -8 Q0 -14 32 -8 Q30 40 0 46 Q-30 40 -32 -8 Z">
          <TopTeeth y={-16} w={34} />
          <ellipse cx={0} cy={44} rx={22} ry={14} fill={C.tongue} />
        </Cavity>
      );
    case "oh":
      return (
        <Cavity id="oh" d="M0 -18 C16 -18 22 -4 22 10 C22 26 14 34 0 34 C-14 34 -22 26 -22 10 C-22 -4 -16 -18 0 -18 Z">
          <ellipse cx={0} cy={32} rx={14} ry={9} fill={C.tongue} />
        </Cavity>
      );
    case "oo":
      return (
        <g>
          <ellipse cx={0} cy={4} rx={17} ry={16} fill={lip} stroke={C.ink} strokeWidth={FLASH_LINE.inner} />
          <ellipse cx={0} cy={5} rx={8} ry={8} fill={C.mouth} stroke={C.ink} strokeWidth={FLASH_LINE.detail} />
        </g>
      );
    case "fv":
      return (
        <Cavity id="fv" d="M-28 -4 Q0 -8 28 -4 Q24 12 0 14 Q-24 12 -28 -4 Z">
          <TopTeeth y={-10} w={30} />
          <path d="M-30 12 Q0 0 30 12 V20 H-30 Z" fill={C.blush} />
        </Cavity>
      );
    case "l":
      return (
        <Cavity id="l" d="M-30 -6 Q0 -12 30 -6 Q28 30 0 34 Q-28 30 -30 -6 Z">
          <TopTeeth y={-14} w={32} />
          <path d="M-14 36 Q-14 2 0 2 Q14 2 14 36 Z" fill={C.tongue} />
        </Cavity>
      );
  }
};

/**
 * The shared 8-shape mouth set (rig-conventions.md) for any flash-cutout
 * character. Shapes are drawn at full rig-head size and scaled per head.
 */
export function MouthSet({shape, x, y, scale = 1, restBend = 0, restSmirk = 0, lip = C.skin}: MouthSetProps) {
  return <g transform={`translate(${x} ${y}) scale(${scale})`}>{shapeFor(shape, restBend, restSmirk, lip)}</g>;
}
