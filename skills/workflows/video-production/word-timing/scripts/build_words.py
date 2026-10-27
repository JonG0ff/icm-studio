#!/usr/bin/env python3
"""Build word-level timing (words.json) for one script variant.

Mode A, made audio: per-line ElevenLabs alignment + ffprobe durations,
offset to match the stitched variant (hook N lines, then body, gap between).
Mode B, brought audio: Whisper word timestamps on a full track, aligned to
script lines in order with fuzzy matching, re-spelled to the script.

Usage:
    python3 build_words.py --script script.md --audio-dir audio/ --variant 1 --out words.json
    python3 build_words.py --script script.md --track full.wav --variant 1 --out words.json \
        [--split-lines lines/] [--whisper-model medium.en]
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

DEFAULT_GAP_MS = 150
DEFAULT_WHISPER_MODEL = "medium.en"
FALLBACK_WHISPER = Path.home() / ".local" / "bin" / "whisper"
FUZZY_WORD_RATIO = 0.6
LINE_FOUND_RATIO = 0.5
SPLIT_PAD_SECONDS = 0.05
LINE_RE = re.compile(r"^\[(h\d+-\d{2}|b-\d{2})\] ([A-Z][A-Z0-9_]*): (.+)$")
ID_LIKE_RE = re.compile(r"^\[(h\d|b-)")
TAG_RE = re.compile(r"\[[^\]]*\]")
NORMALIZE_RE = re.compile(r"[^a-z0-9]+")


class TimingError(ValueError):
    """Input problem the user must fix."""


@dataclass(frozen=True)
class ScriptLine:
    id: str
    speaker: str
    text: str

    @property
    def hook_variant(self) -> int | None:
        return int(self.id[1:].split("-")[0]) if self.id.startswith("h") else None

    @property
    def words(self) -> tuple[str, ...]:
        return tuple(TAG_RE.sub(" ", self.text).split())


@dataclass(frozen=True)
class LineResult:
    line: ScriptLine
    found: bool
    start: float | None
    end: float | None
    words: tuple[dict, ...]
    notes: tuple[str, ...] = ()


# ---------- script (same contract as generate_lines.py) ----------


def parse_script(text: str) -> tuple[ScriptLine, ...]:
    lines: list[ScriptLine] = []
    seen: set[str] = set()
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        match = LINE_RE.match(stripped)
        if not match:
            if ID_LIKE_RE.match(stripped):
                raise TimingError(f"line {number}: malformed script line: {stripped!r}")
            continue
        if match.group(1) in seen:
            raise TimingError(f"line {number}: duplicate id {match.group(1)}")
        seen.add(match.group(1))
        lines.append(ScriptLine(match.group(1), match.group(2), match.group(3).strip()))
    if not lines:
        raise TimingError("script has no spoken lines in `[id] SPEAKER: text` form")
    return tuple(lines)


def variant_order(lines: tuple[ScriptLine, ...], variant: int) -> tuple[ScriptLine, ...]:
    variants = sorted({l.hook_variant for l in lines if l.hook_variant is not None})
    body = tuple(l for l in lines if l.hook_variant is None)
    if not variants:
        if variant != 1:
            raise TimingError(f"script has no hook lines; only variant 1 exists, got {variant}")
        return body
    if variant not in variants:
        raise TimingError(f"variant {variant} not in script; hooks found: {variants}")
    return tuple(l for l in lines if l.hook_variant == variant) + body


# ---------- shared helpers ----------


def normalize(word: str) -> str:
    return NORMALIZE_RE.sub("", word.lower().replace("'", "").replace("’", ""))


def word_entry(word: str, start: float, end: float, line: ScriptLine) -> dict:
    return {"word": word, "start": round(start, 3), "end": round(end, 3),
            "speaker": line.speaker, "line": line.id}


def ffprobe_duration(path: Path) -> float:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise TimingError("ffprobe not found on PATH")
    result = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration",
                             "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    if result.returncode != 0:
        raise TimingError(f"ffprobe failed on {path}: {result.stderr.strip()[:200]}")
    return float(result.stdout.strip())


# ---------- Mode A: made audio ----------


def alignment_to_words(alignment: dict, offset: float, line: ScriptLine) -> tuple[dict, ...]:
    """Group character timings into words. Skips [audio tags] and whitespace."""
    chars = alignment.get("characters") or []
    starts = alignment.get("character_start_times_seconds") or []
    ends = alignment.get("character_end_times_seconds") or []
    if not (len(chars) == len(starts) == len(ends)):
        raise TimingError(f"{line.id}: alignment arrays have different lengths")
    words: list[dict] = []
    current: list[int] = []
    depth = 0
    for index, char in enumerate(chars + [" "]):
        if char == "[":
            depth += 1
        is_break = depth > 0 or char.isspace()
        if char == "]":
            depth = max(0, depth - 1)
        if is_break:
            if current:
                text = "".join(chars[i] for i in current)
                words.append(word_entry(text, offset + starts[current[0]], offset + ends[current[-1]], line))
                current = []
            continue
        current.append(index)
    return tuple(words)


def build_made(lines: tuple[ScriptLine, ...], audio_dir: Path, gap_ms: int, probe=ffprobe_duration):
    results: list[LineResult] = []
    offset = 0.0
    for index, line in enumerate(lines):
        mp3 = audio_dir / f"{line.id}.mp3"
        if not mp3.exists():
            raise TimingError(f"missing {mp3}; generate it before timing (offsets depend on it)")
        if index:
            offset += gap_ms / 1000
        duration = probe(mp3)
        align_path = audio_dir / f"{line.id}.alignment.json"
        if align_path.exists():
            alignment = json.loads(align_path.read_text(encoding="utf-8"))
            words = alignment_to_words(alignment, offset, line)
            results.append(LineResult(line, True, round(offset, 3), round(offset + duration, 3), words))
        else:
            results.append(LineResult(line, False, None, None, (), (f"missing {align_path.name}",)))
        offset += duration
    return tuple(results), round(offset, 3)


# ---------- Mode B: brought audio ----------


def find_whisper(explicit: str | None) -> str:
    candidate = explicit or shutil.which("whisper") or (str(FALLBACK_WHISPER) if FALLBACK_WHISPER.exists() else None)
    if not candidate:
        raise TimingError("whisper CLI not found; install openai-whisper or pass --whisper-bin")
    return candidate


def run_whisper(track: Path, model: str, whisper_bin: str) -> list[dict]:
    """Run the Whisper CLI and return [{word, start, end}]. Isolated so tests can mock it."""
    with tempfile.TemporaryDirectory(prefix="word-timing-") as tmp:
        command = [whisper_bin, str(track), "--model", model, "--word_timestamps", "True",
                   "--output_format", "json", "--output_dir", tmp, "--fp16", "False", "--verbose", "False"]
        if model.endswith(".en"):
            command += ["--language", "en"]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise TimingError(f"whisper failed: {result.stderr.strip()[-300:]}")
        data = json.loads((Path(tmp) / f"{track.stem}.json").read_text(encoding="utf-8"))
    return [{"word": w["word"].strip(), "start": float(w["start"]), "end": float(w["end"])}
            for seg in data.get("segments", []) for w in seg.get("words", []) if w.get("word", "").strip()]


def map_script_to_heard(script_norm: list[str], heard_norm: list[str]) -> dict[int, tuple[int, bool]]:
    """Map script word index -> (heard index, exact_or_fuzzy) via sequence alignment."""
    mapping: dict[int, tuple[int, bool]] = {}
    matcher = difflib.SequenceMatcher(None, script_norm, heard_norm, autojunk=False)
    for tag, s1, s2, h1, h2 in matcher.get_opcodes():
        if tag == "equal":
            mapping.update({s1 + k: (h1 + k, True) for k in range(s2 - s1)})
        elif tag == "replace":
            for k in range(s2 - s1):
                h = h1 + min(k * (h2 - h1) // (s2 - s1), h2 - h1 - 1)
                close = difflib.SequenceMatcher(None, script_norm[s1 + k], heard_norm[h]).ratio()
                mapping[s1 + k] = (h, close >= FUZZY_WORD_RATIO)
    return mapping


def fill_gaps(times: list[tuple[float, float] | None]) -> list[tuple[float, float]]:
    """Give unmatched words a slice of the time between their matched neighbours."""
    filled = list(times)
    index = 0
    while index < len(filled):
        if filled[index] is not None:
            index += 1
            continue
        run_end = index
        while run_end < len(filled) and filled[run_end] is None:
            run_end += 1
        left = filled[index - 1][1] if index > 0 else filled[run_end][0]
        right = filled[run_end][0] if run_end < len(filled) else left
        step = max(0.0, right - left) / (run_end - index)
        for k in range(index, run_end):
            filled[k] = (left + step * (k - index), left + step * (k - index + 1))
        index = run_end
    return filled


def align_line(line, indices, mapping, heard, script_norm) -> LineResult:
    hits = [mapping.get(i) for i in indices]
    good = sum(1 for hit in hits if hit and hit[1])
    if not indices or good / len(indices) < LINE_FOUND_RATIO:
        return LineResult(line, False, None, None, (), (f"matched {good}/{len(indices)} words",))
    notes = tuple(f"script '{line.words[k]}' heard '{heard[hit[0]]['word']}'"
                  for k, hit in enumerate(hits) if hit and script_norm[indices[k]] != normalize(heard[hit[0]]["word"]))
    missing = tuple(f"script '{line.words[k]}' not heard" for k, hit in enumerate(hits) if hit is None)
    times = fill_gaps([(heard[h[0]]["start"], heard[h[0]]["end"]) if h else None for h in hits])
    words = tuple(word_entry(w, s, e, line) for w, (s, e) in zip(line.words, times))
    return LineResult(line, True, words[0]["start"], words[-1]["end"], words, notes + missing)


def align_lines(lines: tuple[ScriptLine, ...], heard: list[dict]) -> tuple[LineResult, ...]:
    owners = [(line_index, word) for line_index, line in enumerate(lines) for word in line.words]
    script_norm = [normalize(word) for _, word in owners]
    mapping = map_script_to_heard(script_norm, [normalize(w["word"]) for w in heard])
    results = []
    for line_index, line in enumerate(lines):
        indices = [i for i, (owner, _) in enumerate(owners) if owner == line_index]
        results.append(align_line(line, indices, mapping, heard, script_norm))
    return tuple(results)


def split_lines(track: Path, results: tuple[LineResult, ...], out_dir: Path, duration: float) -> list[Path]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise TimingError("ffmpeg not found on PATH; needed for --split-lines")
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for result in (r for r in results if r.found):
        start = max(0.0, result.start - SPLIT_PAD_SECONDS)
        end = min(duration, result.end + SPLIT_PAD_SECONDS)
        target = out_dir / f"{result.line.id}.wav"
        command = [ffmpeg, "-y", "-v", "error", "-i", str(track), "-ss", f"{start:.3f}", "-to", f"{end:.3f}", str(target)]
        proc = subprocess.run(command, capture_output=True, text=True)
        if proc.returncode != 0:
            raise TimingError(f"ffmpeg split failed for {result.line.id}: {proc.stderr.strip()[:200]}")
        written.append(target)
    return written


# ---------- outputs ----------


def wpm(word_count: int, seconds: float | None) -> str:
    return f"{word_count / seconds * 60:.0f}" if seconds and seconds > 0 else "-"


def report_markdown(mode: str, variant: int, duration: float, results: tuple[LineResult, ...]) -> str:
    total_words = sum(len(r.words) for r in results)
    found = sum(1 for r in results if r.found)
    out = ["# Timing Report", "", f"- Mode: {mode}", f"- Variant: {variant}",
           f"- Total duration: {duration:.2f} s", f"- Lines found: {found}/{len(results)}",
           f"- Words: {total_words}", f"- Words per minute: {wpm(total_words, duration)}", "",
           "| id | speaker | status | start | end | words | wpm | notes |", "|---|---|---|---|---|---|---|---|"]
    for r in results:
        span = (r.end - r.start) if r.found else None
        cells = [r.line.id, r.line.speaker, "found" if r.found else "NOT FOUND",
                 f"{r.start:.2f}" if r.found else "-", f"{r.end:.2f}" if r.found else "-",
                 str(len(r.words)), wpm(len(r.words), span), "; ".join(r.notes) or "-"]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def words_payload(variant: int, duration: float, results: tuple[LineResult, ...]) -> dict:
    return {
        "variant": variant,
        "duration": duration,
        "lines": [{"id": r.line.id, "speaker": r.line.speaker, "found": r.found, "start": r.start, "end": r.end}
                  for r in results],
        "words": [w for r in results for w in r.words],
    }


# ---------- CLI ----------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Word-level timing for one script variant.")
    p.add_argument("--script", required=True, type=Path)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--audio-dir", type=Path, help="Mode A: dir with <id>.mp3 and <id>.alignment.json")
    source.add_argument("--track", type=Path, help="Mode B: full recorded track (wav/mp3)")
    p.add_argument("--variant", type=int, default=1)
    p.add_argument("--gap-ms", type=int, default=DEFAULT_GAP_MS, help="Mode A only; match generate_lines.py")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--report", type=Path, help="Default: timing-report.md next to --out")
    p.add_argument("--whisper-model", default=DEFAULT_WHISPER_MODEL)
    p.add_argument("--whisper-bin")
    p.add_argument("--split-lines", type=Path, help="Mode B only: write <id>.wav per found line here")
    return p


def run(args: argparse.Namespace, whisper=run_whisper, probe=ffprobe_duration) -> int:
    if args.gap_ms < 0:
        raise TimingError("--gap-ms must be zero or more")
    if args.split_lines and not args.track:
        raise TimingError("--split-lines needs --track (Mode B); Mode A already has per-line files")
    try:
        lines = variant_order(parse_script(args.script.read_text(encoding="utf-8")), args.variant)
    except OSError as exc:
        raise TimingError(f"cannot read script {args.script}: {exc}") from exc
    if args.audio_dir:
        mode = "A (made audio)"
        results, duration = build_made(lines, args.audio_dir, args.gap_ms, probe)
    else:
        if not args.track.exists():
            raise TimingError(f"track not found: {args.track}")
        mode = "B (brought audio)"
        heard = whisper(args.track, args.whisper_model, find_whisper(args.whisper_bin))
        results, duration = align_lines(lines, heard), round(probe(args.track), 3)
        if args.split_lines:
            split_lines(args.track, results, args.split_lines, duration)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(words_payload(args.variant, duration, results), indent=2), encoding="utf-8")
    report = args.report or args.out.with_name("timing-report.md")
    report.write_text(report_markdown(mode, args.variant, duration, results), encoding="utf-8")
    missing = [r.line.id for r in results if not r.found]
    print(f"wrote {args.out} and {report}; lines not found: {', '.join(missing) or 'none'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except TimingError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
