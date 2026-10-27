#!/usr/bin/env python3
"""
Check a downloaded still bank for repeats, unreadable stills, and colour
clustering, then write a variety report.

Every still has to read in under a second at reel speed, under a talking-head
PiP, at 1.3-2s per cut. Anything too dark, too flat, or too close to its
neighbour is wasted. This script flags; it never deletes. You swap a flagged
pick for one of its overshoot siblings.

Two stills count as the same image only when their gradient hash AND their
4x4 colour signature both match. Hash alone is not enough: a flat or purely
vertical frame produces a degenerate hash, so a red panel and a blue panel
would otherwise look identical.

Uses ffmpeg (already required elsewhere in this repo) and falls back to Pillow.

Usage:
    python3 check-variety.py \\
      --bank-root libraries/media/local-media/still-bank/movie-edition-01 \\
      --out .../movie-edition-01-still-bank-variety-report.md
"""

from __future__ import annotations

import argparse
import colorsys
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".tiff", ".bmp"}
SLOT_RE = re.compile(r"^(shot-\d+)")
ALT_RE = re.compile(r"-alt\d+$")

DEFAULT_OVERLAP_DISTANCE = 10
DEFAULT_REPEAT_COLOR = 12.0
DEFAULT_OVERLAP_COLOR = 40.0
DEFAULT_MIN_MEAN = 28.0
DEFAULT_MIN_STDEV = 18.0
DEFAULT_COLOR_CLUSTER = 3

HASH_W, HASH_H = 9, 8
STAT_SIZE = 32
COLOR_GRID = 4


def have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def ffmpeg_raw(path: Path, width: int, height: int, pix_fmt: str) -> bytes:
    command = [
        "ffmpeg",
        "-v", "error",
        "-i", str(path),
        "-vf", f"scale={width}:{height}:flags=area,format={pix_fmt}",
        "-frames:v", "1",
        "-f", "rawvideo",
        "-pix_fmt", pix_fmt,
        "-",
    ]
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode != 0 or not result.stdout:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise ValueError(message or "ffmpeg produced no output")
    return result.stdout


def pillow_raw(path: Path, width: int, height: int, mode: str) -> bytes:
    from PIL import Image

    with Image.open(path) as image:
        return image.convert(mode).resize((width, height)).tobytes()


def sample(path: Path, width: int, height: int, gray: bool, use_ffmpeg: bool) -> bytes:
    if use_ffmpeg:
        return ffmpeg_raw(path, width, height, "gray" if gray else "rgb24")
    return pillow_raw(path, width, height, "L" if gray else "RGB")


def dhash(pixels: bytes) -> int:
    """Row-wise gradient hash over a 9x8 grayscale sample -> 64 bits."""
    bits = 0
    for row in range(HASH_H):
        offset = row * HASH_W
        for col in range(HASH_W - 1):
            bits <<= 1
            if pixels[offset + col] < pixels[offset + col + 1]:
                bits |= 1
    return bits


def hamming(left: int, right: int) -> int:
    return bin(left ^ right).count("1")


def mean_stdev(pixels: bytes) -> tuple[float, float]:
    count = len(pixels)
    mean = sum(pixels) / count
    variance = sum((value - mean) ** 2 for value in pixels) / count
    return mean, variance ** 0.5


def color_cells(pixels: bytes) -> list[tuple[int, int, int]]:
    return [
        (pixels[index], pixels[index + 1], pixels[index + 2])
        for index in range(0, len(pixels), 3)
    ]


def average_rgb(cells: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    count = len(cells)
    return tuple(round(sum(cell[channel] for cell in cells) / count) for channel in range(3))


def color_distance(left: list[list[int]], right: list[list[int]]) -> float:
    """Mean per-cell euclidean RGB distance between two colour signatures."""
    pairs = zip(left, right)
    total = sum(
        sum((a[channel] - b[channel]) ** 2 for channel in range(3)) ** 0.5
        for a, b in pairs
    )
    return total / len(left)


def color_bucket(rgb: tuple[int, int, int]) -> str:
    red, green, blue = (channel / 255 for channel in rgb)
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    if lightness < 0.16:
        return "black"
    if lightness > 0.90 and saturation < 0.20:
        return "white"
    if saturation < 0.15:
        return "grey"
    degrees = hue * 360
    for limit, name in (
        (15, "red"), (45, "orange"), (70, "yellow"), (160, "green"),
        (200, "cyan"), (255, "blue"), (290, "purple"), (335, "magenta"), (360, "red"),
    ):
        if degrees < limit:
            return name
    return "red"


def normalised_slot(name: str) -> str | None:
    match = SLOT_RE.match(name)
    if not match:
        return None
    return ALT_RE.sub("", match.group(1))


def collect_images(bank_root: Path) -> list[Path]:
    return sorted(
        path
        for path in bank_root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def measure(path: Path, bank_root: Path, use_ffmpeg: bool) -> dict:
    gray_hash = sample(path, HASH_W, HASH_H, True, use_ffmpeg)
    gray_stat = sample(path, STAT_SIZE, STAT_SIZE, True, use_ffmpeg)
    cells = color_cells(sample(path, COLOR_GRID, COLOR_GRID, False, use_ffmpeg))
    mean, stdev = mean_stdev(gray_stat)
    rgb = average_rgb(cells)
    return {
        "path": str(path),
        "relative": str(path.relative_to(bank_root)),
        "beat": path.parent.name,
        "slot": normalised_slot(path.name),
        "hash": dhash(gray_hash),
        "signature": [list(cell) for cell in cells],
        "mean": round(mean, 1),
        "stdev": round(stdev, 1),
        "rgb": list(rgb),
        "color": color_bucket(rgb),
    }


def find_pairs(
    records: list[dict],
    overlap_distance: int,
    repeat_color: float,
    overlap_color: float,
) -> tuple[list[dict], list[dict]]:
    """Split cross-slot lookalikes into hard repeats and soft overlaps."""
    repeats: list[dict] = []
    overlaps: list[dict] = []
    for index, left in enumerate(records):
        for right in records[index + 1:]:
            if left["slot"] is not None and left["slot"] == right["slot"]:
                continue
            distance = hamming(left["hash"], right["hash"])
            if distance > overlap_distance:
                continue
            delta = color_distance(left["signature"], right["signature"])
            pair = {
                "a": left["relative"],
                "b": right["relative"],
                "distance": distance,
                "color_delta": round(delta, 1),
            }
            if distance == 0 and delta <= repeat_color:
                repeats.append(pair)
            elif delta <= overlap_color:
                overlaps.append(pair)
    return repeats, sorted(overlaps, key=lambda pair: (pair["distance"], pair["color_delta"]))


def find_clusters(records: list[dict], limit: int) -> list[dict]:
    clusters: list[dict] = []
    for beat in sorted({record["beat"] for record in records}):
        in_beat = [record for record in records if record["beat"] == beat]
        for color in sorted({record["color"] for record in in_beat}):
            matching = [record for record in in_beat if record["color"] == color]
            if len(matching) >= limit:
                clusters.append(
                    {
                        "beat": beat,
                        "color": color,
                        "count": len(matching),
                        "files": [record["relative"] for record in matching],
                    }
                )
    return clusters


def render_report(payload: dict) -> str:
    lines = [
        f"# Still Bank Variety Report: {payload['slug']}",
        "",
        f"- bank_root: `{payload['bank_root']}`",
        f"- checked_at: {payload['checked_at']}",
        f"- files: {payload['counts']['files']} across {payload['counts']['beats']} beat folders",
        f"- hard flags: {payload['counts']['hard_flags']}",
        f"- advisories: {payload['counts']['advisories']}",
        "",
        "Flags are swap prompts, not deletions. Replace a flagged pick with one of its",
        "overshoot siblings, then re-run this check.",
        "",
    ]

    lines += ["## Repeats (same image in two slots)", ""]
    if payload["repeats"]:
        lines += ["| File A | File B | Colour delta |", "|--------|--------|-------------:|"]
        lines += [
            f"| `{pair['a']}` | `{pair['b']}` | {pair['color_delta']} |"
            for pair in payload["repeats"]
        ]
        lines += ["", "No still repeats inside an edition. Swap one of each pair."]
    else:
        lines.append("None. No still repeats inside this edition.")
    lines.append("")

    lines += ["## Overlaps (different slots, similar frame)", ""]
    if payload["overlaps"]:
        lines += [
            "| File A | File B | Hash distance | Colour delta |",
            "|--------|--------|--------------:|-------------:|",
        ]
        lines += [
            f"| `{pair['a']}` | `{pair['b']}` | {pair['distance']} | {pair['color_delta']} |"
            for pair in payload["overlaps"]
        ]
        lines += ["", "Pick different options for these slots, or run the alternate query."]
    else:
        lines.append("None.")
    lines.append("")

    lines += ["## Too dark to read", ""]
    if payload["dark"]:
        lines += ["| File | Mean brightness |", "|------|----------------:|"]
        lines += [f"| `{record['relative']}` | {record['mean']} |" for record in payload["dark"]]
        lines += ["", "Deep blacks are the grade. A frame with no subject left in it is not."]
    else:
        lines.append("None.")
    lines.append("")

    lines += ["## Too flat to read", ""]
    if payload["flat"]:
        lines += ["| File | Contrast |", "|------|---------:|"]
        lines += [f"| `{record['relative']}` | {record['stdev']} |" for record in payload["flat"]]
        lines += ["", "Low contrast disappears under the PiP at 1.3-2s per cut."]
    else:
        lines.append("None.")
    lines.append("")

    lines += ["## Dominant colour clustering", ""]
    if payload["clusters"]:
        lines += ["| Beat | Colour | Count | Files |", "|------|--------|------:|-------|"]
        lines += [
            f"| {cluster['beat']} | {cluster['color']} | {cluster['count']} | "
            + ", ".join(f"`{name}`" for name in cluster["files"])
            + " |"
            for cluster in payload["clusters"]
        ]
        lines += [
            "",
            "Hook panels especially: one dominant colour each, or the 2x2 reads as mush.",
        ]
    else:
        lines.append("None.")
    lines.append("")

    lines += ["## Per-beat inventory", "", "| Beat | Files | Colours |", "|------|------:|---------|"]
    for beat in sorted({record["beat"] for record in payload["records"]}):
        in_beat = [record for record in payload["records"] if record["beat"] == beat]
        colors = sorted({record["color"] for record in in_beat})
        lines.append(f"| {beat} | {len(in_beat)} | {', '.join(colors)} |")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a still bank for repeats and readability.")
    parser.add_argument("--bank-root", required=True, help="Edition folder under local-media/still-bank/")
    parser.add_argument("--out", help="Write the markdown report here (default: stdout)")
    parser.add_argument("--json", dest="json_out", help="Also write the raw measurements here")
    parser.add_argument("--slug", help="Edition slug (default: bank root folder name)")
    parser.add_argument("--overlap-distance", type=int, default=DEFAULT_OVERLAP_DISTANCE)
    parser.add_argument("--repeat-color-distance", type=float, default=DEFAULT_REPEAT_COLOR)
    parser.add_argument("--overlap-color-distance", type=float, default=DEFAULT_OVERLAP_COLOR)
    parser.add_argument("--min-mean", type=float, default=DEFAULT_MIN_MEAN)
    parser.add_argument("--min-stdev", type=float, default=DEFAULT_MIN_STDEV)
    parser.add_argument("--color-cluster", type=int, default=DEFAULT_COLOR_CLUSTER)
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Always exit 0, even when repeats are found",
    )
    args = parser.parse_args()

    bank_root = Path(args.bank_root)
    if not bank_root.is_dir():
        print(f"Error: bank root not found: {bank_root}", file=sys.stderr)
        return 2

    images = collect_images(bank_root)
    if not images:
        print(f"Error: no image files under {bank_root}", file=sys.stderr)
        return 2

    use_ffmpeg = have_ffmpeg()
    records: list[dict] = []
    failures: list[str] = []
    for path in images:
        try:
            records.append(measure(path, bank_root, use_ffmpeg))
        except (ValueError, OSError, ImportError) as exc:
            failures.append(f"{path}: {exc}")

    for failure in failures:
        print(f"Warning: could not measure {failure}", file=sys.stderr)

    if not records:
        print("Error: no images could be measured", file=sys.stderr)
        return 2

    repeats, overlaps = find_pairs(
        records,
        args.overlap_distance,
        args.repeat_color_distance,
        args.overlap_color_distance,
    )
    dark = [record for record in records if record["mean"] < args.min_mean]
    flat = [record for record in records if record["stdev"] < args.min_stdev]
    clusters = find_clusters(records, args.color_cluster)

    payload = {
        "slug": args.slug or bank_root.name,
        "bank_root": str(bank_root),
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "thresholds": {
            "overlap_distance": args.overlap_distance,
            "repeat_color_distance": args.repeat_color_distance,
            "overlap_color_distance": args.overlap_color_distance,
            "min_mean": args.min_mean,
            "min_stdev": args.min_stdev,
            "color_cluster": args.color_cluster,
        },
        "counts": {
            "files": len(records),
            "beats": len({record["beat"] for record in records}),
            "hard_flags": len(repeats),
            "advisories": len(overlaps) + len(dark) + len(flat) + len(clusters),
            "unreadable": len(failures),
        },
        "repeats": repeats,
        "overlaps": overlaps,
        "dark": dark,
        "flat": flat,
        "clusters": clusters,
        "records": records,
    }

    report = render_report(payload)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Wrote {out_path}")
    else:
        sys.stdout.write(report)

    if args.json_out:
        json_path = Path(args.json_out)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"Wrote {json_path}")

    counts = payload["counts"]
    print(
        f"{counts['files']} stills, {counts['hard_flags']} repeats, "
        f"{counts['advisories']} advisories",
        file=sys.stderr,
    )

    if repeats and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
