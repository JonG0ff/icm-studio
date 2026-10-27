import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from "remotion";
import {beatAt, type Mouth} from "./timing";

const C = {
  bg: "#ffcf3f",
  wall: "#ffb627",
  body: "#3d5afe",
  bodyShade: "#2f46d1",
  skin: "#ffb48a",
  ink: "#1b1b3a",
  desk: "#ff5d73",
  deskTop: "#ff8597",
  bar: "#1b1b3a",
  accent: "#00c2a8",
};

const MOUTH_RY: Record<Mouth, number> = {closed: 4, open: 22, wide: 36, o: 60};

const CHART = [0.35, 0.6, 0.45, 0.9];

/**
 * flat-vector: no outlines, clean geometry, smooth full-frame motion,
 * pushed squash and stretch so it doesn't read as corporate.
 */
export function FlatVector() {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const beat = beatAt(frame);

  const shockSpring = beat.shocked ? spring({frame: frame - 76, fps, config: {damping: 7, stiffness: 180}}) : 0;
  const squashY = 1 + 0.28 * Math.sin(shockSpring * Math.PI);
  const squashX = 1 / squashY;
  const mouthRy = MOUTH_RY[beat.mouth];
  const eyeR = beat.blink ? 3 : beat.shocked ? 56 : 30;
  const chartIn = interpolate(frame, [10, 40], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});

  return (
    <AbsoluteFill style={{backgroundColor: C.bg}}>
      <svg viewBox="0 0 1080 1920" width="100%" height="100%">
        <circle cx={540} cy={760} r={520} fill={C.wall} />
        {/* Data-driven monitor chart */}
        <rect x={150} y={400} width={780} height={300} rx={36} fill={C.ink} />
        {CHART.map((v, i) => {
          const h = 220 * v * chartIn * (beat.shocked && i === 3 ? 0.15 : 1);
          return <rect key={i} x={210 + i * 180} y={670 - h} width={110} height={h} rx={14} fill={i === 3 ? C.desk : C.accent} />;
        })}

        <g transform={`translate(${-beat.enter * 900} ${-beat.jump * 110})`}>
          <g transform={`translate(540 1300) scale(${squashX} ${squashY}) translate(-540 -1300)`}>
            {/* Body is one pill */}
            <rect x={370} y={980} width={340} height={420} rx={170} fill={C.body} />
            <rect x={370} y={1080} width={120} height={320} rx={60} fill={C.bodyShade} />
            {/* Arm */}
            <g transform={`rotate(${-140 * beat.armUp} 680 1060)`}>
              <rect x={650} y={1040} width={64} height={240} rx={32} fill={C.body} />
              <circle cx={682} cy={1290} r={44} fill={C.skin} />
            </g>
            {/* Head */}
            <circle cx={540} cy={830} r={200} fill={C.skin} />
            <path d="M340 820 A200 200 0 0 1 740 820 Q640 700 540 730 Q440 700 340 820 Z" fill={C.ink} />
            <ellipse cx={470} cy={840} rx={eyeR * 0.85} ry={eyeR} fill={C.ink} />
            <ellipse cx={610} cy={840} rx={eyeR * 0.85} ry={eyeR} fill={C.ink} />
            {beat.shocked ? (
              <>
                <circle cx={482} cy={826} r={14} fill="#fff" />
                <circle cx={622} cy={826} r={14} fill="#fff" />
              </>
            ) : null}
            <ellipse cx={540} cy={950} rx={beat.mouth === "o" ? 40 : 64} ry={mouthRy} fill="#7a1f3d" />
          </g>
        </g>

        {/* Desk */}
        <rect x={60} y={1300} width={960} height={420} rx={40} fill={C.desk} />
        <rect x={60} y={1300} width={960} height={50} rx={25} fill={C.deskTop} />
        {/* Lower third: swaps from data */}
        <rect x={100} y={1420} width={620 * chartIn} height={110} rx={20} fill={C.bar} />
        <text x={140} y={1495} fontSize={56} fontWeight={800} fontFamily="Helvetica, Arial, sans-serif" fill="#fff" opacity={chartIn}>
          {beat.shocked ? "MARKETS: ?!?!" : "DESK ANCHOR"}
        </text>
      </svg>
    </AbsoluteFill>
  );
}
