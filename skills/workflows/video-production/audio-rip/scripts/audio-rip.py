#!/usr/bin/env python3
"""
Audio Rip Skill - download reference or cleared YouTube audio and extract stems.

Usage:
    python3 audio-rip.py <youtube-url> [output-dir]

Example:
    python3 audio-rip.py "https://www.youtube.com/watch?v=s8S5PN1FnFk" ./music
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd, **kwargs):
    """Run a shell command and print it."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def download_audio(url: str, output_dir: Path, section: str | None = None) -> Path:
    """Download audio from YouTube as MP3 using yt-dlp.

    ``section`` takes a ``START-END`` range (yt-dlp time syntax) and pulls only
    that slice. SFX rips almost always want a few seconds out of a longer
    upload, not the whole file.
    """
    print(f"\n[1/3] Downloading audio from YouTube...")
    output_dir.mkdir(parents=True, exist_ok=True)
    template = str(output_dir / "%(title)s.%(ext)s")
    section_args = ["--download-sections", f"*{section}"] if section else []
    run([
        "yt-dlp",
        "--no-playlist",
        "--extractor-args", "youtube:player_client=android_vr",
        *section_args,
        "-x", "--audio-format", "mp3", "--audio-quality", "0",
        "-o", template,
        url,
    ])

    # Find the downloaded MP3
    mp3_files = sorted(output_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not mp3_files:
        print("Error: No MP3 file found after download.")
        sys.exit(1)
    mp3_path = mp3_files[0]
    print(f"  Downloaded: {mp3_path.name}")
    return mp3_path


def separate_stems(mp3_path: Path, output_dir: Path) -> Path:
    """Separate stems using Demucs."""
    print(f"\n[2/3] Separating stems with Demucs...")
    stems_dir = output_dir / "stems"
    stems_dir.mkdir(parents=True, exist_ok=True)

    # Use the venv python if it exists next to this script
    script_dir = Path(__file__).parent
    venv_python = script_dir.parent / ".venv" / "bin" / "python"
    python = str(venv_python) if venv_python.exists() else sys.executable

    run([
        python, "-m", "demucs.separate",
        "--two-stems", "vocals",   # Produces vocals.wav + no_vocals.wav
        "--mp3",
        "-o", str(stems_dir),
        str(mp3_path),
    ])

    # Demucs writes to stems_dir/<model>/<track_name>/
    track_name = mp3_path.stem
    track_dir = None
    for model_path in stems_dir.iterdir():
        if model_path.is_dir():
            candidate = model_path / track_name
            if candidate.is_dir():
                track_dir = candidate
                break
    
    if not track_dir:
        # Fallback to the old method if not found
        model_dir = next(stems_dir.iterdir())
        track_dir = next(model_dir.iterdir())

    print(f"  Stems written to: {track_dir.relative_to(output_dir.parent)}")
    return track_dir


def organize_results(track_dir: Path, output_dir: Path, original_name: str):
    """Rename stems to beat/vocals and move to final location."""
    print(f"\n[3/3] Organizing results...")

    base = Path(original_name).stem
    beats_file = output_dir / f"{base}__beat.mp3"
    vocals_file = output_dir / f"{base}__vocals.mp3"

    # no_vocals = instrumental / beat
    no_vocals_src = track_dir / "no_vocals.mp3"
    vocals_src = track_dir / "vocals.mp3"

    if no_vocals_src.exists():
        shutil.copy2(no_vocals_src, beats_file)
        print(f"  Beat (no vocals): {beats_file.name}")
    if vocals_src.exists():
        shutil.copy2(vocals_src, vocals_file)
        print(f"  Vocals:           {vocals_file.name}")

    print(f"\nDone. Output: {output_dir}")
    return beats_file, vocals_file


def main():
    parser = argparse.ArgumentParser(description="Audio Rip Skill - YouTube audio to stems")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("output", nargs="?", default=".", help="Output directory (default: current)")
    parser.add_argument(
        "--no-stems",
        action="store_true",
        help="Download the audio only. Use for SFX and foley, where vocal/instrumental separation is meaningless.",
    )
    parser.add_argument(
        "--section",
        help="Rip only a time range, e.g. '0:03-0:11'. Recommended for SFX rips.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output).resolve()

    if args.no_stems:
        mp3_path = download_audio(args.url, output_dir, args.section)
        print(f"\nDone. Output: {mp3_path}")
        return

    temp_dir = output_dir / "temp-tracks"

    # Step 1: Download
    mp3_path = download_audio(args.url, temp_dir, args.section)

    # Step 2: Separate
    track_dir = separate_stems(mp3_path, output_dir)

    # Step 3: Organize
    organize_results(track_dir, output_dir, mp3_path.name)


if __name__ == "__main__":
    main()
