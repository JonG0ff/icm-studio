#!/usr/bin/env python3
"""
Turn a downloaded still bank into the three tracked outputs: the human map, the
on-disk inventory, and the asset-manifest rows.

Files on disk are the source of truth. Tracker files and sidecars written by the
media-sourcing scripts supply the source URL, query, and rights metadata.

Markdown tracks the run. JSON is script I/O only; no status lives in JSON.

Stdlib only.

Usage:
    python3 build-bank-outputs.py \\
      --shot-brief .../movie-edition-01-shot-brief.json \\
      --bank-root libraries/media/local-media/still-bank/movie-edition-01 \\
      --out workspaces/video-production/stages/03-asset-gathering/output
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".tiff", ".bmp"}
SLOT_RE = re.compile(r"^(shot-\d+)")
ALT_RE = re.compile(r"-alt\d+$")
LETTERS = "abcdefghijklmnopqrstuvwxyz"
NONE = "—"

PEXELS_TRACKER = "download-tracker.json"
WEB_STILL_TRACKER = "web-still-download-tracker.json"
COMMONS_TRACKER = "commons-category-tracker.json"

RIGHTS_BY_METHOD = {
    "pexels": "licensed",
    "web-still": "unclear",
    "commons": "public",
    "library-reuse": "licensed",
    "generation": "generated",
}

RIGHTS_NOTE_BY_METHOD = {
    "pexels": "Pexels License. Source page and photographer recorded.",
    "web-still": "Web still. Source URL recorded; rights unclear. Swap from the sidecar URL if a post is pulled.",
    "commons": "Wikimedia Commons. File page, creator, and licence recorded.",
    "library-reuse": "Reused media-library record. Rights carried from the record.",
    "generation": "Generated image. Prompt, tool, and approval date required before ready.",
    "unknown": "Source metadata missing. Record the source URL before edit lock.",
}


BARE_RIGHTS = {
    "public",
    "owned",
    "licensed",
    "generated",
    "pending",
    "internal-reference-only",
    "unclear",
}


def expand_rights_note(note: str | None, method: str) -> str:
    """The manifest wants a sentence. Sidecars often store a bare vocabulary word."""
    fallback = RIGHTS_NOTE_BY_METHOD.get(method, RIGHTS_NOTE_BY_METHOD["unknown"])
    if not note or note.strip().lower() in BARE_RIGHTS:
        return fallback
    return note


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_if_present(path: Path):
    if not path.is_file():
        return None
    try:
        return load_json(path)
    except (OSError, json.JSONDecodeError):
        return None


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


def index_pexels(folder: Path) -> dict[str, dict]:
    """Map filename -> pexels tracker entry for one beat folder."""
    tracker = read_json_if_present(folder / PEXELS_TRACKER)
    if not isinstance(tracker, dict):
        return {}
    return {
        entry["filename"]: entry
        for entries in tracker.values()
        if isinstance(entries, list)
        for entry in entries
        if isinstance(entry, dict) and entry.get("filename")
    }


def index_tracker_list(folder: Path, filename: str) -> dict[str, dict]:
    """Map local filename -> tracker entry for list-shaped trackers."""
    tracker = read_json_if_present(folder / filename)
    if not isinstance(tracker, list):
        return {}
    indexed = {}
    for entry in tracker:
        if not isinstance(entry, dict):
            continue
        local = entry.get("local_path") or entry.get("filename")
        if local:
            indexed[Path(local).name] = entry
    return indexed


def describe(path: Path, folder_index: dict) -> dict:
    """Resolve method, query, and source URLs for one file on disk."""
    sidecar = read_json_if_present(path.with_suffix(".json")) or {}
    name = path.name

    if sidecar.get("url"):
        return {
            "method": "web-still",
            "query": sidecar.get("query") or "",
            "source_url": sidecar.get("final_url") or sidecar.get("url"),
            "source_page": sidecar.get("url"),
            "rights_note": expand_rights_note(sidecar.get("rights_note"), "web-still"),
            "credit": None,
            "licence": None,
        }

    pexels = folder_index["pexels"].get(name)
    if pexels:
        return {
            "method": "pexels",
            "query": pexels.get("query") or "",
            "source_url": pexels.get("url") or "",
            "source_page": pexels.get("url") or "",
            "rights_note": RIGHTS_NOTE_BY_METHOD["pexels"],
            "credit": pexels.get("photographer"),
            "licence": "Pexels License",
        }

    commons = folder_index["commons"].get(name)
    if commons:
        licence = commons.get("license")
        creator = commons.get("creator")
        return {
            "method": "commons",
            "query": commons.get("subject") or "",
            "source_url": commons.get("thumb_url") or "",
            "source_page": commons.get("source_page") or "",
            "rights_note": expand_rights_note(commons.get("rights_note"), "commons"),
            "credit": creator,
            "licence": licence,
        }

    web = folder_index["web"].get(name)
    if web:
        return {
            "method": "web-still",
            "query": web.get("query") or "",
            "source_url": web.get("final_url") or web.get("url") or "",
            "source_page": web.get("url") or "",
            "rights_note": expand_rights_note(web.get("rights_note"), "web-still"),
            "credit": None,
            "licence": None,
        }

    return {
        "method": "unknown",
        "query": "",
        "source_url": "",
        "source_page": "",
        "rights_note": RIGHTS_NOTE_BY_METHOD["unknown"],
        "credit": None,
        "licence": None,
    }


def status_for(method: str, meta: dict) -> str:
    if method == "commons":
        if meta.get("licence") and meta.get("credit"):
            return "ready"
        return "needs-approval"
    if method == "unknown":
        return "needs-approval"
    if method == "generation":
        return "queued-generation"
    return "ready"


def gather_candidates(bank_root: Path, slug: str) -> dict[str, list[dict]]:
    """Group every image on disk by slot, in sorted order, lettered a..z."""
    by_slot: dict[str, list[dict]] = {}
    folder_cache: dict[Path, dict] = {}

    for path in collect_images(bank_root):
        slot = normalised_slot(path.name)
        if slot is None:
            continue
        folder = path.parent
        if folder not in folder_cache:
            folder_cache[folder] = {
                "pexels": index_pexels(folder),
                "web": index_tracker_list(folder, WEB_STILL_TRACKER),
                "commons": index_tracker_list(folder, COMMONS_TRACKER),
            }
        meta = describe(path, folder_cache[folder])
        by_slot.setdefault(slot, []).append(
            {
                **meta,
                "slot": slot,
                "filename": path.name,
                "local_path": str(path),
                "relative": str(path.relative_to(bank_root)),
                "bytes": path.stat().st_size,
            }
        )

    return {
        slot: [
            {
                **candidate,
                "option": LETTERS[index] if index < len(LETTERS) else str(index + 1),
                "asset_id": f"ST-{slot.split('-')[1]}"
                + (LETTERS[index] if index < len(LETTERS) else str(index + 1)),
                "status": status_for(candidate["method"], candidate),
                "rights": RIGHTS_BY_METHOD.get(candidate["method"], "pending"),
            }
            for index, candidate in enumerate(
                sorted(candidates, key=lambda item: item["filename"])
            )
        ]
        for slot, candidates in by_slot.items()
    }


def read_picks(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError('Picks must be a JSON object of {"shot-13": "b"}')
    return {str(key): str(value) for key, value in data.items()}


def choose(candidates: list[dict], wanted: str | None) -> dict | None:
    if not candidates:
        return None
    if wanted:
        for candidate in candidates:
            if wanted in (candidate["option"], candidate["filename"], candidate["asset_id"]):
                return candidate
    return candidates[0]


def scene_label(brief: dict) -> str:
    if brief["kind"] == "hook":
        return f"Hook grid, {brief.get('panel', '').replace('-', ' ')}"
    timecode = brief.get("t")
    return f"{brief['beat_title']}, {timecode}" if timecode else brief["beat_title"]


def plan_lookup(search_plan: dict | None) -> dict[str, dict]:
    if not search_plan:
        return {}
    return {row["slot"]: row for row in search_plan.get("rows", []) if row.get("slot")}


def build_rows(brief_doc: dict, by_slot: dict, picks: dict, plan: dict) -> list[dict]:
    """One row per brief: the picked candidate, or the gap that needs closing."""
    rows = []
    for brief in brief_doc["briefs"]:
        slot = brief["slot"]
        candidates = by_slot.get(slot, [])
        pick = choose(candidates, picks.get(slot))
        planned = plan.get(slot, {})
        number = slot.split("-")[1]

        if pick is None:
            method = planned.get("method") or "unknown"
            if method == "library-reuse" and planned.get("library_id"):
                status, rights = "ready", RIGHTS_BY_METHOD["library-reuse"]
            elif method == "generation":
                status, rights = "queued-generation", RIGHTS_BY_METHOD["generation"]
            else:
                status, rights = "needs-source", "pending"
            rows.append(
                {
                    "asset_id": f"ST-{number}",
                    "slot": slot,
                    "brief": brief,
                    "pick": None,
                    "alternates": [],
                    "method": method,
                    "status": status,
                    "rights": rights,
                    "rights_note": RIGHTS_NOTE_BY_METHOD.get(method, RIGHTS_NOTE_BY_METHOD["unknown"]),
                    "library_id": planned.get("library_id"),
                    "reason": planned.get("reason"),
                }
            )
            continue

        rows.append(
            {
                "asset_id": pick["asset_id"],
                "slot": slot,
                "brief": brief,
                "pick": pick,
                "alternates": [c["asset_id"] for c in candidates if c is not pick],
                "method": pick["method"],
                "status": pick["status"],
                "rights": pick["rights"],
                "rights_note": pick["rights_note"],
                "library_id": planned.get("library_id"),
                "reason": None,
            }
        )
    return rows


def next_action(row: dict) -> str:
    if row["pick"] is None:
        if row["status"] == "queued-generation":
            return "Gated. Present at the Stage 03 checkpoint before spending credits."
        if row["status"] == "ready":
            return "Pull the file from the media-library record."
        return "Source this slot. No candidate on disk."
    if row["status"] == "needs-approval":
        return "Record licence and creator, or swap for another candidate."
    return "Import to Final Cut. Crop to 9:16 and grade."


def render_manifest_rows(rows: list[dict]) -> list[str]:
    lines = [
        "| Asset ID | Scene / Beat | Type | Need | Library ID | Source path / URL / prompt | Status | Rights note | Fallback | Next action |",
        "|----------|--------------|------|------|------------|----------------------------|--------|-------------|----------|-------------|",
    ]
    for row in rows:
        pick = row["pick"]
        if pick:
            source = f"`{pick['local_path']}`"
            if pick.get("source_page"):
                source += f" — {pick['source_page']}"
        elif row["library_id"]:
            source = f"Library record `{row['library_id']}`"
        elif row["reason"]:
            source = f"Generation: {row['reason']}"
        else:
            source = "Not sourced"

        asset_type = "generated-image" if row["method"] == "generation" else "still"
        fallback = ", ".join(row["alternates"]) if row["alternates"] else "Re-run the alternate query"
        lines.append(
            f"| {row['asset_id']} | {scene_label(row['brief'])} | {asset_type} "
            f"| {row['brief']['brief']} | {row['library_id'] or NONE} | {source} "
            f"| {row['status']} | {row['rights_note']} | {fallback} | {next_action(row)} |"
        )
    return lines


def render_readiness(rows: list[dict]) -> list[str]:
    statuses = [row["status"] for row in rows]
    order = (
        "ready",
        "needs-approval",
        "queued-generation",
        "needs-source",
        "needs-generation",
        "blocked",
    )
    return [f"- {status}: {statuses.count(status)}" for status in order]


def render_map(slug: str, brief_doc: dict, by_slot: dict, rows: list[dict], bank_root: Path) -> str:
    picked = {row["slot"]: row["asset_id"] for row in rows if row["pick"]}
    briefs = {brief["slot"]: brief for brief in brief_doc["briefs"]}
    on_disk = sum(len(candidates) for candidates in by_slot.values())

    lines = [
        f"# Still Bank Map: {slug}",
        "",
        f"- purpose: full-frame 9:16 stills behind the talking-head PiP",
        f"- locked_script: `{brief_doc.get('source', '')}`",
        f"- local root: `{bank_root}`",
        f"- slots: {len(briefs)} | candidates on disk: {on_disk} | picked: {len(picked)}",
        f"- built: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "",
        "Pick column marks the still that goes in the cut. The other candidates stay on",
        "disk as the swap pool. Crop to 9:16 and grade in Final Cut.",
        "",
    ]

    for beat in brief_doc["beats"]:
        lines += [
            f"## {beat['title']}" + (f" — `{beat['window']}`" if beat.get("window") else ""),
            "",
            f"Folder: `{beat['folder']}/`",
            "",
            "| ID | Brief | Search query | Method | Source URL | Local path | Pick |",
            "|----|-------|--------------|--------|------------|------------|------|",
        ]
        for slot in beat["slots"]:
            brief = briefs[slot]
            candidates = by_slot.get(slot, [])
            if not candidates:
                lines.append(
                    f"| {slot} | {brief['brief']} | {NONE} | {NONE} | {NONE} "
                    f"| **not sourced** | {NONE} |"
                )
                continue
            for candidate in candidates:
                mark = "**pick**" if candidate["asset_id"] == picked.get(slot) else ""
                source = candidate.get("source_page") or candidate.get("source_url") or NONE
                lines.append(
                    f"| {candidate['asset_id']} | {brief['brief']} | {candidate['query'] or NONE} "
                    f"| {candidate['method']} | {source} | `{candidate['relative']}` | {mark} |"
                )
        lines.append("")

    return "\n".join(lines)


def render_manifest(slug: str, brief_doc: dict, rows: list[dict], bank_root: Path) -> str:
    return "\n".join(
        [
            f"# Asset Manifest: {slug}",
            "",
            f"- slug: {slug}",
            f"- locked_script: {brief_doc.get('source', '')}",
            "- media_library: ../../../../../libraries/media/assets/index.md",
            f"- still_bank: `{bank_root}`",
            f"- map: {slug}-still-bank-map.md",
            f"- variety_report: {slug}-still-bank-variety-report.md",
            "",
            "## Source Readiness Summary",
            "",
            *render_readiness(rows),
            "",
            "## Asset Table",
            "",
            *render_manifest_rows(rows),
            "",
            "## Source And Rights Notes",
            "",
            "- Pexels stills: Pexels License. Source page and photographer are in the map.",
            "- Web stills: `rights_note: unclear`. File on disk is usable in Final Cut; the",
            "  sidecar keeps the source URL so a still can be swapped if a reel is pulled.",
            "- Wikimedia Commons stills: not `ready` until file page, creator, licence,",
            "  licence URL, and attribution requirement are recorded.",
            "",
            "## Gaps",
            "",
            "| Gap | Blocks the edit? | Owner | Next action |",
            "|-----|------------------|-------|-------------|",
            *[
                f"| {row['asset_id']} {row['brief']['brief']} | yes | | {next_action(row)} |"
                for row in rows
                if row["status"] in {"needs-source", "blocked"}
            ],
            "",
            "## Media Library Promotions",
            "",
            "Promote reusable stills after the checkpoint, using",
            "`../../../../../libraries/media/shared/asset-record-format.md`.",
            "",
            "## Edit Readiness Gate",
            "",
            "- [ ] Every slot in the shot brief has a row.",
            "- [ ] The media library was checked before new sourcing.",
            "- [ ] Every external still has a source and rights note.",
            "- [ ] The variety report shows zero repeats.",
            "- [ ] Commons rows record file page, creator, licence, and attribution.",
            "- [ ] Generation rows are approved before any credits are spent.",
            "",
        ]
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the still-bank map, inventory, and asset-manifest rows."
    )
    parser.add_argument("--shot-brief", required=True)
    parser.add_argument("--bank-root", required=True)
    parser.add_argument("--out", required=True, help="Stage 03 output directory")
    parser.add_argument("--picks", help='JSON object of {"shot-13": "b"}')
    parser.add_argument("--search-plan", help="Search plan JSON from build-search-configs.py")
    parser.add_argument(
        "--write-manifest",
        action="store_true",
        help="Also write a full asset manifest when one does not already exist",
    )
    args = parser.parse_args()

    bank_root = Path(args.bank_root)
    if not bank_root.is_dir():
        print(f"Error: bank root not found: {bank_root}", file=sys.stderr)
        return 2

    try:
        brief_doc = load_json(Path(args.shot_brief))
        picks = read_picks(Path(args.picks) if args.picks else None)
        search_plan = load_json(Path(args.search_plan)) if args.search_plan else None
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    slug = brief_doc.get("slug") or bank_root.name
    by_slot = gather_candidates(bank_root, slug)
    rows = build_rows(brief_doc, by_slot, picks, plan_lookup(search_plan))

    out_dir = Path(args.out)
    inventory = [
        {
            **candidate,
            "pick": any(row["pick"] is candidate for row in rows),
            "beat": next(
                (b["beat"] for b in brief_doc["briefs"] if b["slot"] == candidate["slot"]),
                None,
            ),
        }
        for candidates in by_slot.values()
        for candidate in candidates
    ]

    inventory_path = out_dir / f"{slug}-still-bank-on-disk.json"
    write_text(inventory_path, json.dumps(inventory, indent=2, ensure_ascii=False))

    map_path = out_dir / f"{slug}-still-bank-map.md"
    write_text(map_path, render_map(slug, brief_doc, by_slot, rows, bank_root))

    rows_path = out_dir / f"{slug}-still-bank-manifest-rows.md"
    write_text(
        rows_path,
        "\n".join(
            [
                f"# Still Bank Manifest Rows: {slug}",
                "",
                "Merge these rows into the Asset Table of",
                f"`{slug}-asset-manifest.md`. They cover stills only; voiceover, music,",
                "SFX, and overlays are other skills' rows.",
                "",
                "## Source Readiness Summary (stills)",
                "",
                *render_readiness(rows),
                "",
                "## Rows",
                "",
                *render_manifest_rows(rows),
                "",
            ]
        ),
    )

    written = [inventory_path, map_path, rows_path]

    manifest_path = out_dir / f"{slug}-asset-manifest.md"
    if args.write_manifest:
        if manifest_path.exists():
            print(
                f"Manifest already exists, not overwritten: {manifest_path}\n"
                f"Merge the rows from {rows_path.name} by hand.",
                file=sys.stderr,
            )
        else:
            write_text(manifest_path, render_manifest(slug, brief_doc, rows, bank_root))
            written.append(manifest_path)

    for path in written:
        print(f"Wrote {path}")

    statuses = [row["status"] for row in rows]
    print()
    print(f"  slots: {len(rows)}")
    print(f"  candidates on disk: {len(inventory)}")
    for status in sorted(set(statuses)):
        print(f"  {status}: {statuses.count(status)}")

    unsourced = [row["asset_id"] for row in rows if row["status"] == "needs-source"]
    if unsourced:
        print(f"\nUnsourced slots: {', '.join(unsourced)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
