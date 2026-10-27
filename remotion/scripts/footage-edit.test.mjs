import assert from "node:assert/strict";
import test from "node:test";
import {mkdtemp, mkdir, readFile, rm, symlink, writeFile} from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import {randomUUID} from "node:crypto";
import {analysePcm, compileJob, hashFile, readJson, run, runtimeRoot, writeJson} from "./lib/footage-io.mjs";
import {loadTypeScript} from "./lib/load-typescript.mjs";

const cli = path.join(runtimeRoot, "scripts/footage-edit.mjs");
const invoke = (operation, ...args) => run(process.execPath, [cli, operation, ...args]);
async function fixture(callback, {multipleAudio = false} = {}) {
  const directory = await mkdtemp(path.join(os.tmpdir(), "footage-command-"));
  const runtimePath = `assets/.cache/footage-tests-${randomUUID()}/source.mp4`;
  const media = path.join(runtimeRoot, "public", runtimePath);
  await mkdir(path.dirname(media), {recursive: true});
  try {
    const args = ["-v", "error", "-nostdin", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=30:duration=1", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=1"];
    if (multipleAudio) args.push("-f", "lavfi", "-i", "sine=frequency=880:sample_rate=48000:duration=1", "-map", "0:v", "-map", "1:a", "-map", "2:a");
    await run("ffmpeg", [...args, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", media]);
    const sourcesFile = path.join(directory, "sources.json");
    await writeFile(path.join(directory, "rights.md"), "Synthetic FFmpeg test fixture. No production clearance or speech review claimed.\n");
    const flags = multipleAudio ? ["--audio-stream-index", "2"] : [];
    await invoke("inspect", "--source", media, "--job-id", "command-test", "--source-id", "take", "--runtime-path", runtimePath,
      "--rights-ref", "rights.md", "--out", sourcesFile, "--evidence-dir", path.join(directory, "probe"), ...flags);
    const source = (await readJson(sourcesFile)).value.sources[0];
    const decisionsFile = path.join(directory, "decisions.json");
    const decisions = {schemaVersion: 1, artifactType: "edit-decisions", jobId: "command-test", noSpeech: true,
      sourcesRef: {path: "sources.json", sha256: await hashFile(sourcesFile)}, transcriptRefs: [],
      output: {fpsNumerator: 30, fpsDenominator: 1, width: 320, height: 180}, captions: {mode: "none", casing: "preserve"},
      segments: [{id: "second-half", sourceId: "take", sourceStartSeconds: 0.5, sourceEndSeconds: 1, wordIds: []},
        {id: "repeat", sourceId: "take", sourceStartSeconds: 0.5, sourceEndSeconds: 1, wordIds: []}]};
    await writeJson(decisionsFile, decisions);
    await callback({directory, runtimePath, media, sourcesFile, source, decisionsFile, decisions});
  } finally {
    await rm(directory, {recursive: true, force: true});
    await rm(path.dirname(media), {recursive: true, force: true});
  }
}

test("inspect -> validate preserves repeated selections and dynamic revision metadata", async () => fixture(async (f) => {
  const out = path.join(f.directory, "build");
  await invoke("validate", "--decisions", f.decisionsFile, "--out-dir", out);
  const map = (await readJson(path.join(out, "edit-map.json"))).value;
  assert.equal(map.output.durationInFrames, 30);
  assert.deepEqual(map.segments.map((s) => [s.outputStartFrame, s.outputEndFrame]), [[0, 15], [15, 30]]);
  const {footageMetadata} = loadTypeScript(path.join(runtimeRoot, "src/compositions/video-production/selected-footage/metadata.ts"));
  const props = (await readJson(path.join(out, "props.json"))).value;
  assert.deepEqual(footageMetadata(props), {fps: 30, width: 320, height: 180, durationInFrames: 30});
  const otherRate = structuredClone(props);
  otherRate.editMap.output.fps = 24; otherRate.editMap.sources[0].fps = 24;
  assert.equal(footageMetadata(otherRate).fps, 24);
  f.decisions.segments.pop(); f.decisions.output.width = 180; f.decisions.output.height = 320;
  await writeJson(f.decisionsFile, f.decisions);
  const revision = await compileJob(f.decisionsFile);
  assert.deepEqual(footageMetadata(revision.props), {fps: 30, width: 180, height: 320, durationInFrames: 15});
  assert.equal(revision.srt, "");
}));

test("unsupported edits and bad source refs fail before creating render output", async () => fixture(async (f) => {
  f.decisions.segments[0].speed = 2;
  await writeJson(f.decisionsFile, f.decisions);
  await assert.rejects(invoke("render", "--decisions", f.decisionsFile, "--out-dir", path.join(f.directory, "render")), /speed is unsupported/);
  delete f.decisions.segments[0].speed;
  f.decisions.sourcesRef.sha256 = "0".repeat(64);
  await writeJson(f.decisionsFile, f.decisions);
  await assert.rejects(compileJob(f.decisionsFile), /SHA-256 mismatch/);
}));

test("source-byte changes and runtime symlink escapes cannot bypass validation", async () => fixture(async (f) => {
  const original = path.join(f.directory, "outside.mp4");
  await writeFile(original, await readFile(f.media));
  await rm(f.media);
  await symlink(original, f.media);
  await assert.rejects(compileJob(f.decisionsFile), /symlink escapes/);
  await rm(f.media); await writeFile(f.media, await readFile(original));
  await writeFile(f.media, Buffer.from("changed media"));
  await assert.rejects(compileJob(f.decisionsFile), /SHA-256 differs/);
}));

test("selected absolute audio index maps to render ordinal and PCM retains sample range", async () => fixture(async (f) => {
  const job = await compileJob(f.decisionsFile);
  assert.equal(job.props.audioStreamIndex, 1);
  const energy = await analysePcm({source: f.source, original: f.media, startSeconds: 0.2, endSeconds: 0.7});
  assert.equal(energy.rangeStartSeconds, 0.2);
  assert.equal(energy.sampleRate, 16000);
  assert.ok(Math.abs(energy.actualSampleDurationSeconds - 0.5) < 0.005);
  assert.ok(energy.gaps.every((g) => g.start >= 0.2 && g.end <= 0.7 + 1e-6));
  assert.match(energy.warning, /require listening/);
}, {multipleAudio: true}));

test("render refuses missing matching previews before importing browser renderer", async () => fixture(async (f) => {
  const plan = path.join(f.directory, "plan.md"); await writeFile(plan, "Synthetic test plan\n");
  await assert.rejects(invoke("render", "--decisions", f.decisionsFile, "--out-dir", path.join(f.directory, "build"), "--plan", plan, "--reviewer", "test", "--playback-method", "test-only"), /preview-evidence.json/);
}));

test("build cannot overwrite canonical inputs and render budget spans revisions", async () => fixture(async (f) => {
  const colliding = path.join(f.directory, "edit-map.json");
  await writeJson(colliding, f.decisions);
  await assert.rejects(invoke("validate", "--decisions", colliding, "--out-dir", f.directory), /overwrite an input/);
  const out = path.join(f.directory, "build");
  await invoke("validate", "--decisions", f.decisionsFile, "--out-dir", out);
  const propsHash = await hashFile(path.join(out, "props.json"));
  const still = path.join(out, "test.png"); await writeFile(still, "Synthetic gate fixture, not a composition preview");
  await writeJson(path.join(out, "preview-evidence.json"), {propsSha256: propsHash, stills: [{path: "test.png", sha256: await hashFile(still)}]});
  const plan = path.join(f.directory, "plan.md"); await writeFile(plan, "Synthetic gate fixture plan\n");
  for (let i = 1; i <= 3; i++) await writeJson(path.join(out, `render-attempt-${i}.json`), {propsSha256: "older-revision", status: "failed"});
  await assert.rejects(invoke("render", "--decisions", f.decisionsFile, "--out-dir", out, "--plan", plan, "--reviewer", "fixture", "--playback-method", "fixture"), /Three full-render attempts/);
  f.decisions.segments.pop(); await writeJson(f.decisionsFile, f.decisions);
  await assert.rejects(invoke("render", "--decisions", f.decisionsFile, "--out-dir", out, "--plan", plan, "--reviewer", "fixture", "--playback-method", "fixture"), /stale or missing/);
}));

test("canonical words must match raw Whisper exactly; untimed words keep null bounds", async () => {
  const {canonicalWordsMatchRaw} = await import("./lib/footage-io.mjs");
  const raw = {segments: [{words: [{word: " It", start: 1, end: 1, probability: 0.9}, {word: " was", start: 1, end: 1.2}]}]};
  const words = [{id: "s:w000000", rawSegmentIndex: 0, rawWordIndex: 0, text: " It", startSeconds: null, endSeconds: null, confidence: 0.9, timingIssue: "zero-length"},
    {id: "s:w000001", rawSegmentIndex: 0, rawWordIndex: 1, text: " was", startSeconds: 1, endSeconds: 1.2, confidence: null}];
  assert.equal(canonicalWordsMatchRaw(raw, words), true);
  assert.equal(canonicalWordsMatchRaw(raw, [{...words[0], startSeconds: 0.9, endSeconds: 1}, words[1]]), false);
  assert.equal(canonicalWordsMatchRaw(raw, [{...words[0], timingIssue: undefined}, words[1]]), false);
  assert.equal(canonicalWordsMatchRaw(raw, [words[0], {...words[1], text: " is"}]), false);
});
