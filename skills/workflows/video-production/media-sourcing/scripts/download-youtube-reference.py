#!/usr/bin/env python3
"""
YouTube Reference Download - download a short YouTube clip segment for internal reference only.

Uses ONLY Python standard library + yt-dlp (already installed).

Usage:
    python3 download-youtube-reference.py <youtube-url> <campaign-directory> --start <time> --end <time>

Time formats: HH:MM:SS, MM:SS, or raw seconds.

Example:
    python3 download-youtube-reference.py \\
        "https://www.youtube.com/watch?v=..." \\
        ./trailer-campaign-01 \\
        --start 0:15 --end 0:35
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def error(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_time(value):
    """Parse HH:MM:SS, MM:SS, or raw seconds into seconds (int)."""
    value = value.strip()
    if re.match(r"^\d+(\.\d+)?$", value):
        return int(float(value))
    parts = value.split(":")
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        error(f"Invalid time format: '{value}'. Use HH:MM:SS, MM:SS, or raw seconds.")
    if len(nums) == 2:
        m, s = nums
        return int(m * 60 + s)
    elif len(nums) == 3:
        h, m, s = nums
        return int(h * 3600 + m * 60 + s)
    else:
        error(f"Invalid time format: '{value}'. Use HH:MM:SS, MM:SS, or raw seconds.")


def slugify(text):
    """Simple slugify using stdlib only."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def yt_dlp_meta(url):
    """Fetch title, channel, duration from a URL without downloading."""
    cmd = [
        "yt-dlp",
        "--no-download",
        "--no-playlist",
        "--print", "%(title)s",
        "--print", "%(channel)s",
        "--print", "%(duration)s",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        error(f"yt-dlp failed to fetch metadata: {result.stderr.strip()}")
    lines = result.stdout.strip().splitlines()
    while len(lines) < 3:
        lines.append("")
    return lines[0], lines[1], lines[2]


def main():
    parser = argparse.ArgumentParser(
        description="YouTube reference download - internal reference clips only. Never for client deliverables."
    )
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("campaign", help="Campaign directory path")
    parser.add_argument(
        "--start", required=True, help="Clip start time (HH:MM:SS, MM:SS, or seconds)"
    )
    parser.add_argument(
        "--end", required=True, help="Clip end time (HH:MM:SS, MM:SS, or seconds)"
    )
    args = parser.parse_args()

    campaign = Path(args.campaign).resolve()
    footage_dir = campaign / "footage"
    footage_dir.mkdir(parents=True, exist_ok=True)

    start_sec = parse_time(args.start)
    end_sec = parse_time(args.end)

    if end_sec <= start_sec:
        error("--end must be greater than --start")

    # Fetch metadata
    print("Fetching metadata...")
    title, channel, duration = yt_dlp_meta(args.url)

    # Build target paths
    today = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{today}-{slug}.mp4"
    mp4_path = footage_dir / filename
    json_path = footage_dir / f"{today}-{slug}.json"

    # Existing file check
    if mp4_path.exists():
        print(f"Already exists: {mp4_path}")
        sys.exit(0)

    # Download segment
    print(f"Downloading segment {start_sec}s–{end_sec}s...")
    section = f"*{start_sec}-{end_sec}"
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--download-sections", section,
        "-o", str(mp4_path),
        "--merge-output-format", "mp4",
        args.url,
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        error("yt-dlp download failed")

    # Verify file exists
    if not mp4_path.exists():
        error("Expected MP4 not found after download")

    # Write metadata sidecar
    try:
        original_duration = float(duration) if duration and duration != "NA" else None
    except ValueError:
        original_duration = None

    meta = {
        "title": title,
        "channel": channel,
        "source_url": args.url,
        "original_duration": original_duration,
        "clip_start": start_sec,
        "clip_end": end_sec,
        "internal_use_only": True,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")

    print(f"Saved: {mp4_path}")
    print(f"Meta:  {json_path}")


if __name__ == "__main__":
    main()
