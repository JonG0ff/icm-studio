import {createHash} from "node:crypto";
import {createReadStream} from "node:fs";
import {mkdir, readFile, realpath, writeFile} from "node:fs/promises";
import {spawn} from "node:child_process";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {loadTypeScript} from "./load-typescript.mjs";

export const runtimeRoot = fileURLToPath(new URL("../../", import.meta.url));
export const jsonBytes = (value) => JSON.stringify(value, null, 2) + "\n";
export const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
export async function hashFile(filename) {
  const hash = createHash("sha256");
  for await (const chunk of createReadStream(filename)) hash.update(chunk);
  return hash.digest("hex");
}
export async function readJson(filename, expectedHash) {
  const bytes = await readFile(filename);
  const hash = sha256(bytes);
  if (expectedHash && expectedHash !== hash) throw new Error(`SHA-256 mismatch: ${filename}`);
  return {value: JSON.parse(bytes), hash, filename: path.resolve(filename)};
}
export async function writeJson(filename, value) {
  await mkdir(path.dirname(filename), {recursive: true});
  await writeFile(filename, jsonBytes(value));
}
export function run(command, args, {binary = false, maxBytes = 256 * 1024 * 1024} = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {stdio: ["ignore", "pipe", "pipe"]});
    const chunks = [];
    let stderr = "", size = 0, overflow = false;
    child.stdout.on("data", (chunk) => {
      size += chunk.length;
      if (size > maxBytes) {overflow = true; child.kill();} else chunks.push(chunk);
    });
    child.stderr.on("data", (chunk) => {stderr = (stderr + chunk).slice(-12000);});
    child.on("error", reject);
    child.on("close", (code) => {
      if (overflow) return reject(new Error(`${command}: output exceeded ${maxBytes} bytes; select a shorter source/range.`));
      if (code !== 0) return reject(new Error(`${command} exited ${code}: ${stderr.trim()}`));
      const bytes = Buffer.concat(chunks);
      resolve(binary ? bytes : bytes.toString("utf8"));
    });
  });
}
export async function sourceFiles(sources, sourcesFile) {
  if (sources.schemaVersion !== 1 || sources.artifactType !== "sources" || sources.sources?.length !== 1) {
    throw new Error("One version-1 sources artifact is required.");
  }
  const source = sources.sources[0];
  const original = path.resolve(path.dirname(sourcesFile), source.localPath);
  const publicRoot = await realpath(path.join(runtimeRoot, "public"));
  if (typeof source.runtimePath !== "string" || source.runtimePath.includes("\\") || source.runtimePath.includes(":")
    || path.isAbsolute(source.runtimePath) || source.runtimePath.split("/").some((part) => ["", ".", ".."].includes(part))) {
    throw new Error("Source runtimePath must stay inside Remotion public.");
  }
  const runtime = await realpath(path.join(publicRoot, source.runtimePath));
  if (!runtime.startsWith(publicRoot + path.sep)) throw new Error("Runtime media symlink escapes Remotion public.");
  const hashes = await Promise.all([hashFile(original), hashFile(runtime)]);
  if (hashes.some((hash) => hash !== source.sha256)) throw new Error("Original/runtime media SHA-256 differs from sources.json; inspect again.");
  await readFile(path.resolve(path.dirname(sourcesFile), source.rightsRef));
  return {source, original, runtime};
}
export async function probeSource(source, original) {
  const probe = JSON.parse(await run("ffprobe", ["-v", "error", "-show_streams", "-show_format", "-of", "json", original]));
  const videos = probe.streams.filter((s) => s.codec_type === "video");
  const audio = probe.streams.filter((s) => s.codec_type === "audio");
  const video = videos.find((s) => s.index === source.video.streamIndex);
  if (!video || videos[0].index !== video.index || video.disposition?.attached_pic) throw new Error("First release renders the first non-cover video stream only; choose/normalize an explicit derivative first.");
  if (video.width !== source.video.width || video.height !== source.video.height
    || video.time_base !== source.video.timeBase) throw new Error("Video inventory disagrees with FFprobe; inspect again.");
  const rotation = Number(video.tags?.rotate ?? 0) || video.side_data_list?.some((d) => Number(d.rotation));
  if (rotation) throw new Error("Rotated video requires an explicit normalized derivative/time mapping before this release.");
  const selected = source.audio;
  if (!Array.isArray(selected) || selected.length > 1) throw new Error("Select at most one audio stream in the inventory.");
  const ordinal = selected.length ? audio.findIndex((s) => s.index === selected[0].streamIndex) : -1;
  if (selected.length && (ordinal < 0 || Number(audio[ordinal].sample_rate) !== selected[0].sampleRate || audio[ordinal].channels !== selected[0].channels)) {
    throw new Error("Selected audio stream disagrees with FFprobe; inspect again.");
  }
  // Verify actual decoded timestamps again: labels and average rates are insufficient CFR evidence.
  const frameData = JSON.parse(await run("ffprobe", ["-v", "error", "-select_streams", String(video.index), "-show_frames", "-show_entries", "frame=best_effort_timestamp_time,duration_time,pkt_duration_time", "-of", "json", original]));
  const fps = source.video.fpsNumerator / source.video.fpsDenominator;
  const timestamps = frameData.frames.map((f) => Number(f.best_effort_timestamp_time));
  const [tickNum, tickDen] = video.time_base.split("/").map(Number);
  const tick = tickNum / tickDen;
  const tolerance = Math.max(2e-6, tick * 0.51);
  const lastDuration = Number(frameData.frames.at(-1)?.duration_time ?? frameData.frames.at(-1)?.pkt_duration_time);
  if (source.video.frameRateMode !== "cfr" || timestamps.length !== source.video.durationInFrames
    || !Number.isFinite(fps) || fps <= 0 || !Number.isFinite(tick) || tick <= 0 || tick > 1 / fps
    || Math.abs(timestamps[0]) > 2e-6 || !Number.isFinite(lastDuration) || lastDuration <= 0
    || Math.abs(timestamps.at(-1) + lastDuration - timestamps.length / fps) > tolerance
    || Math.abs(source.durationSeconds - timestamps.length / fps) > 1e-8
    || timestamps.some((t, i) => !Number.isFinite(t) || Math.abs(t - i / fps) > tolerance || (i > 0 && t <= timestamps[i - 1]))) {
    throw new Error("Source frame timestamps do not prove the declared zero-origin CFR grid; normalize with an explicit time mapping.");
  }
  if (selected.length) {
    if (Math.abs(Number(audio[ordinal].start_time ?? 0)) > 2e-6) throw new Error("Nonzero audio origin requires an explicit time mapping.");
    const audioFrames = JSON.parse(await run("ffprobe", ["-v", "error", "-select_streams", String(selected[0].streamIndex), "-show_frames", "-show_entries", "frame=best_effort_timestamp_time,nb_samples", "-of", "json", original]));
    let cursor = 0;
    for (const frame of audioFrames.frames) {
      const start = Number(frame.best_effort_timestamp_time), samples = Number(frame.nb_samples);
      if (!Number.isFinite(start) || !Number.isSafeInteger(samples) || samples <= 0 || Math.abs(start - cursor) > Math.max(2e-6, 1.01 / selected[0].sampleRate)) throw new Error("Audio timestamp gaps/origins need an explicit normalization mapping.");
      cursor += samples / selected[0].sampleRate;
    }
    if (!cursor || cursor > source.durationSeconds + 0.05) throw new Error("Selected audio has unsupported duration or no samples.");
  }
  return {audioStreamIndex: Math.max(0, ordinal), muted: selected.length === 0};
}
export async function compileJob(decisionsFile) {
  const {parseDecisions, parseSources, parseTranscript} = loadTypeScript(path.join(runtimeRoot, "src/lib/video-production/contracts.ts"));
  const decisions = await readJson(decisionsFile);
  parseDecisions(decisions.value);
  const resolveRef = (ref) => path.resolve(path.dirname(decisions.filename), ref.path);
  const sources = await readJson(resolveRef(decisions.value.sourcesRef), decisions.value.sourcesRef.sha256);
  parseSources(sources.value);
  const transcripts = await Promise.all(decisions.value.transcriptRefs.map(async (ref) => {
    const transcript = await readJson(resolveRef(ref), ref.sha256);
    parseTranscript(transcript.value);
    if (transcript.value.analysis.rangeStartSeconds !== 0 || transcript.value.analysis.rangeEndSeconds !== sources.value.sources[0].durationSeconds) throw new Error("This adapter supports full-source analysis only; inspect/transcribe the source again.");
    const raw = await readJson(path.resolve(path.dirname(transcript.filename), transcript.value.rawResult.path), transcript.value.rawResult.sha256);
    if (!canonicalWordsMatchRaw(raw.value, transcript.value.words)) throw new Error("Canonical source words disagree with raw Whisper data; use explicit corrections.");
    return transcript;
  }));
  const media = await sourceFiles(sources.value, sources.filename);
  const audio = await probeSource(media.source, media.original);
  const {compileEdit} = loadTypeScript(path.join(runtimeRoot, "src/lib/video-production/compile-edit.ts"));
  const compiled = compileEdit({sources: sources.value, decisions: decisions.value, transcripts: transcripts.map((t) => t.value), inputHashes: {
    sourcesSha256: sources.hash, decisionsSha256: decisions.hash,
    transcriptSha256BySourceId: Object.fromEntries(transcripts.map((t) => [t.value.sourceId, t.hash])),
  }});
  return {...compiled, props: {editMap: compiled.map, captions: compiled.captions, captionMode: decisions.value.captions.mode, ...audio}, media, decisions, sources, transcripts};
}

/** Canonical words repeat raw recognition exactly, except that unusable raw timing stays null. */
export function canonicalWordsMatchRaw(raw, canonical) {
  const words = raw.segments.flatMap((segment, rawSegmentIndex) => segment.words.map((word, rawWordIndex) => ({word, rawSegmentIndex, rawWordIndex})));
  return words.length === canonical.length && words.every(({word, rawSegmentIndex, rawWordIndex}, i) => {
    const normalized = canonical[i];
    const timing = normalized.timingIssue === undefined
      ? normalized.startSeconds === word.start && normalized.endSeconds === word.end
      : normalized.startSeconds === null && normalized.endSeconds === null;
    return normalized.rawSegmentIndex === rawSegmentIndex && normalized.rawWordIndex === rawWordIndex
      && normalized.text === word.word && timing && normalized.confidence === (word.probability ?? null);
  });
}

export async function analysePcm({original, source, startSeconds = 0, endSeconds = source.durationSeconds, gapMs = 250}) {
  if (!Number.isFinite(startSeconds) || !Number.isFinite(endSeconds) || startSeconds < 0 || endSeconds <= startSeconds || endSeconds > source.durationSeconds) throw new Error("PCM range must be positive and inside source time.");
  if (!Number.isFinite(gapMs) || gapMs <= 0) throw new Error("PCM minimum gap must be finite positive milliseconds.");
  if (source.audio.length !== 1) throw new Error("PCM analysis requires one explicitly selected audio stream.");
  const bytes = await run("ffmpeg", ["-v", "error", "-i", original, "-ss", String(startSeconds), "-t", String(endSeconds - startSeconds), "-map", `0:${source.audio[0].streamIndex}`, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "pipe:1"], {binary: true});
  if (!bytes.length || bytes.length % 2) throw new Error("PCM decode returned empty or incomplete samples.");
  const pcm = new Int16Array(bytes.length / 2);
  for (let i = 0; i < pcm.length; i++) pcm[i] = bytes.readInt16LE(i * 2);
  const {analyse, envelopeOf} = loadTypeScript(path.join(runtimeRoot, "src/lib/upstream/open-edit/speech-probe.ts"));
  const result = analyse(envelopeOf(pcm, 160), 10, gapMs, startSeconds);
  const {envelope: _envelope, ...measurements} = result;
  return {artifactType: "energy-candidates", schemaVersion: 1, sourceId: source.id, sourceSha256: source.sha256,
    rangeStartSeconds: startSeconds, requestedEndSeconds: endSeconds,
    actualSampleDurationSeconds: pcm.length / 16000, measuredDurationSeconds: Math.floor(pcm.length / 160) / 100,
    sampleRate: 16000, sampleCount: pcm.length, warning: "Energy candidates require listening; they do not prove speech, silence, or a safe cut.", ...measurements};
}
