import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createRequire} from "node:module";
import {URL} from "node:url";
import test from "node:test";

// Compile the pure TS contract in memory using the runtime's existing compiler.
// No emitted files, loader package, or browser are needed for these checks.
const require = createRequire(import.meta.url);
const ts = require("typescript");
const compiled = ts.transpileModule(readFileSync(new URL("./edit-map.ts", import.meta.url), "utf8"), {
  compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020},
}).outputText;
const module = {exports: {}};
new Function("module", "exports", compiled)(module, module.exports);
const {validateEditMap, outputFrameToSource, sourceFrameToOutputFrames, mapSourceCaptions} = module.exports;
const fixture = () => JSON.parse(readFileSync(new URL("./fixture.json", import.meta.url), "utf8"));

test("24fps original source maps to the 30fps output without speed changes", () => {
  const map = fixture();
  validateEditMap(map);
  for (const [outputFrame, sourceFrame] of [[0, 24], [89, 95.2], [90, 144], [179, 215.2]]) {
    const position = outputFrameToSource(map, outputFrame);
    assert.ok(Math.abs(position.sourceFrame - sourceFrame) < 1e-8);
    assert.ok(Math.abs(position.sourceSeconds - sourceFrame / 24) < 1e-8);
  }
  assert.throws(() => outputFrameToSource(map, 180), /outside the timeline/);
  assert.throws(() => outputFrameToSource(map, -1), /outside the timeline/);
});

test("removed source intervals produce no output position, with exclusive ends", () => {
  const map = fixture();
  assert.deepEqual(sourceFrameToOutputFrames(map, "synthetic-source", 24), [0]);
  assert.deepEqual(sourceFrameToOutputFrames(map, "synthetic-source", 96), []);
  assert.deepEqual(sourceFrameToOutputFrames(map, "synthetic-source", 120), []);
  assert.deepEqual(sourceFrameToOutputFrames(map, "synthetic-source", 144), [90]);
  assert.deepEqual(sourceFrameToOutputFrames(map, "synthetic-source", 216), []);
  assert.throws(() => sourceFrameToOutputFrames(map, "synthetic-source", 240), /outside the original media/);
});

test("repeated source ranges retain every output position", () => {
  const map = fixture();
  Object.assign(map.segments[1], {sourceStartFrame: 24, sourceEndFrame: 96});
  assert.deepEqual(sourceFrameToOutputFrames(map, "synthetic-source", 24), [0, 90]);
  assert.equal(mapSourceCaptions(map).length, 4);
});

test("caption text and provenance survive source-to-output remapping", () => {
  const map = fixture();
  const captions = mapSourceCaptions(map);
  assert.deepEqual(captions.map(({startMs, endMs}) => [startMs, endMs]), [[100, 1500], [1500, 2900], [3100, 4500], [4500, 5900]]);
  assert.deepEqual(captions.map(({text}) => text), map.captionTracks[0].captions.map(({text}) => text));
  assert.ok(captions.every((caption) => caption.provenance === "authored-synthetic-label" && caption.timestampMs === null && caption.confidence === null));
});

test("a caption crossing either side of a cut fails instead of clipping words", () => {
  for (const changedRange of [{startMs: 900}, {endMs: 4100}]) {
    const map = fixture();
    map.captionTracks[0].captions = [{...map.captionTracks[0].captions[0], ...changedRange}];
    assert.throws(() => validateEditMap(map), /caption crosses a cut/);
  }
});

test("output gaps, overlaps, truncation, and implicit rate changes are rejected", () => {
  const mutations = [
    (map) => {map.segments[1].outputStartFrame = 91;},
    (map) => {map.segments[1].outputStartFrame = 89;},
    (map) => {map.output.durationInFrames = 181;},
    (map) => {map.segments[0].sourceEndFrame = 95;},
  ];
  for (const mutate of mutations) {
    const map = fixture();
    mutate(map);
    assert.throws(() => validateEditMap(map), /contiguous|exact declared|playback speed/);
  }
});

test("out-of-bounds or unknown sources and unsafe asset paths are rejected", () => {
  const mutations = [
    (map) => {map.segments[0].sourceStartFrame = -1;},
    (map) => {map.segments[1].sourceEndFrame = 241;},
    (map) => {map.segments[0].sourceId = "missing";},
    (map) => {map.sources[0].path = "../private.mp4";},
    (map) => {map.segments[0].card.imagePath = "https://example.com/image.png";},
  ];
  for (const mutate of mutations) {
    const map = fixture();
    mutate(map);
    assert.throws(() => validateEditMap(map), /source|image path/);
  }
});

test("invalid caption ranges and invented synthetic speech provenance fail", () => {
  const mutations = [
    (map) => {map.captionTracks[0].captions[0].endMs = 1100;},
    (map) => {map.captionTracks[0].captions[0].endMs = 10001;},
    (map) => {map.captionTracks[0].captions[0].timestampMs = 999;},
    (map) => {map.captionTracks[0].provenance = "recorded-speech";},
    (map) => {map.sources[0].kind = "recorded";},
  ];
  for (const mutate of mutations) {
    const map = fixture();
    mutate(map);
    assert.throws(() => validateEditMap(map), /caption|recorded speech/);
  }
});
