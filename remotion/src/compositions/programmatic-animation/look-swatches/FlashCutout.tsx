import {AbsoluteFill, useCurrentFrame} from "remotion";
import {beatAt, stepFrame, type Mouth} from "./timing";

const INK = "#141414";
const LINE = 9;
const SKIN = "#ffd9a8";
const SUIT = "#d63b3b";

const mouthShape = (mouth: Mouth) => {
  switch (mouth) {
    case "closed":
      return <path d="M500 905 Q540 925 580 905" fill="none" />;
    case "open":
      return <ellipse cx={540} cy={912} rx={42} ry={22} fill="#7a1f1f" />;
    case "wide":
      return <path d="M488 895 Q540 975 592 895 Z" fill="#7a1f1f" />;
    case "o":
      return <ellipse cx={540} cy={930} rx={34} ry={52} fill="#7a1f1f" />;
  }
};

const Eyes = ({shocked, blink}: {shocked: boolean; blink: boolean}) => {
  if (blink) {
    return (
      <g fill="none">
        <path d="M455 830 h50" />
        <path d="M575 830 h50" />
      </g>
    );
  }
  const r = shocked ? 58 : 38;
  const pupil = shocked ? 9 : 15;
  return (
    <g>
      {[480, 600].map((cx) => (
        <g key={cx}>
          <circle cx={cx} cy={830} r={r} fill="#fff" />
          <circle cx={cx + 6} cy={834} r={pupil} fill={INK} stroke="none" />
        </g>
      ))}
      <path
        d={shocked ? "M430 745 l90 -20 M560 725 l90 20" : "M440 780 l80 5 M560 785 l80 -5"}
        fill="none"
        strokeWidth={LINE + 4}
      />
    </g>
  );
};

/**
 * flash-cutout: bold outlines, flat fills, separate puppet limbs, swappable
 * mouths. Animated on twos with line boil.
 */
export function FlashCutout() {
  const frame = stepFrame(useCurrentFrame(), 2);
  const beat = beatAt(frame);
  const boilSeed = (frame / 2) % 4;
  const armAngle = -150 * beat.armUp;

  return (
    <AbsoluteFill style={{backgroundColor: "#2f5aa8"}}>
      <svg viewBox="0 0 1080 1920" width="100%" height="100%">
        <defs>
          <filter id="flash-boil">
            <feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves={2} seed={boilSeed} />
            <feDisplacementMap in="SourceGraphic" scale={7} />
          </filter>
        </defs>
        <g filter="url(#flash-boil)" stroke={INK} strokeWidth={LINE} strokeLinejoin="round" strokeLinecap="round">
          {/* Backdrop monitor */}
          <rect x={120} y={420} width={840} height={260} rx={20} fill={beat.shocked ? "#ffe14d" : "#1d2f5c"} />
          <text x={540} y={590} textAnchor="middle" fontSize={130} fontWeight={900} fontFamily="Arial Black, sans-serif" fill={beat.shocked ? INK : "#ffe14d"} stroke="none">
            {beat.shocked ? "WHAT?!" : "NEWS"}
          </text>

          <g transform={`translate(${-beat.enter * 900} ${-beat.jump * 90})`}>
            {/* Torso */}
            <path d="M370 1320 L400 1030 Q540 970 680,1030 L710 1320 Z" fill={SUIT} />
            <path d="M505 1010 L540 1110 L575 1010 Z" fill="#fff" />
            {/* Arm: separate puppet limb pivoting at the shoulder */}
            <g transform={`rotate(${armAngle} 670 1050)`}>
              <rect x={640} y={1040} width={60} height={230} rx={30} fill={SUIT} />
              <circle cx={670} cy={1290} r={42} fill={SKIN} />
            </g>
            {/* Head */}
            <ellipse cx={540} cy={850} rx={175} ry={185} fill={SKIN} />
            <path d="M370 790 Q380 640 540 650 Q700 640 710 790 Q620 700 540 720 Q460 700 370 790 Z" fill="#4a2c17" />
            <Eyes shocked={beat.shocked} blink={beat.blink} />
            <g strokeWidth={LINE}>{mouthShape(beat.mouth)}</g>
          </g>

          {/* Desk in front of the puppet */}
          <path d="M60 1300 H1020 L980 1700 H100 Z" fill="#8a5a2b" />
          <rect x={60} y={1290} width={960} height={50} fill="#b07a3f" />
        </g>
      </svg>
    </AbsoluteFill>
  );
}
