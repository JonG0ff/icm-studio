import {Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import type {HybridSegment} from "./edit-map";

export const SupportingVisual = ({card}: {card: NonNullable<HybridSegment["card"]>}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const entrance = interpolate(frame, [0, 0.3 * fps], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <div style={{position: "absolute", left: 72, right: 152, top: 970, padding: 32, background: "rgba(13, 24, 24, 0.94)", border: "1px solid rgba(255,255,255,0.22)", borderLeft: "5px solid #d7f3a9", opacity: entrance, transform: `translateY(${(1 - entrance) * 20}px)`, color: "#fff"}}>
      {card.imagePath ? <Img src={staticFile(card.imagePath)} style={{width: "100%", height: 120, objectFit: "cover", marginBottom: 18}} /> : null}
      <div style={{fontSize: 22, fontWeight: 700, letterSpacing: 2, color: "#d7f3a9", marginBottom: 14}}>{card.title}</div>
      <div style={{fontSize: 32, lineHeight: 1.25}}>{card.body}</div>
    </div>
  );
};
