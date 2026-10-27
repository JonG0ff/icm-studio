// Ported ChunkWordsTests/TAKE from upstream tests/test_render_captions.py.
// MIT; see LICENSE and upstream.json. SRT/path tests excluded.
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
const {chunkWords, CHUNK_MAX_WORDS, CHUNK_MIN_S} = load("./chunk-words.ts");
const w = (text, start, end) => ({text, start, end});
const TAKE = [
 w("90%", 2.64, 3.04), w("of", 3.06, 3.14), w("what", 3.16, 3.26), w("a", 3.30, 3.34),
 w("web", 3.36, 3.50), w("agent", 3.54, 3.82), w("does", 3.86, 4.14), w("is", 4.48, 4.56),
 w("completely", 4.58, 4.90), w("wasted.", 4.94, 5.34), w("We", 6.08, 6.18), w("fix", 6.24, 6.42),
 w("this.", 6.48, 6.70),
];
const texts = (chunks) => chunks.map((c) => c.map((x) => x.text).join(" "));
test("real take", () => {
 assert.deepEqual(texts(chunkWords(TAKE)), ["90% of", "what a web", "agent does", "is completely", "wasted.", "We fix this."]);
});
test("pause splits across words", () => {
 assert.ok(!texts(chunkWords(TAKE)).some((c) => c.toLowerCase() === "does is"));
});
test("no multiword cue flashes except at cap", () => {
 for (const c of chunkWords(TAKE)) {
   if (c.length > 1 && c.length < CHUNK_MAX_WORDS) assert.ok(c[c.length-1].end - c[0].start >= CHUNK_MIN_S);
 }
});
test("punctuation still breaks", () => {
 assert.deepEqual(texts(chunkWords([w("Hi,", 0, .1), w("there", .12, .2)])), ["Hi,", "there"]);
});
test("caps at max words", () => {
 const fast = Array.from({length:7}, (_, i) => w(`w${i}`, i*.05, i*.05+.04));
 assert.ok(chunkWords(fast).every((c) => c.length <= CHUNK_MAX_WORDS));
});
test("skips empty words", () => {
 assert.deepEqual(texts(chunkWords([w(" ",0,.1), w("ok",.1,.5)])), ["ok"]);
 assert.deepEqual(chunkWords([]), []);
});
test("CMP grouping preserves IDs, raw text, case, metadata and object identity", () => {
 const words = TAKE.map((word, i) => Object.freeze({...word, id:`source:w${String(i).padStart(6,"0")}`, text:` ${word.text} `, sourceId:"source"}));
 Object.freeze(words);
 const grouped = chunkWords(words).flat();
 grouped.forEach((word,i) => assert.equal(word,words[i]));
 assert.deepEqual(grouped.map((word)=>word.text), words.map((word)=>word.text));
});
test("invalid word times are refused", () => {
 for (const value of [NaN,Infinity,-1]) assert.throws(()=>chunkWords([w("x",value,1)]),/finite ordered/);
 assert.throws(()=>chunkWords([w("x",1,1)]),/finite ordered/);
});
