import type {ReactNode} from "react";
import {AbsoluteFill} from "remotion";
import {LineBoilFilter} from "./flash-shapes";
import {FLASH_PALETTE as C} from "./looks/flash-cutout";

export const POSE_BOARD_W = 1920;

const FONT = "Menlo, monospace";
const CELL_W = 450;
const CELL_H = 560;
const POSES_PER_ROW = 4;

export type PoseCell = {label: string; render: () => ReactNode};
export type FaceCell = {label: string; render: () => ReactNode};

export type PoseSheetBoardProps = {
  title: string;
  subtitle: string;
  poses: readonly PoseCell[];
  expressions: readonly FaceCell[];
  mouths: readonly FaceCell[];
  /** viewBox around the character's whole figure in its 640x1080 box. */
  figureBox: string;
  /** viewBox around the character's head, for expression and mouth crops. */
  headBox: string;
  /** Line boil on the figures. Off for looks with clean, still lines. */
  boil?: boolean;
};

const Label = ({x, y, size = 24, children}: {x: number; y: number; size?: number; children: ReactNode}) => (
  <text x={x} y={y} textAnchor="middle" fontSize={size} fontFamily={FONT} fill={C.ink}>
    {children}
  </text>
);

const Section = ({y, children}: {y: number; children: ReactNode}) => (
  <text x={60} y={y} fontSize={34} fontWeight={700} fontFamily={FONT} fill={C.ink}>
    {children}
  </text>
);

/** Height of the board for a given pose count. */
export const poseBoardHeight = (poseCount: number): number => 175 + Math.ceil(poseCount / POSES_PER_ROW) * (CELL_H + 20) + 900;

/** Workshop 03 pose sheet: every pose, expression and mouth on one still. */
export function PoseSheetBoard({title, subtitle, poses, expressions, mouths, figureBox, headBox, boil = true}: PoseSheetBoardProps) {
  const figureFilter = boil ? "url(#pose-boil)" : undefined;
  const posesBottom = 175 + Math.ceil(poses.length / POSES_PER_ROW) * (CELL_H + 20);
  const exprW = (POSE_BOARD_W - 120) / expressions.length;
  const mouthW = (POSE_BOARD_W - 120) / mouths.length;
  return (
    <AbsoluteFill style={{backgroundColor: "#f4efe4"}}>
      <svg viewBox={`0 0 ${POSE_BOARD_W} ${poseBoardHeight(poses.length)}`} width="100%" height="100%">
        <defs>
          <LineBoilFilter id="pose-boil" seed={3} scale={3} />
        </defs>
        <text x={60} y={80} fontSize={48} fontWeight={800} fontFamily={FONT} fill={C.ink}>
          {title}
        </text>
        <text x={60} y={124} fontSize={26} fontFamily={FONT} fill={C.ink} opacity={0.6}>
          {subtitle}
        </text>
        <Section y={160}>POSES</Section>
        {poses.map(({label, render}, i) => (
          <g key={label} transform={`translate(${60 + (i % POSES_PER_ROW) * (CELL_W + 10)} ${175 + Math.floor(i / POSES_PER_ROW) * (CELL_H + 20)})`}>
            <rect width={CELL_W} height={CELL_H} rx={18} fill="#fbf8f1" />
            <svg x={10} y={10} width={CELL_W - 20} height={CELL_H - 70} viewBox={figureBox}>
              <g filter={figureFilter}>{render()}</g>
            </svg>
            <Label x={CELL_W / 2} y={CELL_H - 22}>
              {label}
            </Label>
          </g>
        ))}
        <Section y={posesBottom + 40}>EXPRESSIONS</Section>
        {expressions.map(({label, render}, i) => (
          <g key={label} transform={`translate(${60 + i * exprW} ${posesBottom + 65})`}>
            <rect width={exprW - 14} height={370} rx={18} fill="#fbf8f1" />
            <svg x={6} y={6} width={exprW - 26} height={316} viewBox={headBox}>
              <g filter={figureFilter}>{render()}</g>
            </svg>
            <Label x={(exprW - 14) / 2} y={352}>
              {label}
            </Label>
          </g>
        ))}
        <Section y={posesBottom + 490}>MOUTH SET</Section>
        {mouths.map(({label, render}, i) => (
          <g key={label} transform={`translate(${60 + i * mouthW} ${posesBottom + 515})`}>
            <rect width={mouthW - 12} height={260} rx={16} fill="#fbf8f1" />
            <svg x={5} y={4} width={mouthW - 22} height={214} viewBox={headBox}>
              {render()}
            </svg>
            <Label x={(mouthW - 12) / 2} y={244} size={22}>
              {label}
            </Label>
          </g>
        ))}
      </svg>
    </AbsoluteFill>
  );
}
