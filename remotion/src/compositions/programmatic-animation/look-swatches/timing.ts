import {Easing, interpolate, random} from "remotion";

/**
 * One shared beat for every look: the anchor slides in, talks, raises an
 * arm, then reacts in shock. Cues never change between looks, only the
 * render layer does.
 */
export const LOOK_DURATION = 120;
export const LOOK_FPS = 30;

const TALK_START = 20;
const TALK_END = 72;
const SHOCK_START = 76;

const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;

export type Mouth = "closed" | "open" | "wide" | "o";

export type Beat = {
  /** 1 = fully offscreen left, 0 = in place. */
  enter: number;
  /** 0 = arm down, 1 = arm raised. */
  armUp: number;
  shocked: boolean;
  /** 0 to 1 hop on the shock hit. */
  jump: number;
  mouth: Mouth;
  blink: boolean;
};

/** Hold each drawing for `step` frames ("animate on twos/threes"). */
export const stepFrame = (frame: number, step: number): number =>
  Math.floor(frame / step) * step;

/** Deterministic offset in [-amp, amp]. */
export const jitter = (seed: string, amp: number): number =>
  (random(seed) - 0.5) * 2 * amp;

const mouthAt = (frame: number): Mouth => {
  if (frame >= SHOCK_START) return "o";
  if (frame < TALK_START || frame >= TALK_END) return "closed";
  const roll = random(`mouth-${Math.floor(frame / 3)}`);
  if (roll < 0.3) return "closed";
  return roll < 0.75 ? "open" : "wide";
};

export const beatAt = (frame: number): Beat => ({
  enter: interpolate(frame, [0, 18], [1, 0], {
    ...clamp,
    easing: Easing.out(Easing.back(1.4)),
  }),
  armUp: interpolate(frame, [36, 44, 64, 72], [0, 1, 1, 0], clamp),
  shocked: frame >= SHOCK_START,
  jump: interpolate(
    frame,
    [SHOCK_START, SHOCK_START + 5, SHOCK_START + 12],
    [0, 1, 0],
    clamp,
  ),
  mouth: mouthAt(frame),
  blink: frame >= 28 && frame < 31,
});
