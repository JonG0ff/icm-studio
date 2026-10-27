// Adapted from VEED open-edit at 1d3b75b7f46280061bae5ab4cb47b9538276d8fb.
// Apache-2.0; see LICENSE, NOTICE and upstream.json. Local validation added.

export interface Gap {
  start: number;
  end: number;
  duration: number;
}

export interface ProbeResult {
  /** Measured noise floor in dBFS: the 10th percentile of the envelope. */
  floor: number;
  /** Loudest window in dBFS. */
  peak: number;
  /** Threshold used to separate speech from floor, in dBFS. */
  threshold: number;
  /** First window at or above threshold, in seconds FROM THE START OF THE FILE — an EDL in-point. */
  onset: number | null;
  /** End of the last window at or above threshold, also in file seconds. */
  decay: number | null;
  /** Sub-threshold stretches at least `--gap` milliseconds long, in file seconds — energy-based cut candidates requiring listening review. */
  gaps: Gap[];
  /** False when the signal has no dynamic range to separate speech from floor. `floor`, `peak` and
   *  `threshold` still hold real measurements; `onset`, `decay` and `gaps` do not. */
  speechFound: boolean;
  /** Per-window dBFS, so a caller can render or re-threshold without decoding again. Omitted from
   *  --json: a ten-minute clip is sixty thousand numbers, and the caller of --json is an agent whose
   *  context they would fill for nothing. */
  envelope: number[];
  windowMs: number;
  rangeStart: number;
}

/** dBFS of each fixed-length window of 16-bit mono PCM. */
export function envelopeOf(pcm: Int16Array, windowSamples: number): number[] {
  if (!Number.isSafeInteger(windowSamples) || windowSamples <= 0) {
    throw new Error("windowSamples must be a positive safe integer");
  }
  const out: number[] = [];
  for (let i = 0; i + windowSamples <= pcm.length; i += windowSamples) {
    let sum = 0;
    for (let j = i; j < i + windowSamples; j++) sum += pcm[j] * pcm[j];
    const rms = Math.sqrt(sum / windowSamples);
    out.push(rms > 0 ? 20 * Math.log10(rms / 32768) : -100);
  }
  return out;
}

export function percentile(values: number[], p: number): number {
  if (!Number.isFinite(p) || !values.every(Number.isFinite)) {
    throw new Error("percentile requires finite values and p");
  }
  if (values.length === 0) return -100;
  const sorted = [...values].sort((a, b) => a - b);
  const index = Math.min(sorted.length - 1, Math.max(0, Math.round((sorted.length - 1) * p)));
  return sorted[index];
}

// Below this the clip is one flat level — digital silence, room tone with nobody talking, or a decode
// that returned nothing. A threshold derived from it equals the floor, every window then counts as
// speech, and the probe reports unbroken voicing over a clip with no voice in it.
export const MIN_DYNAMIC_RANGE_DB = 6;

/**
 * Speech is separated from the floor by a margin above the MEASURED floor, so the same numbers work
 * on a street and in a booth. The margin is deliberately generous: a false gap costs a bad cut, a
 * missed gap only costs a cut opportunity.
 */
export function analyse(envelope: number[], windowMs: number, gapMs: number, rangeStart: number): ProbeResult {
  if (!Number.isFinite(windowMs) || windowMs <= 0 || !Number.isFinite(gapMs) || gapMs <= 0
    || !Number.isFinite(rangeStart) || rangeStart < 0) {
    throw new Error("windowMs and gapMs must be finite and positive; rangeStart must be finite and nonnegative");
  }
  const floor = percentile(envelope, 0.1);
  // reduce, not Math.max(...envelope): spreading one argument per window throws RangeError past about
  // 125k of them, which at a 10ms window is any clip over roughly twenty minutes.
  const peak = envelope.reduce((hi, v) => (v > hi ? v : hi), -100);
  const threshold = Math.min(floor + 12, floor + (peak - floor) * 0.35);
  if (envelope.length === 0 || peak - floor < MIN_DYNAMIC_RANGE_DB) {
    return { floor, peak, threshold, onset: null, decay: null, gaps: [], speechFound: false, envelope, windowMs, rangeStart };
  }
  const perSecond = 1000 / windowMs;
  const at = (index: number) => rangeStart + index / perSecond;

  const first = envelope.findIndex((v) => v >= threshold);
  // ES2018 runtime compatibility: equivalent to upstream findLastIndex.
  let last = envelope.length - 1;
  while (last >= 0 && envelope[last] < threshold) last--;
  const onset = first < 0 ? null : at(first);
  const decay = last < 0 ? null : at(last + 1);

  // ceil, not round: a reported gap is AT LEAST --gap long.
  const minWindows = Math.max(1, Math.ceil(gapMs / windowMs - 1e-9));
  const gaps: Gap[] = [];
  let runStart = -1;
  for (let i = 0; i <= envelope.length; i++) {
    const quiet = i < envelope.length && envelope[i] < threshold;
    if (quiet && runStart < 0) runStart = i;
    if (!quiet && runStart >= 0) {
      if (i - runStart >= minWindows) {
        gaps.push({ start: at(runStart), end: at(i), duration: (i - runStart) / perSecond });
      }
      runStart = -1;
    }
  }

  return { floor, peak, threshold, onset, decay, gaps, speechFound: true, envelope, windowMs, rangeStart };
}

