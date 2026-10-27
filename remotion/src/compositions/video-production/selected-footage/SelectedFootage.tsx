import {useMemo} from "react";
import {AbsoluteFill, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {FootageCaptions} from "./FootageCaptions";
import {footageMetadata, type SelectedFootageProps} from "./metadata";

/** Timing stays in the compiled map. Treatment adds only requested captions/emphasis. */
export const SelectedFootage = (props: SelectedFootageProps) => {
  const {editMap, captions, captionMode, audioStreamIndex, muted} = props;
  const output = useMemo(() => footageMetadata(props), [props]);
  const config = useVideoConfig();
  const frame = useCurrentFrame();
  if (output.fps !== config.fps || output.width !== config.width || output.height !== config.height || output.durationInFrames !== config.durationInFrames) {
    throw new Error("Resolve selected-footage metadata before rendering.");
  }
  const source = editMap.sources[0];
  const fontSize = Math.round(Math.min(output.width, output.height) * 0.055);
  return <AbsoluteFill style={{backgroundColor: "black", fontFamily: "Arial, Helvetica, sans-serif", fontSize}}>
    {editMap.segments.map((segment) => {
      const framing = segment.framing ?? {xPercent: 50, yPercent: 50, scale: 1};
      return <Sequence key={segment.id} from={segment.outputStartFrame} durationInFrames={segment.outputEndFrame - segment.outputStartFrame}>
        <AbsoluteFill style={{overflow: "hidden"}}>
          <OffthreadVideo src={staticFile(source.path)}
            trimBefore={segment.sourceStartFrame} trimAfter={segment.sourceEndFrame}
            playbackRate={1} audioStreamIndex={audioStreamIndex} muted={muted}
            style={{width: "100%", height: "100%", objectFit: "cover", objectPosition: `${framing.xPercent}% ${framing.yPercent}%`, transform: `scale(${framing.scale})`, transformOrigin: `${framing.xPercent}% ${framing.yPercent}%`}} />
          {segment.emphasis ? <div style={{position: "absolute", top: "9%", left: "7%", right: "7%", textAlign: "center", color: "white", fontWeight: 700, textShadow: "0 2px 8px #000", whiteSpace: "pre-wrap"}}>{segment.emphasis}</div> : null}
        </AbsoluteFill>
      </Sequence>;
    })}
    {captionMode === "burned-in" ? <FootageCaptions cues={captions.cues} timeSeconds={frame / output.fps} /> : null}
  </AbsoluteFill>;
};
