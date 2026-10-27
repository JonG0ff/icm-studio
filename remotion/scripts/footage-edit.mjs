#!/usr/bin/env node
import {parseArgs} from "node:util";
import {lstat, mkdir, readFile, readdir, writeFile} from "node:fs/promises";
import path from "node:path";
import {pathToFileURL} from "node:url";
import {muxEditAudio} from "./lib/footage-audio.mjs";
import {analysePcm, compileJob, hashFile, jsonBytes, probeSource, readJson, run, runtimeRoot, sha256, sourceFiles, writeJson} from "./lib/footage-io.mjs";

const compositionId = "video-production-selected-footage";
// Every registered composition loads at bundle start. Under full-length 4K frame
// extraction, another proof's font load outlasted Remotion's 30 s default on
// 2026-10-23 (it finished in 33.6 s at 120 s). Waiting longer changes no pixels.
const RENDER_TIMEOUT_MS = 120000;
const help = `Local selected-footage tools (no hosted transcription).
  inspect     Python inspection flags; optional --energy-out FILE
  transcribe  Python Whisper/cache flags (model and language required)
  validate    --decisions FILE --out-dir DIR
  preview     --decisions FILE --out-dir DIR [--frames 0,30] [--scale 0.5]
              [--timeline] (source filmstrip, waveform, and effective word labels)
  render      --decisions FILE --out-dir DIR --plan FILE --reviewer NAME --playback-method METHOD
Inspect/transcribe flags: python3 scripts/footage_analysis.py <operation> --help
Render requires matching actual preview evidence in out-dir. QA remains pending until full playback.
See scripts/FOOTAGE_EDIT.md for contracts, supported inputs, and examples.`;
const textOption = {type: "string"};
const required = (values, key) => {if (!values[key]?.trim()) throw new Error(`--${key} is required`); return values[key];};

async function analyseOperation(operation, args) {
  // Python owns these flags. Only strip our optional energy bridge argument.
  const forwarded = [...args];
  const energyAt = forwarded.indexOf("--energy-out");
  let energyOut;
  if (energyAt >= 0) {
    energyOut = forwarded[energyAt + 1];
    if (operation !== "inspect" || !energyOut || energyOut.startsWith("--")) throw new Error("--energy-out FILE is supported by inspect only.");
    forwarded.splice(energyAt, 2);
  }
  const stdout = await run("python3", ["-B", path.join(runtimeRoot, "scripts/footage_analysis.py"), operation, ...forwarded]);
  process.stdout.write(stdout);
  if (energyOut) {
    const outAt = forwarded.indexOf("--out");
    if (outAt < 0) throw new Error("--out SOURCES_JSON is required for energy analysis.");
    const inventory = await readJson(forwarded[outAt + 1]);
    const {source, original} = await sourceFiles(inventory.value, inventory.filename);
    await probeSource(source, original);
    await writeJson(energyOut, await analysePcm({source, original}));
    console.log(`Energy candidates: ${path.resolve(energyOut)} (listening required)`);
  }
}

async function writeBuild(outDir, job) {
  await mkdir(outDir, {recursive: true});
  const paths = {map: path.join(outDir, "edit-map.json"), captions: path.join(outDir, "captions.json"), props: path.join(outDir, "props.json")};
  const protectedInputs = new Set([job.decisions.filename, job.sources.filename, job.media.original, job.media.runtime,
    ...job.transcripts.flatMap((t) => [t.filename, path.resolve(path.dirname(t.filename), t.value.rawResult.path)]),
    path.resolve(path.dirname(job.sources.filename), job.media.source.rightsRef),
    path.resolve(path.dirname(job.sources.filename), job.media.source.video.timingEvidence)]);
  for (const name of ["edit-map.json", "captions.json", "props.json", "captions.srt", "output-timeline-words.json", "build-notes.md", "source-timeline-words.json", "source-timeline.png", "preview-evidence.json"]) {
    const file = path.join(outDir, name);
    if (protectedInputs.has(file)) throw new Error(`Build output would overwrite an input: ${file}`);
    try {if ((await lstat(file)).isSymbolicLink()) throw new Error(`Build outputs must not overwrite symlinks: ${file}`);} catch (error) {if (error.code !== "ENOENT") throw error;}
  }
  await writeJson(paths.map, job.map);
  await writeJson(paths.captions, job.captions);
  await writeJson(paths.props, job.props);
  // Always replace the derivative: changing to no captions must not leave a stale sidecar.
  await writeFile(path.join(outDir, "captions.srt"), job.srt);
  await writeJson(path.join(outDir, "output-timeline-words.json"), {words: job.captions.cues.flatMap((cue) => cue.words.map((w) => ({type: "word", text: w.text, start: w.outputStartSeconds, end: w.outputEndSeconds})))});
  const notes = `# Selected-footage build\n\nContract: HybridEditMap-v1. Compiler: selected-footage-v1.\n\n- Decisions: ${job.decisions.filename} (SHA-256 ${job.decisions.hash})\n- Sources: ${job.sources.filename} (SHA-256 ${job.sources.hash})\n- Map SHA-256: ${await hashFile(paths.map)}\n- Props SHA-256: ${await hashFile(paths.props)}\n- Composition: ${compositionId}\n- Output: ${job.map.output.width} × ${job.map.output.height}, ${job.map.output.fps} fps, ${job.map.output.durationInFrames} frames.\n- Source analysis is reused; compilation never transcribes.\n- Captions: ${job.decisions.value.captions.mode}. SRT uses mapped output timing.\n- Playback QA: pending. Technical checks and stills do not establish audiovisual QA.\n- Rights remain governed by the source record and job approval.\n`;
  await writeFile(path.join(outDir, "build-notes.md"), notes);
  return paths;
}

export async function main(args = process.argv.slice(2)) {
  const [operation, ...rest] = args;
  if (!operation || ["--help", "-h", "help"].includes(operation)) {console.log(help); return;}
  if (["inspect", "transcribe"].includes(operation)) return analyseOperation(operation, rest);
  if (!["validate", "preview", "render"].includes(operation)) throw new Error(`Unknown operation ${operation}. Use --help.`);
  const options = {decisions: textOption, "out-dir": textOption};
  if (operation === "preview") Object.assign(options, {frames: textOption, scale: textOption, timeline: {type: "boolean"}});
  if (operation === "render") Object.assign(options, {plan: textOption, reviewer: textOption, "playback-method": textOption});
  const {values} = parseArgs({args: rest, options, strict: true, allowPositionals: false});
  const decisionsFile = path.resolve(required(values, "decisions"));
  const outDir = path.resolve(required(values, "out-dir"));
  const job = await compileJob(decisionsFile);
  // Compile and validate every input before loading Chromium or spending render time.
  const paths = await writeBuild(outDir, job);
  if (operation === "validate") {console.log(jsonBytes(paths)); return paths;}
  const propsHash = sha256(jsonBytes(job.props));
  let frames, scale, attempt, plan;
  if (operation === "preview") {
    frames = (values.frames ?? `0,${Math.floor((job.map.output.durationInFrames - 1) / 2)},${job.map.output.durationInFrames - 1}`).split(",").map(Number);
    frames = [...new Set(frames)];
    scale = Number(values.scale ?? "0.5");
    if (!frames.length || frames.length > 64 || frames.some((f) => !Number.isSafeInteger(f) || f < 0 || f >= job.map.output.durationInFrames) || !Number.isFinite(scale) || scale <= 0 || scale > 1) throw new Error("Preview requires 1–64 in-range integer frames and 0 < scale <= 1.");
    if (values.timeline) {
      if (job.props.muted) throw new Error("The waveform timeline requires selected audio; use composition stills for the no-audio branch.");
      const bridge = path.join(outDir, "source-timeline-words.json");
      await writeJson(bridge, {words: (job.map.captionTracks[0]?.captions ?? []).map((w) => ({type: "word", text: w.text, start: w.startMs / 1000, end: w.endMs / 1000}))});
      const selection = job.map.segments[0];
      await run("python3", ["-B", path.join(runtimeRoot, "scripts/vendor/video-use/timeline_view.py"), job.media.original,
        String(selection.sourceStartFrame / job.map.output.fps), String(selection.sourceEndFrame / job.map.output.fps),
        "--audio-track", String(job.props.audioStreamIndex), "--transcript", bridge, "-o", path.join(outDir, "source-timeline.png")]);
    }
  } else {
    plan = path.resolve(required(values, "plan"));
    await readFile(plan);
    required(values, "reviewer"); required(values, "playback-method");
    const preview = (await readJson(path.join(outDir, "preview-evidence.json"))).value;
    if (preview.propsSha256 !== propsHash || !preview.stills?.length) throw new Error("Preview evidence is stale or missing; preview these exact decisions before rendering.");
    for (const still of preview.stills) if (await hashFile(path.join(outDir, still.path)) !== still.sha256) throw new Error("Preview file changed; preview again.");
    const attempts = (await readdir(outDir)).filter((f) => /^render-attempt-\d+\.json$/.test(f));
    if (attempts.length >= 3) throw new Error("Three full-render attempts recorded for this build. Stop for the job's spend review before starting another run.");
    attempt = path.join(outDir, `render-attempt-${attempts.length + 1}.json`);
    await writeFile(attempt, jsonBytes({status: "started", propsSha256: propsHash, plan, planSha256: await hashFile(plan), reviewer: values.reviewer, playbackMethod: values["playback-method"], qa: "pending-full-audiovisual-playback"}), {flag: "wx"});
  }
  const {bundle} = await import("@remotion/bundler");
  const {openBrowser, selectComposition, renderStill, renderMedia} = await import("@remotion/renderer");
  const serveUrl = await bundle({entryPoint: path.join(runtimeRoot, "src/index.ts"), publicDir: path.join(runtimeRoot, "public"), outDir: path.join(outDir, "bundle")});
  const browser = await openBrowser("chrome");
  try {
    const composition = await selectComposition({serveUrl, id: compositionId, inputProps: job.props, puppeteerInstance: browser});
    for (const key of ["durationInFrames", "width", "height", "fps"]) {
      if (composition[key] !== job.map.output[key]) throw new Error(`Dynamic composition ${key} disagrees with compiled output.`);
    }
    if (operation === "preview") {
      const stills = [];
      for (const frame of frames) {
        const filename = `frame-${String(frame).padStart(6, "0")}.png`;
        await renderStill({serveUrl, composition, inputProps: job.props, output: path.join(outDir, filename), frame, scale, imageFormat: "png", timeoutInMilliseconds: RENDER_TIMEOUT_MS, puppeteerInstance: browser});
        stills.push({frame, path: filename, sha256: await hashFile(path.join(outDir, filename))});
      }
      await writeJson(path.join(outDir, "preview-evidence.json"), {propsSha256: propsHash, inputHashes: job.captions.inputHashes, output: job.map.output, stills, qa: "technical-stills-only; full audiovisual playback pending"});
      console.log(jsonBytes({compositionId, output: job.map.output, stills, outDir}));
    } else {
      const outputLocation = path.join(outDir, `video-${path.basename(attempt, ".json")}.mp4`);
      const selectedAudio = job.sources.value.sources[0].audio[0];
      // Remotion renders picture only; audio is cut from the same compiled frames (see lib/footage-audio.mjs).
      const picture = job.props.muted ? outputLocation : path.join(outDir, `picture-${path.basename(attempt, ".json")}.mp4`);
      let audioMux;
      try {
        await renderMedia({serveUrl, composition, inputProps: job.props, outputLocation: picture, codec: "h264", pixelFormat: "yuv420p", muted: true, timeoutInMilliseconds: RENDER_TIMEOUT_MS, puppeteerInstance: browser});
        audioMux = job.props.muted ? {method: "none: no selected audio"} : await muxEditAudio({picture, original: job.media.original,
          audioStreamIndex: selectedAudio.streamIndex, map: job.map, sampleRate: selectedAudio.sampleRate, output: outputLocation});
      } catch (error) {
        // The failed attempt still counts against the run budget; keep its reason.
        await writeJson(attempt, {...(await readJson(attempt)).value, status: "failed", error: String(error.message).split("\n")[0]});
        throw error;
      }
      const evidence = (await readJson(attempt)).value;
      await writeJson(attempt, {...evidence, status: "rendered", output: outputLocation, sha256: await hashFile(outputLocation), audioMux, qa: "pending-full-audiovisual-playback"});
      console.log(jsonBytes({outputLocation, evidence: attempt, qa: "pending-full-audiovisual-playback"}));
    }
  } finally {await browser.close({silent: true});}
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  main().catch((error) => {console.error(`Footage edit: ${error.message}`); process.exitCode = 1;});
}
