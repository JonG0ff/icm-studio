import {defineComposition} from "../../types";
import {SelectedFootage} from "./SelectedFootage";
import {calculateFootageMetadata, type SelectedFootageProps} from "./metadata";

// Registration placeholder only. Supply compiler-generated props through footage-edit.mjs.
const defaultProps: SelectedFootageProps = {
  editMap: {
    output: {fps: 30, width: 1080, height: 1920, durationInFrames: 1},
    sources: [{id: "source", path: "assets/selected-footage/source.mp4", fps: 30, durationInFrames: 1, kind: "recorded"}],
    segments: [{id: "selection", sourceId: "source", sourceStartFrame: 0, sourceEndFrame: 1, outputStartFrame: 0, outputEndFrame: 1}],
    captionTracks: [],
  },
  captions: {cues: []}, captionMode: "none", audioStreamIndex: 0, muted: true,
};

export const selectedFootageDefinition = defineComposition<SelectedFootageProps>({
  id: "video-production-selected-footage", component: SelectedFootage,
  ...defaultProps.editMap.output, defaultProps, calculateMetadata: calculateFootageMetadata,
});
