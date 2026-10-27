import type { CSSProperties } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { MOTION, revealProgress } from "./motion";

export type NormalizedPoint = { x: number; y: number };

/** Onda's label-then-line choreography, with explicit normalized anchors and no house theme. */
export const Callout = ({
  label,
  anchor,
  position,
  delay = 0,
  duration = MOTION.enter,
  color = "currentColor",
  fontSize = 30,
  style,
}: {
  label: string;
  anchor: NormalizedPoint;
  position: NormalizedPoint;
  delay?: number;
  duration?: number;
  color?: string;
  fontSize?: number;
  style?: CSSProperties;
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const enter = revealProgress(frame, fps, delay, duration);
  const line = revealProgress(frame, fps, delay + duration * 0.4, duration);
  const x = position.x * width;
  const y = position.y * height;
  const ax = anchor.x * width;
  const ay = anchor.y * height;
  const labelEdgeY = y + (ay >= y ? 1 : -1) * fontSize * 0.7;
  return (
    <div
      data-motion-module="callout"
      style={{ position: "absolute", inset: 0, pointerEvents: "none", color }}
    >
      <svg
        width={width}
        height={height}
        style={{ position: "absolute", inset: 0, overflow: "visible" }}
      >
        <path
          d={`M ${x} ${labelEdgeY} L ${x} ${ay} L ${ax} ${ay}`}
          fill="none"
          stroke={color}
          strokeWidth={2}
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - line}
        />
        <circle cx={ax} cy={ay} r={4} fill={color} opacity={line} />
      </svg>
      <div
        style={{
          position: "absolute",
          left: x,
          top: y,
          maxWidth: width * 0.36,
          transform: `translate(-50%, -50%) scale(${0.94 + enter * 0.06})`,
          opacity: enter,
          fontSize,
          lineHeight: 1.15,
          letterSpacing: "0.02em",
          ...style,
        }}
      >
        {label}
      </div>
    </div>
  );
};
