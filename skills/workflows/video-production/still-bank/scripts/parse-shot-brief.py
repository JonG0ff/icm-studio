#!/usr/bin/env python3
"""
Parse the Hook Grid and B-Roll sections of a locked script into a structured
shot brief.

The locked script is the input to a still-bank run. This script turns its
numbered, timecoded briefs into JSON so query planning, downloading, and
manifest building all key off the same slot IDs.

Stdlib only.

Usage:
    python3 parse-shot-brief.py \\
      --script workspaces/video-production/stages/01-script-lock/output/movie-edition-01-locked-script.md \\
      --out workspaces/video-production/stages/03-asset-gathering/output/movie-edition-01-shot-brief.json

Slot IDs are global and stable: shot-01..shot-40 for body stills in script
order, then the hook panels in top-left, top-right, bottom-left, bottom-right
order. Filenames on disk use the slot, so a folder listing sorts by beat.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BODY_STILL_TARGET = 40
HOOK_PANEL_TARGET = 4

HOOK_PANELS = (
    ("top-left", "top left"),
    ("top-right", "top right"),
    ("bottom-left", "bottom left"),
    ("bottom-right", "bottom right"),
)

HEADING_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$")
BEAT_RE = re.compile(r"^\*\*(?P<title>.+?)\*\*(?P<rest>.*)$")
WINDOW_RE = re.compile(r"`(?P<window>[0-9][0-9:.]*\s*[–—-]\s*[0-9][0-9:.]*)`")
SEPARATOR_RE = re.compile(r"^[\s|:\-]+$")
NUMBER_RE = re.compile(r"^\d+$")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def strip_code(text: str) -> str:
    return text.replace("`", "").strip()


def section_lines(lines: list[str], heading: str) -> list[str]:
    """Return the lines under a `## heading`, stopping at the next `## `."""
    wanted = heading.strip().lower()
    collected: list[str] = []
    inside = False
    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            if inside:
                break
            inside = match.group("title").strip().lower() == wanted
            continue
        if inside:
            collected.append(line)
    return collected


def table_cells(line: str) -> list[str] | None:
    """Split a markdown table row into cells. Returns None for non-rows."""
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    if SEPARATOR_RE.match(stripped):
        return None
    inner = stripped.strip("|")
    return [cell.strip() for cell in inner.split("|")]


def parse_hook_grid(lines: list[str]) -> list[dict]:
    """Read the `| Panel | Brief |` table into four ordered panel briefs."""
    by_label = {}
    for line in lines:
        cells = table_cells(line)
        if not cells or len(cells) < 2:
            continue
        label = cells[0].strip().lower()
        brief = cells[1].strip()
        if label in {"panel", ""} or not brief:
            continue
        by_label[label] = brief

    panels = []
    for slug, label in HOOK_PANELS:
        brief = by_label.get(label)
        if brief is None:
            continue
        panels.append({"panel": slug, "label": label, "brief": brief})
    return panels


def parse_b_roll(lines: list[str]) -> tuple[list[dict], list[dict]]:
    """Read the beat-grouped B-roll tables. Handles 3-column and 2-column rows."""
    beats: list[dict] = []
    rows: list[dict] = []
    current: dict | None = None

    for line in lines:
        beat_match = BEAT_RE.match(line.strip())
        if beat_match:
            title = beat_match.group("title").strip()
            window_match = WINDOW_RE.search(beat_match.group("rest"))
            current = {
                "beat": slugify(title),
                "title": title,
                "window": window_match.group("window").strip() if window_match else None,
            }
            beats.append(current)
            continue

        cells = table_cells(line)
        if not cells or current is None:
            continue
        if not NUMBER_RE.match(cells[0]):
            continue

        number = int(cells[0])
        if len(cells) >= 3:
            timecode = strip_code(cells[1]) or None
            brief = cells[2].strip()
        else:
            timecode = None
            brief = cells[1].strip()
        if not brief:
            continue

        rows.append(
            {
                "n": number,
                "beat": current["beat"],
                "beat_title": current["title"],
                "t": timecode,
                "brief": brief,
            }
        )

    used = {row["beat"] for row in rows}
    return [beat for beat in beats if beat["beat"] in used], rows


def folder_for(index: int, beat_slug: str) -> str:
    return f"{index:02d}-{beat_slug}"


def build_brief(script_path: Path, slug: str) -> dict:
    lines = script_path.read_text(encoding="utf-8").splitlines()

    hook_panels = parse_hook_grid(section_lines(lines, "Hook Grid"))
    beats, body_rows = parse_b_roll(section_lines(lines, "B-Roll"))

    beat_folders = {
        beat["beat"]: folder_for(index + 1, beat["beat"])
        for index, beat in enumerate(beats)
    }

    body_briefs = [
        {
            "slot": f"shot-{row['n']:02d}",
            "n": row["n"],
            "kind": "body",
            "beat": row["beat"],
            "beat_title": row["beat_title"],
            "folder": beat_folders[row["beat"]],
            "t": row["t"],
            "brief": row["brief"],
        }
        for row in body_rows
    ]

    highest = max((brief["n"] for brief in body_briefs), default=0)
    hook_briefs = [
        {
            "slot": f"shot-{highest + index + 1:02d}",
            "n": highest + index + 1,
            "kind": "hook",
            "beat": "hook-grid",
            "beat_title": "Hook grid",
            "folder": "hook-grid",
            "panel": panel["panel"],
            "t": None,
            "brief": panel["brief"],
        }
        for index, panel in enumerate(hook_panels)
    ]

    all_beats = [
        {
            "beat": beat["beat"],
            "title": beat["title"],
            "window": beat["window"],
            "folder": beat_folders[beat["beat"]],
            "slots": [b["slot"] for b in body_briefs if b["beat"] == beat["beat"]],
        }
        for beat in beats
    ]
    if hook_briefs:
        all_beats = [
            {
                "beat": "hook-grid",
                "title": "Hook grid",
                "window": None,
                "folder": "hook-grid",
                "slots": [b["slot"] for b in hook_briefs],
            }
        ] + all_beats

    return {
        "slug": slug,
        "source": str(script_path),
        "parsed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": {
            "body": len(body_briefs),
            "hook": len(hook_briefs),
            "total": len(body_briefs) + len(hook_briefs),
        },
        "beats": all_beats,
        "briefs": body_briefs + hook_briefs,
    }


def validate(brief: dict) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Errors mean the parse is unusable."""
    errors: list[str] = []
    warnings: list[str] = []

    body = [b for b in brief["briefs"] if b["kind"] == "body"]
    numbers = [b["n"] for b in body]

    duplicates = sorted({n for n in numbers if numbers.count(n) > 1})
    if duplicates:
        errors.append(f"Duplicate B-roll numbers: {duplicates}")

    if numbers:
        expected = list(range(1, max(numbers) + 1))
        missing = sorted(set(expected) - set(numbers))
        if missing:
            errors.append(f"Gaps in B-roll numbering: {missing}")

    slots = [b["slot"] for b in brief["briefs"]]
    if len(slots) != len(set(slots)):
        errors.append("Duplicate slot IDs after numbering")

    if not body:
        errors.append("No B-roll rows found. Check the `## B-Roll` heading.")

    if len(body) != BODY_STILL_TARGET:
        warnings.append(
            f"Found {len(body)} body stills; the locked format calls for {BODY_STILL_TARGET}."
        )

    hooks = [b for b in brief["briefs"] if b["kind"] == "hook"]
    if len(hooks) != HOOK_PANEL_TARGET:
        warnings.append(
            f"Found {len(hooks)} hook panels; the locked format calls for {HOOK_PANEL_TARGET}."
        )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse a locked script's Hook Grid and B-Roll sections into a shot brief JSON."
    )
    parser.add_argument("--script", required=True, help="Path to the locked script markdown")
    parser.add_argument("--out", help="Write JSON here (default: stdout)")
    parser.add_argument(
        "--slug",
        help="Edition slug (default: derived from the script filename)",
    )
    args = parser.parse_args()

    script_path = Path(args.script)
    if not script_path.is_file():
        print(f"Error: script not found: {script_path}", file=sys.stderr)
        return 2

    slug = args.slug or re.sub(r"-locked-script$", "", script_path.stem)

    try:
        brief = build_brief(script_path, slug)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    errors, warnings = validate(brief)
    for warning in warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    for error in errors:
        print(f"Error: {error}", file=sys.stderr)
    if errors:
        return 1

    payload = json.dumps(brief, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload, encoding="utf-8")
        counts = brief["counts"]
        print(
            f"Parsed {counts['body']} body stills and {counts['hook']} hook panels "
            f"across {len(brief['beats'])} beats -> {out_path}"
        )
    else:
        sys.stdout.write(payload)

    return 0


if __name__ == "__main__":
    sys.exit(main())
