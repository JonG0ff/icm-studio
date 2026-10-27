"""Filmstrip + waveform composite PNG for a time range of a video.

The only visual drill-down tool. Given a video and a [start, end] range,
extracts N evenly spaced frames via ffmpeg, composites them into a
horizontal filmstrip, and renders a waveform ribbon below with word
labels overlaid from the transcript (if available) and transcript gaps
shaded.

Use this at decision points — ambiguous pauses, retake disambiguation,
cut-point sanity checks. Do NOT call it in a scan loop over every
utterance; it's an on-demand drill-down, not a background index.

Usage:
    python helpers/timeline_view.py <video> <start> <end>
    python helpers/timeline_view.py <video> <start> <end> -o out.png
    python helpers/timeline_view.py <video> <start> <end> --n-frames 12
    python helpers/timeline_view.py <video> <start> <end> --transcript <path>
    python helpers/timeline_view.py --edl <edl.json>   (full-project view — not yet)
"""

from __future__ import annotations

import argparse
from bisect import bisect_right
from fractions import Fraction
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from pack_transcripts import validate_words

# Packet reading stops at an interval end in decode order. B-frame reordering
# can then hide the last in-range frames, so read past the end and select by PTS.
REORDER_MARGIN_S = 1.0

# Adapted from browser-use/video-use; see LICENSE and upstream.json.


def validate_range(start: float, end: float) -> None:
    if not math.isfinite(start) or not math.isfinite(end) or start < 0 or end <= start:
        raise ValueError("range must be finite and satisfy 0 <= start < end")


def validate_media(video: Path, start: float, end: float, audio_track: int = 0) -> dict:
    """audio_track is a zero-based audio ordinal (ffmpeg 0:a:N)."""
    validate_range(start, end)
    if not video.is_file():
        raise ValueError(f"video not found: {video}")
    if isinstance(audio_track, bool) or not isinstance(audio_track, int) or audio_track < 0:
        raise ValueError("audio track must be a nonnegative integer")
    result = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(video)], check=True, capture_output=True, text=True)
    metadata = json.loads(result.stdout)
    duration = float(metadata.get("format", {}).get("duration", "nan"))
    if not math.isfinite(duration) or duration <= 0 or end > duration:
        raise ValueError(f"range exceeds finite media duration ({duration}s)")
    streams = metadata.get("streams", [])
    if not any(s.get("codec_type") == "video" for s in streams):
        raise ValueError("source requires a video stream")
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    if audio_track >= len(audio):
        raise ValueError(f"audio track {audio_track} unavailable; source has {len(audio)} audio tracks")
    return metadata


# -------- Frame extraction ---------------------------------------------------


def sample_frames(video: Path, start: float, end: float, n: int, dest_dir: Path) -> list[tuple[Path, float]]:
    """Sample bin centers in [start, end); return each covering frame and its actual PTS.

    A center after the last presentation timestamp still belongs to that final
    frame's display interval. Seeking directly to the center would discard it.
    Probe the selected interval (including decoder keyframe preroll), then select
    exact integer PTS with copyts. No FPS guesses or temporal-range changes.
    """
    validate_range(start, end)
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 64:
        raise ValueError("n_frames must be an integer from 1 to 64")
    dest_dir.mkdir(parents=True, exist_ok=True)
    times = [start + (i + 0.5) * (end - start) / n for i in range(n)]
    result = subprocess.run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-read_intervals", f"{start:.12f}%{end + REORDER_MARGIN_S:.12f}", "-show_frames",
        "-show_entries", "frame=best_effort_timestamp,duration,pkt_duration:stream=time_base",
        "-of", "json", str(video),
    ], check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    if len(streams) != 1:
        raise ValueError("frame sampling requires one selected video stream")
    try:
        time_base = Fraction(streams[0]["time_base"])
    except (KeyError, ValueError, ZeroDivisionError) as exc:
        raise ValueError("frame sampling requires a valid video time base") from exc
    if time_base <= 0:
        raise ValueError("frame sampling requires a positive video time base")
    frames = data.get("frames", [])
    try:
        pts = [int(frame["best_effort_timestamp"]) for frame in frames]
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError("frame sampling requires presentation timestamps") from exc
    if not pts or any(a >= b for a, b in zip(pts, pts[1:])):
        raise ValueError("frame sampling requires nonempty, strictly ordered presentation timestamps")
    frame_times = [float(timestamp * time_base) for timestamp in pts]

    samples: list[tuple[Path, float]] = []
    decoded: dict[int, Path] = {}
    for i, t in enumerate(times):
        index = bisect_right(frame_times, t) - 1
        if index < 0:
            raise ValueError(f"no video frame covers sample center {t:.9f}s")
        raw_duration = frames[index].get("duration", frames[index].get("pkt_duration"))
        try:
            duration_ticks = int(raw_duration) if raw_duration is not None else 0
        except (ValueError, TypeError) as exc:
            raise ValueError("frame sampling encountered an invalid frame duration") from exc
        if duration_ticks > 0:
            frame_end = float((pts[index] + duration_ticks) * time_base)
        elif index + 1 < len(pts):
            frame_end = frame_times[index + 1]
        else:
            raise ValueError("final sampled frame has no duration evidence")
        if t >= frame_end:
            raise ValueError(f"no video frame covers sample center {t:.9f}s")
        actual_pts = frame_times[index]
        if pts[index] in decoded:
            samples.append((decoded[pts[index]], actual_pts))
            continue
        out = dest_dir / f"f_{i:03d}.jpg"
        cmd = [
            "ffmpeg", "-y", "-copyts",
            "-ss", f"{max(0, actual_pts - 0.5):.12f}",
            "-to", f"{end + REORDER_MARGIN_S:.12f}",
            "-i", str(video),
            "-map", "0:v:0",
            "-frames:v", "1",
            "-q:v", "4",
            "-vf", f"select=eq(pts\\,{pts[index]}),scale=320:-2",
            str(out),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not out.is_file() or out.stat().st_size == 0:
            raise ValueError(f"no video frame decoded at actual PTS {actual_pts:.9f}s (sample center {t:.9f}s)")
        decoded[pts[index]] = out
        samples.append((out, actual_pts))
    return samples


def extract_frames(video: Path, start: float, end: float, n: int, dest_dir: Path) -> list[Path]:
    """Compatibility view of sample_frames: paths in requested sample order."""
    return [path for path, _ in sample_frames(video, start, end, n, dest_dir)]


# -------- Audio envelope (FFmpeg PCM + NumPy only) -------------------------


def compute_envelope(video: Path, start: float, end: float, samples: int = 2000, audio_track: int = 0) -> np.ndarray:
    """Extract the audio segment and return an RMS envelope of length `samples`.

    Uses ffmpeg to dump mono 16kHz PCM to a temp wav, then computes a
    windowed RMS. Missing tracks and empty/undecodable audio fail explicitly.
    """
    validate_media(video, start, end, audio_track)
    if isinstance(samples, bool) or not isinstance(samples, int) or samples < 1:
        raise ValueError("samples must be a positive integer")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav = Path(f.name)
    try:
        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{start:.3f}",
            "-i", str(video),
            "-map", f"0:a:{audio_track}",
            "-t", f"{(end - start):.3f}",
            "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
            str(wav),
        ]
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0 or not wav.exists() or wav.stat().st_size == 0:
            raise ValueError("selected audio track could not be decoded")

        # Read the WAV manually — avoid librosa as a hard dep
        import wave
        with wave.open(str(wav), "rb") as w:
            frames = w.readframes(w.getnframes())
        pcm = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        if pcm.size == 0:
            raise ValueError("selected audio range contains no PCM samples")

        # Windowed RMS → envelope of length `samples`
        # Cover the entire requested PCM range, including its final partial bin.
        env = np.array([np.sqrt(np.mean(chunk ** 2)) if chunk.size else 0.0
                        for chunk in np.array_split(pcm, samples)])
        # Normalize to [0, 1]
        if env.max() > 0:
            env = env / env.max()
        return env
    finally:
        wav.unlink(missing_ok=True)


# -------- Transcript word overlays ------------------------------------------


def words_in_range(transcript_path: Path, start: float, end: float) -> list[dict]:
    validate_range(start, end)
    data = json.loads(transcript_path.read_text())
    if not isinstance(data, dict) or "words" not in data:
        raise ValueError("transcript must be an object with an explicit words list")
    validate_words(data["words"])
    out: list[dict] = []
    for w in data.get("words", []):
        if w["type"] != "word":
            continue
        ws = w.get("start")
        we = w.get("end")
        if ws is None or we is None:
            continue
        if we <= start or ws >= end:
            continue
        out.append(w)
    return out


def find_silences(words: list[dict], start: float, end: float, threshold: float = 0.4) -> list[tuple[float, float]]:
    """Find gaps >= threshold seconds inside [start, end] between kept tokens."""
    gaps: list[tuple[float, float]] = []
    prev_end = start
    for w in words:
        if w.get("type") == "spacing":
            continue
        ws = max(start, w.get("start", start))
        if ws - prev_end >= threshold:
            gaps.append((prev_end, ws))
        prev_end = max(prev_end, w.get("end", ws))
    if end - prev_end >= threshold:
        gaps.append((prev_end, end))
    return gaps


# -------- Font loading -------------------------------------------------------


FONT_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFNSMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]


def load_font(size: int) -> ImageFont.ImageFont:
    for fp in FONT_CANDIDATES:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


# -------- Composite ----------------------------------------------------------


BG = (18, 18, 22)
FG = (235, 235, 235)
DIM = (110, 110, 120)
ACCENT = (255, 140, 60)
SILENCE = (50, 80, 120, 120)  # muted blue, semi-transparent
WAVE = (140, 180, 255)


def render_timeline(
    video: Path,
    start: float,
    end: float,
    out_path: Path,
    n_frames: int,
    transcript: Path | None,
    audio_track: int = 0,
) -> None:
    validate_media(video, start, end, audio_track)
    if isinstance(n_frames, bool) or not isinstance(n_frames, int) or not 1 <= n_frames <= 64:
        raise ValueError("n_frames must be an integer from 1 to 64")
    words = words_in_range(transcript, start, end) if transcript else []
    # Frame extraction
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        print(f"extracting {n_frames} frames from {start:.2f}s to {end:.2f}s")
        frame_samples = sample_frames(video, start, end, n_frames, tmp_dir)
        frame_paths = [path for path, _ in frame_samples]

        # Layout metrics
        canvas_width = 1920
        frame_h = 180
        filmstrip_y = 50
        filmstrip_h = frame_h
        wave_y = filmstrip_y + filmstrip_h + 20
        wave_h = 220
        label_y = wave_y + wave_h + 10
        canvas_height = label_y + 60

        # Load + resize frames to uniform height and compute total width
        imgs: list[Image.Image] = []
        for fp in frame_paths:
            img = Image.open(fp).convert("RGB")
            aspect = img.width / img.height
            new_w = int(frame_h * aspect)
            imgs.append(img.resize((new_w, frame_h), Image.LANCZOS))

        total_frame_w = sum(img.width for img in imgs) + (len(imgs) - 1) * 4
        content_w = max(1400, total_frame_w)
        canvas_width = max(canvas_width, content_w + 100)

        canvas = Image.new("RGB", (canvas_width, canvas_height), BG)
        draw = ImageDraw.Draw(canvas, "RGBA")

        header_font = load_font(22)
        label_font = load_font(14)
        small_font = load_font(12)

        # Header — time range
        draw.text(
            (50, 12),
            f"{video.name}   {start:.2f}s → {end:.2f}s   ({(end - start):.2f}s, {n_frames} frames, audio {audio_track})",
            fill=FG,
            font=header_font,
        )

        # Filmstrip
        x = 50
        strip_width = canvas_width - 100
        if total_frame_w <= strip_width:
            cursor = 50
            for img, (_, source_pts) in zip(imgs, frame_samples):
                canvas.paste(img, (cursor, filmstrip_y))
                draw.rectangle((cursor, filmstrip_y + frame_h - 19, cursor + img.width, filmstrip_y + frame_h), fill=BG)
                draw.text((cursor + 3, filmstrip_y + frame_h - 17), f"PTS {source_pts:.6f}s", fill=FG, font=small_font)
                cursor += img.width + 4
            draw_width = cursor - 50
        else:
            scale = strip_width / total_frame_w
            new_h = int(frame_h * scale)
            cursor = 50
            for img, (_, source_pts) in zip(imgs, frame_samples):
                new_w = int(img.width * scale)
                scaled = img.resize((new_w, new_h), Image.LANCZOS)
                canvas.paste(scaled, (cursor, filmstrip_y + (filmstrip_h - new_h) // 2))
                text_y = filmstrip_y + (filmstrip_h + new_h) // 2 - 17
                draw.rectangle((cursor, text_y - 2, cursor + new_w, text_y + 17), fill=BG)
                draw.text((cursor + 3, text_y), f"PTS {source_pts:.6f}s", fill=FG, font=small_font)
                cursor += new_w + max(2, int(4 * scale))
            draw_width = cursor - 50

        strip_x0 = 50
        strip_x1 = 50 + draw_width
        strip_span = strip_x1 - strip_x0

        def time_to_x(t: float) -> int:
            frac = (t - start) / max(1e-6, (end - start))
            return int(strip_x0 + frac * strip_span)

        # Waveform background
        draw.rectangle((strip_x0, wave_y, strip_x1, wave_y + wave_h), fill=(28, 28, 34))

        # Silence shading (under the waveform)
        silences = find_silences(words, start, end, threshold=0.4) if words else []
        for a, b in silences:
            xa = time_to_x(a)
            xb = time_to_x(b)
            draw.rectangle((xa, wave_y, xb, wave_y + wave_h), fill=SILENCE)

        # Waveform envelope
        env = compute_envelope(video, start, end, samples=max(strip_span, 200), audio_track=audio_track)
        mid_y = wave_y + wave_h // 2
        max_amp = wave_h // 2 - 8
        points_top: list[tuple[int, int]] = []
        points_bot: list[tuple[int, int]] = []
        for i, v in enumerate(env):
            xi = strip_x0 + int(i * strip_span / max(1, len(env) - 1))
            a = int(v * max_amp)
            points_top.append((xi, mid_y - a))
            points_bot.append((xi, mid_y + a))
        if points_top:
            draw.line(points_top, fill=WAVE, width=1, joint="curve")
            draw.line(points_bot, fill=WAVE, width=1, joint="curve")
            # Fill between
            poly = points_top + list(reversed(points_bot))
            draw.polygon(poly, fill=(*WAVE, 60))

        # Word labels above the waveform (only words lasting ≥ 50ms to avoid clutter)
        last_label_x = -9999
        for w in words:
            if w.get("type") != "word":
                continue
            ws = w.get("start")
            we = w.get("end")
            text = (w.get("text") or "").strip()
            if not text or ws is None or we is None:
                continue
            if (we - ws) < 0.05:
                continue
            cx = (time_to_x(ws) + time_to_x(we)) // 2
            if cx - last_label_x < 28:
                continue
            # Tiny tick on the waveform
            draw.line((cx, wave_y - 4, cx, wave_y), fill=DIM, width=1)
            # Text above the waveform
            draw.text((cx + 2, wave_y - 18), text, fill=FG, font=small_font)
            last_label_x = cx

        # Time ruler below waveform
        ruler_y = wave_y + wave_h + 2
        n_ticks = 6
        for i in range(n_ticks + 1):
            frac = i / n_ticks
            t = start + frac * (end - start)
            xi = strip_x0 + int(frac * strip_span)
            draw.line((xi, ruler_y, xi, ruler_y + 6), fill=DIM, width=1)
            draw.text((xi - 20, ruler_y + 8), f"{t:.2f}s", fill=DIM, font=label_font)

        # Silences legend if any
        if silences:
            txt = f"shaded bands = transcript gaps ≥ 400ms ({len(silences)}); not verified silence"
            draw.text((strip_x0, label_y + 30), txt, fill=DIM, font=label_font)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out_path, "PNG", optimize=True)
        print(f"saved: {out_path}  ({out_path.stat().st_size // 1024} KB)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Filmstrip + waveform composite for a video range")
    ap.add_argument("video", type=Path, nargs="?", help="Source video")
    ap.add_argument("start", type=float, nargs="?", help="Start time in seconds")
    ap.add_argument("end", type=float, nargs="?", help="End time in seconds")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output PNG path")
    ap.add_argument("--n-frames", type=int, default=10, help="Number of frames in the filmstrip (default 10)")
    ap.add_argument("--audio-track", type=int, default=0, help="Zero-based audio ordinal, mapped as 0:a:N (default 0)")
    ap.add_argument(
        "--transcript",
        type=Path,
        default=None,
        help="Path to transcript.json for word labels + unverified transcript-gap shading. "
             "If omitted, will auto-resolve to <video_parent>/edit/transcripts/<video_stem>.json",
    )
    ap.add_argument(
        "--edl",
        type=Path,
        default=None,
        help="(Not yet implemented) Render a full-project timeline from an EDL",
    )
    args = ap.parse_args()

    if args.edl:
        sys.exit("--edl mode is not implemented yet; use range mode")

    if not args.video or args.start is None or args.end is None:
        ap.error("video, start, and end are required")

    video = args.video.resolve()
    if not video.exists():
        sys.exit(f"video not found: {video}")

    if args.end <= args.start:
        sys.exit("end must be > start")

    # Auto-resolve transcript if not given
    transcript = args.transcript
    if transcript is None:
        auto = video.parent / "edit" / "transcripts" / f"{video.stem}.json"
        if auto.exists():
            transcript = auto

    out_path = args.output
    if out_path is None:
        out_dir = video.parent / "edit" / "verify"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{video.stem}_{args.start:.2f}-{args.end:.2f}.png"

    try:
        render_timeline(
            video=video,
            start=args.start,
            end=args.end,
            out_path=out_path,
            n_frames=args.n_frames,
            transcript=transcript,
            audio_track=args.audio_track,
        )
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        ap.error(str(exc))


if __name__ == "__main__":
    main()
