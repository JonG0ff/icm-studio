import {defineComposition} from "../../types";
import {HybridShort, type HybridShortProps} from "./HybridShort";
import {validateEditMap} from "./edit-map";
import editMap from "./fixture.json";

validateEditMap(editMap);

export const hybridShortPrototypeDefinition = defineComposition<HybridShortProps>({
  id: "video-production-hybrid-short-prototype",
  component: HybridShort,
  ...editMap.output,
  defaultProps: {editMap},
});
