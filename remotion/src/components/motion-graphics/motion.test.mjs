import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { URL } from "node:url";
import test from "node:test";
import ts from "typescript";

const require = createRequire(import.meta.url);
const source = readFileSync(new URL("./motion.ts", import.meta.url), "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText;
const loaded = { exports: {} };
new Function("require", "module", "exports", compiled)(
  require,
  loaded,
  loaded.exports,
);
const { revealProgress } = loaded.exports;

test("reveal holds before its cue and settles exactly after its duration", () => {
  assert.equal(revealProgress(-20, 30, 1, 0.6), 0);
  assert.equal(revealProgress(30, 30, 1, 0.6), 0);
  assert.equal(revealProgress(48, 30, 1, 0.6), 1);
  assert.equal(revealProgress(300, 30, 1, 0.6), 1);
});

test("seconds-based timing stays equivalent across delivery frame rates", () => {
  for (const time of [0, 0.25, 0.5, 0.75, 1, 1.5]) {
    assert.equal(
      revealProgress(time * 24, 24, 0.2, 0.8),
      revealProgress(time * 60, 60, 0.2, 0.8),
    );
  }
});

test("random access is deterministic, finite, bounded, and monotonic", () => {
  const frames = [0, 18, 7, 2, 11, 7, 40];
  assert.equal(revealProgress(frames[2], 30), revealProgress(frames[5], 30));
  let previous = 0;
  for (let frame = -10; frame <= 80; frame++) {
    const progress = revealProgress(frame, 30, 0.5, 1);
    assert.ok(
      Number.isFinite(progress) &&
        progress >= previous &&
        progress >= 0 &&
        progress <= 1,
    );
    previous = progress;
  }
});

test("invalid timing fails instead of propagating non-finite SVG or CSS values", () => {
  for (const args of [
    [0, 0],
    [0, 30, 0, 0],
    [NaN, 30],
    [0, 30, Infinity],
  ]) {
    assert.throws(() => revealProgress(...args), /Motion timing/);
  }
});
