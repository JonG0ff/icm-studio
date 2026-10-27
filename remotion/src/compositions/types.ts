import type {ComponentType} from "react";
import type {CalculateMetadataFunction} from "remotion";

export type CompositionDefinition = {
  id: string;
  component: ComponentType<Record<string, unknown>>;
  durationInFrames: number;
  fps: number;
  width: number;
  height: number;
  defaultProps: Record<string, unknown>;
  calculateMetadata?: CalculateMetadataFunction<Record<string, unknown>>;
};

export const defineComposition = <Props extends Record<string, unknown>>(
  definition: Omit<CompositionDefinition, "component" | "defaultProps" | "calculateMetadata"> & {
    component: ComponentType<Props>;
    defaultProps: Props;
    calculateMetadata?: CalculateMetadataFunction<Props>;
  },
): CompositionDefinition => definition as CompositionDefinition;
