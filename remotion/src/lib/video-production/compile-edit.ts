import {createHash} from "node:crypto";
import {mapSourceCaptions, validateEditMap, type HybridEditMap} from "../../compositions/video-production/hybrid-short/edit-map";
import {snapToFrames} from "../upstream/open-edit/edl";
import {chunkWords, CHUNK_WORDS, CHUNK_MAX_WORDS, CHUNK_MIN_S, CHUNK_PAUSE_S} from "../upstream/video-use/chunk-words";
import {parseSources, parseDecisions, parseTranscript, parseInputHashes, requireCondition as check,
  type CaptionsArtifact, type CompilerInputHashes, type TranscriptArtifact,
  type TranscriptWord, type WordCorrection, type CaptionOutputWord} from "./contracts";

/** This serialization is also the byte contract used by captions.inputHashes.mapSha256. */
export const serializeEditMap = (map: HybridEditMap): string => JSON.stringify(map, null, 2) + "\n";

/** Deterministic byte hashing only. Compilation never reads or writes files. */
export const sha256Text = (text: string): string => createHash("sha256").update(text, "utf8").digest("hex");

type EffectiveWord = TranscriptWord & {raw: TranscriptWord; correction?: WordCorrection};
type TimedWord = EffectiveWord & {startSeconds: number; endSeconds: number};
const timed = (word: EffectiveWord): word is TimedWord => word.startSeconds !== null && word.endSeconds !== null;
const includesRange = (outer: readonly [number, number], start: number, end: number) => start >= outer[0] && end <= outer[1];
/** Smallest source range covering both raw and effective bounds; untimed raw recognition contributes none. */
const evidenceBounds = (raw: TranscriptWord, start: number, end: number): [number, number] =>
  raw.startSeconds === null || raw.endSeconds === null ? [start, end] : [Math.min(raw.startSeconds, start), Math.max(raw.endSeconds, end)];

function effectiveWords(transcript: TranscriptArtifact, duration: number): EffectiveWord[] {
  check(transcript.analysis.rangeEndSeconds <= duration, "analysis exceeds original source duration");
  const byId = new Map(transcript.words.map((word) => [word.id, word]));
  const corrections = new Map<string, WordCorrection>();
  for (const correction of transcript.corrections) {
    const raw = byId.get(correction.wordId);
    check(raw, `correction names unknown word ${correction.wordId}`);
    check(raw.text === correction.originalText, `${raw.id}: correction originalText differs from raw recognition`);
    check(raw.startSeconds !== null || (correction.startSeconds !== undefined && correction.endSeconds !== undefined),
      `${raw.id}: untimed recognition needs a listening correction with both startSeconds and endSeconds`);
    const start = correction.startSeconds ?? raw.startSeconds as number;
    const end = correction.endSeconds ?? raw.endSeconds as number;
    check(includesRange(correction.evidence.sourceRangeSeconds, ...evidenceBounds(raw, start, end)), `${raw.id}: correction evidence does not cover original and effective word`);
    check(correction.evidence.sourceRangeSeconds[1] <= duration, `${raw.id}: correction evidence exceeds source duration`);
    corrections.set(raw.id, correction);
  }
  let previousEnd = 0;
  const words = transcript.words.map((raw): EffectiveWord => {
    const correction = corrections.get(raw.id);
    if (!correction && raw.startSeconds === null) return {...raw, raw};
    const recognized: Record<string, unknown> = {...raw}; delete recognized.timingIssue;
    const word = {...(recognized as TranscriptWord), text: correction?.text ?? raw.text,
      startSeconds: (correction?.startSeconds ?? raw.startSeconds) as number,
      endSeconds: (correction?.endSeconds ?? raw.endSeconds) as number, raw,
      ...(correction ? {correction} : {})};
    check(word.startSeconds >= previousEnd && word.startSeconds >= transcript.analysis.rangeStartSeconds
      && word.endSeconds > word.startSeconds && word.endSeconds <= transcript.analysis.rangeEndSeconds && word.endSeconds <= duration,
    `${word.id}: effective word ranges must remain positive, ordered and inside source/analysis bounds`);
    previousEnd = word.endSeconds;
    return word;
  });
  const verification = transcript.verification;
  if (verification.status !== "automatic") {
    check(verification.sourceId === transcript.sourceId && verification.sourceSha256 === transcript.sourceSha256, "listening verification source identity/hash mismatch");
    for (const r of verification.sourceRangesSeconds) check(r[1] <= duration, "listening verification range exceeds original source");
    for (const id of verification.reviewedWordIds) check(byId.has(id), `listening verification names unknown word ${id}`);
  }
  return words;
}

function selectedWords(words: EffectiveWord[], ids: string[], start: number, end: number, context: string): TimedWord[] {
  // Without bounds, an untimed word can lie anywhere between its timed neighbors.
  words.forEach((word, i) => {
    if (timed(word)) return;
    const before = words.slice(0, i).filter(timed).pop(); const after = words.slice(i + 1).find(timed);
    const windowStart = before ? before.endSeconds : 0; const windowEnd = after ? after.startSeconds : Infinity;
    check(!(start < windowEnd && end > windowStart), `${context}: selection may contain untimed recognized word ${word.id}; record a listening correction with its bounds`);
  });
  const intersecting = words.filter(timed).filter((w) => w.endSeconds > start && w.startSeconds < end);
  check(ids.length === intersecting.length && ids.every((id, i) => id === intersecting[i].id), `${context}: wordIds must exactly match intersecting words in source order`);
  for (const w of intersecting) check(w.startSeconds >= start && w.endSeconds <= end, `${context}: partial-word cut at ${w.id}`);
  return intersecting;
}

const displayText = (words: readonly {text: string}[]): string => words.reduce((result, word, i) =>
  result + (i > 0 && !/\s$/.test(result) && !/^\s|^[.,!?;:]/.test(word.text) ? " " : "") + word.text, "");

/** Round only the final cue edges. Do not clip, merge, or silently repair collisions. */
export function captionsToSrt(cues: CaptionsArtifact["cues"]): string {
  let previousEnd = 0;
  const stamp = (ms: number): string => {
    const hours = Math.floor(ms / 3600000);
    return `${String(hours).padStart(2,"0")}:${String(Math.floor(ms / 60000) % 60).padStart(2,"0")}:${String(Math.floor(ms / 1000) % 60).padStart(2,"0")},${String(ms % 1000).padStart(3,"0")}`;
  };
  return cues.map((cue, i) => {
    check(Number.isFinite(cue.startSeconds) && Number.isFinite(cue.endSeconds) && cue.startSeconds >= 0 && cue.endSeconds > cue.startSeconds, `${cue.id}: invalid SRT cue range`);
    const start = Math.round(cue.startSeconds * 1000); const end = Math.round(cue.endSeconds * 1000);
    check(Number.isSafeInteger(start) && Number.isSafeInteger(end) && end > start, `${cue.id}: SRT range collapses after millisecond rounding`);
    check(start >= previousEnd, `${cue.id}: SRT collision after millisecond rounding`);
    check(cue.text.trim().length > 0 && !/[\r\n]/.test(cue.text) && !cue.text.includes(String.fromCharCode(0)), `${cue.id}: SRT text must be a single nonempty line`);
    previousEnd = end;
    return `${i + 1}\n${stamp(start)} --> ${stamp(end)}\n${cue.text}\n`;
  }).join("\n");
}

export type CompileEditInput = {sources: unknown; decisions: unknown; transcripts: readonly unknown[]; inputHashes: CompilerInputHashes};
export type CompiledEdit = {map: HybridEditMap; captions: CaptionsArtifact; srt: string};

/** Pure editorial compilation. Callers must first hash and validate referenced file bytes. */
export function compileEdit(input: CompileEditInput): CompiledEdit {
  check(input !== null && typeof input === "object" && !Array.isArray(input), "compiler input must be an object");
  check(Object.keys(input).every((k) => ["sources", "decisions", "transcripts", "inputHashes"].includes(k)), "unsupported compiler input field");
  const sources = parseSources(input.sources); const decisions = parseDecisions(input.decisions);
  const hashes = parseInputHashes(input.inputHashes);
  check(Array.isArray(input.transcripts), "transcripts must be an array");
  const transcripts = input.transcripts.map(parseTranscript);
  check(sources.jobId === decisions.jobId && transcripts.every((t) => t.jobId === sources.jobId), "mismatched artifact job IDs");
  check(decisions.sourcesRef.sha256 === hashes.sourcesSha256, "sources reference hash mismatch");
  check(sources.sources.length === 1, "v1 supports exactly one selected source; normalize other edits first");
  const source = sources.sources[0]; const video = source.video;
  check(source.kind === "recorded", "v1 selected-footage compiler requires recorded source media");
  check(video.frameRateMode === "cfr", "v1 requires CFR timing evidence; normalize VFR/unknown media first");
  check(source.audio.length <= 1, "v1 supports at most one audio stream; normalize an explicit selected audio track first");
  const fps = decisions.output.fpsNumerator / decisions.output.fpsDenominator;
  check(Number.isSafeInteger(video.fpsNumerator * decisions.output.fpsDenominator)
    && Number.isSafeInteger(decisions.output.fpsNumerator * video.fpsDenominator), "frame rate rational cross-products exceed safe integer precision");
  check(video.fpsNumerator * decisions.output.fpsDenominator === decisions.output.fpsNumerator * video.fpsDenominator, "source/output rates must match exactly; normalize mixed rates first");
  check(Number.isFinite(fps) && fps > 0, "invalid output frame rate");
  check(transcripts.length === decisions.transcriptRefs.length && transcripts.length === Object.keys(hashes.transcriptSha256BySourceId).length, "transcript references, loaded inputs and hashes must correspond exactly");
  check(new Set(transcripts.map((t) => t.sourceId)).size === transcripts.length, "duplicate transcript for source");
  for (const transcript of transcripts) {
    check(transcript.sourceId === source.id && transcript.sourceSha256 === source.sha256, "transcript source identity/hash mismatch");
    const ref = decisions.transcriptRefs.find((r) => r.sourceId === transcript.sourceId);
    check(ref && Object.prototype.hasOwnProperty.call(hashes.transcriptSha256BySourceId, transcript.sourceId)
      && ref.sha256 === hashes.transcriptSha256BySourceId[transcript.sourceId], "transcript reference hash mismatch");
    check(source.audio.some((a) => a.streamIndex === transcript.analysis.audioStreamIndex), "transcript analyzed an unavailable audio stream");
  }
  const noSpeech = decisions.noSpeech === true;
  check(noSpeech ? transcripts.length === 0 : transcripts.length === 1, noSpeech ? "explicit noSpeech requires no transcript inputs/references" : "speech edit requires a canonical source transcript or explicit noSpeech decision");
  const transcript = transcripts[0];
  const words = transcript ? effectiveWords(transcript, source.durationSeconds) : [];
  let cursor = 0;
  const identity: Array<{segmentId: string; word: TimedWord}> = [];
  const segments = decisions.segments.map((segment, i) => {
    check(segment.sourceId === source.id, `${segment.id}: unknown selected source`);
    check(segment.sourceEndSeconds <= source.durationSeconds, `${segment.id}: selection exceeds original source duration`);
    if (transcript) check(segment.sourceStartSeconds >= transcript.analysis.rangeStartSeconds && segment.sourceEndSeconds <= transcript.analysis.rangeEndSeconds, `${segment.id}: selection exceeds analyzed source range`);
    const original = selectedWords(words, segment.wordIds, segment.sourceStartSeconds, segment.sourceEndSeconds, `${segment.id} original bounds`);
    const snapped = snapToFrames({source: source.id, start: segment.sourceStartSeconds, end: segment.sourceEndSeconds}, fps, i);
    const selected = selectedWords(words, segment.wordIds, snapped.start, snapped.end, `${segment.id} snapped bounds`);
    check(original.length === selected.length, `${segment.id}: snapping changed selected speech`);
    for (const word of selected) {
      const verification = transcript.verification;
      check(verification.status !== "automatic" && verification.reviewedWordIds.includes(word.id)
        && verification.sourceRangesSeconds.some((r) => includesRange(r, ...evidenceBounds(word.raw, word.startSeconds, word.endSeconds))),
      `${segment.id}/${word.id}: selection lock requires explicit listening/context verification`);
      identity.push({segmentId: segment.id, word});
    }
    // The adopted snap helper can return -0 at the origin; canonical frame indexes use +0.
    const sourceStartFrame = Math.max(0, Math.round(snapped.start * fps)); const sourceEndFrame = Math.round(snapped.end * fps);
    check(sourceEndFrame <= video.durationInFrames, `${segment.id}: snapped selection exceeds video frames`);
    const outputStartFrame = cursor; cursor += sourceEndFrame - sourceStartFrame;
    return {id: segment.id, sourceId: source.id, sourceStartFrame, sourceEndFrame, outputStartFrame, outputEndFrame: cursor,
      ...(segment.framing ? {framing: {...segment.framing}} : {}), ...(segment.emphasis !== undefined ? {emphasis: segment.emphasis} : {})};
  });
  check(noSpeech || identity.length > 0, "an edit with no selected speech requires explicit noSpeech and no transcript");
  const map: HybridEditMap = {
    output: {fps, width: decisions.output.width, height: decisions.output.height, durationInFrames: cursor},
    sources: [{id: source.id, path: source.runtimePath, fps, durationInFrames: video.durationInFrames, kind: source.kind}],
    segments,
    // Unresolved untimed words cannot fall inside any selection; they are absent here, not given bounds.
    captionTracks: noSpeech ? [] : [{sourceId: source.id, provenance: "recorded-speech", captions: words.filter(timed).map((w) => ({
      text: w.text, startMs: w.startSeconds * 1000, endMs: w.endSeconds * 1000, timestampMs: null, confidence: w.confidence}))}],
  };
  validateEditMap(map);
  const mapped = mapSourceCaptions(map);
  check(mapped.length === identity.length, "mapped caption count differs from explicit word identity table");
  const bySegment = new Map<string, CaptionOutputWord[]>();
  mapped.forEach((caption, i) => {
    const {segmentId, word} = identity[i];
    check(caption.segmentId === segmentId && caption.sourceId === source.id, "mapper order differs from explicit segment/word identity table");
    const outputWord: CaptionOutputWord = {
      id: word.id, rawSegmentIndex: word.rawSegmentIndex, rawWordIndex: word.rawWordIndex,
      rawText: word.raw.text, text: word.text, sourceStartSeconds: word.startSeconds, sourceEndSeconds: word.endSeconds,
      outputStartSeconds: caption.startMs / 1000, outputEndSeconds: caption.endMs / 1000, confidence: caption.confidence,
      ...(word.correction ? {correction: word.correction} : {}),
    };
    const entries = bySegment.get(segmentId) ?? []; entries.push(outputWord); bySegment.set(segmentId, entries);
  });
  const cues: CaptionsArtifact["cues"] = [];
  for (const segment of segments) {
    const grouped = chunkWords((bySegment.get(segment.id) ?? []).map((word) => ({text: word.text, start: word.outputStartSeconds, end: word.outputEndSeconds, word})));
    grouped.forEach((group, i) => {
      const groupedWords = group.map((w) => w.word);
      cues.push({id: `${segment.id}:cue${String(i).padStart(6,"0")}`, segmentId: segment.id, sourceId: source.id,
        wordIds: groupedWords.map((w) => w.id), words: groupedWords, text: displayText(groupedWords),
        startSeconds: groupedWords[0].outputStartSeconds, endSeconds: groupedWords[groupedWords.length - 1].outputEndSeconds,
        provenance: "recorded-speech", verification: "verified"});
    });
  }
  const captions: CaptionsArtifact = {
    schemaVersion: 1, artifactType: "captions", jobId: sources.jobId,
    inputHashes: {...hashes, transcriptSha256BySourceId: {...hashes.transcriptSha256BySourceId}, mapSha256: sha256Text(serializeEditMap(map))},
    timeDomain: "output-seconds",
    grouping: {algorithm: "video-use/chunk_words", revision: "43cfc566833548093455c9d4a46bd69913b7e552",
      settings: {chunkWords: CHUNK_WORDS, chunkMaxWords: CHUNK_MAX_WORDS, chunkMinSeconds: CHUNK_MIN_S, chunkPauseSeconds: CHUNK_PAUSE_S, punctuation: ".,!?;:"}, casing: "preserve"},
    cues,
  };
  return {map, captions, srt: captionsToSrt(cues)};
}
