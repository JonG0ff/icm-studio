// Adapted from VEED open-edit at 1d3b75b7f46280061bae5ab4cb47b9538276d8fb.
// Apache-2.0; see LICENSE, NOTICE and upstream.json. Local validation added.

/** One kept interval of one source, in that source's own seconds. */
export interface EdlRange {
  source: string;
  start: number;
  end: number;
  /** Free text carried through for the agent's own reading; ignored here. */
  note?: string;
}

/** A range whose edges sit on its source's frame grid. */
export interface SnappedRange extends EdlRange {
  fps: number;
}

/**
 * Both edges moved UP to the next frame instant. ffmpeg's `trim` keeps the frames whose time is at or
 * after `start` and before `end`, so a range cut between frames keeps a whole number of frames that
 * `end - start` does not describe; audio cut to the raw edges then differs from the picture by up to
 * a frame per range, in either direction, and the drift grows with every join. On the grid, picture,
 * sound and the retimed transcript are all exactly (end - start) long.
 */
export function snapToFrames(range: EdlRange, fps: number, index = 0): SnappedRange {
  if (!Number.isFinite(fps) || fps <= 0 || !Number.isFinite(range.start)
    || !Number.isFinite(range.end) || range.start < 0 || range.end <= range.start
    || !Number.isFinite(range.start * fps) || !Number.isFinite(range.end * fps)) {
    throw new Error("fps must be finite and positive; range must have finite ordered nonnegative seconds");
  }
  const up = (t: number) => Math.ceil(t * fps - 1e-6) / fps;
  const snapped = { ...range, start: up(range.start), end: up(range.end), fps };
  if (!(snapped.end > snapped.start)) {
    throw new Error(`range ${index} of "${range.source}" (${range.start}-${range.end}) is shorter than one frame at ${fps} fps`);
  }
  return snapped;
}

