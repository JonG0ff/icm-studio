import {spawnSync} from "node:child_process";
import {mkdirSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

const runtimeRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const output = resolve(runtimeRoot, "public/assets/video-production/hybrid-short/synthetic-source.mp4");
mkdirSync(dirname(output), {recursive: true});

// Original technical fixture: moving test pattern and quiet tone, with no speech.
// 24 fps source tests timebase conversion into the 30 fps composition.
const result = spawnSync("ffmpeg", [
  "-hide_banner", "-loglevel", "error", "-y",
  "-f", "lavfi", "-i", "testsrc2=size=720x1280:rate=24:duration=10",
  "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=10",
  "-map", "0:v:0", "-map", "1:a:0",
  "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-threads", "2",
  "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
  "-af", "volume=0.12", "-movflags", "+faststart", "-shortest", output,
], {stdio: "inherit"});
if (result.error) throw result.error;
if (result.status !== 0) process.exit(result.status ?? 1);
console.log(`Synthetic source: ${output}`);
