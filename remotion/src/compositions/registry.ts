import {lookSwatchReelDefinition} from "./programmatic-animation/look-swatches/definition";
import {smokeTestDefinition} from "./script-to-animation/smoke-test/definition";
import type {CompositionDefinition} from "./types";
import {hybridShortPrototypeDefinition} from "./video-production/hybrid-short/definition";
import {selectedFootageDefinition} from "./video-production/selected-footage/definition";

/**
 * Add every runnable composition here. Composition IDs must use hyphens and
 * include the workspace and topic slug, for example:
 * `programmatic-animation-hurricane-reporter-v1`.
 */
export const compositionRegistry = [
  smokeTestDefinition,
  hybridShortPrototypeDefinition,
  lookSwatchReelDefinition,
  selectedFootageDefinition,
] satisfies CompositionDefinition[];
