import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type SmokeTestProps = {
  eyebrow: string;
  title: string;
};

export const SmokeTest: React.FC<SmokeTestProps> = ({eyebrow, title}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const entrance = spring({frame, fps, config: {damping: 18, stiffness: 120}});
  const glow = interpolate(frame, [0, 45, 89], [0.15, 0.35, 0.15], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        background: "#07130f",
        color: "#f3f7f5",
        fontFamily: "Arial, Helvetica, sans-serif",
        justifyContent: "center",
        overflow: "hidden",
      }}
    >
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 50% 55%, #2bf59b 0%, transparent 48%)",
          opacity: glow,
          transform: `scale(${1 + frame / 900})`,
        }}
      />
      <div
        style={{
          alignItems: "center",
          display: "flex",
          flexDirection: "column",
          gap: 24,
          opacity: entrance,
          transform: `translateY(${(1 - entrance) * 48}px) scale(${0.96 + entrance * 0.04})`,
        }}
      >
        <div
          style={{
            color: "#62f5b5",
            fontSize: 28,
            fontWeight: 700,
            letterSpacing: 8,
            textTransform: "uppercase",
          }}
        >
          {eyebrow}
        </div>
        <div
          style={{
            fontSize: 92,
            fontWeight: 700,
            letterSpacing: -4,
            textAlign: "center",
          }}
        >
          {title}
        </div>
        <div
          style={{
            background: "#62f5b5",
            borderRadius: 999,
            height: 8,
            marginTop: 8,
            transform: `scaleX(${entrance})`,
            width: 280,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
