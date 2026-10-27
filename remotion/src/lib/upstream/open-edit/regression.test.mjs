// Pure regressions ported from upstream cli/tests/speech-probe.test.ts and edl.test.ts.
// Apache-2.0; see LICENSE, NOTICE and upstream.json. CLI/ffmpeg tests excluded.
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createRequire} from "node:module";
import {URL} from "node:url";
import test from "node:test";
const require = createRequire(import.meta.url);
const ts = require("typescript");
function load(file) {
  const compiled = ts.transpileModule(readFileSync(new URL(file, import.meta.url), "utf8"), {
    compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2018},
  }).outputText;
  const module = {exports: {}};
  new Function("module", "exports", compiled)(module, module.exports);
  return module.exports;
}
const {analyse, envelopeOf, MIN_DYNAMIC_RANGE_DB, percentile} = load("./speech-probe.ts");
const {snapToFrames} = load("./edl.ts");
test("CMP finite boundary validation rejects invalid windows without hanging", () => {
  for (const n of [0,-1,NaN,Infinity,.5]) assert.throws(() => envelopeOf(new Int16Array(10),n), /positive safe integer/);
  for (const n of [0,-1,NaN,Infinity]) {
    assert.throws(() => analyse([],n,250,0), /finite and positive/);
    assert.throws(() => analyse([],10,n,0), /finite and positive/);
    assert.throws(() => snapToFrames({source:"a",start:0,end:1},n), /finite and positive/);
  }
  assert.throws(() => analyse([NaN],10,250,0), /finite values/);
  assert.throws(() => percentile([Infinity],.1), /finite values/);
  assert.throws(() => percentile([0],NaN), /finite values/);
  assert.throws(() => analyse([],10,250,-1), /nonnegative/);
  assert.throws(() => snapToFrames({source:"a",start:0,end:Infinity},30), /finite/);
});
test("CMP long envelope avoids spread argument limits", () => {
  assert.equal(analyse(Array(150000).fill(-50),10,250,0).speechFound,false);
});
/** dBFS -> the constant 16-bit amplitude that measures as that level. */
const amplitudeFor = (db) => Math.round(32768 * 10 ** (db / 20));
/** PCM whose level follows `plan`, one entry per window of `windowSamples`. */
const pcmFrom = (plan, windowSamples) => {
    const out = new Int16Array(plan.length * windowSamples);
    plan.forEach((db, w) => {
        const amp = amplitudeFor(db);
        for (let i = 0; i < windowSamples; i++)
            out[w * windowSamples + i] = i % 2 === 0 ? amp : -amp;
    });
    return out;
};
await test('the envelope reports each window in dBFS', () => {
    const env = envelopeOf(pcmFrom([-6, -20, -40], 160), 160);
    assert.equal(env.length, 3);
    env.forEach((db, i) => assert.ok(Math.abs(db - [-6, -20, -40][i]) < 0.1, `window ${i} was ${db}`));
});
await test('a trailing partial window is not measured as a quiet one', () => {
    // 2.5 windows of signal must produce 2 readings, not 3 with the last one wrong.
    const pcm = new Int16Array(400).fill(amplitudeFor(-6));
    assert.equal(envelopeOf(pcm, 160).length, 2);
});
await test('digital silence reads as the floor sentinel rather than -Infinity', () => {
    assert.deepEqual(envelopeOf(new Int16Array(320), 160), [-100, -100]);
});
await test('percentile picks from the sorted values and clamps at both ends', () => {
    const values = [-10, -50, -30, -20, -40];
    assert.equal(percentile(values, 0), -50);
    assert.equal(percentile(values, 1), -10);
    assert.equal(percentile(values, 0.5), -30);
});
await test('an empty envelope does not throw', () => {
    assert.equal(percentile([], 0.1), -100);
    const result = analyse([], 10, 250, 0);
    assert.equal(result.onset, null);
    assert.equal(result.decay, null);
    assert.deepEqual(result.gaps, []);
});
await test('onset and decay bracket the speech, and gaps are reported in source seconds', () => {
    // 500ms of floor, 300ms of speech, 400ms of floor, at 10ms per window.
    const plan = [...Array(50).fill(-50), ...Array(30).fill(-15), ...Array(40).fill(-50)];
    const result = analyse(plan, 10, 250, 0);
    assert.ok(Math.abs(result.onset - 0.5) < 1e-9, `onset ${result.onset}`);
    assert.ok(Math.abs(result.decay - 0.8) < 1e-9, `decay ${result.decay}`);
    assert.equal(result.gaps.length, 2);
    assert.ok(Math.abs(result.gaps[0].duration - 0.5) < 1e-9);
    assert.ok(Math.abs(result.gaps[1].duration - 0.4) < 1e-9);
});
await test('a range offset is carried into every reported time, so the numbers address the source', () => {
    const plan = [...Array(50).fill(-50), ...Array(30).fill(-15)];
    const result = analyse(plan, 10, 250, 12.5);
    assert.ok(Math.abs(result.onset - 13.0) < 1e-9, `onset ${result.onset}`);
    assert.ok(Math.abs(result.gaps[0].start - 12.5) < 1e-9);
});
await test('a gap shorter than the minimum is not offered as a cut point', () => {
    // 100ms of quiet inside continuous speech: real, and far too short to cut in.
    const plan = [...Array(30).fill(-15), ...Array(10).fill(-50), ...Array(30).fill(-15)];
    assert.deepEqual(analyse(plan, 10, 250, 0).gaps, []);
    assert.equal(analyse(plan, 10, 80, 0).gaps.length, 1);
});
await test('the threshold follows the MEASURED floor, so the same numbers work on a street and in a booth', () => {
    const quiet = [...Array(50).fill(-60), ...Array(30).fill(-15)];
    const street = [...Array(50).fill(-37), ...Array(30).fill(-15)];
    const q = analyse(quiet, 10, 250, 0);
    const s = analyse(street, 10, 250, 0);
    assert.ok(q.threshold < s.threshold, 'a quieter floor must lower the threshold with it');
    // Both find the same speech, which a fixed threshold could not do.
    assert.ok(Math.abs(q.onset - 0.5) < 1e-9);
    assert.ok(Math.abs(s.onset - 0.5) < 1e-9);
});
await test('a flat level offers no trusted cut point or speech onset', () => {
    const result = analyse(Array(80).fill(-15), 10, 250, 0);
    assert.deepEqual(result.gaps, []);
    // Upstream's null-minus-zero assertion accidentally passed through coercion.
    assert.equal(result.onset, null);
    assert.equal(result.speechFound, false);
});
await test('a constant level is NOT reported as unbroken speech', () => {
    // peak === floor makes the threshold equal the floor, so every window counts as speech and the gap
    // search finds nothing. Printed as "no gaps", that tells the agent not to cut anywhere on a clip
    // with no voice in it at all.
    for (const level of [-100, -45, -12]) {
        const result = analyse(Array(200).fill(level), 10, 250, 0);
        assert.equal(result.speechFound, false, `${level} dBFS flat must not read as speech`);
        assert.equal(result.onset, null);
        assert.deepEqual(result.gaps, []);
    }
});
await test('an envelope that measured nothing reports no speech rather than no gaps', () => {
    const result = analyse([], 10, 250, 0);
    assert.equal(result.speechFound, false);
});
await test('a real signal just over the dynamic-range floor is still analysed', () => {
    const plan = [...Array(50).fill(-50), ...Array(30).fill(-50 + MIN_DYNAMIC_RANGE_DB + 1)];
    const result = analyse(plan, 10, 250, 0);
    assert.equal(result.speechFound, true);
    assert.ok(result.onset !== null);
});
await test('a gap is reported only when it is AT LEAST --gap long — 240ms does not satisfy 250', () => {
    // 30ms windows: 8 quiet ones are 240ms, 9 are 270ms. Rounding 250/30 down to 8 reported the first.
    const speech = Array(20).fill(-10);
    const short = analyse([...speech, ...Array(8).fill(-60), ...speech], 30, 250, 0);
    const long = analyse([...speech, ...Array(9).fill(-60), ...speech], 30, 250, 0);
    assert.equal(short.gaps.length, 0, 'a 240ms gap must not pass as 250');
    assert.equal(long.gaps.length, 1);
    assert.ok(long.gaps[0].duration >= 0.25);
});
await test('snapping moves both edges UP to the next frame instant and keeps a grid value where it is', () => {
    assert.deepEqual(snapToFrames({ source: 'a', start: 0.013, end: 0.9 }, 25), { source: 'a', start: 0.04, end: 0.92, fps: 25 });
    assert.deepEqual(snapToFrames({ source: 'a', start: 1, end: 2 }, 25), { source: 'a', start: 1, end: 2, fps: 25 });
    // 1.0s is NOT on the 29.97 grid: frame 30 sits at 1.001s.
    const ntsc = snapToFrames({ source: 'a', start: 1, end: 2 }, 30000 / 1001);
    assert.ok(Math.abs(ntsc.start - 30 * 1001 / 30000) < 1e-9);
    assert.ok(Math.abs(ntsc.end - 60 * 1001 / 30000) < 1e-9);
});
await test('a range shorter than one frame is refused rather than snapped to nothing', () => {
    assert.throws(() => snapToFrames({ source: 'a', start: 1.001, end: 1.011 }, 25, 3), /range 3 of "a" .*shorter than one frame at 25 fps/);
});
