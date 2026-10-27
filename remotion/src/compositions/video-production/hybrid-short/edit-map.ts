import type {Caption} from "@remotion/captions";

export type HybridSource = {
  id: string;
  /** Relative to the shared runtime's public directory. */
  path: string;
  fps: number;
  durationInFrames: number;
  kind: "recorded" | "synthetic";
};

export type HybridSegment = {
  id: string;
  sourceId: string;
  /** Original source frames, with an exclusive end. */
  sourceStartFrame: number;
  sourceEndFrame: number;
  /** Composition frames, with an exclusive end. */
  outputStartFrame: number;
  outputEndFrame: number;
  framing?: {xPercent: number; yPercent: number; scale: number};
  /** Written overlay copy, separate from any recorded speech. */
  emphasis?: string;
  card?: {title: string; body: string; imagePath?: string};
};

export type CaptionProvenance = "recorded-speech" | "authored-synthetic-label";
export type SourceCaptionTrack = {
  sourceId: string;
  provenance: CaptionProvenance;
  /** Original source milliseconds. Text is preserved verbatim. */
  captions: Caption[];
};

export type HybridEditMap = {
  output: {fps: number; width: number; height: number; durationInFrames: number};
  sources: HybridSource[];
  segments: HybridSegment[];
  captionTracks: SourceCaptionTrack[];
};

export type MappedCaption = Caption & {
  sourceId: string;
  segmentId: string;
  provenance: CaptionProvenance;
};

const assert = (condition: boolean, message: string): void => {
  if (!condition) throw new Error(`Hybrid edit map: ${message}`);
};
const positive = (value: number): boolean => Number.isFinite(value) && value > 0;
const frameIndex = (value: number): boolean => Number.isSafeInteger(value) && value >= 0;
const text = (value: string): boolean => typeof value === "string" && value.trim().length > 0;
const localPath = (value: string): boolean =>
  text(value) && !value.startsWith("/") && !value.includes(":") && !value.includes("\\") &&
  !value.split("/").some((part) => part === ".." || part === "." || part === "");
const close = (a: number, b: number): boolean => Math.abs(a - b) < 1e-8;

const sourceFor = (map: HybridEditMap, id: string): HybridSource => {
  const source = map.sources.find((item) => item.id === id);
  if (!source) throw new Error(`Hybrid edit map: unknown source ${id}`);
  return source;
};

/** Check the full serializable plan before loading or rendering media. */
export const validateEditMap = (map: HybridEditMap): void => {
  const {output} = map;
  assert(positive(output.fps), "output fps must be positive");
  assert(frameIndex(output.width) && output.width > 0, "output width must be a positive integer");
  assert(frameIndex(output.height) && output.height > 0, "output height must be a positive integer");
  assert(frameIndex(output.durationInFrames) && output.durationInFrames > 0, "output duration must be a positive frame count");
  assert(map.sources.length > 0, "at least one source is required");
  assert(map.segments.length > 0, "at least one segment is required");
  const sourceIds = new Set<string>();
  for (const source of map.sources) {
    assert(text(source.id) && !sourceIds.has(source.id), "source IDs must be unique and nonempty");
    sourceIds.add(source.id);
    assert(localPath(source.path), `${source.id}: source path must stay inside public`);
    assert(positive(source.fps), `${source.id}: source fps must be positive`);
    assert(frameIndex(source.durationInFrames) && source.durationInFrames > 0, `${source.id}: invalid source duration`);
    assert(source.kind === "recorded" || source.kind === "synthetic", `${source.id}: invalid source kind`);
  }
  const segmentIds = new Set<string>();
  let cursor = 0;
  for (const segment of map.segments) {
    const source = sourceFor(map, segment.sourceId);
    assert(text(segment.id) && !segmentIds.has(segment.id), "segment IDs must be unique and nonempty");
    segmentIds.add(segment.id);
    assert(frameIndex(segment.sourceStartFrame) && frameIndex(segment.sourceEndFrame), `${segment.id}: source bounds must be frame indices`);
    assert(segment.sourceStartFrame < segment.sourceEndFrame && segment.sourceEndFrame <= source.durationInFrames, `${segment.id}: source range is outside the original media`);
    assert(frameIndex(segment.outputStartFrame) && frameIndex(segment.outputEndFrame), `${segment.id}: output bounds must be frame indices`);
    assert(segment.outputStartFrame === cursor && segment.outputEndFrame > cursor, `${segment.id}: output must be contiguous, ordered, and nonoverlapping`);
    const sourceSeconds = (segment.sourceEndFrame - segment.sourceStartFrame) / source.fps;
    const outputSeconds = (segment.outputEndFrame - segment.outputStartFrame) / output.fps;
    assert(close(sourceSeconds, outputSeconds), `${segment.id}: duration mismatch would change playback speed`);
    cursor = segment.outputEndFrame;
    if (segment.framing) {
      const {xPercent, yPercent, scale} = segment.framing;
      assert(Number.isFinite(xPercent) && xPercent >= 0 && xPercent <= 100, `${segment.id}: invalid horizontal framing`);
      assert(Number.isFinite(yPercent) && yPercent >= 0 && yPercent <= 100, `${segment.id}: invalid vertical framing`);
      assert(Number.isFinite(scale) && scale >= 1 && scale <= 3, `${segment.id}: framing scale must be between 1 and 3`);
    }
    if (segment.emphasis !== undefined) assert(text(segment.emphasis), `${segment.id}: emphasis must contain authored text`);
    if (segment.card) {
      assert(text(segment.card.title) && text(segment.card.body), `${segment.id}: card text must be nonempty`);
      if (segment.card.imagePath !== undefined) assert(localPath(segment.card.imagePath), `${segment.id}: image path must stay inside public`);
    }
  }
  assert(cursor === output.durationInFrames, "segments must fill the exact declared output duration");
  const trackSources = new Set<string>();
  for (const track of map.captionTracks) {
    const source = sourceFor(map, track.sourceId);
    assert(!trackSources.has(track.sourceId), `${track.sourceId}: only one caption track is supported per source`);
    trackSources.add(track.sourceId);
    assert(track.provenance === "recorded-speech" || track.provenance === "authored-synthetic-label", `${track.sourceId}: invalid caption provenance`);
    assert(source.kind !== "synthetic" || track.provenance === "authored-synthetic-label", `${track.sourceId}: synthetic labels cannot claim recorded speech`);
    assert(source.kind !== "recorded" || track.provenance === "recorded-speech", `${track.sourceId}: recorded media cannot claim synthetic caption provenance`);
    let previousEnd = 0;
    for (const caption of track.captions) {
      assert(text(caption.text), `${track.sourceId}: empty caption text`);
      assert(Number.isFinite(caption.startMs) && Number.isFinite(caption.endMs) && caption.startMs >= previousEnd && caption.endMs > caption.startMs, `${track.sourceId}: captions must have ordered, nonoverlapping, positive ranges`);
      assert(caption.endMs <= (source.durationInFrames / source.fps) * 1000, `${track.sourceId}: caption exceeds original media`);
      assert(caption.timestampMs === null || (Number.isFinite(caption.timestampMs) && caption.timestampMs >= caption.startMs && caption.timestampMs <= caption.endMs), `${track.sourceId}: caption timestamp is outside its range`);
      assert(caption.confidence === null || (Number.isFinite(caption.confidence) && caption.confidence >= 0 && caption.confidence <= 1), `${track.sourceId}: invalid caption confidence`);
      previousEnd = caption.endMs;
    }
  }
  mapSourceCaptionsUnchecked(map);
};

/** Return original media time; differing source fps never becomes a speed change. */
export const outputFrameToSource = (map: HybridEditMap, outputFrame: number) => {
  validateEditMap(map);
  assert(frameIndex(outputFrame) && outputFrame < map.output.durationInFrames, "output frame is outside the timeline");
  const segment = map.segments.find((item) => outputFrame >= item.outputStartFrame && outputFrame < item.outputEndFrame)!;
  const source = sourceFor(map, segment.sourceId);
  const sourceFrame = segment.sourceStartFrame + ((outputFrame - segment.outputStartFrame) / map.output.fps) * source.fps;
  return {sourceId: source.id, segmentId: segment.id, sourceFrame, sourceSeconds: sourceFrame / source.fps};
};

/** Return all output positions for a source frame, including repeated selections. */
export const sourceFrameToOutputFrames = (map: HybridEditMap, sourceId: string, sourceFrame: number): number[] => {
  validateEditMap(map);
  const source = sourceFor(map, sourceId);
  assert(frameIndex(sourceFrame) && sourceFrame < source.durationInFrames, "source frame is outside the original media");
  return map.segments.filter((segment) => segment.sourceId === sourceId && sourceFrame >= segment.sourceStartFrame && sourceFrame < segment.sourceEndFrame)
    .map((segment) => segment.outputStartFrame + ((sourceFrame - segment.sourceStartFrame) / source.fps) * map.output.fps);
};

const mapSourceCaptionsUnchecked = (map: HybridEditMap): MappedCaption[] => {
  const mapped: MappedCaption[] = [];
  for (const segment of map.segments) {
    const source = sourceFor(map, segment.sourceId);
    const track = map.captionTracks.find((item) => item.sourceId === source.id);
    if (!track) continue;
    const fromMs = (segment.sourceStartFrame / source.fps) * 1000;
    const toMs = (segment.sourceEndFrame / source.fps) * 1000;
    const offsetMs = (segment.outputStartFrame / map.output.fps) * 1000 - fromMs;
    for (const caption of track.captions) {
      if (caption.endMs <= fromMs || caption.startMs >= toMs) continue;
      assert(caption.startMs >= fromMs && caption.endMs <= toMs, `${segment.id}: caption crosses a cut; split and verify its words before editing`);
      mapped.push({...caption, startMs: caption.startMs + offsetMs, endMs: caption.endMs + offsetMs,
        timestampMs: caption.timestampMs === null ? null : caption.timestampMs + offsetMs,
        sourceId: source.id, segmentId: segment.id, provenance: track.provenance});
    }
  }
  return mapped;
};

export const mapSourceCaptions = (map: HybridEditMap): MappedCaption[] => {
  validateEditMap(map);
  return mapSourceCaptionsUnchecked(map);
};
