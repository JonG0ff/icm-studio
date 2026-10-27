import type {ReactNode} from "react";
import {useScopedId} from "./flash-shapes";
import {InkLine} from "./sitcom-shapes";
import {SITCOM_LINE, SITCOM_PALETTE as C} from "./looks/sitcom-toon";
import type {MouthShape} from "./mouth-driver";

export type SitcomMouthSetProps = {
  shape: MouthShape;
  /** Mouth center in the character's box. */
  x: number;
  y: number;
  scale?: number;
  /** Curve of the resting mouth; positive smiles. */
  restBend?: number;
  /** Lift on the picture-right corner of the resting mouth (smirk). */
  restSmirk?: number;
  /** Skin tone for the lower lip on `fv` and the `oo` pucker. */
  skin?: string;
};

/** An open mouth: dark cavity, contents clipped inside, outline on top. */
function Cavity({id, d, children}: {id: string; d: string; children?: ReactNode}) {
  const clipId = useScopedId(`sitcom-mouth-${id}`);
  return (
    <g>
      <clipPath id={clipId}>
        <path d={d} />
      </clipPath>
      <path d={d} fill={C.mouth} />
      <g clipPath={`url(#${clipId})`}>{children}</g>
      <path d={d} fill="none" stroke={C.ink} strokeWidth={SITCOM_LINE.inner} strokeLinejoin="round" />
    </g>
  );
}

const TopTeeth = ({y, w}: {y: number; w: number}) => <rect x={-w} y={y} width={w * 2} height={10} fill={C.teeth} />;

const shapeFor = (shape: MouthShape, restBend: number, restSmirk: number, skin: string): ReactNode => {
  switch (shape) {
    case "rest":
      return (
        <g>
          <InkLine d={`M-30 ${-restBend * 0.4} Q0 ${restBend * 1.6} 30 ${-restBend * 0.4 - restSmirk}`} />
          {/* Corner ticks: the small dimple marks at each end (sitcom-toon-03). */}
          <InkLine d={`M-33 ${-restBend * 0.4 - 4} Q-31 ${-restBend * 0.4} -27 ${-restBend * 0.4 + 3}`} width={SITCOM_LINE.detail} />
          <InkLine d={`M33 ${-restBend * 0.4 - restSmirk - 4} Q31 ${-restBend * 0.4 - restSmirk} 27 ${-restBend * 0.4 - restSmirk + 3}`} width={SITCOM_LINE.detail} />
        </g>
      );
    case "mbp":
      return <InkLine d="M-26 0 Q0 5 26 0" width={SITCOM_LINE.inner + 1} />;
    case "ee":
      return (
        <Cavity id="ee" d="M-34 -6 Q0 -10 34 -6 Q30 14 0 16 Q-30 14 -34 -6 Z">
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
          <ellipse cx={0} cy={4} rx={15} ry={14} fill={skin} stroke={C.ink} strokeWidth={SITCOM_LINE.inner} />
          <ellipse cx={0} cy={5} rx={7} ry={7} fill={C.mouth} stroke={C.ink} strokeWidth={SITCOM_LINE.detail} />
        </g>
      );
    case "fv":
      return (
        <Cavity id="fv" d="M-28 -4 Q0 -8 28 -4 Q24 12 0 14 Q-24 12 -28 -4 Z">
          <TopTeeth y={-10} w={30} />
          <path d="M-30 12 Q0 2 30 12 V20 H-30 Z" fill={skin} />
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
 * The shared 8-shape mouth set (rig-conventions.md) for any sitcom-toon
 * character, drawn with the look's thin line.
 */
export function SitcomMouthSet({shape, x, y, scale = 1, restBend = 0, restSmirk = 0, skin = C.skin}: SitcomMouthSetProps) {
  return <g transform={`translate(${x} ${y}) scale(${scale})`}>{shapeFor(shape, restBend, restSmirk, skin)}</g>;
}
