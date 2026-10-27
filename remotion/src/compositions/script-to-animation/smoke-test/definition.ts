import {defineComposition} from "../../types";
import {SmokeTest, type SmokeTestProps} from "./SmokeTest";

export const smokeTestDefinition = defineComposition<SmokeTestProps>({
  id: "script-to-animation-smoke-test",
  component: SmokeTest,
  durationInFrames: 90,
  fps: 30,
  width: 1920,
  height: 1080,
  defaultProps: {
    eyebrow: "Marlo Labs",
    title: "Remotion is ready.",
  },
});
