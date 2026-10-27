#!/usr/bin/env python3
"""
Sound Effects Mix - SFX Map Generator

Reads a sound effects mix JSON config and generates three editor-friendly documents:
1. sfx-timeline.md - timecoded placement guide
2. sfx-download-checklist.md - sourcing checklist with search terms
3. sfx-processing-notes.md - per-clip EQ, filter, and ducking instructions

Usage:
    python3 generate-sfx-map.py <config.json> <output-dir>

Example:
    python3 generate-sfx-map.py \
        ../templates/trailer-campaign-01-sfx.json \
        /path/to/campaign/music/sfx/
"""

import json
import sys
import os
from pathlib import Path
from urllib.parse import quote


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fmt_time(seconds: float, frame_rate: int = 24) -> str:
    """Convert seconds to MM:SS.FF timecode."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    frames = int((seconds - int(seconds)) * frame_rate)
    return f"{minutes:02d}:{secs:02d}:{frames:02d}"


def pixabay_sfx_url(query: str) -> str:
    return f"https://pixabay.com/sound-effects/search/{quote(query.strip(), safe='')}/"


def generate_timeline(config: dict, output_dir: Path) -> Path:
    out = output_dir / "sfx-timeline.md"
    frame_rate = config.get("frame_rate", 24)
    hard_cut = config.get("hard_cut_seconds")
    music = config.get("music_track", "N/A")
    codename = config.get("codename", "N/A")

    lines = [
        f"# SFX Timeline - {config['project_name']}",
        f"",
        f"**Codename:** `{codename}`  ",
        f"**Frame Rate:** {frame_rate}fps  ",
        f"**Music:** {music}  ",
        f"**Hard Cut:** {fmt_time(hard_cut, frame_rate) if hard_cut else 'N/A'}  ",
        f"",
        f"---",
        f"",
    ]

    # Group by scene
    scenes = {}
    for sfx in config["sfx"]:
        scene = sfx.get("scene", "Uncategorized")
        scenes.setdefault(scene, []).append(sfx)

    for scene, items in scenes.items():
        lines.append(f"## {scene}")
        lines.append("")
        lines.append("| Timecode | SFX | Mix | Visual | Notes |")
        lines.append("|----------|-----|-----|--------|-------|")

        for sfx in items:
            tc = f"{fmt_time(sfx['timestamp_start'], frame_rate)} - {fmt_time(sfx['timestamp_end'], frame_rate)}"
            mix = f"{sfx['mix_level_db']}dB ({sfx['mix_level_percent']})"
            visual = sfx.get("visual", "")
            notes = sfx.get("notes", "").replace("|", "/")
            lines.append(f"| {tc} | `{sfx['id']}` | {mix} | {visual} | {notes} |")

        lines.append("")

    # Hard cut reminder
    if hard_cut:
        lines.append("---")
        lines.append("")
        lines.append(f"## HARD CUT - {fmt_time(hard_cut, frame_rate)}")
        lines.append("")
        lines.append("**Every SFX must cut dead here. No tails. No reverb rings. The silence should feel like the air was sucked out of the room.**")
        lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def generate_checklist(config: dict, output_dir: Path) -> Path:
    out = output_dir / "sfx-download-checklist.md"
    lines = [
        f"# SFX Download Checklist - {config['project_name']}",
        f"",
        f"**Total SFX layers:** {len(config['sfx'])}  ",
        f"**Pixabay source packet:** run `source-pixabay-sfx.py --config [this config] --out [this folder]` for search links, local reuse checks, and selected-download tracking.  ",
        f"",
        f"---",
        f"",
    ]

    for sfx in config["sfx"]:
        lines.append(f"- [ ] `{sfx['id']}` - {sfx['name']}")
        lines.append(f"  - **Scene:** {sfx.get('scene', 'N/A')}")
        lines.append(f"  - **Search terms:** {', '.join(sfx.get('source_terms', []))}")
        pixabay_links = [pixabay_sfx_url(term) for term in sfx.get("source_terms", [])]
        if pixabay_links:
            lines.append(f"  - **Pixabay searches:** {', '.join(pixabay_links)}")
        lines.append(f"  - **Try first:** {', '.join(sfx.get('suggested_sources', []))}")
        lines.append(f"  - **Format:** {sfx.get('file_format', '48kHz / 24-bit WAV')}")
        lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def generate_processing_notes(config: dict, output_dir: Path) -> Path:
    out = output_dir / "sfx-processing-notes.md"
    frame_rate = config.get("frame_rate", 24)
    lines = [
        f"# SFX Processing Notes - {config['project_name']}",
        f"",
        f"**Frame Rate:** {frame_rate}fps  ",
        f"",
        f"---",
        f"",
        f"## Mix Busses",
        f"",
    ]

    for bus in config.get("mix_busses", []):
        lines.append(f"- **{bus['name']}** - default duck {bus.get('default_duck', 0)}dB to music")
    lines.append("")

    for sfx in config["sfx"]:
        lines.append(f"---")
        lines.append("")
        lines.append(f"## {sfx['name']} (`{sfx['id']}`)")
        lines.append("")
        lines.append(f"**Time:** {fmt_time(sfx['timestamp_start'], frame_rate)} - {fmt_time(sfx['timestamp_end'], frame_rate)}")
        lines.append(f"**Scene:** {sfx.get('scene', 'N/A')}")
        lines.append(f"**Mix:** {sfx['mix_level_db']}dB peak ({sfx['mix_level_percent']})")
        lines.append(f"**Duck to music:** {'Yes' if sfx.get('duck_to_music') else 'No'}")
        lines.append("")
        lines.append(f"**EQ:**")
        eq = sfx.get("eq", {})
        lines.append(f"- High-pass: {eq.get('high_pass_hz', 'N/A')}Hz")
        lines.append(f"- Low-pass: {eq.get('low_pass_hz', 'N/A')}Hz")
        if eq.get("shelf_boost_db"):
            lines.append(f"- Shelf boost: {eq['shelf_boost_db']}dB")
        lines.append("")
        lines.append(f"**Processing:**")
        for step in sfx.get("processing", []):
            lines.append(f"- {step}")
        lines.append("")
        lines.append(f"**Placement:** {sfx.get('placement', 'Stereo')}")
        if sfx.get("notes"):
            lines.append(f"**Director notes:** {sfx['notes']}")
        lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main():
    if len(sys.argv) == 2 and sys.argv[1] in {"-h", "--help"}:
        print("Usage: python3 generate-sfx-map.py <config.json> <output-dir>")
        sys.exit(0)

    if len(sys.argv) < 3:
        print("Usage: python3 generate-sfx-map.py <config.json> <output-dir>")
        sys.exit(1)

    config_path = sys.argv[1]
    output_dir = Path(sys.argv[2])

    config = load_config(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    timeline = generate_timeline(config, output_dir)
    checklist = generate_checklist(config, output_dir)
    processing = generate_processing_notes(config, output_dir)

    print(f"Generated:")
    print(f"  - {timeline}")
    print(f"  - {checklist}")
    print(f"  - {processing}")


if __name__ == "__main__":
    main()
