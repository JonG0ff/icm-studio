#!/usr/bin/env node
/**
 * Download audio from a YouTube URL as MP3 using yt-dlp.
 *
 * Usage:
 *   node download-youtube.mjs "https://youtube.com/watch?v=..." ./music/temp-tracks/
 *   node download-youtube.mjs --playlist "https://youtube.com/playlist?list=..." ./music/temp-tracks/
 */

import { execSync } from "child_process";
import { existsSync, mkdirSync } from "fs";
import path from "path";

function printUsage() {
  console.log(`
Usage:
  node download-youtube.mjs <youtube-url> <output-directory>
  node download-youtube.mjs --playlist <youtube-playlist-url> <output-directory>

Examples:
  node download-youtube.mjs "https://www.youtube.com/watch?v=dQw4w9WgXcQ" ./music/temp-tracks/
  node download-youtube.mjs --playlist "https://www.youtube.com/playlist?list=PL..." ./music/temp-tracks/
`);
  process.exit(1);
}

function downloadAudio(url, outputDir, isPlaylist = false) {
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }

  const playlistFlag = isPlaylist ? "--yes-playlist" : "--no-playlist";
  const outputTemplate = path.join(outputDir, "%(title)s.%(ext)s");

  const cmd = [
    "yt-dlp",
    "--extract-audio",
    "--audio-format", "mp3",
    "--audio-quality", "0",        // best quality
    "--embed-thumbnail",          // keep thumbnail in file
    "--add-metadata",             // keep title/artist metadata
    playlistFlag,
    "--output", outputTemplate,
    `"${url}"`,
  ].join(" ");

  console.log(`Running: ${cmd}\n`);
  try {
    execSync(cmd, { stdio: "inherit", cwd: process.cwd() });
    console.log(`\nDone. File(s) saved to: ${outputDir}`);
  } catch (err) {
    console.error("Download failed:", err.message);
    process.exit(1);
  }
}

// ── main ──
const args = process.argv.slice(2);

if (args.length < 2) {
  printUsage();
}

let isPlaylist = false;
let urlIndex = 0;

if (args[0] === "--playlist") {
  isPlaylist = true;
  urlIndex = 1;
}

if (args.length < urlIndex + 2) {
  printUsage();
}

const url = args[urlIndex];
const outputDir = path.resolve(args[urlIndex + 1]);

downloadAudio(url, outputDir, isPlaylist);
