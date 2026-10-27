import {defineComposition} from "../../types";
import {LOOKS, LookSwatchReel} from "./LookSwatchReel";
import {LOOK_DURATION, LOOK_FPS} from "./timing";

export const lookSwatchReelDefinition = defineComposition<Record<string, never>>({
  id: "programmatic-animation-look-swatches-v1",
  component: LookSwatchReel,
  durationInFrames: LOOK_DURATION * LOOKS.length,
  fps: LOOK_FPS,
  width: 1080,
  height: 1920,
  defaultProps: {},
});
