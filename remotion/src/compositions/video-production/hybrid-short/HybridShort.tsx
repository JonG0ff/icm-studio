import {useMemo} from "react";
import {AbsoluteFill, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {CaptionLayer} from "./CaptionLayer";
import {SupportingVisual} from "./SupportingVisual";
import {mapSourceCaptions, validateEditMap, type HybridEditMap, type HybridSegment, type HybridSource} from "./edit-map";

export type HybridShortProps = {editMap: HybridEditMap};

const Segment = ({segment, source, outputFps}: {segment: HybridSegment; source: HybridSource; outputFps: number}) => {
  const framing = segment.framing ?? {xPercent: 50, yPercent: 50, scale: 1};
  return (
    <AbsoluteFill style={{overflow: "hidden"}}>
      <OffthreadVideo src={staticFile(source.path)}
        // Remotion trim units use the composition fps, never the source fps.
        trimBefore={(segment.sourceStartFrame / source.fps) * outputFps}
        trimAfter={(segment.sourceEndFrame / source.fps) * outputFps}
        playbackRate={1}
        style={{width: "100%", height: "100%", objectFit: "cover", objectPosition: `${framing.xPercent}% ${framing.yPercent}%`, transform: `scale(${framing.scale})`, transformOrigin: `${framing.xPercent}% ${framing.yPercent}%`}} />
      <AbsoluteFill style={{background: "linear-gradient(180deg, rgba(3,12,12,0.55) 0%, transparent 43%, rgba(3,12,12,0.6) 68%, #030c0c 100%)"}} />
      {segment.emphasis ? <div style={{position: "absolute", left: 72, right: 152, top: 365, color: "#fff", fontSize: 106, lineHeight: 0.97, fontWeight: 900, letterSpacing: -5, textShadow: "0 3px 24px rgba(0,0,0,0.5)"}}>{segment.emphasis}</div> : null}
      {segment.card ? <SupportingVisual card={segment.card} /> : null}
    </AbsoluteFill>
  );
};

export const HybridShort = ({editMap}: HybridShortProps) => {
  const frame = useCurrentFrame();
  const config = useVideoConfig();
  const captions = useMemo(() => {
    validateEditMap(editMap);
    return mapSourceCaptions(editMap);
  }, [editMap]);
  const {output} = editMap;
  if (output.fps !== config.fps || output.width !== config.width || output.height !== config.height || output.durationInFrames !== config.durationInFrames) {
    throw new Error("Hybrid edit map output must match registered composition metadata; register a matching definition before changing duration, fps, or dimensions.");
  }
  const isSynthetic = editMap.sources.some((source) => source.kind === "synthetic");
  return (
    <AbsoluteFill style={{background: "#030c0c", fontFamily: "Arial, Helvetica, sans-serif"}}>
      {editMap.segments.map((segment) => {
        const source = editMap.sources.find((item) => item.id === segment.sourceId)!;
        return <Sequence key={segment.id} from={segment.outputStartFrame} durationInFrames={segment.outputEndFrame - segment.outputStartFrame} premountFor={Math.ceil(output.fps)}>
          <Segment segment={segment} source={source} outputFps={output.fps} />
        </Sequence>;
      })}
      <div style={{position: "absolute", left: 72, right: 152, top: 268, borderTop: "2px solid #d7f3a9", paddingTop: 18, color: "#d7f3a9", fontSize: 22, fontWeight: 700, letterSpacing: 2.5}}>
        {isSynthetic ? "TECHNICAL PROTOTYPE / SYNTHETIC MEDIA" : "VIDEO PRODUCTION"}
      </div>
      <CaptionLayer captions={captions} timeMs={(frame / output.fps) * 1000} />
    </AbsoluteFill>
  );
};
