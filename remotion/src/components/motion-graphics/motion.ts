import { Easing, interpolate } from "remotion";

/** Shared seconds-based vocabulary, adapted from Onda's choreography separation. */
export const MOTION = {
  enter: 0.6,
  exit: 0.3,
  stagger: 0.1,
  settle: 1.2,
} as const;
export const settleEase = Easing.bezier(0.16, 1, 0.3, 1);

export const revealProgress = (
  frame: number,
  fps: number,
  delay = 0,
  duration: number = MOTION.enter,
): number => {
  if (
    ![frame, fps, delay, duration].every(Number.isFinite) ||
    fps <= 0 ||
    duration <= 0
  ) {
    throw new Error(
      "Motion timing requires finite values, positive fps, and a positive duration.",
    );
  }
  return interpolate(frame / fps, [delay, delay + duration], [0, 1], {
    easing: settleEase,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};
