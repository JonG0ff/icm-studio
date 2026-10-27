import assert from "node:assert/strict";
import test from "node:test";
import {mkdtemp, rm} from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import {run} from "./lib/footage-io.mjs";
import {audioSampleRanges, decodeMono, measureDelay, muxEditAudio} from "./lib/footage-audio.mjs";

const RATE = 48000;
const map = (fps, segments, sourceFrames) => ({
  output: {fps, width: 160, height: 90, durationInFrames: segments.reduce((sum, [start, end]) => sum + end - start, 0)},
  sources: [{id: "take", path: "assets/test/take.mp4", fps, durationInFrames: sourceFrames, kind: "recorded"}],
  segments: segments.reduce((list, [start, end], i) => {
    const outputStartFrame = list.length ? list.at(-1).outputEndFrame : 0;
    return [...list, {id: `s${i}`, sourceId: "take", sourceStartFrame: start, sourceEndFrame: end, outputStartFrame, outputEndFrame: outputStartFrame + end - start}];
  }, []),
  captionTracks: [],
});

test("sample ranges follow compiled frames exactly at integer and NTSC rates", () => {
  assert.deepEqual(audioSampleRanges(map(30, [[30, 60], [0, 15]], 90), RATE),
    {ranges: [{segmentId: "s0", startSample: 48000, endSample: 96000}, {segmentId: "s1", startSample: 0, endSample: 24000}], totalSamples: 72000});
  const ntsc = audioSampleRanges(map(24000 / 1001, [[24, 48], [0, 1]], 100), RATE);
  assert.deepEqual(ntsc.ranges.map((r) => [r.startSample, r.endSample]), [[48048, 96096], [0, 2002]]);
  assert.equal(ntsc.totalSamples, 25 * 2002);
  assert.throws(() => audioSampleRanges(map(30, [[0, 30]], 90), 0), /sample rate/);
});

test("muxed edit audio starts at sample zero, matches picture length, and keeps cut content", async () => {
  const dir = await mkdtemp(path.join(os.tmpdir(), "footage-audio-"));
  try {
    // One-second tone steps: 440 Hz, 880 Hz, 1320 Hz. Picture is video-only, as rendered muted.
    const source = path.join(dir, "source.mp4"), picture = path.join(dir, "picture.mp4"), output = path.join(dir, "out.mp4");
    await run("ffmpeg", ["-v", "error", "-nostdin", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=30:duration=3",
      "-f", "lavfi", "-i", `aevalsrc='sin(2*PI*440*(1+floor(t))*t)':s=${RATE}:d=3`, "-c:v", "libx264", "-pix_fmt", "yuv420p",
      "-c:a", "aac", "-shortest", source]);
    const edit = map(30, [[60, 90], [0, 30]], 90);
    await run("ffmpeg", ["-v", "error", "-nostdin", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=30", "-frames:v", "60",
      "-c:v", "libx264", "-pix_fmt", "yuv420p", picture]);
    const evidence = await muxEditAudio({picture, original: source, audioStreamIndex: 1, map: edit, sampleRate: RATE, output});
    assert.equal(evidence.expectedSamples, 2 * RATE);
    assert.equal(evidence.signaledSamples, 2 * RATE);
    assert.ok(evidence.decodedSamples >= 2 * RATE && evidence.decodedSamples < 2 * RATE + 1024);
    assert.equal(evidence.videoFrames, 60);
    assert.deepEqual(evidence.alignment.map((a) => a.delaySamples), [0, 0]);
    const samples = await decodeMono(output, RATE);
    const firstAudible = samples.findIndex((x) => Math.abs(x) > 0.05);
    assert.ok(firstAudible >= 0 && firstAudible < 48, `audio must start at zero, first audible sample ${firstAudible}`);
    const crossings = (from, to) => {let n = 0; for (let i = from + 1; i < to; i++) if (samples[i - 1] < 0 && samples[i] >= 0) n++; return n;};
    // Each half-second window away from the cut shows the selected tone.
    assert.ok(Math.abs(crossings(12000, 36000) - 660) <= 3, `first segment is the 1320 Hz source range, got ${crossings(12000, 36000) * 2} Hz`);
    assert.ok(Math.abs(crossings(60000, 84000) - 220) <= 3, `second segment is the 440 Hz source range, got ${crossings(60000, 84000) * 2} Hz`);
  } finally {await rm(dir, {recursive: true, force: true});}
});

test("cross-correlation reports a late copy as positive delay and refuses silence", () => {
  const source = Float32Array.from({length: 48000}, (_, i) => Math.sin(i * 0.05) * Math.sin(i * 0.0011) + 0.3 * Math.sin(i * 0.37));
  const late = Float32Array.from({length: 48000}, (_, i) => source[i - 2048] ?? 0);
  assert.equal(measureDelay(late, 0, source, 0, 48000, RATE).delaySamples, 2048);
  assert.equal(measureDelay(source, 0, source, 0, 48000, RATE).delaySamples, 0);
  assert.equal(measureDelay(new Float32Array(48000), 0, source, 0, 48000, RATE), null);
});

test("NTSC output keeps a sample-exact signaled audio length, not millisecond-rounded", async () => {
  const dir = await mkdtemp(path.join(os.tmpdir(), "footage-audio-ntsc-"));
  try {
    const source = path.join(dir, "source.mp4"), picture = path.join(dir, "picture.mp4"), output = path.join(dir, "out.mp4");
    await run("ffmpeg", ["-v", "error", "-nostdin", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=24000/1001:duration=3",
      "-f", "lavfi", "-i", `aevalsrc='0.5*sin(2*PI*(300+200*t)*t)':s=${RATE}:d=3`, "-c:v", "libx264", "-pix_fmt", "yuv420p",
      "-c:a", "aac", "-shortest", source]);
    // 25 frames = 50050 samples = 1.0427083 s, which milliseconds cannot represent.
    const edit = map(24000 / 1001, [[30, 55]], 72);
    await run("ffmpeg", ["-v", "error", "-nostdin", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=24000/1001", "-frames:v", "25",
      "-c:v", "libx264", "-pix_fmt", "yuv420p", picture]);
    const evidence = await muxEditAudio({picture, original: source, audioStreamIndex: 1, map: edit, sampleRate: RATE, output});
    assert.equal(evidence.signaledSamples, 50050);
    assert.equal(evidence.videoFrames, 25);
  } finally {await rm(dir, {recursive: true, force: true});}
});
