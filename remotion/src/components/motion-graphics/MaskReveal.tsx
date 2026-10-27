import type { CSSProperties, ReactNode } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { MOTION, revealProgress } from "./motion";

/** Adapted from Onda's MaskReveal. See NOTICE.md and upstream.json. */
export const MaskReveal = ({
  children,
  delay = 0,
  duration = MOTION.enter,
  direction = "bottom",
  style,
}: {
  children: ReactNode;
  delay?: number;
  duration?: number;
  direction?: "left" | "right" | "top" | "bottom";
  style?: CSSProperties;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cover = (1 - revealProgress(frame, fps, delay, duration)) * 100;
  const insets = {
    left: `0 ${cover}% 0 0`,
    right: `0 0 0 ${cover}%`,
    top: `0 0 ${cover}% 0`,
    bottom: `${cover}% 0 0 0`,
  };
  const clipPath = `inset(${insets[direction]})`;
  return (
    <div
      data-motion-module="mask-reveal"
      style={{ ...style, clipPath, WebkitClipPath: clipPath }}
    >
      {children}
    </div>
  );
};
