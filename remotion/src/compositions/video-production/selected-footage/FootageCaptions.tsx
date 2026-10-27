import type {FootageCue} from "./metadata";

export const FootageCaptions = ({cues, timeSeconds}: {cues: FootageCue[]; timeSeconds: number}) => {
  const cue = cues.find((c) => timeSeconds >= c.startSeconds && timeSeconds < c.endSeconds);
  if (!cue) return null;
  return <div style={{position: "absolute", bottom: "9%", left: "7%", right: "7%", textAlign: "center", color: "white", fontSize: "inherit", fontWeight: 700, lineHeight: 1.15, whiteSpace: "pre-wrap", textShadow: "0 2px 5px #000, 0 0 12px #000"}}>{cue.text}</div>;
};
