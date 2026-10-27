import type {MappedCaption} from "./edit-map";
import type {CSSProperties} from "react";

/** Phrase-level timing only; this layer does not invent word alignment. */
export const CaptionLayer = ({captions, timeMs, style}: {captions: MappedCaption[]; timeMs: number; style?: CSSProperties}) => {
  const caption = captions.find((item) => timeMs >= item.startMs && timeMs < item.endMs);
  if (!caption) return null;
  return (
    <div style={{position: "absolute", left: 80, right: 150, top: 1340, textAlign: "center", color: "#fff", fontSize: 56, lineHeight: 1.13, fontWeight: 800, whiteSpace: "pre-wrap", textShadow: "0 3px 12px #000, 0 1px 2px #000", ...style}}>
      {caption.text}
      {caption.provenance === "authored-synthetic-label" ? (
        <div style={{marginTop: 20, fontSize: 19, fontWeight: 500, letterSpacing: 2, color: "#c9d0ce"}}>AUTHORED LABEL / NO RECORDED SPEECH</div>
      ) : null}
    </div>
  );
};
