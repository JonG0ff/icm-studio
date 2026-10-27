import {AbsoluteFill, useCurrentFrame} from "remotion";
import {beatAt, stepFrame, type Mouth} from "./timing";

/** 90x160 grid scaled exactly 12x to 1080x1920. Never fractional. */
const GRID_W = 90;
const GRID_H = 160;

/** PICO-8 palette subset: a tight palette is part of the look. */
const P = {
  night: "#1d2b53",
  wall: "#29366f",
  star: "#fff1e8",
  ink: "#000000",
  skin: "#ffccaa",
  hair: "#ab5236",
  suit: "#008751",
  suitDark: "#005c37",
  desk: "#7e2553",
  deskTop: "#ff77a8",
  screen: "#29adff",
  alert: "#ff004d",
  yellow: "#ffec27",
  white: "#fff1e8",
};

type PxProps = {x: number; y: number; w?: number; h?: number; c: string};
const Px = ({x, y, w = 1, h = 1, c}: PxProps) => (
  <rect x={x} y={y} width={w} height={h} fill={c} />
);

const STARS: ReadonlyArray<readonly [number, number]> = [
  [6, 10], [20, 22], [70, 8], [82, 30], [40, 14], [58, 26], [12, 40], [76, 46],
];

const MOUTHS: Record<Mouth, PxProps> = {
  closed: {x: 43, y: 69, w: 4, h: 1, c: P.ink},
  open: {x: 43, y: 68, w: 4, h: 2, c: P.ink},
  wide: {x: 42, y: 68, w: 6, h: 3, c: P.ink},
  o: {x: 43, y: 68, w: 3, h: 4, c: P.ink},
};

const Anchor = ({shocked, blink, mouth, armUp}: {shocked: boolean; blink: boolean; mouth: Mouth; armUp: boolean}) => (
  <g>
    {/* Body */}
    <Px x={34} y={76} w={22} h={34} c={P.suit} />
    <Px x={34} y={76} w={2} h={34} c={P.suitDark} />
    <Px x={43} y={76} w={4} h={6} c={P.white} />
    {/* Arm: two discrete poses, no rotation */}
    {armUp ? (
      <>
        <Px x={56} y={70} w={4} h={10} c={P.suit} />
        <Px x={58} y={62} w={4} h={8} c={P.suit} />
        <Px x={58} y={58} w={4} h={4} c={P.skin} />
      </>
    ) : null}
    {/* Head */}
    <Px x={37} y={56} w={16} h={18} c={P.skin} />
    <Px x={36} y={54} w={18} h={5} c={P.hair} />
    <Px x={36} y={59} w={2} h={4} c={P.hair} />
    {/* Eyes */}
    {blink ? (
      <>
        <Px x={40} y={63} w={3} h={1} c={P.ink} />
        <Px x={47} y={63} w={3} h={1} c={P.ink} />
      </>
    ) : shocked ? (
      <>
        <Px x={39} y={61} w={4} h={4} c={P.white} />
        <Px x={47} y={61} w={4} h={4} c={P.white} />
        <Px x={41} y={63} c={P.ink} />
        <Px x={49} y={63} c={P.ink} />
      </>
    ) : (
      <>
        <Px x={40} y={62} w={2} h={2} c={P.ink} />
        <Px x={48} y={62} w={2} h={2} c={P.ink} />
      </>
    )}
    <Px {...MOUTHS[mouth]} />
  </g>
);

/**
 * pixel-art: tight palette, discrete poses, whole-pixel moves on threes,
 * CRT scanlines as the finishing filter.
 */
export function PixelArt() {
  const frame = stepFrame(useCurrentFrame(), 3);
  const beat = beatAt(frame);
  const dx = Math.round(-beat.enter * 70);
  const dy = Math.round(-beat.jump * 8);
  const alertOn = beat.shocked && Math.floor(frame / 6) % 2 === 0;

  return (
    <AbsoluteFill style={{backgroundColor: P.night}}>
      <svg viewBox={`0 0 ${GRID_W} ${GRID_H}`} width="100%" height="100%" shapeRendering="crispEdges">
        {STARS.map(([x, y]) => (
          <Px key={`${x}-${y}`} x={x} y={y} c={P.star} />
        ))}
        <Px x={0} y={50} w={GRID_W} h={60} c={P.wall} />
        {/* Monitor */}
        <Px x={14} y={30} w={62} h={18} c={P.ink} />
        <Px x={16} y={32} w={58} h={14} c={alertOn ? P.alert : P.screen} />
        {beat.shocked ? (
          <>
            <Px x={44} y={34} w={2} h={7} c={P.yellow} />
            <Px x={44} y={43} w={2} h={2} c={P.yellow} />
          </>
        ) : (
          <Px x={22} y={38} w={46} h={2} c={P.white} />
        )}
        <g transform={`translate(${dx} ${dy})`}>
          <Anchor shocked={beat.shocked} blink={beat.blink} mouth={beat.mouth} armUp={beat.armUp > 0.5} />
        </g>
        {/* Desk */}
        <Px x={4} y={108} w={82} h={3} c={P.deskTop} />
        <Px x={6} y={111} w={78} h={30} c={P.desk} />
        <Px x={6} y={111} w={78} h={1} c={P.ink} />
      </svg>
      <AbsoluteFill
        style={{
          backgroundImage: "repeating-linear-gradient(0deg, rgba(0,0,0,0.28) 0px, rgba(0,0,0,0.28) 3px, transparent 3px, transparent 6px)",
        }}
      />
    </AbsoluteFill>
  );
}
