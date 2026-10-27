/** Selected-footage v1. Filesystem, byte hashes and reference resolution belong to the CLI. */
export type ArtifactRef = {path: string; sha256: string};
export type SourcesArtifact = {
  schemaVersion: 1; artifactType: "sources"; jobId: string;
  sources: Array<{
    id: string; sha256: string; localPath: string; runtimePath: string;
    durationSeconds: number; kind: "recorded" | "synthetic";
    video: {streamIndex: number; width: number; height: number; fpsNumerator: number;
      fpsDenominator: number; timeBase: string; durationInFrames: number;
      frameRateMode: "cfr" | "vfr" | "unknown"; timingEvidence: string};
    audio: Array<{streamIndex: number; sampleRate: number; channels: number}>;
    rightsRef: string;
  }>;
};
export type EditDecisionsArtifact = {
  schemaVersion: 1; artifactType: "edit-decisions"; jobId: string;
  sourcesRef: ArtifactRef; transcriptRefs: Array<ArtifactRef & {sourceId: string}>;
  output: {fpsNumerator: number; fpsDenominator: number; width: number; height: number};
  captions: {mode: "burned-in" | "srt" | "fcp-subtitles" | "none"; casing: "preserve"};
  /** Explicit no-speech branch; never inferred from missing recognition. */
  noSpeech?: boolean;
  segments: Array<{id: string; sourceId: string; sourceStartSeconds: number;
    sourceEndSeconds: number; wordIds: string[];
    framing?: {xPercent: number; yPercent: number; scale: number}; emphasis?: string}>;
};
export type TimedTranscriptWord = {
  id: string; rawSegmentIndex: number; rawWordIndex: number; text: string;
  startSeconds: number; endSeconds: number; confidence: number | null; speaker?: string;
};
/** Recognized text whose raw timing is unusable. Bounds come only from a listening correction. */
export type UntimedTranscriptWord = Omit<TimedTranscriptWord, "startSeconds" | "endSeconds"> & {
  startSeconds: null; endSeconds: null; timingIssue: "zero-length" | "overlap" | "out-of-source";
};
export type TranscriptWord = TimedTranscriptWord | UntimedTranscriptWord;
export type ReviewEvidence = {
  reviewer: string; reviewedAt: string; sourceRangeSeconds: [number, number];
};
export type WordCorrection = {
  wordId: string; originalText: string; text?: string; startSeconds?: number;
  endSeconds?: number; reason: string; evidence: ReviewEvidence;
};
export type TranscriptVerification = {status: "automatic"} | {
  status: "partial" | "verified"; reviewer: string; reviewedAt: string;
  sourceId: string; sourceSha256: string; sourceRangesSeconds: [number, number][];
  listeningObservations: string; reviewedWordIds: string[];
};
export type TranscriptArtifact = {
  schemaVersion: 1; artifactType: "transcript"; jobId: string;
  sourceId: string; sourceSha256: string;
  analysis: {engine: string; engineVersion: string; model: string; language: string;
    settings: Record<string, unknown>; audioStreamIndex: number;
    rangeStartSeconds: number; rangeEndSeconds: number; cacheKey: string;
    modelWeightSha256?: string};
  rawResult: ArtifactRef; verification: TranscriptVerification;
  words: TranscriptWord[]; corrections: WordCorrection[];
};
export type CompilerInputHashes = {
  sourcesSha256: string; decisionsSha256: string;
  transcriptSha256BySourceId: Record<string, string>;
};
export type CaptionOutputWord = {
  id: string; rawSegmentIndex: number; rawWordIndex: number;
  /** Verbatim recognition survives even when a reviewed correction is applied. */
  rawText: string; text: string; sourceStartSeconds: number; sourceEndSeconds: number;
  outputStartSeconds: number; outputEndSeconds: number; confidence: number | null;
  correction?: WordCorrection;
};
export type CaptionsArtifact = {
  schemaVersion: 1; artifactType: "captions"; jobId: string;
  inputHashes: CompilerInputHashes & {mapSha256: string};
  timeDomain: "output-seconds";
  grouping: {algorithm: "video-use/chunk_words"; revision: string;
    settings: {chunkWords: number; chunkMaxWords: number; chunkMinSeconds: number;
      chunkPauseSeconds: number; punctuation: string}; casing: "preserve"};
  cues: Array<{id: string; segmentId: string; sourceId: string; wordIds: string[];
    words: CaptionOutputWord[]; text: string; startSeconds: number; endSeconds: number;
    provenance: "recorded-speech"; verification: "verified"}>;
};

export function requireCondition(value: unknown, message: string): asserts value {
  if (!value) throw new Error(`Selected-footage compiler: ${message}`);
}
type Obj = Record<string, unknown>;
const object = (value: unknown, name: string, required: string[], optional: string[] = []): Obj => {
  requireCondition(value !== null && typeof value === "object" && !Array.isArray(value), `${name} must be an object`);
  const obj = value as Obj;
  for (const key of required) requireCondition(Object.prototype.hasOwnProperty.call(obj, key), `${name}.${key} is required`);
  for (const key of Object.keys(obj)) requireCondition(required.includes(key) || optional.includes(key), `${name}.${key} is unsupported`);
  return obj;
};
export const nonempty = (value: unknown, name: string): void => {
  requireCondition(typeof value === "string" && value.trim().length > 0, `${name} must be nonempty text`);
};
export const hash = (value: unknown, name: string): void => {
  requireCondition(typeof value === "string" && /^[0-9a-f]{64}$/.test(value), `${name} must be a lowercase SHA-256`);
};
const number = (value: unknown, name: string, positive = false): void => {
  requireCondition(typeof value === "number" && Number.isFinite(value) && (positive ? value > 0 : value >= 0), `${name} must be finite and ${positive ? "positive" : "nonnegative"}`);
};
const integer = (value: unknown, name: string, positive = false): void => {
  number(value, name, positive);
  requireCondition(Number.isSafeInteger(value), `${name} must be a safe integer`);
};
const array = (value: unknown, name: string): unknown[] => {
  requireCondition(Array.isArray(value), `${name} must be an array`);
  return value;
};
const strings = (value: unknown, name: string): void => {
  const entries = array(value, name);
  entries.forEach((entry, i) => nonempty(entry, `${name}[${i}]`));
  requireCondition(new Set(entries).size === entries.length, `${name} contains duplicate IDs`);
};
const range = (start: unknown, end: unknown, name: string): void => {
  number(start, `${name}.start`); number(end, `${name}.end`, true);
  requireCondition((end as number) > (start as number), `${name} must have end greater than start`);
};
const tupleRange = (value: unknown, name: string): void => {
  const pair = array(value, name);
  requireCondition(pair.length === 2, `${name} must be [startSeconds, endSeconds]`);
  range(pair[0], pair[1], name);
};
const date = (value: unknown, name: string): void => {
  nonempty(value, name);
  requireCondition(/^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$/.test(value as string) && Number.isFinite(Date.parse(value as string)), `${name} must be an ISO datetime with timezone`);
};
const ref = (value: unknown, name: string, sourceId = false): void => {
  const obj = object(value, name, sourceId ? ["path", "sha256", "sourceId"] : ["path", "sha256"]);
  nonempty(obj.path, `${name}.path`); hash(obj.sha256, `${name}.sha256`);
  if (sourceId) nonempty(obj.sourceId, `${name}.sourceId`);
};
const header = (obj: Obj, type: string): void => {
  requireCondition(obj.schemaVersion === 1, `${type}: unsupported schemaVersion`);
  requireCondition(obj.artifactType === type, `expected artifactType ${type}`);
  nonempty(obj.jobId, `${type}.jobId`);
};

export function parseSources(value: unknown): SourcesArtifact {
  const root = object(value, "sources", ["schemaVersion", "artifactType", "jobId", "sources"]);
  header(root, "sources");
  const entries = array(root.sources, "sources.sources");
  requireCondition(entries.length > 0, "sources.sources must not be empty");
  const ids = new Set<unknown>();
  entries.forEach((entry, i) => {
    const name = `sources.sources[${i}]`;
    const s = object(entry, name, ["id", "sha256", "localPath", "runtimePath", "durationSeconds", "kind", "video", "audio", "rightsRef"]);
    ["id", "localPath", "runtimePath", "rightsRef"].forEach((k) => nonempty(s[k], `${name}.${k}`));
    requireCondition(!ids.has(s.id), "duplicate source ID"); ids.add(s.id);
    hash(s.sha256, `${name}.sha256`); number(s.durationSeconds, `${name}.durationSeconds`, true);
    requireCondition(s.kind === "recorded" || s.kind === "synthetic", `${name}.kind is unsupported`);
    const v = object(s.video, `${name}.video`, ["streamIndex", "width", "height", "fpsNumerator", "fpsDenominator", "timeBase", "durationInFrames", "frameRateMode", "timingEvidence"]);
    integer(v.streamIndex, `${name}.video.streamIndex`);
    ["width", "height", "fpsNumerator", "fpsDenominator", "durationInFrames"].forEach((k) => integer(v[k], `${name}.video.${k}`, true));
    requireCondition(typeof v.timeBase === "string" && /^[1-9]\d*\/[1-9]\d*$/.test(v.timeBase), `${name}.video.timeBase must be a positive rational`);
    nonempty(v.timingEvidence, `${name}.video.timingEvidence`);
    requireCondition(["cfr", "vfr", "unknown"].includes(v.frameRateMode as string), `${name}.video.frameRateMode is invalid`);
    const streamIds = new Set<unknown>([v.streamIndex]);
    array(s.audio, `${name}.audio`).forEach((entry, j) => {
      const a = object(entry, `${name}.audio[${j}]`, ["streamIndex", "sampleRate", "channels"]);
      integer(a.streamIndex, `${name}.audio.streamIndex`);
      ["sampleRate", "channels"].forEach((k) => integer(a[k], `${name}.audio.${k}`, true));
      requireCondition(!streamIds.has(a.streamIndex), `${name}: duplicate stream index`); streamIds.add(a.streamIndex);
    });
  });
  return value as SourcesArtifact;
}

export function parseDecisions(value: unknown): EditDecisionsArtifact {
  const root = object(value, "decisions", ["schemaVersion", "artifactType", "jobId", "sourcesRef", "transcriptRefs", "output", "captions", "segments"], ["noSpeech"]);
  header(root, "edit-decisions"); ref(root.sourcesRef, "decisions.sourcesRef");
  const refs = array(root.transcriptRefs, "decisions.transcriptRefs");
  refs.forEach((r, i) => ref(r, `decisions.transcriptRefs[${i}]`, true));
  requireCondition(new Set(refs.map((r) => (r as Obj).sourceId)).size === refs.length, "duplicate transcript source reference");
  const o = object(root.output, "decisions.output", ["fpsNumerator", "fpsDenominator", "width", "height"]);
  Object.keys(o).forEach((k) => integer(o[k], `decisions.output.${k}`, true));
  const c = object(root.captions, "decisions.captions", ["mode", "casing"]);
  requireCondition(["burned-in", "srt", "fcp-subtitles", "none"].includes(c.mode as string), "unsupported caption mode");
  requireCondition(c.casing === "preserve", "caption casing must preserve recognized text");
  if (root.noSpeech !== undefined) requireCondition(typeof root.noSpeech === "boolean", "decisions.noSpeech must be boolean");
  const segments = array(root.segments, "decisions.segments");
  requireCondition(segments.length > 0, "at least one editorial segment is required");
  const ids = new Set<unknown>();
  segments.forEach((entry, i) => {
    const name = `decisions.segments[${i}]`;
    const s = object(entry, name, ["id", "sourceId", "sourceStartSeconds", "sourceEndSeconds", "wordIds"], ["framing", "emphasis"]);
    nonempty(s.id, `${name}.id`); nonempty(s.sourceId, `${name}.sourceId`);
    requireCondition(!ids.has(s.id), "segment IDs must be unique"); ids.add(s.id);
    range(s.sourceStartSeconds, s.sourceEndSeconds, name); strings(s.wordIds, `${name}.wordIds`);
    if (s.emphasis !== undefined) nonempty(s.emphasis, `${name}.emphasis`);
    if (s.framing !== undefined) {
      const f = object(s.framing, `${name}.framing`, ["xPercent", "yPercent", "scale"]);
      ["xPercent", "yPercent", "scale"].forEach((k) => number(f[k], `${name}.framing.${k}`));
      requireCondition((f.xPercent as number) <= 100 && (f.yPercent as number) <= 100 && (f.scale as number) >= 1 && (f.scale as number) <= 3, `${name}: framing exceeds supported limits`);
    }
  });
  return value as EditDecisionsArtifact;
}

export function parseTranscript(value: unknown): TranscriptArtifact {
  const root = object(value, "transcript", ["schemaVersion", "artifactType", "jobId", "sourceId", "sourceSha256", "analysis", "rawResult", "verification", "words", "corrections"]);
  header(root, "transcript"); nonempty(root.sourceId, "transcript.sourceId"); hash(root.sourceSha256, "transcript.sourceSha256");
  const a = object(root.analysis, "transcript.analysis", ["engine", "engineVersion", "model", "language", "settings", "audioStreamIndex", "rangeStartSeconds", "rangeEndSeconds", "cacheKey"], ["modelWeightSha256"]);
  ["engine", "engineVersion", "model", "language"].forEach((k) => nonempty(a[k], `transcript.analysis.${k}`));
  requireCondition(a.settings !== null && typeof a.settings === "object" && !Array.isArray(a.settings), "transcript.analysis.settings must be an object");
  integer(a.audioStreamIndex, "transcript.analysis.audioStreamIndex"); range(a.rangeStartSeconds, a.rangeEndSeconds, "transcript.analysis"); hash(a.cacheKey, "transcript.analysis.cacheKey");
  if (a.modelWeightSha256 !== undefined) hash(a.modelWeightSha256, "transcript.analysis.modelWeightSha256");
  ref(root.rawResult, "transcript.rawResult");
  const verification = root.verification as Obj | null;
  const automatic = verification !== null && typeof verification === "object" && verification.status === "automatic";
  const v = object(root.verification, "transcript.verification", automatic ? ["status"] : ["status", "reviewer", "reviewedAt", "sourceId", "sourceSha256", "sourceRangesSeconds", "listeningObservations", "reviewedWordIds"]);
  if (!automatic) {
    requireCondition(v.status === "partial" || v.status === "verified", "invalid transcript verification status");
    ["reviewer", "sourceId", "listeningObservations"].forEach((k) => nonempty(v[k], `transcript.verification.${k}`));
    date(v.reviewedAt, "transcript.verification.reviewedAt"); hash(v.sourceSha256, "transcript.verification.sourceSha256");
    const ranges = array(v.sourceRangesSeconds, "transcript.verification.sourceRangesSeconds");
    requireCondition(ranges.length > 0, "verification needs reviewed source ranges");
    ranges.forEach((r) => tupleRange(r, "transcript.verification.sourceRangesSeconds"));
    strings(v.reviewedWordIds, "transcript.verification.reviewedWordIds");
  }
  let previousEnd = 0;
  let previousSegment = -1;
  let previousWord = -1;
  array(root.words, "transcript.words").forEach((entry, i) => {
    const name = `transcript.words[${i}]`;
    const w = object(entry, name, ["id", "rawSegmentIndex", "rawWordIndex", "text", "startSeconds", "endSeconds", "confidence"], ["speaker", "timingIssue"]);
    requireCondition(w.id === `${root.sourceId}:w${String(i).padStart(6, "0")}`, `${name}: ID must retain raw traversal ordinal`);
    integer(w.rawSegmentIndex, `${name}.rawSegmentIndex`); integer(w.rawWordIndex, `${name}.rawWordIndex`);
    requireCondition((w.rawSegmentIndex as number) > previousSegment || (w.rawSegmentIndex === previousSegment && (w.rawWordIndex as number) > previousWord), `${name}: raw indexes must follow traversal order`);
    previousSegment = w.rawSegmentIndex as number; previousWord = w.rawWordIndex as number;
    nonempty(w.text, `${name}.text`);
    if (w.timingIssue !== undefined) {
      requireCondition(["zero-length", "overlap", "out-of-source"].includes(w.timingIssue as string), `${name}: unknown timingIssue`);
      requireCondition(w.startSeconds === null && w.endSeconds === null, `${name}: untimed word must keep null timestamps; never invent bounds`);
    } else {
      range(w.startSeconds, w.endSeconds, name);
      requireCondition((w.startSeconds as number) >= previousEnd && (w.startSeconds as number) >= (a.rangeStartSeconds as number) && (w.endSeconds as number) <= (a.rangeEndSeconds as number), `${name}: timestamps must be ordered and inside analysis bounds`);
      previousEnd = w.endSeconds as number;
    }
    if (w.confidence !== null) {number(w.confidence, `${name}.confidence`); requireCondition((w.confidence as number) <= 1, `${name}: confidence exceeds 1`);}
    if (w.speaker !== undefined) nonempty(w.speaker, `${name}.speaker`);
  });
  const corrected = new Set<unknown>();
  array(root.corrections, "transcript.corrections").forEach((entry, i) => {
    const name = `transcript.corrections[${i}]`;
    const c = object(entry, name, ["wordId", "originalText", "reason", "evidence"], ["text", "startSeconds", "endSeconds"]);
    ["wordId", "originalText", "reason"].forEach((k) => nonempty(c[k], `${name}.${k}`));
    requireCondition(!corrected.has(c.wordId), "duplicate word correction"); corrected.add(c.wordId);
    requireCondition(c.text !== undefined || c.startSeconds !== undefined || c.endSeconds !== undefined, `${name}: correction must change an explicit field`);
    if (c.text !== undefined) nonempty(c.text, `${name}.text`);
    if (c.startSeconds !== undefined) number(c.startSeconds, `${name}.startSeconds`);
    if (c.endSeconds !== undefined) number(c.endSeconds, `${name}.endSeconds`, true);
    const e = object(c.evidence, `${name}.evidence`, ["reviewer", "reviewedAt", "sourceRangeSeconds"]);
    nonempty(e.reviewer, `${name}.evidence.reviewer`); date(e.reviewedAt, `${name}.evidence.reviewedAt`); tupleRange(e.sourceRangeSeconds, `${name}.evidence.sourceRangeSeconds`);
  });
  return value as TranscriptArtifact;
}

export function parseInputHashes(value: unknown): CompilerInputHashes {
  const obj = object(value, "inputHashes", ["sourcesSha256", "decisionsSha256", "transcriptSha256BySourceId"]);
  hash(obj.sourcesSha256, "inputHashes.sourcesSha256"); hash(obj.decisionsSha256, "inputHashes.decisionsSha256");
  requireCondition(obj.transcriptSha256BySourceId !== null && typeof obj.transcriptSha256BySourceId === "object" && !Array.isArray(obj.transcriptSha256BySourceId), "inputHashes.transcriptSha256BySourceId must be an object");
  Object.entries(obj.transcriptSha256BySourceId as Obj).forEach(([id, digest]) => {nonempty(id, "inputHashes transcript source ID"); hash(digest, `inputHashes transcript ${id}`);});
  return value as CompilerInputHashes;
}
