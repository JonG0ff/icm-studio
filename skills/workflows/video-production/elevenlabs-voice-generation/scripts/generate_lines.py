#!/usr/bin/env python3
"""Generate one ElevenLabs take per script line, then stitch variants.

Script lines look like `[b-01] HOST: [excited] Text here.` (see SKILL.md).
Each line becomes `<id>.mp3` plus `<id>.alignment.json` from the
text-to-speech with-timestamps endpoint. Each variant is stitched as
hook N lines then all body lines, with a fixed gap between lines.

Usage:
    env $(grep -h '^ELEVENLABS_API_KEY=' .env) python3 generate_lines.py \
        --script script.md --voices cast-voices.json \
        --out-audio audio/ --out-manifest manifest/ [--lines b-03,h2-01] [--dry-run]
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

API_BASE = "https://api.elevenlabs.io/v1/text-to-speech"
API_KEY_VARS = ("ELEVENLABS_API_KEY", "ELEVEN_API_KEY")
DEFAULT_MODEL = "eleven_v3"
DEFAULT_FORMAT = "mp3_44100_128"
DEFAULT_GAP_MS = 150
MAX_RETRIES = 3
BACKOFF_SECONDS = (1.0, 2.0, 4.0)
HTTP_TIMEOUT_SECONDS = 120
ERROR_BODY_CHARS = 300
LINE_RE = re.compile(r"^\[(h\d+-\d{2}|b-\d{2})\] ([A-Z][A-Z0-9_]*): (.+)$")
ID_LIKE_RE = re.compile(r"^\[(h\d|b-)")
FORMAT_RE = re.compile(r"^mp3_(\d+)_(\d+)$")


class ScriptError(ValueError):
    """Script, cast, or argument problem the user must fix."""


class ApiError(RuntimeError):
    """ElevenLabs returned an error after retries."""


@dataclass(frozen=True)
class ScriptLine:
    id: str
    speaker: str
    text: str

    @property
    def hook_variant(self) -> int | None:
        if self.id.startswith("h"):
            return int(self.id[1:].split("-")[0])
        return None


# ---------- script and cast ----------


def parse_script(text: str) -> tuple[ScriptLine, ...]:
    """Parse spoken lines. Fails on lines that look like ids but are malformed."""
    lines: list[ScriptLine] = []
    seen: set[str] = set()
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        match = LINE_RE.match(stripped)
        if not match:
            if ID_LIKE_RE.match(stripped):
                raise ScriptError(f"line {number}: malformed script line: {stripped!r}")
            continue
        line_id, speaker, body = match.groups()
        if line_id in seen:
            raise ScriptError(f"line {number}: duplicate id {line_id}")
        seen.add(line_id)
        lines.append(ScriptLine(line_id, speaker, body.strip()))
    if not lines:
        raise ScriptError("script has no spoken lines in `[id] SPEAKER: text` form")
    return tuple(lines)


def hook_variants(lines: tuple[ScriptLine, ...]) -> tuple[int, ...]:
    return tuple(sorted({l.hook_variant for l in lines if l.hook_variant is not None}))


def variant_order(lines: tuple[ScriptLine, ...], variant: int) -> tuple[ScriptLine, ...]:
    """Hook lines for `variant` in file order, then every body line."""
    variants = hook_variants(lines)
    body = tuple(l for l in lines if l.hook_variant is None)
    if not variants:
        if variant != 1:
            raise ScriptError(f"script has no hook lines; only variant 1 exists, got {variant}")
        return body
    if variant not in variants:
        raise ScriptError(f"variant {variant} not in script; hooks found: {list(variants)}")
    return tuple(l for l in lines if l.hook_variant == variant) + body


def load_voices(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScriptError(f"cannot read voices file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ScriptError(f"{path} must be a JSON object keyed by speaker")
    for speaker, cfg in data.items():
        if not isinstance(cfg, dict) or not isinstance(cfg.get("voice_id"), str) or not cfg["voice_id"]:
            raise ScriptError(f"{path}: speaker {speaker} needs a non-empty voice_id")
    return data


def check_voices(lines: tuple[ScriptLine, ...], voices: dict) -> None:
    missing = sorted({l.speaker for l in lines} - set(voices))
    if missing:
        raise ScriptError(f"no voice in cast-voices.json for: {', '.join(missing)}")


def parse_line_ids(raw: str | None, lines: tuple[ScriptLine, ...]) -> frozenset[str]:
    if not raw:
        return frozenset()
    wanted = frozenset(part.strip() for part in raw.split(",") if part.strip())
    unknown = sorted(wanted - {l.id for l in lines})
    if unknown:
        raise ScriptError(f"--lines ids not in script: {', '.join(unknown)}")
    return wanted


def sample_rate(output_format: str) -> int:
    match = FORMAT_RE.match(output_format)
    if not match:
        raise ScriptError(f"--output-format must be an mp3 format like {DEFAULT_FORMAT}, got {output_format}")
    return int(match.group(1))


# ---------- ElevenLabs HTTP ----------


def http_post(url: str, headers: dict, body: bytes) -> tuple[int, bytes]:
    """POST and return (status, body). Network failures return status 0."""
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except urllib.error.URLError as exc:
        return 0, str(exc.reason).encode("utf-8")


def is_retryable(status: int) -> bool:
    return status == 0 or status == 429 or status >= 500


def tts_with_timestamps(
    line: ScriptLine,
    voice: dict,
    api_key: str,
    output_format: str,
    post: Callable[[str, dict, bytes], tuple[int, bytes]] = http_post,
    sleep: Callable[[float], None] = time.sleep,
) -> dict:
    url = f"{API_BASE}/{voice['voice_id']}/with-timestamps?output_format={output_format}"
    payload = {"text": line.text, "model_id": voice.get("model_id", DEFAULT_MODEL)}
    if voice.get("settings"):
        payload["voice_settings"] = voice["settings"]
    headers = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "application/json"}
    body = json.dumps(payload).encode("utf-8")
    for attempt in range(MAX_RETRIES + 1):
        status, raw = post(url, headers, body)
        if status == 200:
            return json.loads(raw)
        snippet = raw.decode("utf-8", "replace")[:ERROR_BODY_CHARS]
        if not is_retryable(status) or attempt == MAX_RETRIES:
            raise ApiError(f"{line.id}: HTTP {status}: {snippet}")
        print(f"  {line.id}: HTTP {status}, retry {attempt + 1}/{MAX_RETRIES}", file=sys.stderr)
        sleep(BACKOFF_SECONDS[attempt])
    raise ApiError(f"{line.id}: retries exhausted")  # pragma: no cover


def save_take(response: dict, line_id: str, out_audio: Path) -> None:
    audio_b64 = response.get("audio_base64")
    alignment = response.get("alignment") or response.get("normalized_alignment")
    if not audio_b64 or not alignment:
        raise ApiError(f"{line_id}: response missing audio_base64 or alignment")
    (out_audio / f"{line_id}.mp3").write_bytes(base64.b64decode(audio_b64))
    (out_audio / f"{line_id}.alignment.json").write_text(json.dumps(alignment, indent=2), encoding="utf-8")


def read_api_key() -> str:
    for name in API_KEY_VARS:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    raise ScriptError(
        "ELEVENLABS_API_KEY is not set. Run with: "
        "env $(grep -h '^ELEVENLABS_API_KEY=' .env) python3 generate_lines.py ..."
    )


# ---------- stitching ----------


def stitch_command(files: list[Path], out: Path, gap_ms: int, rate: int, ffmpeg: str) -> list[str]:
    """ffmpeg concat with silence between lines. All inputs resampled to mono at `rate`."""
    fmt = f"aresample={rate},aformat=sample_fmts=fltp:channel_layouts=mono"
    parts: list[str] = []
    labels: list[str] = []
    for index in range(len(files)):
        if index and gap_ms > 0:
            parts.append(f"anullsrc=r={rate}:cl=mono,atrim=duration={gap_ms / 1000:.3f},{fmt}[g{index}]")
            labels.append(f"[g{index}]")
        parts.append(f"[{index}:a]{fmt}[a{index}]")
        labels.append(f"[a{index}]")
    parts.append(f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1[out]")
    inputs = [arg for f in files for arg in ("-i", str(f))]
    return [ffmpeg, "-y", "-v", "error", *inputs, "-filter_complex", ";".join(parts),
            "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "128k", str(out)]


def run_command(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{Path(command[0]).name} failed: {result.stderr.strip()[:ERROR_BODY_CHARS]}")


def stitch_variants(lines, out_audio: Path, gap_ms: int, rate: int, runner=run_command) -> list[dict]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise ScriptError("ffmpeg not found on PATH; install it to stitch variants")
    stitched = []
    for variant in hook_variants(lines) or (1,):
        ordered = variant_order(lines, variant)
        files = [out_audio / f"{l.id}.mp3" for l in ordered]
        missing = [f.name for f in files if not f.exists()]
        if missing:
            print(f"skip variant-v{variant}: missing {', '.join(missing)}", file=sys.stderr)
            continue
        out = out_audio / f"variant-v{variant}.mp3"
        runner(stitch_command(files, out, gap_ms, rate, ffmpeg))
        stitched.append({"variant": variant, "file": out, "lines": [l.id for l in ordered]})
    return stitched


# ---------- manifest and summary ----------


def rel(path: Path, base: Path) -> str:
    return os.path.relpath(path.resolve(), base.resolve())


def manifest_markdown(lines, out_audio: Path, out_manifest: Path, stitched: list[dict], gap_ms: int) -> str:
    rows = ["# Voice Manifest", "", "| id | speaker | file | source | chars |", "|---|---|---|---|---|"]
    for line in lines:
        mp3 = out_audio / f"{line.id}.mp3"
        file_cell = rel(mp3, out_manifest) if mp3.exists() else "(missing)"
        rows.append(f"| {line.id} | {line.speaker} | {file_cell} | made | {len(line.text)} |")
    rows += ["", f"## Stitched variants (gap {gap_ms} ms)", "",
             "| variant | file | lines |", "|---|---|---|"]
    for item in stitched:
        rows.append(f"| v{item['variant']} | {rel(item['file'], out_manifest)} | {', '.join(item['lines'])} |")
    return "\n".join(rows) + "\n"


def summary_text(lines, todo: list[ScriptLine]) -> str:
    by_speaker: dict[str, tuple[int, int]] = {}
    for line in lines:
        count, chars = by_speaker.get(line.speaker, (0, 0))
        by_speaker = {**by_speaker, line.speaker: (count + 1, chars + len(line.text))}
    out = ["speaker      lines   chars"]
    out += [f"{name:<12} {count:>5} {chars:>7}" for name, (count, chars) in sorted(by_speaker.items())]
    out.append(f"{'TOTAL':<12} {len(lines):>5} {sum(len(l.text) for l in lines):>7}")
    out.append(f"variants: {', '.join(f'v{v}' for v in (hook_variants(lines) or (1,)))}")
    out.append(f"to generate: {len(todo)} lines, {sum(len(l.text) for l in todo)} chars "
               f"({', '.join(l.id for l in todo) or 'none'})")
    return "\n".join(out)


def lines_to_generate(lines, out_audio: Path, reroll: frozenset[str]) -> list[ScriptLine]:
    """Listed lines always; other lines only when their audio or alignment is missing."""
    def exists(line: ScriptLine) -> bool:
        return (out_audio / f"{line.id}.mp3").exists() and (out_audio / f"{line.id}.alignment.json").exists()
    return [l for l in lines if l.id in reroll or not exists(l)]


# ---------- CLI ----------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Per-line ElevenLabs takes with alignment, stitched per variant.")
    p.add_argument("--script", required=True, type=Path)
    p.add_argument("--voices", required=True, type=Path)
    p.add_argument("--out-audio", required=True, type=Path)
    p.add_argument("--out-manifest", required=True, type=Path)
    p.add_argument("--lines", help="Comma-separated ids to re-roll, e.g. b-03,h2-01")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--output-format", default=DEFAULT_FORMAT)
    p.add_argument("--gap-ms", type=int, default=DEFAULT_GAP_MS)
    return p


def run(args: argparse.Namespace, post=http_post, sleep=time.sleep, runner=run_command) -> int:
    if args.gap_ms < 0:
        raise ScriptError("--gap-ms must be zero or more")
    try:
        script_text = args.script.read_text(encoding="utf-8")
    except OSError as exc:
        raise ScriptError(f"cannot read script {args.script}: {exc}") from exc
    lines = parse_script(script_text)
    voices = load_voices(args.voices)
    check_voices(lines, voices)
    rate = sample_rate(args.output_format)
    todo = lines_to_generate(lines, args.out_audio, parse_line_ids(args.lines, lines))
    print(summary_text(lines, todo))
    if args.dry_run:
        print("dry run: no API calls made")
        return 0
    api_key = read_api_key() if todo else ""
    args.out_audio.mkdir(parents=True, exist_ok=True)
    args.out_manifest.mkdir(parents=True, exist_ok=True)
    for line in todo:
        print(f"generating {line.id} ({line.speaker}, {len(line.text)} chars)")
        response = tts_with_timestamps(line, voices[line.speaker], api_key, args.output_format, post, sleep)
        save_take(response, line.id, args.out_audio)
    stitched = stitch_variants(lines, args.out_audio, args.gap_ms, rate, runner)
    manifest = args.out_manifest / "voice-manifest.md"
    manifest.write_text(manifest_markdown(lines, args.out_audio, args.out_manifest, stitched, args.gap_ms),
                        encoding="utf-8")
    print(f"wrote {manifest}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except (ScriptError, ApiError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
