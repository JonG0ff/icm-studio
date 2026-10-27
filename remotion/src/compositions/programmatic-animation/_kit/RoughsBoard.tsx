import type {ComponentType} from "react";
import {AbsoluteFill} from "remotion";
import {LineBoilFilter, ShadeScope, SilhouetteFilter} from "./flash-shapes";
import {FLASH_PALETTE as C} from "./looks/flash-cutout";

export type RoughDirection = {letter: string; name: string; note: string; component: ComponentType};

export const ROUGHS_COL_W = 640;
export const ROUGHS_H = 1240;

/**
 * Rough directions side by side for the workshop 02 checkpoint. Each column
 * also shows a small solid-black silhouette for the phone-size read.
 */
export function RoughsBoard({directions}: {directions: readonly RoughDirection[]}) {
  const width = directions.length * ROUGHS_COL_W;
  return (
    <AbsoluteFill style={{backgroundColor: "#ece6da"}}>
      <svg viewBox={`0 0 ${width} ${ROUGHS_H}`} width="100%" height="100%">
        <defs>
          <LineBoilFilter id="roughs-boil" seed={1} scale={3} />
          <SilhouetteFilter id="roughs-silhouette" />
        </defs>
        {directions.map(({letter, name, note, component: Rough}, i) => (
          <g key={letter} transform={`translate(${i * ROUGHS_COL_W} 0)`}>
            <rect x={20} y={20} width={ROUGHS_COL_W - 40} height={ROUGHS_H - 40} rx={24} fill="#f7f3ea" />
            <ShadeScope prefix={`r${letter}`}>
              <g filter="url(#roughs-boil)" transform="translate(0 20)">
                <Rough />
              </g>
            </ShadeScope>
            <ShadeScope prefix={`s${letter}`}>
              <g filter="url(#roughs-silhouette)" transform="translate(470 40) scale(0.22)">
                <Rough />
              </g>
            </ShadeScope>
            <text x={ROUGHS_COL_W / 2} y={1150} textAnchor="middle" fontSize={44} fontWeight={800} fontFamily="Menlo, monospace" fill={C.ink}>
              {letter} / {name}
            </text>
            <text x={ROUGHS_COL_W / 2} y={1195} textAnchor="middle" fontSize={24} fontFamily="Menlo, monospace" fill={C.ink} opacity={0.65}>
              {note}
            </text>
          </g>
        ))}
      </svg>
    </AbsoluteFill>
  );
}
