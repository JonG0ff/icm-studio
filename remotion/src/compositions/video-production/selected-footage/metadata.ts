import type {CalculateMetadataFunction} from "remotion";
import {validateEditMap, type HybridEditMap} from "../hybrid-short/edit-map";

/** Display cues are derived by compileEdit; source word records remain in captions.json. */
export type FootageCue = {id: string; segmentId: string; text: string; startSeconds: number; endSeconds: number};
export type SelectedFootageProps = {
  editMap: HybridEditMap;
  captions: {cues: FootageCue[]};
  captionMode: "burned-in" | "srt" | "fcp-subtitles" | "none";
  /** Zero-based audio ordinal, converted from the inventory's absolute stream index. */
  audioStreamIndex: number;
  muted: boolean;
};

export const footageMetadata = (props: SelectedFootageProps) => {
  validateEditMap(props.editMap);
  const {output, sources, segments} = props.editMap;
  if (sources.length !== 1 || sources[0].fps !== output.fps || segments.some((s) => s.card)) {
    throw new Error("Selected footage requires one same-rate source, normal cuts, and no cards.");
  }
  if (!["burned-in", "srt", "fcp-subtitles", "none"].includes(props.captionMode)
    || !Number.isSafeInteger(props.audioStreamIndex) || props.audioStreamIndex < 0 || typeof props.muted !== "boolean") {
    throw new Error("Invalid selected-footage caption/audio treatment.");
  }
  let previousEnd = 0;
  for (const cue of props.captions.cues) {
    const segment = segments.find((s) => s.id === cue.segmentId);
    if (!segment || typeof cue.text !== "string" || !cue.text.trim()
      || !Number.isFinite(cue.startSeconds) || !Number.isFinite(cue.endSeconds)
      || cue.startSeconds < previousEnd || cue.endSeconds <= cue.startSeconds
      || cue.startSeconds < segment.outputStartFrame / output.fps - 1e-8
      || cue.endSeconds > segment.outputEndFrame / output.fps + 1e-8) {
      throw new Error("Caption cues must have ordered positive output ranges within their selection.");
    }
    previousEnd = cue.endSeconds;
  }
  return {...output};
};

export const calculateFootageMetadata: CalculateMetadataFunction<SelectedFootageProps> = ({props}) => footageMetadata(props);
