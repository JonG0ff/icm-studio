#!/usr/bin/env python3
"""Acquire and promote Swipe Engine reference context packages."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import uuid
from math import ceil
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 3
SOCIAL_HOSTS = {
    "instagram.com",
    "www.instagram.com",
    "tiktok.com",
    "www.tiktok.com",
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "vimeo.com",
    "www.vimeo.com",
    "x.com",
    "twitter.com",
}
IMAGE_EXTENSIONS = {".avif", ".gif", ".heic", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
VIDEO_EXTENSIONS = {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".webm"}
AUDIO_EXTENSIONS = {".aac", ".aiff", ".flac", ".m4a", ".mp3", ".ogg", ".opus", ".wav"}
MEDIA_SOURCE_TYPES = {"audio", "video", "social-video"}


class IntakeError(RuntimeError):
    pass


def repo_root() -> Path:
    override = os.environ.get("SWIPE_ENGINE_REPO_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[4]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def valid_slug(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise IntakeError("slug must be lowercase kebab-case")
    return value


def validate_handoff(
    handoff_path: Path,
    *,
    expected_stage: str,
    expected_slug: str,
    expected_state: str | None = None,
    root: Path,
) -> dict[str, Any]:
    """Validate the small, tracked Markdown contract between stages."""
    if not handoff_path.is_file():
        raise IntakeError(f"stage handoff is missing: {repo_relative(handoff_path, root)}")
    text = handoff_path.read_text(encoding="utf-8")
    fields: dict[str, str] = {}
    for field in ("slug", "stage", "state", "completed-at", "next-action", "user-response"):
        match = re.search(rf"^- {re.escape(field)}:\s*(.+?)\s*$", text, flags=re.MULTILINE)
        if not match:
            raise IntakeError(
                f"stage handoff is missing '- {field}:' in {repo_relative(handoff_path, root)}"
            )
        fields[field] = match.group(1)
    if fields["slug"] != expected_slug:
        raise IntakeError(
            f"stage handoff slug mismatch: expected {expected_slug}, got {fields['slug']}"
        )
    if fields["stage"] != expected_stage:
        raise IntakeError(
            f"stage handoff stage mismatch: expected {expected_stage}, got {fields['stage']}"
        )
    if expected_state and fields["state"] != expected_state:
        raise IntakeError(
            f"stage handoff state mismatch: expected {expected_state}, got {fields['state']}"
        )
    for section in ("## Completed", "## Artifacts", "## Visual inspection", "## Warnings or blockers"):
        if section.lower() not in text.lower():
            raise IntakeError(
                f"stage handoff is missing '{section}' in {repo_relative(handoff_path, root)}"
            )
    return {
        "status": "valid",
        "handoff": repo_relative(handoff_path, root),
        "slug": fields["slug"],
        "stage": fields["stage"],
        "state": fields["state"],
    }


def repo_relative(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise IntakeError(f"artifact escaped repository root: {resolved}") from exc


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{uuid.uuid4().hex}")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def recorded_source(source: str, root: Path) -> str:
    if is_url(source):
        return source
    resolved = Path(source).expanduser().resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return f"external-file:{resolved.name}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def require_command(name: str) -> str:
    command = shutil.which(name)
    if not command:
        raise IntakeError(f"missing required command: {name}")
    return command


def is_url(source: str) -> bool:
    return urllib.parse.urlparse(source).scheme in {"http", "https"}


def remote_content_type(source: str) -> str:
    request = urllib.request.Request(
        source,
        method="HEAD",
        headers={"User-Agent": "Mozilla/5.0 SwipeEngineReferenceIntake/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.headers.get_content_type().lower()
    except Exception:
        return ""


def classify(source: str, captured_file: str | None, override: str | None) -> str:
    if override:
        return override
    if captured_file:
        return "webpage"
    if is_url(source):
        parsed = urllib.parse.urlparse(source)
        host = parsed.netloc.lower().split(":")[0]
        extension = Path(parsed.path).suffix.lower()
        if host in SOCIAL_HOSTS:
            return "social-video"
        if extension in IMAGE_EXTENSIONS:
            return "image"
        if extension == ".pdf":
            return "pdf"
        if extension in VIDEO_EXTENSIONS:
            return "video"
        content_type = remote_content_type(source)
        if content_type.startswith("image/"):
            return "image"
        if content_type == "application/pdf":
            return "pdf"
        if content_type.startswith("video/"):
            return "video"
        if content_type.startswith("audio/"):
            return "audio"
        return "webpage"
    path = Path(source).expanduser()
    if not path.is_file():
        raise IntakeError(f"source file does not exist: {path}")
    extension = path.suffix.lower()
    if extension in IMAGE_EXTENSIONS:
        return "image"
    if extension == ".pdf":
        return "pdf"
    if extension in VIDEO_EXTENSIONS:
        return "video"
    if extension in AUDIO_EXTENSIONS:
        return "audio"
    guessed = mimetypes.guess_type(path.name)[0] or ""
    if guessed.startswith("image/"):
        return "image"
    if guessed.startswith("video/"):
        return "video"
    if guessed.startswith("audio/"):
        return "audio"
    raise IntakeError(f"unsupported local file type: {path.suffix or 'unknown'}")


def download_direct(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 SwipeEngineReferenceIntake/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=45) as response, destination.open("wb") as output:
            shutil.copyfileobj(response, output)
    except Exception as exc:
        raise IntakeError(f"failed to download {url}: {exc}") from exc


def copy_or_download(source: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if is_url(source):
        download_direct(source, destination)
    else:
        shutil.copy2(Path(source).expanduser().resolve(), destination)


def add_file(records: list[dict[str, Any]], path: Path, role: str, persist: bool, root: Path) -> None:
    records.append(
        {
            "path": repo_relative(path, root),
            "role": role,
            "mime_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "persist": persist,
        }
    )


def find_duplicate(root: Path, source_hash: str, exclude: Path | None = None) -> str | None:
    locations = [
        root / "libraries/swipes/stages/01-save/output/assets",
        root / "libraries/swipes/knowledge-layer/assets",
    ]
    for location in locations:
        if not location.exists():
            continue
        for manifest_path in location.glob("*/manifest.json"):
            if exclude and manifest_path.resolve() == exclude.resolve():
                continue
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if manifest.get("source_hash") == source_hash:
                return repo_relative(manifest_path, root)
    return None


def extract_pdf_text(source: Path, output: Path, warnings: list[str], tools: list[str]) -> bool:
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        result = run([pdftotext, str(source), str(output)])
        if result.returncode == 0 and output.exists():
            tools.append("pdftotext")
            return True
        warnings.append(f"pdftotext failed: {(result.stderr or result.stdout).strip()}")
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(source))
        text = "\n\n".join((page.extract_text() or "") for page in reader.pages)
        output.write_text(text, encoding="utf-8")
        tools.append("pypdf")
        return True
    except (ImportError, OSError, ValueError) as exc:
        warnings.append(f"PDF text extraction unavailable: install pdftotext or pypdf ({exc})")
        return False


def render_pdf(source: Path, context: Path, warnings: list[str], tools: list[str]) -> list[Path]:
    context.mkdir(parents=True, exist_ok=True)
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm:
        prefix = context / "page"
        result = run([pdftoppm, "-png", "-r", "150", str(source), str(prefix)])
        pages = sorted(context.glob("page-*.png"))
        if result.returncode == 0 and pages:
            tools.append("pdftoppm")
            return pages
        warnings.append(f"pdftoppm failed: {(result.stderr or result.stdout).strip()}")
    qlmanage = shutil.which("qlmanage")
    if qlmanage:
        result = run([qlmanage, "-t", "-s", "1800", "-o", str(context), str(source)])
        pages = sorted(context.glob("*.png"))
        if result.returncode == 0 and pages:
            tools.append("qlmanage")
            warnings.append("PDF renderer produced a preview only; install pdftoppm for every page")
            return pages
        warnings.append(f"qlmanage failed: {(result.stderr or result.stdout).strip()}")
    raise IntakeError("missing PDF renderer: install pdftoppm (preferred) or provide qlmanage")


def probe_media(source: Path, output: Path, tools: list[str]) -> dict[str, Any]:
    ffprobe = require_command("ffprobe")
    result = run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration,size,format_name:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
            "-of",
            "json",
            str(source),
        ]
    )
    if result.returncode != 0:
        raise IntakeError(f"ffprobe failed: {(result.stderr or result.stdout).strip()}")
    data = json.loads(result.stdout)
    output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tools.append("ffprobe")
    return data


def media_duration(probe: dict[str, Any]) -> float:
    try:
        return max(float(probe.get("format", {}).get("duration", 0)), 0.0)
    except (TypeError, ValueError):
        return 0.0


def format_timestamp(seconds: float) -> str:
    seconds = max(seconds, 0.0)
    minutes, remainder = divmod(seconds, 60)
    hours, minutes = divmod(int(minutes), 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{remainder:05.2f}"
    return f"{minutes:02d}:{remainder:05.2f}"


def timestamp_slug(seconds: float) -> str:
    return f"{max(seconds, 0.0):08.2f}s".replace(".", "p")


def media_streams(probe: dict[str, Any], codec_type: str) -> list[dict[str, Any]]:
    return [stream for stream in probe.get("streams", []) if stream.get("codec_type") == codec_type]


def sampled_times(duration: float, limit: int = 12) -> list[float]:
    if duration <= 0:
        return [0.0]
    count = min(limit, max(1, ceil(duration / 0.5)))
    if count == 1:
        return [0.0]
    # Container duration can extend slightly past the last decodable video frame.
    # Leave enough room for FFmpeg to seek and decode the final sample reliably.
    usable_end = max(duration - 0.25, 0.0)
    return [round((usable_end / (count - 1)) * index, 2) for index in range(count)]


def extract_timestamped_frames(source: Path, context: Path, duration: float, warnings: list[str], tools: list[str]) -> list[dict[str, Any]]:
    ffmpeg = require_command("ffmpeg")
    frames_dir = context / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    frame_entries: list[dict[str, Any]] = []
    for index, timestamp in enumerate(sampled_times(duration), start=1):
        frame = frames_dir / f"frame_{index:04d}_{timestamp_slug(timestamp)}.jpg"
        result = run(
            [
                ffmpeg,
                "-v",
                "error",
                "-ss",
                f"{timestamp:.2f}",
                "-i",
                str(source),
                "-frames:v",
                "1",
                "-vf",
                "scale='min(1280,iw)':-2",
                "-q:v",
                "2",
                str(frame),
            ]
        )
        if result.returncode == 0 and frame.exists():
            frame_entries.append(
                {
                    "index": index,
                    "time": timestamp,
                    "time_label": format_timestamp(timestamp),
                    "path": frame,
                    "artifact": frame.relative_to(context).as_posix(),
                }
            )
        else:
            warnings.append(f"frame extraction failed at {timestamp:.2f}s: {(result.stderr or result.stdout).strip()}")
    if not frame_entries:
        raise IntakeError("ffmpeg frame extraction failed: no sampled frames produced")
    tools.append("ffmpeg")
    return frame_entries


def write_frame_index(frame_entries: list[dict[str, Any]], output: Path) -> None:
    lines = [
        "# Frame Index",
        "",
        "| Frame | Timestamp | Artifact |",
        "|---|---:|---|",
    ]
    for entry in frame_entries:
        lines.append(f"| {entry['index']} | {entry['time_label']} | {entry['artifact']} |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def image_delta(left: Path, right: Path) -> float | None:
    try:
        from PIL import Image, ImageChops, ImageStat  # type: ignore
    except ImportError:
        return None
    with Image.open(left) as left_image, Image.open(right) as right_image:
        left_rgb = left_image.convert("RGB").resize((96, 54))
        right_rgb = right_image.convert("RGB").resize((96, 54))
        diff = ImageChops.difference(left_rgb, right_rgb)
        stat = ImageStat.Stat(diff)
        return sum(stat.mean) / len(stat.mean)


def motion_level(delta: float | None) -> str:
    if delta is None:
        return "unknown"
    if delta < 4:
        return "low"
    if delta < 16:
        return "medium"
    return "high"


def build_motion_events(frame_entries: list[dict[str, Any]], warnings: list[str]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    missing_pil = False
    for previous, current in zip(frame_entries, frame_entries[1:]):
        delta = image_delta(previous["path"], current["path"])
        if delta is None:
            missing_pil = True
        events.append(
            {
                "from": previous["time_label"],
                "to": current["time_label"],
                "delta": None if delta is None else round(delta, 2),
                "level": motion_level(delta),
            }
        )
    if missing_pil:
        warnings.append("motion index used timestamp intervals only: missing Python package PIL")
    return events


def write_motion_index(events: list[dict[str, Any]], output: Path) -> None:
    lines = [
        "# Motion Index",
        "",
        "| From | To | Visual delta | Motion |",
        "|---:|---:|---:|---|",
    ]
    if not events:
        lines.append("| none | none | none | single sampled frame |")
    for event in events:
        delta = "unknown" if event["delta"] is None else f"{event['delta']:.2f}"
        lines.append(f"| {event['from']} | {event['to']} | {delta} | {event['level']} |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def scene_candidates(frame_entries: list[dict[str, Any]], motion_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    if frame_entries:
        candidates.append(
            {
                "time": frame_entries[0]["time_label"],
                "frame": frame_entries[0]["artifact"],
                "reason": "opening frame",
            }
        )
    for event, frame in zip(motion_events, frame_entries[1:]):
        delta = event.get("delta")
        if isinstance(delta, (int, float)) and delta >= 16:
            candidates.append(
                {
                    "time": event["to"],
                    "frame": frame["artifact"],
                    "reason": f"high visual delta ({delta:.2f})",
                }
            )
    return candidates


def write_scene_index(candidates: list[dict[str, Any]], output: Path) -> None:
    lines = [
        "# Scene Index",
        "",
        "| Timestamp | Frame | Reason |",
        "|---:|---|---|",
    ]
    for candidate in candidates:
        lines.append(f"| {candidate['time']} | {candidate['frame']} | {candidate['reason']} |")
    if len(candidates) <= 1:
        lines.append("| none observed | sampled frames | no large sampled-frame scene change detected |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_contact_sheet(frame_entries: list[dict[str, Any]], output: Path, warnings: list[str]) -> bool:
    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
    except ImportError:
        warnings.append("labeled contact sheet unavailable: missing Python package PIL")
        return False
    if not frame_entries:
        return False
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.LANCZOS
    columns = 4
    thumb_width = 320
    label_height = 30
    padding = 8
    thumbnails: list[tuple[Any, str]] = []
    for entry in frame_entries:
        with Image.open(entry["path"]) as image:
            frame = image.convert("RGB")
            frame.thumbnail((thumb_width, 220), resample)
            thumbnails.append((frame.copy(), f"{entry['index']:02d}  {entry['time_label']}"))
    thumb_height = max(frame.height for frame, _label in thumbnails)
    rows = ceil(len(thumbnails) / columns)
    sheet_width = columns * thumb_width + (columns + 1) * padding
    sheet_height = rows * (thumb_height + label_height) + (rows + 1) * padding
    sheet = Image.new("RGB", (sheet_width, sheet_height), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, (frame, label) in enumerate(thumbnails):
        column = index % columns
        row = index // columns
        x = padding + column * (thumb_width + padding)
        y = padding + row * (thumb_height + label_height + padding)
        draw.text((x, y), label, fill=(20, 20, 20), font=font)
        sheet.paste(frame, (x, y + label_height))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=92)
    return output.exists()


def write_ocr_text(frame_entries: list[dict[str, Any]], context: Path, warnings: list[str], tools: list[str]) -> Path | None:
    tesseract = shutil.which("tesseract")
    if not tesseract:
        warnings.append("optional OCR unavailable: missing command tesseract")
        return None
    lines = ["# On-Screen Text", ""]
    found_text = False
    for entry in frame_entries:
        result = run([tesseract, str(entry["path"]), "stdout", "--psm", "6"])
        text = result.stdout.strip()
        if result.returncode == 0 and text:
            found_text = True
            lines.extend([f"## {entry['time_label']}", "", text, ""])
    if not found_text:
        lines.append("No OCR text detected in sampled frames.")
    output = context / "on-screen-text.md"
    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    tools.append("tesseract")
    return output


def parse_whisper_json(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data.get("text"), str):
        return data["text"].strip()
    segments = data.get("segments")
    if isinstance(segments, list):
        return " ".join(str(segment.get("text", "")).strip() for segment in segments).strip()
    return ""


def read_transcript_text(paths: list[Path]) -> str:
    for path in paths:
        try:
            if path.suffix.lower() == ".json":
                text = parse_whisper_json(path)
            else:
                text = path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if text:
            return text
    return ""


def acquire_transcript(
    source: Path,
    context: Path,
    records: list[dict[str, Any]],
    root: Path,
    warnings: list[str],
    tools: list[str],
    transcript_file: str | None,
) -> tuple[list[Path], str]:
    transcript_dir = context / "transcript"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    transcript_paths: list[Path] = []
    if transcript_file:
        provided = Path(transcript_file).expanduser().resolve()
        if not provided.is_file():
            raise IntakeError(f"transcript file does not exist: {provided}")
        suffix = provided.suffix.lower() or ".txt"
        target = transcript_dir / f"provided-transcript{suffix}"
        shutil.copy2(provided, target)
        transcript_paths.append(target)
        tools.append("provided-transcript")
    else:
        whisper = shutil.which("whisper")
        if whisper:
            transcription = run([whisper, str(source), "--output_dir", str(transcript_dir), "--output_format", "all"])
            transcript_paths = sorted(
                path
                for path in transcript_dir.glob("*")
                if path.suffix.lower() in {".json", ".md", ".srt", ".tsv", ".txt", ".vtt"}
            )
            if transcription.returncode == 0 and transcript_paths:
                tools.append("whisper")
            else:
                warnings.append(f"optional Whisper transcription failed: {(transcription.stderr or transcription.stdout).strip()}")
                transcript_paths = []
        else:
            warnings.append("optional transcript unavailable: missing command whisper")
    for path in transcript_paths:
        add_file(records, path, "transcript", True, root)
    ordered = sorted(transcript_paths, key=lambda path: (path.suffix.lower() != ".txt", path.name))
    return transcript_paths, read_transcript_text(ordered)


def parse_volume_stats(output: str) -> dict[str, str]:
    stats: dict[str, str] = {}
    for line in output.splitlines():
        match = re.search(r"(mean_volume|max_volume):\s*(-?\d+(?:\.\d+)?) dB", line)
        if match:
            stats[match.group(1)] = f"{match.group(2)} dB"
    return stats


def parse_silence_events(output: str) -> list[dict[str, float]]:
    events: list[dict[str, float]] = []
    current: dict[str, float] | None = None
    for line in output.splitlines():
        start = re.search(r"silence_start:\s*(\d+(?:\.\d+)?)", line)
        if start:
            current = {"start": float(start.group(1))}
            events.append(current)
            continue
        end = re.search(r"silence_end:\s*(\d+(?:\.\d+)?)\s*\|\s*silence_duration:\s*(\d+(?:\.\d+)?)", line)
        if end:
            target = current or {}
            target["end"] = float(end.group(1))
            target["duration"] = float(end.group(2))
            if current is None:
                events.append(target)
            current = None
    return events


def write_audio_profile(source: Path, context: Path, probe: dict[str, Any], warnings: list[str], tools: list[str]) -> tuple[Path, dict[str, Any]]:
    ffmpeg = require_command("ffmpeg")
    audio_streams = media_streams(probe, "audio")
    profile: dict[str, Any] = {
        "duration_seconds": round(media_duration(probe), 3),
        "audio_streams": audio_streams,
        "video_streams": media_streams(probe, "video"),
        "volume": {},
        "silence_events": [],
    }
    if audio_streams:
        volume = run([ffmpeg, "-v", "info", "-i", str(source), "-af", "volumedetect", "-f", "null", "-"])
        if volume.returncode == 0:
            profile["volume"] = parse_volume_stats(volume.stderr or volume.stdout)
        else:
            warnings.append(f"audio volume profiling failed: {(volume.stderr or volume.stdout).strip()}")
        silence = run([ffmpeg, "-v", "info", "-i", str(source), "-af", "silencedetect=n=-35dB:d=0.5", "-f", "null", "-"])
        if silence.returncode == 0:
            profile["silence_events"] = parse_silence_events(silence.stderr or silence.stdout)
        else:
            warnings.append(f"audio silence profiling failed: {(silence.stderr or silence.stdout).strip()}")
        tools.append("ffmpeg")
    else:
        warnings.append("audio profile has no audio stream to inspect")
    output = context / "audio-profile.json"
    output.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    return output, profile


def transcript_hook(transcript_text: str) -> str:
    compact = " ".join(transcript_text.split())
    if not compact:
        return "(none available)"
    return compact[:220] + ("..." if len(compact) > 220 else "")


def transcript_ctas(transcript_text: str) -> list[str]:
    if not transcript_text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", " ".join(transcript_text.split()))
    cta_terms = ("book", "buy", "call", "click", "comment", "dm", "download", "follow", "get", "learn more", "subscribe", "visit")
    matches = [sentence for sentence in sentences if any(term in sentence.lower() for term in cta_terms)]
    return matches[:5]


def write_media_timeline(
    context: Path,
    duration: float,
    frame_entries: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    motion_events: list[dict[str, Any]],
    transcript_text: str,
) -> Path:
    scene_times = {candidate["time"]: candidate["reason"] for candidate in candidates}
    motion_by_end = {event["to"]: event["level"] for event in motion_events}
    transcript_note = transcript_hook(transcript_text)
    lines = [
        "# Media Timeline",
        "",
        f"- duration: {format_timestamp(duration)}",
        f"- transcript preview: {transcript_note}",
        "",
        "| Timestamp | Visual artifact | Scene candidate | Motion | Audio note |",
        "|---:|---|---|---|---|",
    ]
    if frame_entries:
        for entry in frame_entries:
            label = entry["time_label"]
            lines.append(
                f"| {label} | {entry['artifact']} | {scene_times.get(label, '')} | {motion_by_end.get(label, '')} | inspect transcript/audio profile |"
            )
    else:
        lines.append("| audio-only | none | none | none | inspect transcript/audio profile |")
    output = context / "media-timeline.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def write_media_analysis(
    context: Path,
    source_type: str,
    duration: float,
    frame_entries: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    motion_events: list[dict[str, Any]],
    transcript_text: str,
    audio_profile: dict[str, Any],
    ocr_text: str,
) -> Path:
    motion_counts: dict[str, int] = {}
    for event in motion_events:
        motion_counts[event["level"]] = motion_counts.get(event["level"], 0) + 1
    ctas = transcript_ctas(transcript_text)
    volume = audio_profile.get("volume") or {}
    lines = [
        "# Media Analysis Draft",
        "",
        f"- source-type: {source_type}",
        f"- duration: {format_timestamp(duration)}",
        "- status: draft-for-stage-02-review",
        "",
        "## Video",
    ]
    if frame_entries:
        lines.extend(
            [
                f"- sampled frames: {len(frame_entries)}",
                f"- scene candidates: {len(candidates)}",
                f"- motion summary: {', '.join(f'{key}={value}' for key, value in sorted(motion_counts.items())) or 'none'}",
                f"- on-screen text: {ocr_text or '(OCR unavailable or no text detected)'}",
            ]
        )
    else:
        lines.append("- none observed; source is audio-only")
    lines.extend(
        [
            "",
            "## Audio",
            f"- audio streams: {len(audio_profile.get('audio_streams') or [])}",
            f"- volume: mean {volume.get('mean_volume', '(unknown)')}, max {volume.get('max_volume', '(unknown)')}",
            f"- transcript hook: {transcript_hook(transcript_text)}",
            f"- spoken CTA candidates: {', '.join(ctas) if ctas else '(none detected)'}",
            "- tone/music: review transcript, audio profile, and source playback if needed",
            "",
            "## Combined Patterns",
            "- Map scene candidates against transcript/audio beats during Stage 02.",
            "- Mark hooks, CTAs, motion peaks, and text overlays as reusable only when visible or audible in artifacts.",
        ]
    )
    output = context / "media-analysis.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def extract_video_context(
    source: Path,
    context: Path,
    records: list[dict[str, Any]],
    root: Path,
    warnings: list[str],
    tools: list[str],
    transcript_file: str | None = None,
) -> None:
    context.mkdir(parents=True, exist_ok=True)
    probe_path = context / "probe.json"
    probe = probe_media(source, probe_path, tools)
    add_file(records, probe_path, "probe", True, root)
    duration = media_duration(probe)
    frame_entries = extract_timestamped_frames(source, context, duration, warnings, tools)
    for frame in frame_entries:
        add_file(records, frame["path"], "video-frame", True, root)
    frame_index = context / "frame-index.md"
    write_frame_index(frame_entries, frame_index)
    add_file(records, frame_index, "frame-index", True, root)
    contact_sheet = context / "contact-sheet.jpg"
    if write_contact_sheet(frame_entries, contact_sheet, warnings):
        add_file(records, contact_sheet, "contact-sheet", True, root)
    motion_events = build_motion_events(frame_entries, warnings)
    motion_index = context / "motion-index.md"
    write_motion_index(motion_events, motion_index)
    add_file(records, motion_index, "motion-index", True, root)
    candidates = scene_candidates(frame_entries, motion_events)
    scene_index = context / "scene-index.md"
    write_scene_index(candidates, scene_index)
    add_file(records, scene_index, "scene-index", True, root)
    ocr_path = write_ocr_text(frame_entries, context, warnings, tools)
    ocr_text = ""
    if ocr_path:
        add_file(records, ocr_path, "ocr-text", True, root)
        ocr_text = ocr_path.read_text(encoding="utf-8").strip()
    _transcript_paths, transcript_text = acquire_transcript(source, context, records, root, warnings, tools, transcript_file)
    audio_profile_path, audio_profile = write_audio_profile(source, context, probe, warnings, tools)
    add_file(records, audio_profile_path, "audio-profile", True, root)
    timeline = write_media_timeline(context, duration, frame_entries, candidates, motion_events, transcript_text)
    add_file(records, timeline, "media-timeline", True, root)
    analysis = write_media_analysis(
        context,
        "video",
        duration,
        frame_entries,
        candidates,
        motion_events,
        transcript_text,
        audio_profile,
        ocr_text,
    )
    add_file(records, analysis, "media-analysis", True, root)


def extract_audio_context(
    source: Path,
    context: Path,
    records: list[dict[str, Any]],
    root: Path,
    warnings: list[str],
    tools: list[str],
    transcript_file: str | None = None,
) -> None:
    context.mkdir(parents=True, exist_ok=True)
    probe_path = context / "probe.json"
    probe = probe_media(source, probe_path, tools)
    add_file(records, probe_path, "probe", True, root)
    duration = media_duration(probe)
    _transcript_paths, transcript_text = acquire_transcript(source, context, records, root, warnings, tools, transcript_file)
    audio_profile_path, audio_profile = write_audio_profile(source, context, probe, warnings, tools)
    add_file(records, audio_profile_path, "audio-profile", True, root)
    timeline = write_media_timeline(context, duration, [], [], [], transcript_text)
    add_file(records, timeline, "media-timeline", True, root)
    analysis = write_media_analysis(context, "audio", duration, [], [], [], transcript_text, audio_profile, "")
    add_file(records, analysis, "media-analysis", True, root)


def acquire_social(
    source: str,
    raw: Path,
    warnings: list[str],
    tools: list[str],
    cookies: str | None = None,
    cookies_from_browser: str | None = None,
) -> list[Path]:
    yt_dlp = require_command("yt-dlp")
    raw.mkdir(parents=True, exist_ok=True)
    host = urllib.parse.urlparse(source).netloc.lower()
    playlist_mode = ["--no-playlist"] if "youtube.com" in host or host == "youtu.be" else []
    template = raw / "source-%(id)s.%(ext)s"
    cookie_args: list[str] = []
    if cookies and cookies_from_browser:
        raise IntakeError("use either --cookies or --cookies-from-browser, not both")
    if cookies:
        cookie_path = Path(cookies).expanduser().resolve()
        if not cookie_path.is_file():
            raise IntakeError(f"cookies file does not exist: {cookie_path}")
        cookie_args.extend(["--cookies", str(cookie_path)])
    if cookies_from_browser:
        cookie_args.extend(["--cookies-from-browser", cookies_from_browser])
    result = run(
        [
            yt_dlp,
            *playlist_mode,
            *cookie_args,
            "--restrict-filenames",
            "--print",
            "after_move:filepath",
            "-o",
            str(template),
            source,
        ]
    )
    if result.returncode != 0:
        raise IntakeError(
            "yt-dlp failed; the post may be private, deleted, or rate-limited. "
            f"Use a screenshot or local file fallback. Details: {(result.stderr or result.stdout).strip()}"
        )
    candidates = [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
    candidates = [path for path in candidates if path.is_file()]
    if not candidates:
        candidates = [path for path in raw.glob("source-*") if path.is_file()]
    candidates = list(dict.fromkeys(candidates))
    if not candidates:
        raise IntakeError("yt-dlp completed but produced no source file")
    tools.append("yt-dlp")
    return candidates


def run_info_rip(source: str, context: Path, root: Path, records: list[dict[str, Any]], warnings: list[str], tools: list[str]) -> None:
    host = urllib.parse.urlparse(source).netloc.lower()
    if "youtube.com" not in host and host != "youtu.be":
        return
    script = root / "skills/ai-capabilities/integrations/youtube/info-rip/scripts/info-rip.py"
    if not script.is_file():
        warnings.append("optional YouTube info-rip unavailable: script not found")
        return
    output_dir = context / "youtube"
    output_dir.mkdir(parents=True, exist_ok=True)
    result = run([sys.executable, str(script), source, str(output_dir)], cwd=root)
    markdown_files = sorted(output_dir.glob("*.md"))
    if result.returncode == 0 and markdown_files:
        tools.append("info-rip")
        for markdown in markdown_files:
            add_file(records, markdown, "metadata", True, root)
    else:
        warnings.append(f"optional YouTube info-rip failed: {(result.stderr or result.stdout).strip()}")


def fallback_metadata(args: argparse.Namespace, root: Path) -> dict[str, str] | None:
    if not any([args.fallback_source, args.fallback_reason, args.fallback_tool, args.fallback_error]):
        return None
    if not args.fallback_source:
        raise IntakeError("--fallback-source is required when recording fallback metadata")
    if not args.fallback_reason:
        raise IntakeError("--fallback-reason is required when recording fallback metadata")

    fallback = {
        "original_source": recorded_source(args.fallback_source, root),
        "fallback_source": recorded_source(args.source, root),
        "failed_tool": args.fallback_tool or "yt-dlp",
        "reason": args.fallback_reason,
    }
    if args.fallback_error:
        fallback["error"] = args.fallback_error.strip()
    return fallback


def write_fallback_note(context: Path, fallback: dict[str, str]) -> Path:
    context.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Fallback Acquisition Note",
        "",
        f"- Original source: {fallback['original_source']}",
        f"- Fallback source: {fallback['fallback_source']}",
        f"- Failed tool or route: {fallback['failed_tool']}",
        f"- Reason: {fallback['reason']}",
    ]
    if fallback.get("error"):
        lines.extend(["- Failure detail:", "", "```text", fallback["error"], "```"])
    note = context / "fallback-note.md"
    note.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return note


def build_manifest(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.workspace_root).expanduser().resolve() if args.workspace_root else repo_root()
    slug = valid_slug(args.slug)
    output_base = Path(args.output_dir).expanduser().resolve() if args.output_dir else root / "libraries/swipes/stages/01-save/output/assets"
    if not output_base.is_relative_to(root):
        raise IntakeError("output directory must stay inside the repository")
    output_base.mkdir(parents=True, exist_ok=True)
    final_dir = output_base / slug
    if final_dir.exists():
        raise IntakeError(f"intake package already exists for slug: {slug}")
    temp_dir = output_base / f".{slug}.tmp-{uuid.uuid4().hex}"
    temp_dir.mkdir(parents=True)
    source_type = classify(args.source, args.captured_file, args.source_type)
    records: list[dict[str, Any]] = []
    warnings: list[str] = []
    tools: list[str] = []
    fallback: dict[str, str] | None = None
    primary_relative: Path | None = None
    acquired_source: Path | None = None
    source_hash: str | None = None
    try:
        fallback = fallback_metadata(args, root)
        if source_type == "image":
            extension = Path(urllib.parse.urlparse(args.source).path if is_url(args.source) else args.source).suffix.lower()
            if not extension and is_url(args.source):
                extension = mimetypes.guess_extension(remote_content_type(args.source)) or ".img"
            extension = extension or ".img"
            target = temp_dir / "context" / f"source{extension}"
            copy_or_download(args.source, target)
            acquired_source = target
            primary_relative = target.relative_to(temp_dir)
        elif source_type == "webpage":
            if not args.captured_file:
                raise IntakeError(
                    "webpage capture requires --captured-file. Capture a full-page screenshot with the browser or Playwright tool, then retry"
                )
            captured = Path(args.captured_file).expanduser().resolve()
            if not captured.is_file():
                raise IntakeError(f"captured webpage file does not exist: {captured}")
            extension = captured.suffix.lower() or ".png"
            target = temp_dir / "context" / f"full-page{extension}"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(captured, target)
            acquired_source = target
            primary_relative = target.relative_to(temp_dir)
            tools.append("browser-capture")
        elif source_type == "pdf":
            raw_source = temp_dir / "raw" / "source.pdf"
            copy_or_download(args.source, raw_source)
            acquired_source = raw_source
            pages = render_pdf(raw_source, temp_dir / "context" / "pages", warnings, tools)
            primary_relative = pages[0].relative_to(temp_dir)
            text_path = temp_dir / "context" / "document.txt"
            extract_pdf_text(raw_source, text_path, warnings, tools)
        elif source_type in MEDIA_SOURCE_TYPES:
            if source_type == "social-video" and is_url(args.source):
                downloaded = acquire_social(
                    args.source,
                    temp_dir / "raw",
                    warnings,
                    tools,
                    args.cookies,
                    args.cookies_from_browser,
                )
                image_media = [path for path in downloaded if path.suffix.lower() in IMAGE_EXTENSIONS]
                video_media = [path for path in downloaded if path.suffix.lower() in VIDEO_EXTENSIONS]
                audio_media = [path for path in downloaded if path.suffix.lower() in AUDIO_EXTENSIONS]
                if image_media and not video_media:
                    context_media = temp_dir / "context" / "social"
                    context_media.mkdir(parents=True, exist_ok=True)
                    for index, image_media_path in enumerate(image_media, start=1):
                        target = context_media / f"image-{index:02d}{image_media_path.suffix.lower()}"
                        shutil.copy2(image_media_path, target)
                        add_file(records, target, "primary-context" if index == 1 else "image-reference", True, root)
                        add_file(records, image_media_path, "source-media", False, root)
                    acquired_source = image_media[0]
                    primary_relative = Path("context/social") / f"image-01{image_media[0].suffix.lower()}"
                    bundle = hashlib.sha256()
                    for media_path in image_media:
                        bundle.update(bytes.fromhex(sha256(media_path)))
                    source_hash = bundle.hexdigest()
                    if len(image_media) > 1:
                        warnings.append(f"social carousel acquired with {len(image_media)} images")
                elif video_media:
                    raw_source = video_media[0]
                    if len(video_media) > 1:
                        warnings.append(f"social source produced {len(video_media)} videos; using the first as primary")
                elif audio_media:
                    raw_source = audio_media[0]
                    source_type = "audio"
                    warnings.append("social source produced audio only; treating acquired media as audio")
                else:
                    raise IntakeError("yt-dlp produced no supported image, video, or audio files")
            else:
                extension = Path(urllib.parse.urlparse(args.source).path if is_url(args.source) else args.source).suffix.lower()
                extension = extension or (".audio" if source_type == "audio" else ".media")
                raw_source = temp_dir / "raw" / f"source{extension}"
                copy_or_download(args.source, raw_source)
            if not acquired_source:
                acquired_source = raw_source
                if source_type == "audio":
                    extract_audio_context(raw_source, temp_dir / "context", records, root, warnings, tools, args.transcript_file)
                    primary_relative = Path("context/media-analysis.md")
                else:
                    extract_video_context(raw_source, temp_dir / "context", records, root, warnings, tools, args.transcript_file)
                    primary_relative = (
                        Path("context/contact-sheet.jpg")
                        if (temp_dir / "context/contact-sheet.jpg").exists()
                        else Path("context/media-analysis.md")
                    )
                if is_url(args.source):
                    run_info_rip(args.source, temp_dir / "context", root, records, warnings, tools)
        else:
            raise IntakeError(f"unsupported source type: {source_type}")

        if not acquired_source or not acquired_source.is_file() or not primary_relative:
            raise IntakeError("acquisition did not produce a source and primary context artifact")
        if fallback:
            note = write_fallback_note(temp_dir / "context", fallback)
            add_file(records, note, "fallback-note", True, root)
            warnings.append(f"fallback acquisition recorded after {fallback['failed_tool']} failed")
        source_hash = source_hash or sha256(acquired_source)
        duplicate = find_duplicate(root, source_hash)
        if duplicate:
            shutil.rmtree(temp_dir)
            return {"status": "duplicate", "source_hash": source_hash, "existing_manifest": duplicate}

        # Paths in records must point at the final package, not its temporary directory.
        final_primary = final_dir / primary_relative
        if source_type in {"image", "webpage"}:
            add_file(records, temp_dir / primary_relative, "primary-context", True, root)
        elif source_type == "pdf":
            add_file(records, acquired_source, "source-media", False, root)
            for page in sorted((temp_dir / "context/pages").glob("*.png")):
                add_file(records, page, "pdf-page", True, root)
            text_path = temp_dir / "context/document.txt"
            if text_path.exists():
                add_file(records, text_path, "extracted-text", True, root)
        elif not any(record["role"] == "source-media" for record in records):
            add_file(records, acquired_source, "source-media", False, root)

        temp_prefix = repo_relative(temp_dir, root)
        final_prefix = repo_relative(final_dir, root)
        for record in records:
            if record["path"].startswith(temp_prefix + "/"):
                record["path"] = final_prefix + record["path"][len(temp_prefix) :]

        manifest = {
            "schema_version": SCHEMA_VERSION,
            "slug": slug,
            "status": "staged",
            "workflow_state": "awaiting-save-approval",
            "next_action": "present-save-checkpoint",
            "ready_for_stage_02": False,
            "ready_for_promotion": False,
            "source": recorded_source(args.source, root),
            "source_type": source_type,
            "source_hash": source_hash,
            "acquired_at": utc_now(),
            "primary_context": repo_relative(final_primary, root),
            "files": sorted(records, key=lambda item: (item["role"], item["path"])),
            "tools": list(dict.fromkeys(tools)),
            "warnings": warnings,
            "quality_status": "degraded" if warnings else "ok",
            "warning_count": len(warnings),
        }
        if fallback:
            manifest["fallback"] = fallback
        (temp_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        temp_dir.rename(final_dir)
        return manifest
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def finalize_save(args: argparse.Namespace) -> dict[str, Any]:
    if not args.human_approved:
        raise IntakeError("Stage 01 save approval is required; present the checkpoint before running finalize-save")
    root = Path(args.workspace_root).expanduser().resolve() if args.workspace_root else repo_root()
    manifest_path = Path(args.manifest).expanduser().resolve()
    if not manifest_path.is_file():
        raise IntakeError(f"manifest does not exist: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") not in {"staged", "complete"}:
        raise IntakeError("only a staged acquisition manifest can be finalized for Stage 01")
    slug = valid_slug(str(manifest.get("slug", "")))
    intake_path = root / "libraries/swipes/stages/01-save/output" / f"{slug}-intake.md"
    if intake_path.exists():
        raise IntakeError(f"Stage 01 intake record already exists: {repo_relative(intake_path, root)}")
    if not manifest.get("primary_context") or not (root / manifest["primary_context"]).is_file():
        raise IntakeError("manifest primary_context is missing or does not resolve")
    if not args.why_saved.strip():
        raise IntakeError("--why-saved must contain the human's reason for saving this reference")

    intake_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Intake: {args.title.strip()}",
        "",
        f"- slug: {slug}",
        f"- source: {manifest['source']}",
        f"- source-type: {manifest['source_type']}",
        f"- type: {args.type}",
        f"- saved: {args.saved or today()}",
        f"- tags: {args.tags.strip()}",
        f"- asset-manifest: {repo_relative(manifest_path, root)}",
        f"- primary-context: {manifest['primary_context']}",
        "- acquisition-status: complete",
        "- status: pending-extraction",
        "",
        "## Why saved",
        "",
        args.why_saved.strip(),
        "",
        "## Raw notes",
        "",
        args.raw_notes.strip() if args.raw_notes else "None provided.",
        "",
        "## Source content",
        "",
        manifest["source"],
        "",
    ]
    intake_path.write_text("\n".join(lines), encoding="utf-8")
    manifest.update(
        {
            "workflow_state": "save-approved",
            "next_action": "run-stage-02-extraction",
            "ready_for_stage_02": True,
            "ready_for_promotion": False,
            "intake_record": repo_relative(intake_path, root),
            "save_approved_at": utc_now(),
        }
    )
    write_json_atomic(manifest_path, manifest)
    return {
        "status": "save-approved",
        "manifest": repo_relative(manifest_path, root),
        "intake_record": repo_relative(intake_path, root),
        "next_action": manifest["next_action"],
        "warnings": manifest.get("warnings", []),
    }


def promote(args: argparse.Namespace) -> dict[str, Any]:
    if not args.human_approved:
        raise IntakeError("Stage 03 curation approval is required; do not promote before the curation checkpoint")
    root = Path(args.workspace_root).expanduser().resolve() if args.workspace_root else repo_root()
    manifest_path = Path(args.manifest).expanduser().resolve()
    if not manifest_path.is_file():
        raise IntakeError(f"manifest does not exist: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") not in {"staged", "complete"}:
        raise IntakeError("only a staged acquisition manifest can be promoted")
    if manifest.get("status") == "staged" and not manifest.get("ready_for_stage_02"):
        raise IntakeError("Stage 01 is not complete: finalize-save after explicit save approval before promotion")
    if manifest.get("status") == "staged":
        if manifest.get("workflow_state") != "save-approved":
            raise IntakeError(
                "Stage 01 workflow_state must be save-approved before Stage 03 promotion"
            )
        intake_record = manifest.get("intake_record")
        if not intake_record or not (root / intake_record).is_file():
            raise IntakeError("Stage 01 intake record is missing; run finalize-save before promotion")
        extraction_path = root / "libraries/swipes/stages/02-extract/output" / f"{manifest['slug']}-extraction.md"
        if not extraction_path.is_file():
            raise IntakeError(
                f"Stage 02 extraction is missing: {repo_relative(extraction_path, root)}; do not promote from Stage 01"
            )
        extraction_text = extraction_path.read_text(encoding="utf-8")
        if manifest.get("source_type") in MEDIA_SOURCE_TYPES:
            lowered_extraction = extraction_text.lower()
            if "## visual inspection" not in lowered_extraction:
                raise IntakeError(
                    f"Stage 02 extraction lacks a Visual inspection section: {repo_relative(extraction_path, root)}"
                )
            if "gitignored" in lowered_extraction and "not directly viewable" in lowered_extraction:
                raise IntakeError(
                    "Stage 02 extraction claims gitignored frames are not viewable; open the local frames and revise it"
                )
        handoff_path = root / "libraries/swipes/stages/02-extract/output" / f"{manifest['slug']}-handoff.md"
        validate_handoff(
            handoff_path,
            expected_stage="02-extract",
            expected_slug=str(manifest["slug"]),
            expected_state="ready-for-review",
            root=root,
        )
    slug = valid_slug(str(manifest.get("slug", "")))
    destination_base = Path(args.destination).expanduser().resolve() if args.destination else root / "libraries/swipes/knowledge-layer/assets"
    if not destination_base.is_relative_to(root):
        raise IntakeError("promotion destination must stay inside the repository")
    destination_base.mkdir(parents=True, exist_ok=True)
    final_dir = destination_base / slug
    if final_dir.exists():
        existing = final_dir / "manifest.json"
        if existing.is_file():
            existing_manifest = json.loads(existing.read_text(encoding="utf-8"))
            if existing_manifest.get("source_hash") == manifest.get("source_hash"):
                return existing_manifest
        raise IntakeError(f"knowledge-layer asset package already exists for slug: {slug}")
    temp_dir = destination_base / f".{slug}.tmp-{uuid.uuid4().hex}"
    temp_dir.mkdir(parents=True)
    staged_dir = manifest_path.parent
    promoted_records: list[dict[str, Any]] = []
    try:
        for record in manifest.get("files", []):
            if not record.get("persist"):
                continue
            source_path = root / record["path"]
            if not source_path.is_file():
                raise IntakeError(f"persistent artifact is missing: {record['path']}")
            try:
                relative = source_path.resolve().relative_to(staged_dir.resolve())
            except ValueError as exc:
                raise IntakeError(f"artifact is outside its staging package: {record['path']}") from exc
            target = temp_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target)
            promoted_record = dict(record)
            promoted_record["path"] = repo_relative(final_dir / relative, root)
            promoted_records.append(promoted_record)
        if not promoted_records:
            raise IntakeError("manifest has no persistent context artifacts")
        primary_source = root / manifest["primary_context"]
        primary_relative = primary_source.resolve().relative_to(staged_dir.resolve())
        promoted = {
            **manifest,
            "status": "curated",
            "workflow_state": "curated",
            "next_action": "write-knowledge-layer-entry",
            "ready_for_stage_02": False,
            "ready_for_promotion": False,
            "promoted_at": utc_now(),
            "staging_manifest": repo_relative(manifest_path, root),
            "primary_context": repo_relative(final_dir / primary_relative, root),
            "files": sorted(promoted_records, key=lambda item: (item["role"], item["path"])),
        }
        (temp_dir / "manifest.json").write_text(json.dumps(promoted, indent=2) + "\n", encoding="utf-8")
        temp_dir.rename(final_dir)
        return promoted
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def check_handoff(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.workspace_root).expanduser().resolve() if args.workspace_root else repo_root()
    handoff_path = Path(args.handoff).expanduser().resolve()
    return validate_handoff(
        handoff_path,
        expected_stage=args.stage,
        expected_slug=valid_slug(args.slug),
        expected_state=args.state,
        root=root,
    )


def parser() -> argparse.ArgumentParser:
    root_parser = argparse.ArgumentParser(description=__doc__)
    subparsers = root_parser.add_subparsers(dest="command", required=True)
    acquire_parser = subparsers.add_parser("acquire", help="Acquire and normalize one reference")
    acquire_parser.add_argument("source", help="URL or local file path")
    acquire_parser.add_argument("--slug", required=True, help="Lowercase kebab-case reference slug")
    acquire_parser.add_argument("--captured-file", help="Full-page screenshot for webpage sources")
    acquire_parser.add_argument("--source-type", choices=["audio", "image", "webpage", "pdf", "video", "social-video"])
    acquire_parser.add_argument("--transcript-file", help="Optional transcript file for audio or video sources")
    acquire_parser.add_argument("--cookies", help="Netscape-format cookies file for yt-dlp social downloads")
    acquire_parser.add_argument("--cookies-from-browser", help="Browser profile to read cookies from for yt-dlp social downloads")
    acquire_parser.add_argument("--fallback-source", help="Original source that failed before acquiring this fallback file")
    acquire_parser.add_argument("--fallback-tool", help="Tool or route that failed before fallback acquisition")
    acquire_parser.add_argument("--fallback-reason", help="Why this fallback file was used")
    acquire_parser.add_argument("--fallback-error", help="Failure detail to preserve in the manifest and fallback note")
    acquire_parser.add_argument("--workspace-root", help="Repository root override")
    acquire_parser.add_argument("--output-dir", help="Staging assets directory override")
    acquire_parser.set_defaults(handler=build_manifest)
    finalize_parser = subparsers.add_parser(
        "finalize-save",
        help="Write the Stage 01 intake record after explicit human save approval",
    )
    finalize_parser.add_argument("manifest", help="Staged manifest path")
    finalize_parser.add_argument("--title", required=True, help="Human-facing reference title")
    finalize_parser.add_argument(
        "--type",
        required=True,
        choices=["ad", "landing-page", "email", "brand-guide", "social-post", "screenshot", "pdf", "other"],
        help="Reference type used by the Stage 01 intake contract",
    )
    finalize_parser.add_argument("--tags", required=True, help="Comma-separated lowercase tags")
    finalize_parser.add_argument("--why-saved", required=True, help="The human's reason for saving the reference")
    finalize_parser.add_argument("--raw-notes", help="Optional notes captured before extraction")
    finalize_parser.add_argument("--saved", help="Save date in YYYY-MM-DD format; defaults to today")
    finalize_parser.add_argument(
        "--human-approved",
        action="store_true",
        help="Required acknowledgement that the Stage 01 save checkpoint was approved",
    )
    finalize_parser.add_argument("--workspace-root", help="Repository root override")
    finalize_parser.set_defaults(handler=finalize_save)
    promote_parser = subparsers.add_parser("promote", help="Promote persistent artifacts after Stage 03 approval")
    promote_parser.add_argument("manifest", help="Staged manifest path")
    promote_parser.add_argument(
        "--human-approved",
        action="store_true",
        help="Required acknowledgement that the Stage 03 curation checkpoint was approved",
    )
    promote_parser.add_argument("--workspace-root", help="Repository root override")
    promote_parser.add_argument("--destination", help="Knowledge-layer assets directory override")
    promote_parser.set_defaults(handler=promote)
    check_parser = subparsers.add_parser(
        "check-handoff",
        help="Validate a tracked stage handoff before returning the checkpoint",
    )
    check_parser.add_argument("handoff", help="Stage handoff Markdown path")
    check_parser.add_argument("--stage", required=True, choices=["01-save", "02-extract", "03-curate"])
    check_parser.add_argument("--slug", required=True, help="Lowercase kebab-case reference slug")
    check_parser.add_argument("--state", help="Expected handoff state")
    check_parser.add_argument("--workspace-root", help="Repository root override")
    check_parser.set_defaults(handler=check_handoff)
    return root_parser


def main() -> int:
    args = parser().parse_args()
    try:
        result = args.handler(args)
    except (IntakeError, json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
