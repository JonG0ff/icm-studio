import type {ComponentType} from "react";
import {AbsoluteFill, Series} from "remotion";
import {FlashCutout} from "./FlashCutout";
import {FlatVector} from "./FlatVector";
import {PaperCollage} from "./PaperCollage";
import {PixelArt} from "./PixelArt";
import {LOOK_DURATION} from "./timing";

type LookEntry = {slug: string; study: string; component: ComponentType};

export const LOOKS: readonly LookEntry[] = [
  {slug: "flash-cutout", study: "Eddsworld, Homestar Runner", component: FlashCutout},
  {slug: "pixel-art", study: "Chrono Trigger, Stardew Valley", component: PixelArt},
  {slug: "paper-collage", study: "Gilliam cutouts, early South Park", component: PaperCollage},
  {slug: "flat-vector", study: "Clean vector explainers", component: FlatVector},
];

const Label = ({index, slug, study}: {index: number; slug: string; study: string}) => (
  <div
    style={{
      position: "absolute",
      top: 1745,
      left: 60,
      padding: "18px 28px",
      backgroundColor: "#000",
      color: "#fff",
      fontFamily: "Menlo, monospace",
    }}
  >
    <div style={{fontSize: 48, fontWeight: 700}}>
      {String(index + 1).padStart(2, "0")} / {slug.toUpperCase()}
    </div>
    <div style={{fontSize: 28, opacity: 0.7, marginTop: 6}}>study: {study}</div>
  </div>
);

/** All four looks back to back, same beat, labeled. */
export function LookSwatchReel() {
  return (
    <AbsoluteFill style={{backgroundColor: "#000"}}>
      <Series>
        {LOOKS.map(({slug, study, component: Look}, i) => (
          <Series.Sequence key={slug} durationInFrames={LOOK_DURATION}>
            <Look />
            <Label index={i} slug={slug} study={study} />
          </Series.Sequence>
        ))}
      </Series>
    </AbsoluteFill>
  );
}
