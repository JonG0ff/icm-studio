import { useCurrentFrame, useVideoConfig } from "remotion";
import { revealProgress } from "./motion";

export type ProcessNode = { id: string; label: string; detail?: string };

/** Original Marlo Labs module. Layout is local to its SVG; timing is in seconds. */
export const ProcessDiagram = ({
  nodes,
  width = 860,
  height = 760,
  delay = 0,
  stepDuration = 1.3,
  initialNodeVisible = false,
  color = "#fff",
  background = "#101010",
  fontFamily = "sans-serif",
}: {
  nodes: readonly ProcessNode[];
  width?: number;
  height?: number;
  delay?: number;
  stepDuration?: number;
  initialNodeVisible?: boolean;
  color?: string;
  background?: string;
  fontFamily?: string;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (
    nodes.length < 2 ||
    nodes.length > 6 ||
    new Set(nodes.map((node) => node.id)).size !== nodes.length
  ) {
    throw new Error("ProcessDiagram needs two to six nodes with distinct IDs.");
  }
  const radius = Math.min(width * 0.095, (height / nodes.length) * 0.28);
  const x = width * 0.24;
  const gap = (height - radius * 2 - 16) / (nodes.length - 1);
  const yAt = (index: number) => radius + 8 + gap * index;
  return (
    <svg
      data-motion-module="process-diagram"
      role="img"
      aria-label={nodes.map((node) => node.label).join(" then ")}
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      style={{ overflow: "visible", fontFamily }}
    >
      {nodes.slice(1).map((node, index) => {
        const progress = revealProgress(
          frame,
          fps,
          delay + index * stepDuration + 0.4,
          0.8,
        );
        return (
          <line
            key={node.id}
            x1={x}
            y1={yAt(index) + radius}
            x2={x}
            y2={yAt(index + 1) - radius}
            stroke={color}
            strokeWidth={2}
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - progress}
            opacity={0.7}
          />
        );
      })}
      {nodes.map((node, index) => {
        const enter =
          index === 0 && initialNodeVisible
            ? 1
            : revealProgress(frame, fps, delay + index * stepDuration, 0.65);
        const active = revealProgress(
          frame,
          fps,
          delay + index * stepDuration + 0.2,
          0.6,
        );
        return (
          <g
            key={node.id}
            opacity={enter}
            transform={`translate(0 ${(1 - enter) * 18})`}
          >
            <circle
              cx={x}
              cy={yAt(index)}
              r={radius}
              fill={background}
              stroke={color}
              strokeWidth={2}
            />
            <circle cx={x} cy={yAt(index)} r={radius * active} fill={color} />
            <text
              x={x}
              y={yAt(index) + 10}
              fill={active > 0.6 ? background : color}
              textAnchor="middle"
              fontSize={30}
              fontWeight={500}
            >
              {String(index + 1).padStart(2, "0")}
            </text>
            <text
              x={x + radius + 54}
              y={yAt(index) - 6}
              fill={color}
              fontSize={62}
              fontWeight={600}
              letterSpacing={-2}
            >
              {node.label}
            </text>
            {node.detail ? (
              <text
                x={x + radius + 57}
                y={yAt(index) + 46}
                fill={color}
                opacity={0.62}
                fontSize={34}
              >
                {node.detail}
              </text>
            ) : null}
          </g>
        );
      })}
    </svg>
  );
};
