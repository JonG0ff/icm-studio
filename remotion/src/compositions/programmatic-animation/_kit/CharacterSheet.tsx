import type {ReactNode} from "react";
import {AbsoluteFill} from "remotion";
import {LineBoilFilter, SilhouetteFilter} from "./flash-shapes";
import {FLASH_PALETTE as C} from "./looks/flash-cutout";

export const CHARACTER_SHEET_W = 1920;
export const CHARACTER_SHEET_H = 1300;

const FONT = "Menlo, monospace";
const COL_W = 480;

export type SheetView = "front" | "three-quarter";

export type CharacterSheetProps = {
  title: string;
  subtitle: string;
  /** Draws the character in its 640x1080 box at the given view. */
  figure: (view: SheetView) => ReactNode;
  swatches: ReadonlyArray<readonly [string, string]>;
  /** Line boil on the figures. Off for looks with clean, still lines. */
  boil?: boolean;
};

const PANELS: ReadonlyArray<{label: string; view: SheetView; silhouette: boolean}> = [
  {label: "front", view: "front", silhouette: false},
  {label: "three-quarter", view: "three-quarter", silhouette: false},
  {label: "silhouette / front", view: "front", silhouette: true},
  {label: "silhouette / 3/4", view: "three-quarter", silhouette: true},
];

const Label = ({x, y, size = 26, children}: {x: number; y: number; size?: number; children: ReactNode}) => (
  <text x={x} y={y} textAnchor="middle" fontSize={size} fontFamily={FONT} fill={C.ink}>
    {children}
  </text>
);

/** Workshop 02 clean sheet: both views, both silhouettes, palette. */
export function CharacterSheet({title, subtitle, figure, swatches, boil = true}: CharacterSheetProps) {
  const swatchW = Math.min(182, (CHARACTER_SHEET_W - 120) / swatches.length);
  return (
    <AbsoluteFill style={{backgroundColor: "#f4efe4"}}>
      <svg viewBox={`0 0 ${CHARACTER_SHEET_W} ${CHARACTER_SHEET_H}`} width="100%" height="100%">
        <defs>
          <LineBoilFilter id="sheet-boil" seed={2} scale={3} />
          <SilhouetteFilter id="sheet-silhouette" />
        </defs>
        <text x={60} y={80} fontSize={48} fontWeight={800} fontFamily={FONT} fill={C.ink}>
          {title}
        </text>
        <text x={60} y={124} fontSize={26} fontFamily={FONT} fill={C.ink} opacity={0.6}>
          {subtitle}
        </text>
        {PANELS.map(({label, view, silhouette}, i) => (
          <g key={label} transform={`translate(${i * COL_W} 150)`}>
            <rect x={14} y={0} width={COL_W - 28} height={830} rx={18} fill="#fbf8f1" />
            <g filter={silhouette ? "url(#sheet-silhouette)" : boil ? "url(#sheet-boil)" : undefined} transform="translate(0 -4) scale(0.75)">
              {figure(view)}
            </g>
            <Label x={COL_W / 2} y={872}>
              {label}
            </Label>
          </g>
        ))}
        <text x={60} y={1080} fontSize={34} fontWeight={700} fontFamily={FONT} fill={C.ink}>
          PALETTE
        </text>
        {swatches.map(([name, color], i) => (
          <g key={name} transform={`translate(${60 + i * swatchW} 1104)`}>
            <rect width={swatchW - 18} height={90} rx={12} fill={color} stroke={C.ink} strokeWidth={3} />
            <Label x={(swatchW - 18) / 2} y={122} size={18}>
              {name}
            </Label>
            <Label x={(swatchW - 18) / 2} y={146} size={16}>
              {color}
            </Label>
          </g>
        ))}
      </svg>
    </AbsoluteFill>
  );
}
