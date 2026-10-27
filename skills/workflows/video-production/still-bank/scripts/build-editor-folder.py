#!/usr/bin/env python3
"""
Build the editor's Finder folder from a still bank.

The bank is organised for agents: beat folders mixed with _clips, _frames,
trackers and nested source folders. The editor needs one clean folder per beat,
images only, so Finder can be kept open beside Final Cut.

Copies (never moves) every image under each beat folder into:

    <dest>/
      00-PREVIEW.jpg          contact sheet of everything, labelled
      0-HOOK-GRID/            one flat folder per beat, images only
      1-THE-READ/
      ...

Rules:
- Top-level folders starting with "_" or "." are skipped (working files).
- Nested images are flattened with their subfolder as a prefix
  ("pexels/lecture-hall_001.jpeg" -> "pexels-lecture-hall_001.jpeg").
- --pick STEM prefixes that image with PICK_.
- Refuses to write into an existing folder unless --replace is given AND the
  folder was built by this script.

Usage:
    python3 build-editor-folder.py \\
        --bank-root libraries/media/local-media/still-bank/anime-edition-04 \\
        --dest ~/Desktop/anime-edition-04-stills \\
        --pick avatar-aang-avatar-state-glow --open
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
MARKER = ".still-bank-editor-folder"
PREVIEW_NAME = "00-PREVIEW.jpg"
THUMB_W, THUMB_H, PREVIEW_COLS = 320, 180, 8


def beat_label(folder_name: str, index: int) -> str:
    match = re.match(r"^(\d+)[-_ ]+(.*)$", folder_name)
    number, rest = (int(match.group(1)), match.group(2)) if match else (index, folder_name)
    return f"{number}-{rest.upper()}"


def beat_folders(bank_root: Path) -> list[Path]:
    return sorted(
        p for p in bank_root.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))
    )


def flat_name(image: Path, beat: Path, picks: frozenset[str]) -> str:
    parts = image.relative_to(beat).parts
    name = "-".join(parts)
    return f"PICK_{name}" if image.stem in picks else name


def plan_copies(bank_root: Path, picks: frozenset[str]) -> list[tuple[Path, str, str]]:
    plan = []
    for index, beat in enumerate(beat_folders(bank_root)):
        label = beat_label(beat.name, index)
        for image in sorted(beat.rglob("*")):
            if image.suffix.lower() in IMAGE_SUFFIXES and image.is_file():
                plan.append((image, label, flat_name(image, beat, picks)))
    return plan


def prepare_dest(dest: Path, replace: bool) -> None:
    if dest.exists() and any(dest.iterdir()):
        if not replace:
            sys.exit(f"Error: {dest} already exists. Re-run with --replace to rebuild it.")
        if not (dest / MARKER).exists():
            sys.exit(f"Error: {dest} was not built by this script. Not overwritten.")
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / MARKER).write_text("built by build-editor-folder.py\n", encoding="utf-8")


def write_preview(dest: Path, copied: list[Path]) -> None:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("PIL not installed; skipping preview sheet.", file=sys.stderr)
        return
    rows = (len(copied) + PREVIEW_COLS - 1) // PREVIEW_COLS
    sheet = Image.new("RGB", (PREVIEW_COLS * THUMB_W, max(rows, 1) * THUMB_H), "black")
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(copied):
        x, y = (i % PREVIEW_COLS) * THUMB_W, (i // PREVIEW_COLS) * THUMB_H
        try:
            with Image.open(path) as im:
                thumb = im.convert("RGB")
                thumb.thumbnail((THUMB_W, THUMB_H))
                sheet.paste(thumb, (x, y))
        except OSError as exc:
            print(f"Preview skipped {path.name}: {exc}", file=sys.stderr)
        label = f"{path.parent.name}/{path.name}"[:44]
        draw.rectangle([x, y, x + THUMB_W, y + 14], fill="black")
        draw.text((x + 3, y + 1), label, fill="yellow")
    sheet.save(dest / PREVIEW_NAME, quality=85)


def build(
    bank_root: Path, dest: Path, picks: frozenset[str], replace: bool
) -> tuple[list[Path], frozenset[str]]:
    plan = plan_copies(bank_root, picks)
    if not plan:
        sys.exit(f"Error: no images found in beat folders under {bank_root}")
    prepare_dest(dest, replace)
    copied = []
    for source, label, name in plan:
        target = dest / label / name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(source, target)
        copied.append(target)
    matched = frozenset(source.stem for source, _, _ in plan) & picks
    return copied, matched


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--bank-root", required=True, type=Path)
    parser.add_argument("--dest", required=True, type=Path)
    parser.add_argument("--pick", action="append", default=[], help="image stem to mark PICK_")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--no-preview", action="store_true")
    parser.add_argument("--open", action="store_true", help="open the folder in Finder")
    args = parser.parse_args()

    bank_root, dest = args.bank_root.expanduser(), args.dest.expanduser()
    if not bank_root.is_dir():
        sys.exit(f"Error: bank root not found: {bank_root}")

    picks = frozenset(args.pick)
    copied, matched = build(bank_root, dest, picks, args.replace)
    if not args.no_preview:
        write_preview(dest, copied)

    for stem in sorted(picks - matched):
        print(f"Warning: --pick {stem} matched no image", file=sys.stderr)

    counts: dict[str, int] = {}
    for path in copied:
        counts[path.parent.name] = counts.get(path.parent.name, 0) + 1
    for label, count in sorted(counts.items()):
        print(f"{label}: {count}")
    print(f"Editor folder: {dest}")

    if args.open:
        subprocess.run(["open", str(dest)], check=False)


if __name__ == "__main__":
    main()
