/**
 * Final audio for selected-footage renders. Remotion renders picture only; this
 * cuts the original audio from the same compiled frames, so sound and picture
 * share one edit. Remotion's own AAC step added ~42.7 ms of leading silence and
 * ran past the picture in the 2026-10-22 synthetic render check.
 */
import {run} from "./footage-io.mjs";

/** Sample-exact ranges for each compiled segment, in output order. */
export function audioSampleRanges(map, sampleRate) {
  if (!Number.isSafeInteger(sampleRate) || sampleRate <= 0) throw new Error("Audio mux needs a positive integer sample rate.");
  const fps = map.output.fps;
  if (!Number.isFinite(fps) || fps <= 0) throw new Error("Audio mux needs a positive output fps.");
  const toSample = (frame) => Math.round((frame * sampleRate) / fps);
  const ranges = map.segments.map((segment) => ({segmentId: segment.id,
    startSample: toSample(segment.sourceStartFrame), endSample: toSample(segment.sourceEndFrame)}));
  if (ranges.some((r) => r.endSample <= r.startSample)) throw new Error("A compiled segment has no audio samples.");
  return {ranges, totalSamples: toSample(map.output.durationInFrames)};
}

/** Decode one mono float track; the decoder applies the container's priming/edit list. */
export async function decodeMono(file, sampleRate, streamIndex = null) {
  const bytes = await run("ffmpeg", ["-v", "error", "-nostdin", "-i", file, "-map", streamIndex === null ? "0:a:0" : `0:${streamIndex}`, "-ac", "1", "-ar", String(sampleRate), "-f", "f32le", "pipe:1"], {binary: true});
  return new Float32Array(bytes.buffer, bytes.byteOffset, Math.floor(bytes.byteLength / 4));
}

async function streamFacts(file) {
  const facts = JSON.parse(await run("ffprobe", ["-v", "error", "-count_frames", "-show_entries", "stream=codec_type,start_time,time_base,duration_ts,nb_read_frames", "-of", "json", file]));
  return {video: facts.streams.filter((s) => s.codec_type === "video"), audio: facts.streams.filter((s) => s.codec_type === "audio")};
}

const AAC_FRAME = 1024;
const MAX_LAG_MS = 50;
const WINDOW_MS = 500;

/** Output delay in samples relative to the source range (positive = late), by normalized cross-correlation. */
export function measureDelay(output, outputStart, source, sourceStart, length, sampleRate) {
  const maxLag = Math.round(sampleRate * MAX_LAG_MS / 1000);
  const window = Math.min(Math.round(sampleRate * WINDOW_MS / 1000), length - 2 * maxLag);
  if (window <= 0) return null;
  const offset = Math.floor((length - window) / 2);
  let best = null, bestScore = -Infinity;
  for (let delay = -maxLag; delay <= maxLag; delay++) {
    let dot = 0, outEnergy = 0, srcEnergy = 0;
    for (let i = 0; i < window; i++) {
      const o = output[outputStart + offset + i], r = source[sourceStart + offset + i - delay] ?? 0;
      dot += o * r; outEnergy += o * o; srcEnergy += r * r;
    }
    if (outEnergy < 1e-6 || srcEnergy < 1e-6) return null;
    const score = dot / Math.sqrt(outEnergy * srcEnergy);
    if (score > bestScore) {bestScore = score; best = delay;}
  }
  return {delaySamples: best, correlation: bestScore};
}

/**
 * Mux picture with original audio cut at the compiled frame bounds.
 * audioStreamIndex is the absolute FFprobe index in the original file.
 */
export async function muxEditAudio({picture, original, audioStreamIndex, map, sampleRate, output, bitrate = "256k"}) {
  if (!Number.isSafeInteger(audioStreamIndex) || audioStreamIndex < 0) throw new Error("Audio mux needs an absolute audio stream index.");
  const {ranges, totalSamples} = audioSampleRanges(map, sampleRate);
  const trims = ranges.map((r, i) => `[1:${audioStreamIndex}]atrim=start_sample=${r.startSample}:end_sample=${r.endSample},asetpts=PTS-STARTPTS[a${i}]`);
  const joined = `${ranges.map((_, i) => `[a${i}]`).join("")}concat=n=${ranges.length}:v=0:a=1,atrim=end_sample=${totalSamples},apad=whole_len=${totalSamples}[aout]`;
  await run("ffmpeg", ["-v", "error", "-nostdin", "-i", picture, "-i", original, "-filter_complex", [...trims, joined].join(";"),
    "-map", "0:v:0", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", bitrate, "-ar", String(sampleRate),
    // The default 1000 movie timescale rounds edit lists to milliseconds; use the sample rate.
    "-movflags", "+faststart", "-movie_timescale", String(sampleRate), output]);
  const facts = await streamFacts(output);
  if (facts.video.length !== 1 || facts.audio.length !== 1) throw new Error("Muxed render must contain one video and one audio stream.");
  const [video] = facts.video; const [audio] = facts.audio;
  const [tbNum, tbDen] = audio.time_base.split("/").map(Number);
  const signaledSamples = Math.round(Number(audio.duration_ts) * tbNum * sampleRate / tbDen);
  const decoded = await decodeMono(output, sampleRate);
  const source = await decodeMono(original, sampleRate, audioStreamIndex);
  let cursor = 0;
  const alignment = ranges.map((r) => {
    const length = r.endSample - r.startSample;
    const measured = measureDelay(decoded, cursor, source, r.startSample, length, sampleRate);
    cursor += length;
    return {segmentId: r.segmentId, ...(measured ?? {delaySamples: null, correlation: null, note: "too short or silent to measure"})};
  });
  const evidence = {method: "remotion-muted-picture + ffmpeg sample-exact atrim/concat from compiled map; AAC encoded once",
    sampleRate, ranges, expectedSamples: totalSamples, signaledSamples, decodedSamples: decoded.length,
    videoFrames: Number(video.nb_read_frames), expectedVideoFrames: map.output.durationInFrames,
    videoStartTime: Number(video.start_time), audioStartTime: Number(audio.start_time), alignment};
  if (evidence.videoFrames !== map.output.durationInFrames) throw new Error(`Muxed picture has ${evidence.videoFrames} frames; expected ${map.output.durationInFrames}.`);
  if (signaledSamples !== totalSamples) throw new Error(`Muxed audio signals ${signaledSamples} samples; expected ${totalSamples}.`);
  // Raw decoding keeps the final partial AAC frame; the container's edit list trims it.
  if (decoded.length < totalSamples || decoded.length >= totalSamples + AAC_FRAME) throw new Error(`Muxed audio decodes to ${decoded.length} samples; expected ${totalSamples} plus under one AAC frame.`);
  if (Math.abs(evidence.videoStartTime) > 1e-6 || Math.abs(evidence.audioStartTime) > 1e-6) throw new Error("Muxed streams must both start at zero.");
  const tolerance = Math.round(sampleRate / 1000);
  const late = alignment.find((a) => a.delaySamples !== null && Math.abs(a.delaySamples) > tolerance);
  if (late) throw new Error(`${late.segmentId}: muxed audio is offset ${late.delaySamples} samples from its source range.`);
  return evidence;
}
