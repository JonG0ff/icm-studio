import type {ReactNode} from "react";
import {AbsoluteFill, random, useCurrentFrame} from "remotion";
import {beatAt, jitter, stepFrame} from "./timing";

/** Polygon around an ellipse with a ragged, hand-torn edge. */
const tornEllipse = (cx: number, cy: number, rx: number, ry: number, seed: string): string =>
  Array.from({length: 48}, (_, i) => {
    const a = (i / 48) * Math.PI * 2;
    const k = 1 + (random(`${seed}-${i}`) - 0.5) * 0.07;
    return `${(cx + Math.cos(a) * rx * k).toFixed(1)},${(cy + Math.sin(a) * ry * k).toFixed(1)}`;
  }).join(" ");

/** Polygon around a rectangle with ragged edges. */
const tornRect = (x: number, y: number, w: number, h: number, seed: string): string => {
  const edge = (from: [number, number], to: [number, number], side: number) =>
    Array.from({length: 10}, (_, i) => {
      const t = i / 10;
      const n = jitter(`${seed}-${side}-${i}`, 7);
      return `${(from[0] + (to[0] - from[0]) * t + (side % 2 ? n : 0)).toFixed(1)},${(from[1] + (to[1] - from[1]) * t + (side % 2 ? 0 : n)).toFixed(1)}`;
    });
  return [
    ...edge([x, y], [x + w, y], 0),
    ...edge([x + w, y], [x + w, y + h], 1),
    ...edge([x + w, y + h], [x, y + h], 2),
    ...edge([x, y + h], [x, y], 3),
  ].join(" ");
};

/** Every cut piece wobbles a little each held drawing: stiff on purpose. */
const Piece = ({id, step, children}: {id: string; step: number; children: ReactNode}) => (
  <g
    filter="url(#paper)"
    transform={`translate(${jitter(`${id}-x-${step}`, 3)} ${jitter(`${id}-y-${step}`, 3)}) rotate(${jitter(`${id}-r-${step}`, 1.2)} 540 900)`}
  >
    {children}
  </g>
);

const LETTERS = [
  {ch: "N", bg: "#f2e6c9", fg: "#b3261e", font: "Georgia, serif"},
  {ch: "E", bg: "#1f1f1f", fg: "#f2e6c9", font: "Impact, sans-serif"},
  {ch: "W", bg: "#d9c27a", fg: "#1f1f1f", font: "Courier New, monospace"},
  {ch: "S", bg: "#9fb8c9", fg: "#b3261e", font: "Times New Roman, serif"},
];

/**
 * paper-collage: torn paper scraps, oversized head on a tiny body, a
 * hinged skull for a mouth. Animated on threes; the stiffness is the joke.
 */
export function PaperCollage() {
  const frame = stepFrame(useCurrentFrame(), 3);
  const beat = beatAt(frame);
  const step = frame / 3;
  const talking = beat.mouth === "open" || beat.mouth === "wide";
  const skullLift = beat.shocked ? -38 : talking ? (beat.mouth === "wide" ? -22 : -12) : 0;
  const headPop = beat.jump * 160;
  const eyeR = beat.shocked ? 62 : 36;

  return (
    <AbsoluteFill style={{backgroundColor: "#c9a66b"}}>
      <svg viewBox="0 0 1080 1920" width="100%" height="100%">
        <defs>
          <filter id="paper" x="-10%" y="-10%" width="120%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={3} seed={7} result="grain" />
            <feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -0.9 0.55" result="speck" />
            <feComposite in="speck" in2="SourceGraphic" operator="in" result="textured" />
            <feMerge result="merged">
              <feMergeNode in="SourceGraphic" />
              <feMergeNode in="textured" />
            </feMerge>
            <feDropShadow in="merged" dx={8} dy={10} stdDeviation={4} floodOpacity={0.35} />
          </filter>
        </defs>

        {/* Ransom-note sign: every letter its own scrap */}
        {LETTERS.map((l, i) => {
          const x = 170 + i * 190;
          return (
            <Piece key={l.ch} id={`letter-${i}`} step={step}>
              <polygon points={tornRect(x, 420, 170, 200, `letter-${i}`)} fill={beat.shocked && i % 2 ? "#e85d3a" : l.bg} />
              <text x={x + 85} y={580} textAnchor="middle" fontSize={170} fontFamily={l.font} fontWeight={700} fill={l.fg}>
                {beat.shocked ? "?!"[i % 2] : l.ch}
              </text>
            </Piece>
          );
        })}

        <g transform={`translate(${Math.round(-beat.enter * 3) * 300} 0)`}>
          {/* Tiny body */}
          <Piece id="body" step={step}>
            <polygon points={tornRect(450, 1110, 180, 220, "body")} fill="#3b4d61" />
            <polygon points={tornRect(515, 1110, 50, 120, "tie")} fill="#b3261e" />
          </Piece>
          {/* Stiff arm strip, rotates as one block */}
          <g transform={`rotate(${-130 * beat.armUp} 615 1140)`}>
            <Piece id="arm" step={step}>
              <polygon points={tornRect(600, 1130, 40, 210, "arm")} fill="#3b4d61" />
              <polygon points={tornEllipse(620, 1350, 38, 34, "hand")} fill="#e8c4a0" />
            </Piece>
          </g>
          <g transform={`translate(0 ${-headPop})`}>
            {/* Jaw stays put */}
            <Piece id="jaw" step={step}>
              <polygon points={tornRect(380, 920, 320, 170, "jaw")} fill="#e8c4a0" />
              <rect x={440} y={935} width={200} height={24} fill="#5a1414" />
            </Piece>
            {/* Skull hinges open at the back of the head */}
            <g transform={`rotate(${skullLift} 380 930)`}>
              <Piece id="skull" step={step}>
                <polygon points={tornEllipse(540, 800, 240, 160, "skull")} fill="#e8c4a0" />
                <polygon points={tornRect(330, 640, 420, 90, "hat")} fill="#1f1f1f" />
                <polygon points={tornEllipse(465, 810, eyeR + 12, eyeR + 12, "eyeL")} fill="#fffaf0" />
                <polygon points={tornEllipse(615, 810, eyeR + 12, eyeR + 12, "eyeR")} fill="#fffaf0" />
                <circle cx={470} cy={815} r={beat.blink ? 0 : 14} fill="#1f1f1f" />
                <circle cx={620} cy={815} r={beat.blink ? 0 : 14} fill="#1f1f1f" />
                <polygon points={tornRect(470, 880, 140, 40, "mustache")} fill="#5c3a1e" />
              </Piece>
            </g>
          </g>
        </g>

        {/* Desk: a scrap of wood-grain paper */}
        <Piece id="desk" step={step}>
          <polygon points={tornRect(60, 1300, 960, 400, "desk")} fill="#6e4a2a" />
          <polygon points={tornRect(60, 1290, 960, 60, "desktop")} fill="#9a6b3d" />
        </Piece>
      </svg>
    </AbsoluteFill>
  );
}
