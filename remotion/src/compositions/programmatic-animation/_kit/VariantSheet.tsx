import type {ReactNode} from "react";
import {AbsoluteFill} from "remotion";
import {LineBoilFilter, ShadeScope, SilhouetteFilter} from "./flash-shapes";
import {FLASH_PALETTE as C} from "./looks/flash-cutout";
import type {SheetView} from "./CharacterSheet";

export const VARIANT_SHEET_W = 1920;
export const VARIANT_SHEET_H = 1300;

const FONT = "Menlo, monospace";
const PANEL_W = 320;
const PANEL_H = 700;
const VIEWS: readonly SheetView[] = ["front", "three-quarter"];

export type VariantSheetProps = {
  title: string;
  subtitle: string;
  /** Exactly three variant names, one pair of panels each. */
  variants: readonly string[];
  /** Draws one variant in its 640x1080 box at the given view. */
  figure: (variant: string, view: SheetView) => ReactNode;
  /** viewBox around the widest, tallest variant in the 640x1080 box. */
  figureBox: string;
  swatches: ReadonlyArray<readonly [string, string]>;
};

const Label = ({x, y, size = 24, children}: {x: number; y: number; size?: number; children: ReactNode}) => (
  <text x={x} y={y} textAnchor="middle" fontSize={size} fontFamily={FONT} fill={C.ink}>
    {children}
  </text>
);

/**
 * Workshop 02 clean sheet for a rig with three variants: front and 3/4 of
 * each variant, all three silhouettes on one ground line, palette.
 */
export function VariantSheet({title, subtitle, variants, figure, figureBox, swatches}: VariantSheetProps) {
  const swatchW = Math.min(110, 1060 / swatches.length);
  return (
    <AbsoluteFill style={{backgroundColor: "#f4efe4"}}>
      <svg viewBox={`0 0 ${VARIANT_SHEET_W} ${VARIANT_SHEET_H}`} width="100%" height="100%">
        <defs>
          <LineBoilFilter id="vsheet-boil" seed={2} scale={3} />
          <SilhouetteFilter id="vsheet-silhouette" />
        </defs>
        <text x={60} y={80} fontSize={48} fontWeight={800} fontFamily={FONT} fill={C.ink}>
          {title}
        </text>
        <text x={60} y={124} fontSize={26} fontFamily={FONT} fill={C.ink} opacity={0.6}>
          {subtitle}
        </text>
        {variants.flatMap((variant, vi) =>
          VIEWS.map((view, ki) => {
            const i = vi * 2 + ki;
            return (
              <g key={`${variant}-${view}`} transform={`translate(${i * PANEL_W} 150)`}>
                <rect x={10} y={0} width={PANEL_W - 20} height={PANEL_H} rx={18} fill="#fbf8f1" />
                <svg x={10} y={10} width={PANEL_W - 20} height={PANEL_H - 20} viewBox={figureBox} preserveAspectRatio="xMidYMax meet">
                  <ShadeScope prefix={`v${i}`}>
                    <g filter="url(#vsheet-boil)">{figure(variant, view)}</g>
                  </ShadeScope>
                </svg>
                <Label x={PANEL_W / 2} y={PANEL_H + 34}>
                  {variant} / {view === "front" ? "front" : "3/4"}
                </Label>
              </g>
            );
          }),
        )}
        <text x={60} y={940} fontSize={34} fontWeight={700} fontFamily={FONT} fill={C.ink}>
          SILHOUETTES
        </text>
        <g transform="translate(60 960)">
          <rect width={640} height={300} rx={18} fill="#fbf8f1" />
          {variants.map((variant, i) => (
            <svg key={variant} x={10 + i * 205} y={10} width={205} height={280} viewBox={figureBox} preserveAspectRatio="xMidYMax meet">
              <ShadeScope prefix={`s${i}`}>
                <g filter="url(#vsheet-silhouette)">{figure(variant, "front")}</g>
              </ShadeScope>
            </svg>
          ))}
        </g>
        <text x={780} y={940} fontSize={34} fontWeight={700} fontFamily={FONT} fill={C.ink}>
          PALETTE
        </text>
        {swatches.map(([name, color], i) => {
          const row = Math.floor(i / 10);
          const col = i % 10;
          return (
            <g key={name} transform={`translate(${780 + col * swatchW} ${960 + row * 150})`}>
              <rect width={swatchW - 14} height={80} rx={10} fill={color} stroke={C.ink} strokeWidth={3} />
              <Label x={(swatchW - 14) / 2} y={104} size={15}>
                {name}
              </Label>
              <Label x={(swatchW - 14) / 2} y={124} size={13}>
                {color}
              </Label>
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
}
