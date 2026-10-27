#!/usr/bin/env python3
"""
Validate an agent-written query plan against a shot brief, then fan it out into
the config files the media-sourcing scripts already accept.

This script does not invent queries. Query writing is judgment work and stays
with the agent, guided by `../references/query-patterns.md`. This script checks
coverage, enforces the overshoot rule, and packages the result.

Stdlib only.

Usage:
    python3 build-search-configs.py \\
      --shot-brief .../movie-edition-01-shot-brief.json \\
      --queries .../movie-edition-01-queries.json \\
      --out .../still-bank-configs/movie-edition-01

Query plan shape (a JSON array, or an object with a "plan" array):

    [
      {"slot": "shot-01", "method": "pexels",
       "queries": ["dark cinema audience from behind screen glow", "...", "..."]},
      {"slot": "shot-33", "method": "web-still", "queries": ["...", "...", "..."]},
      {"slot": "shot-25", "method": "commons", "subject": "Clapperboard",
       "categories": ["Category:Clapperboards"], "queries": ["...", "...", "..."]},
      {"slot": "shot-07", "method": "library-reuse", "library_id": "ml-2026-06-30-..."}
    ]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SEARCH_METHODS = ("pexels", "web-still", "commons")
STATIC_METHODS = ("library-reuse", "generation")
VALID_METHODS = SEARCH_METHODS + STATIC_METHODS

DEFAULT_MIN_QUERIES = 3
DEFAULT_PER_SLOT = 3


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_plan(path: Path) -> list[dict]:
    data = load_json(path)
    entries = data.get("plan") if isinstance(data, dict) else data
    if not isinstance(entries, list):
        raise ValueError('Query plan must be a JSON array, or an object with a "plan" array')
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"Plan entry {index} must be an object")
    return entries


def validate(plan: list[dict], briefs: list[dict], min_queries: int) -> list[str]:
    """Return a list of human-readable errors. Empty means the plan is usable."""
    errors: list[str] = []
    brief_slots = [b["slot"] for b in briefs]
    plan_slots = [entry.get("slot") for entry in plan]

    unknown = sorted({s for s in plan_slots if s not in set(brief_slots)})
    if unknown:
        errors.append(f"Plan covers slots that are not in the shot brief: {unknown}")

    missing = [s for s in brief_slots if s not in set(plan_slots)]
    if missing:
        errors.append(f"Shot brief slots with no plan entry: {missing}")

    duplicates = sorted({s for s in plan_slots if plan_slots.count(s) > 1})
    if duplicates:
        errors.append(f"Slots planned more than once: {duplicates}")

    for entry in plan:
        slot = entry.get("slot", "<missing slot>")
        method = entry.get("method")
        if method not in VALID_METHODS:
            errors.append(f"{slot}: method {method!r} is not one of {list(VALID_METHODS)}")
            continue

        queries = entry.get("queries") or []
        if not isinstance(queries, list) or any(not isinstance(q, str) or not q.strip() for q in queries):
            errors.append(f"{slot}: queries must be a list of non-empty strings")
            continue

        if method in SEARCH_METHODS and len(queries) < min_queries:
            errors.append(
                f"{slot}: {len(queries)} queries, needs at least {min_queries} "
                "(overshoot rule — the extras are the swap pool)"
            )
        if method == "commons" and not entry.get("categories"):
            errors.append(f"{slot}: commons entries need a non-empty categories list")
        if method == "library-reuse" and not entry.get("library_id"):
            errors.append(f"{slot}: library-reuse entries need a library_id")
        if method == "generation" and not entry.get("reason"):
            errors.append(
                f"{slot}: generation entries need a reason recording why tiers 1-3 cannot serve it"
            )

    return errors


def merge(plan: list[dict], briefs: list[dict]) -> list[dict]:
    """Join each brief with its plan entry. Returns new records."""
    by_slot = {entry["slot"]: entry for entry in plan}
    return [
        {
            **brief,
            "method": by_slot[brief["slot"]].get("method"),
            "queries": list(by_slot[brief["slot"]].get("queries") or []),
            "categories": list(by_slot[brief["slot"]].get("categories") or []),
            "subject": by_slot[brief["slot"]].get("subject") or brief["brief"],
            "library_id": by_slot[brief["slot"]].get("library_id"),
            "reason": by_slot[brief["slot"]].get("reason"),
        }
        for brief in briefs
    ]


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_pexels_configs(rows: list[dict], out_dir: Path, per_slot: int) -> list[Path]:
    """One config per beat folder: primary query at full count, alternates suffixed."""
    written: list[Path] = []
    folders = sorted({row["folder"] for row in rows})
    for folder in folders:
        in_folder = [row for row in rows if row["folder"] == folder]
        if not in_folder:
            continue
        primary = [
            {"shot_id": row["slot"], "query": row["queries"][0], "count": per_slot}
            for row in in_folder
        ]
        alternates = [
            {"shot_id": f"{row['slot']}-alt{index}", "query": query, "count": per_slot}
            for row in in_folder
            for index, query in enumerate(row["queries"][1:], start=1)
        ]
        primary_path = out_dir / "pexels" / f"{folder}.searches.json"
        write_json(primary_path, primary)
        written.append(primary_path)
        if alternates:
            alt_path = out_dir / "pexels" / f"{folder}.alt-searches.json"
            write_json(alt_path, alternates)
            written.append(alt_path)
    return written


def write_commons_config(rows: list[dict], out_dir: Path) -> Path | None:
    if not rows:
        return None
    payload = [
        {"section": row["slot"], "subject": row["subject"], "categories": row["categories"]}
        for row in rows
    ]
    path = out_dir / "commons" / "section-categories.json"
    write_json(path, payload)
    return path


def write_web_still_packet(rows: list[dict], out_dir: Path, slug: str, per_slot: int) -> list[Path]:
    """Web stills need one direct image URL each. Emit a packet to fill, plus a template."""
    if not rows:
        return []

    letters = "abcdefghijklmnopqrstuvwxyz"
    template = [
        {
            "id": f"{row['slot']}{letters[index]}",
            "url": "",
            "query": row["queries"][index] if index < len(row["queries"]) else row["queries"][0],
        }
        for row in rows
        for index in range(per_slot)
    ]
    template_path = out_dir / "web-stills" / f"{slug}-web-stills.json"
    write_json(template_path, template)

    lines = [
        f"# Web Still Packet: {slug}",
        "",
        "One direct image URL per row. Find the URL, paste it into the matching `id` in",
        f"`{template_path.name}`, then run `download-web-still.py --config`.",
        "",
        "Search for the work, not the person. Do not scrape image search in bulk.",
        "",
        "| Slot | Beat | Brief | Query | Destination ID | Direct image URL |",
        "|------|------|-------|-------|----------------|------------------|",
    ]
    for row in rows:
        for index in range(per_slot):
            query = row["queries"][index] if index < len(row["queries"]) else row["queries"][0]
            lines.append(
                f"| {row['slot']} | {row['beat_title']} | {row['brief']} | {query} "
                f"| `{row['slot']}{letters[index]}` | |"
            )
    lines.append("")

    packet_path = out_dir / "web-stills" / f"{slug}-web-still-packet.md"
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text("\n".join(lines), encoding="utf-8")
    return [template_path, packet_path]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a still-bank query plan and write media-sourcing configs."
    )
    parser.add_argument("--shot-brief", required=True, help="Shot brief JSON from parse-shot-brief.py")
    parser.add_argument("--queries", required=True, help="Agent-written query plan JSON")
    parser.add_argument("--out", required=True, help="Directory for the generated configs")
    parser.add_argument(
        "--per-slot",
        type=int,
        default=DEFAULT_PER_SLOT,
        help=f"Candidates to download per slot (default: {DEFAULT_PER_SLOT})",
    )
    parser.add_argument(
        "--min-queries",
        type=int,
        default=DEFAULT_MIN_QUERIES,
        help=f"Queries required per searched slot (default: {DEFAULT_MIN_QUERIES})",
    )
    args = parser.parse_args()

    try:
        brief_doc = load_json(Path(args.shot_brief))
        plan = read_plan(Path(args.queries))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    briefs = brief_doc.get("briefs") or []
    if not briefs:
        print("Error: shot brief has no briefs", file=sys.stderr)
        return 2

    errors = validate(plan, briefs, args.min_queries)
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        return 2

    rows = merge(plan, briefs)
    out_dir = Path(args.out)
    slug = brief_doc.get("slug") or "still-bank"

    by_method = {method: [r for r in rows if r["method"] == method] for method in VALID_METHODS}

    written = write_pexels_configs(by_method["pexels"], out_dir, args.per_slot)
    commons_path = write_commons_config(by_method["commons"], out_dir)
    if commons_path:
        written.append(commons_path)
    written.extend(write_web_still_packet(by_method["web-still"], out_dir, slug, args.per_slot))

    planned_candidates = sum(
        len(by_method[method]) * args.per_slot for method in SEARCH_METHODS
    )
    search_plan = {
        "slug": slug,
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "shot_brief": args.shot_brief,
        "per_slot": args.per_slot,
        "counts": {method: len(by_method[method]) for method in VALID_METHODS},
        "planned_candidates": planned_candidates,
        "rows": rows,
    }
    plan_path = out_dir / f"{slug}-still-bank-search-plan.json"
    write_json(plan_path, search_plan)
    written.append(plan_path)

    for path in written:
        print(f"Wrote {path}")
    print()
    for method in VALID_METHODS:
        print(f"  {method}: {len(by_method[method])} slots")
    print(f"  planned candidates: {planned_candidates}")

    if by_method["generation"]:
        slots = ", ".join(row["slot"] for row in by_method["generation"])
        print(
            f"\nGated: {slots} route to generation. Do not spend credits before the "
            "Stage 03 checkpoint.",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
