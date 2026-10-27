import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {createRequire} from "node:module";
import {fileURLToPath, URL} from "node:url";
import {dirname, resolve} from "node:path";
import test from "node:test";

// Use the installed TypeScript compiler, without emitted artifacts or a custom loader dependency.
const require = createRequire(import.meta.url);
const ts = require("typescript");
const cache = new Map();
function load(path) {
  if (cache.has(path)) return cache.get(path).exports;
  const mod = {exports: {}};
  cache.set(path, mod);
  const source = ts.transpileModule(readFileSync(path,"utf8"), {
    compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020},
  }).outputText;
  const localRequire = (name) => name.startsWith(".") ? load(resolve(dirname(path), name + ".ts")) : require(name);
  new Function("module", "exports", "require", source)(mod,mod.exports,localRequire);
  return mod.exports;
}
const {compileEdit, serializeEditMap, captionsToSrt} = load(fileURLToPath(new URL("./compile-edit.ts",import.meta.url)));
const {parseTranscript} = load(fileURLToPath(new URL("./contracts.ts",import.meta.url)));
const H = "a".repeat(64);
const clone = (value) => JSON.parse(JSON.stringify(value));
const wordId = (i) => `talk:w${String(i).padStart(6,"0")}`;

function fixture() {
  const words = [["Hello",.1,.3],[" world.",.35,.55],["Again",1.1,1.3],[" AGAIN",1.35,1.55]].map(([text,startSeconds,endSeconds],i) => ({
    id:wordId(i),rawSegmentIndex:0,rawWordIndex:i,text,startSeconds,endSeconds,confidence:null,
  }));
  const transcript = {
    schemaVersion:1,artifactType:"transcript",jobId:"test",sourceId:"talk",sourceSha256:H,
    analysis:{engine:"openai-whisper",engineVersion:"test",model:"tiny.en",language:"en",settings:{word_timestamps:true},audioStreamIndex:1,rangeStartSeconds:0,rangeEndSeconds:5,cacheKey:H},
    rawResult:{path:"raw.json",sha256:H},
    verification:{status:"verified",reviewer:"Test fixture only",reviewedAt:"2026-10-22T12:00:00Z",sourceId:"talk",sourceSha256:H,sourceRangesSeconds:[[0,5]],listeningObservations:"Synthetic test evidence; never production verification.",reviewedWordIds:words.map((w)=>w.id)},
    words,corrections:[],
  };
  const segment = (id,start,end,ids) => ({id,sourceId:"talk",sourceStartSeconds:start,sourceEndSeconds:end,wordIds:ids.map(wordId),framing:{xPercent:50,yPercent:50,scale:1}});
  return {
    sources:{schemaVersion:1,artifactType:"sources",jobId:"test",sources:[{
      id:"talk",sha256:H,localPath:"talk.mp4",runtimePath:"assets/test/talk.mp4",durationSeconds:5,kind:"recorded",
      video:{streamIndex:0,width:1920,height:1080,fpsNumerator:30,fpsDenominator:1,timeBase:"1/15360",durationInFrames:150,frameRateMode:"cfr",timingEvidence:"timing.json"},
      audio:[{streamIndex:1,sampleRate:48000,channels:1}],rightsRef:"rights.md",
    }]},
    decisions:{schemaVersion:1,artifactType:"edit-decisions",jobId:"test",sourcesRef:{path:"sources.json",sha256:H},transcriptRefs:[{sourceId:"talk",path:"transcript.json",sha256:H}],output:{fpsNumerator:30,fpsDenominator:1,width:1080,height:1920},captions:{mode:"burned-in",casing:"preserve"},segments:[segment("later",1,2,[2,3]),segment("earlier",0,1,[0,1]),segment("repeat",1,2,[2,3])]},
    transcripts:[transcript], inputHashes:{sourcesSha256:H,decisionsSha256:H,transcriptSha256BySourceId:{talk:H}},
  };
}
const t = (f) => f.transcripts[0];
const s = (f) => f.sources.sources[0];
const onlyFirstSourceRange = (f) => {f.decisions.segments = [f.decisions.segments[1]]; return f;};

test("reorder/removal/repetition preserve IDs, raw text, timing and deterministic input-bound map hash", () => {
  const input = fixture(); const before = clone(input);
  const result = compileEdit(input);
  assert.deepEqual(input,before,"compiler must not mutate recognition or decisions");
  assert.deepEqual(result.map.segments.map((seg)=>[seg.sourceStartFrame,seg.sourceEndFrame,seg.outputStartFrame,seg.outputEndFrame]),[[30,60,0,30],[0,30,30,60],[30,60,60,90]]);
  assert.equal(result.map.output.durationInFrames,90);
  assert.deepEqual(result.captions.cues.map((c)=>c.segmentId),["later","earlier","repeat"]);
  assert.deepEqual(result.captions.cues.map((c)=>c.wordIds),[[wordId(2),wordId(3)],[wordId(0),wordId(1)],[wordId(2),wordId(3)]]);
  assert.deepEqual(result.captions.cues.flatMap((c)=>c.words.map((w)=>w.rawText)),["Again"," AGAIN","Hello"," world.","Again"," AGAIN"]);
  assert.deepEqual(result.captions.cues.map((c)=>c.text),["Again AGAIN","Hello world.","Again AGAIN"]);
  assert.ok(Math.abs(result.captions.cues[0].words[0].outputStartSeconds - .1)<1e-12);
  assert.ok(Math.abs(result.captions.cues[2].words[0].outputStartSeconds - 2.1)<1e-12);
  assert.equal(result.captions.inputHashes.mapSha256,createHash("sha256").update(serializeEditMap(result.map)).digest("hex"));
  assert.equal(result.captions.inputHashes.decisionsSha256,H);
  assert.deepEqual(compileEdit(input),result);
  assert.match(result.srt,/1\n00:00:00,100 --> 00:00:00,550\nAgain AGAIN/);
  assert.match(result.srt,/3\n00:00:02,100 --> 00:00:02,550/);
});

test("punctuation, pauses and cuts group independently without changing word objects", () => {
  const f=fixture();
  t(f).words[2].text="Again.";
  const result=compileEdit(f);
  assert.deepEqual(result.captions.cues.map((c)=>c.segmentId),["later","later","earlier","repeat","repeat"]);
  assert.equal(result.captions.cues[0].words[0].text,"Again.");
  const g=fixture(); t(g).words[1].startSeconds=.65; t(g).words[1].endSeconds=.75;
  assert.equal(compileEdit(g).captions.cues.filter((c)=>c.segmentId==="earlier").length,2);
});

test("snap once to the frame grid and derive every output edge from that cut", () => {
  const f=onlyFirstSourceRange(fixture());
  f.decisions.segments[0].sourceStartSeconds=.01; f.decisions.segments[0].sourceEndSeconds=.99;
  const result=compileEdit(f);
  assert.equal(result.map.segments[0].sourceStartFrame,1);
  assert.equal(result.map.segments[0].sourceEndFrame,30);
  assert.equal(result.map.output.durationInFrames,29);
  assert.ok(Math.abs(result.captions.cues[0].startSeconds-(.1-1/30))<1e-12);
});

test("partial-word cuts fail before snapping, after snapping, and when expansion adds a word", () => {
  const original=onlyFirstSourceRange(fixture()); original.decisions.segments[0].sourceStartSeconds=.15;
  assert.throws(()=>compileEdit(original),/original bounds: partial-word cut/);
  const snapped=onlyFirstSourceRange(fixture()); t(snapped).words[0].startSeconds=.11; snapped.decisions.segments[0].sourceStartSeconds=.105;
  assert.throws(()=>compileEdit(snapped),/snapped bounds: partial-word cut/);
  const expanded=onlyFirstSourceRange(fixture()); t(expanded).words[2].startSeconds=.985; t(expanded).words[2].endSeconds=.995;
  expanded.decisions.segments[0].sourceEndSeconds=.98;
  assert.throws(()=>compileEdit(expanded),/snapped bounds: wordIds must exactly match/);
});

test("word selection requires exactly ordered identities; repeated selection needs a new segment ID", () => {
  for (const ids of [[wordId(1)],[wordId(1),wordId(0)],[wordId(0),wordId(0)],["unknown"]]) {
    const f=onlyFirstSourceRange(fixture()); f.decisions.segments[0].wordIds=ids;
    assert.throws(()=>compileEdit(f),/wordIds|duplicate IDs/);
  }
  const f=fixture(); f.decisions.segments[2].id="later";
  assert.throws(()=>compileEdit(f),/segment IDs must be unique/);
});

test("automatic status, partial coverage, wrong source evidence and global labels never certify speech", () => {
  const mutations=[
    (f)=>{t(f).verification={status:"automatic"};},
    (f)=>{t(f).verification.reviewedWordIds.pop();},
    (f)=>{t(f).verification.sourceRangesSeconds=[[0,1.4]];},
    (f)=>{t(f).verification.sourceSha256="b".repeat(64);},
    (f)=>{t(f).verification={status:"verified"};},
    (f)=>{t(f).verification.listeningObservations="";},
  ];
  for(const mutate of mutations){const f=fixture();mutate(f);assert.throws(()=>compileEdit(f),/verification|listening/);}
  const f=fixture(); t(f).verification.status="partial";
  assert.equal(compileEdit(f).captions.cues.length,3,"partial overall review can cover every selected word");
  const none=fixture(); none.decisions.captions.mode="none"; t(none).verification={status:"automatic"};
  assert.throws(()=>compileEdit(none),/requires explicit listening/);
});

test("explicit corrections retain raw recognition and require identity, range evidence and listening coverage", () => {
  const f=fixture(); const raw=clone(t(f).words);
  t(f).corrections=[{wordId:wordId(0),originalText:"Hello",text:"HELLO",startSeconds:.12,reason:"Test correction only",evidence:{reviewer:"Test reviewer",reviewedAt:"2026-10-22T12:00:00Z",sourceRangeSeconds:[0,1]}}];
  const result=compileEdit(f); const word=result.captions.cues.find((c)=>c.segmentId==="earlier").words[0];
  assert.equal(word.rawText,"Hello");assert.equal(word.text,"HELLO");assert.equal(word.id,wordId(0));assert.equal(word.sourceStartSeconds,.12);
  assert.equal(word.correction.reason,"Test correction only"); assert.deepEqual(t(f).words,raw);
  for (const mutate of [
    (g)=>{t(g).corrections[0].originalText="different";},
    (g)=>{t(g).corrections[0].wordId="unknown";},
    (g)=>{t(g).corrections[0].evidence.sourceRangeSeconds=[.12,.3];},
    (g)=>{t(g).corrections[0].endSeconds=.4;},
    (g)=>{t(g).verification.reviewedWordIds=t(g).verification.reviewedWordIds.filter((id)=>id!==wordId(0));},
  ]){const g=clone(f);mutate(g);assert.throws(()=>compileEdit(g),/correction|effective word ranges|listening/);}
});

test("explicit no-speech has no transcript, captions or invented verification", () => {
  const f=fixture(); f.decisions.noSpeech=true;f.transcripts=[];f.decisions.transcriptRefs=[];f.inputHashes.transcriptSha256BySourceId={};
  f.decisions.segments.forEach((seg)=>{seg.wordIds=[];});
  const result=compileEdit(f);assert.deepEqual(result.map.captionTracks,[]);assert.deepEqual(result.captions.cues,[]);assert.equal(result.srt,"");
  const g=fixture();g.decisions.noSpeech=true;assert.throws(()=>compileEdit(g),/requires no transcript/);
  const h=clone(f);delete h.decisions.noSpeech;assert.throws(()=>compileEdit(h),/canonical source transcript/);
  const j=clone(f);j.decisions.segments[0].wordIds=[wordId(0)];assert.throws(()=>compileEdit(j),/wordIds/);
});

test("unknown fields, malformed unknown input and unsupported retiming fail closed", () => {
  for(const field of ["speed","transition","retiming","card"]){const f=fixture();f.decisions.segments[0][field]=1;assert.throws(()=>compileEdit(f),/unsupported/);}
  const cases=[null,{},[],{sources:null},{...fixture(),decisions:null},{...fixture(),transcripts:null},{...fixture(),inputHashes:null}];
  for(const f of cases) assert.throws(()=>compileEdit(f),/compiler|sources|decisions|transcripts|inputHashes/);
  const f=fixture();f.decisions.output.extra=1;assert.throws(()=>compileEdit(f),/unsupported/);
});

test("versions, jobs, references and source identities are hash-bound", () => {
  const mutations=[
    (f)=>{f.sources.schemaVersion=2;},(f)=>{f.decisions.jobId="different";},
    (f)=>{f.inputHashes.sourcesSha256="b".repeat(64);},(f)=>{f.inputHashes.transcriptSha256BySourceId.talk="b".repeat(64);},
    (f)=>{t(f).sourceSha256="b".repeat(64);},(f)=>{f.decisions.segments[0].sourceId="missing";},
    (f)=>{f.transcripts.push(clone(t(f)));f.decisions.transcriptRefs.push({...f.decisions.transcriptRefs[0]});},
    (f)=>{f.inputHashes.decisionsSha256="SHORT";},(f)=>{f.decisions.transcriptRefs=[];},
  ];
  for(const mutate of mutations){const f=fixture();mutate(f);assert.throws(()=>compileEdit(f),/schemaVersion|job IDs|hash|source|transcript|SHA-256/);}
});

test("CFR, same-rate, source frame bounds, runtime paths and selected audio are enforced", () => {
  const mutations=[
    (f)=>{s(f).video.frameRateMode="vfr";},(f)=>{s(f).video.frameRateMode="unknown";},
    (f)=>{f.decisions.output.fpsNumerator=25;},(f)=>{f.sources.sources.push({...s(f),id:"second"});},
    (f)=>{f.decisions.segments[0].sourceEndSeconds=6;},(f)=>{s(f).runtimePath="../escape.mp4";},
    (f)=>{t(f).analysis.audioStreamIndex=9;},(f)=>{s(f).audio.push({streamIndex:2,sampleRate:48000,channels:1});},
    (f)=>{s(f).video.durationInFrames=40;},(f)=>{s(f).video.fpsNumerator=Number.MAX_SAFE_INTEGER;f.decisions.output.fpsNumerator=Number.MAX_SAFE_INTEGER;f.decisions.output.fpsDenominator=2;s(f).video.fpsDenominator=2;},
  ];
  for(const mutate of mutations){const f=fixture();mutate(f);assert.throws(()=>compileEdit(f),/CFR|rates|source|public|audio|frame|precision|analysis/);}
});

test("raw and corrected timings remain strict and unsupported words cannot be normalized", () => {
  for(const mutate of [
    (f)=>{t(f).words[0].endSeconds=t(f).words[0].startSeconds;},
    (f)=>{t(f).words[1].startSeconds=.2;},(f)=>{t(f).words[0].startSeconds=null;},
    (f)=>{t(f).words[0].id="invented";},(f)=>{t(f).words[0].confidence=1.1;},
    (f)=>{t(f).words[0].text=" ";},(f)=>{t(f).words[0].rawSegmentIndex=.5;},
  ]){const f=fixture();mutate(f);assert.throws(()=>parseTranscript(t(f)),/word|timestamp|ID|confidence|text|integer/);}
});

const untimeWorld = (f) => {Object.assign(t(f).words[1],{startSeconds:null,endSeconds:null,timingIssue:"zero-length"}); return f;};

test("untimed recognition keeps its ID, never gets invented bounds, and blocks only selections that could contain it", () => {
  parseTranscript(t(untimeWorld(fixture())));
  for(const mutate of [
    (f)=>{untimeWorld(f);t(f).words[1].startSeconds=.35;},
    (f)=>{untimeWorld(f);t(f).words[1].timingIssue="guessed";},
    (f)=>{t(f).words[1].timingIssue="zero-length";},
  ]){const f=fixture();mutate(f);assert.throws(()=>parseTranscript(t(f)),/untimed|timing|timestamp|word/);}
  const blocked = untimeWorld(fixture());
  assert.throws(()=>compileEdit(blocked),/untimed recognized word talk:w000001/);
  const listed = untimeWorld(onlyFirstSourceRange(fixture())); listed.decisions.segments[0].wordIds=[wordId(0),wordId(1)];
  assert.throws(()=>compileEdit(listed),/untimed|wordIds/);
  const clear = untimeWorld(fixture());
  clear.decisions.segments=[{...clear.decisions.segments[0],id:"clear",sourceStartSeconds:1.1}];
  assert.deepEqual(compileEdit(clear).captions.cues.flatMap((cue)=>cue.wordIds),[wordId(2),wordId(3)]);
});

test("a listening correction must supply both bounds before an untimed word can be selected", () => {
  const correction = {wordId:wordId(1),originalText:" world.",startSeconds:.35,endSeconds:.55,reason:"Zero-length recognition; bounds set by listening.",evidence:{reviewer:"Test fixture only",reviewedAt:"2026-10-22T12:00:00Z",sourceRangeSeconds:[0,1]}};
  const fixed = untimeWorld(fixture()); t(fixed).corrections=[correction];
  const result = compileEdit(fixed);
  const word = result.captions.cues.flatMap((cue)=>cue.words).find((w)=>w.id===wordId(1));
  assert.equal(word.rawText," world."); assert.equal(word.sourceStartSeconds,.35); assert.deepEqual(word.correction,correction);
  const half = untimeWorld(fixture()); t(half).corrections=[{...correction,endSeconds:undefined}];
  assert.throws(()=>compileEdit(half),/both startSeconds and endSeconds/);
});

test("SRT uses the same output cues and rejects collisions or collapsed rounded ranges", () => {
  const base=compileEdit(fixture()).captions.cues[0];
  assert.throws(()=>captionsToSrt([{...base,startSeconds:0,endSeconds:.0004}]),/collapses/);
  assert.throws(()=>captionsToSrt([{...base,startSeconds:0,endSeconds:1},{...base,id:"second",startSeconds:.999,endSeconds:2}]),/collision/);
  assert.throws(()=>captionsToSrt([{...base,text:"bad\n\ntext"}]),/single nonempty line/);
  assert.equal(captionsToSrt([{...base,startSeconds:3661.001,endSeconds:3662.999,text:"same"}]),"1\n01:01:01,001 --> 01:01:02,999\nsame\n");
});
