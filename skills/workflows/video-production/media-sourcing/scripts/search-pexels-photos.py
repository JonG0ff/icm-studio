#!/usr/bin/env python3
"""
Search and download stock still images from Pexels API.

Uses ONLY Python standard library — no external dependencies.

Usage modes:
    --campaign    Read shot-list.md and download per shot
    --query       Single search query
    --config      JSON array of {shot_id, query, count} objects

Examples:
    export PEXELS_API_KEY="your_key_here"

    # One-off search
    python3 search-pexels-photos.py --query "night city skyline silhouette" --count 5 --out skills/workflows/video-production/media-sourcing/stills

    # From a campaign shot list
    python3 search-pexels-photos.py --campaign /path/to/trailer-campaign-02 --per-shot 3

    # From JSON config
    python3 search-pexels-photos.py --config searches.json --out skills/workflows/video-production/media-sourcing/stills

Free tier: 200 requests/hour, 20,000 requests/month
"""

import argparse
import json
import os
import re
import ssl
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, urlencode, quote
from urllib.request import Request, urlopen

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
if not PEXELS_API_KEY:
    print("Error: Set PEXELS_API_KEY environment variable")
    sys.exit(1)

API_BASE = "https://api.pexels.com/v1/search"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


def api_get(url):
    """Make authenticated GET request to Pexels API."""
    req = Request(url, headers={"Authorization": PEXELS_API_KEY, "User-Agent": USER_AGENT})
    ctx = ssl.create_default_context()
    with urlopen(req, context=ctx, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download_image(url, path):
    """Download an image file from URL to path using stdlib."""
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        ctx = ssl.create_default_context()
        with urlopen(req, context=ctx, timeout=60) as resp:
            with open(path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"  Download failed: {e}")
        return False


def pick_best_source(photo):
    """Return the highest-resolution image source from a Pexels photo object."""
    src = photo.get("src", {})
    sizes = [
        ("original", src.get("original", "")),
        ("large2x", src.get("large2x", "")),
        ("large", src.get("large", "")),
        ("medium", src.get("medium", "")),
        ("small", src.get("small", "")),
    ]
    for label, url in sizes:
        if url:
            return {"label": label, "url": url}
    return None


def parse_shot_list(path):
    """Read shot-list.md and extract rows with search terms."""
    if not path.exists():
        print(f"Shot list not found: {path}")
        return []

    shots = []
    in_table = False

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("|"):
                parts = [p.strip() for p in line.split("|")]
                parts = [p for p in parts if p]
                if not parts:
                    continue
                if "Stock Search Terms" in line or "Description" in line:
                    in_table = True
                    continue
                if in_table and set(line) <= {"|", "-", " "}:
                    continue
                if in_table and len(parts) >= 4:
                    shot_num = parts[0]
                    search_terms = parts[4] if len(parts) > 4 else parts[2]
                    if search_terms and search_terms not in ("Stock Search Terms", "Description"):
                        shots.append({"shot_id": f"shot-{int(shot_num):02d}", "query": search_terms, "count": 3})
    return shots


def search_and_download(queries, out_dir, orientation="landscape", per_count=3):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load any existing tracker so repeat runs against the same beat folder
    # (primary pass, then alt queries, then a rescue pass) accumulate rather
    # than overwrite. Losing a prior pass's entries loses the source URL and
    # photographer for stills already on disk, which breaks attribution.
    tracker_path = out_dir / "download-tracker.json"
    tracker = {}
    if tracker_path.exists():
        try:
            with open(tracker_path) as f:
                existing = json.load(f)
            if isinstance(existing, dict):
                tracker = existing
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  Warning: could not read existing tracker ({exc}); starting fresh")

    for item in queries:
        shot_id = item.get("shot_id", "shot")
        query = item["query"]
        count = item.get("count", per_count)
        print(f"\nSearching: {query} (shot: {shot_id})")

        try:
            params = urlencode({"query": query, "per_page": count, "orientation": orientation})
            data = api_get(f"{API_BASE}?{params}")
        except Exception as e:
            print(f"  Search failed: {e}")
            continue

        photos = data.get("photos", [])
        if not photos:
            print("  No results found")
            continue

        tracker[shot_id] = []
        slug = re.sub(r"[\W]+", "-", query).lower().strip("-")[:40]

        for i, photo in enumerate(photos[:count]):
            best = pick_best_source(photo)
            if not best:
                continue

            url = best["url"]
            ext = Path(urlparse(url).path).suffix or ".jpg"

            if shot_id.startswith("shot-"):
                filename = f"{shot_id}_option-{i+1}{ext}"
            else:
                filename = f"{slug}_{i+1:03d}{ext}"

            filepath = out_dir / filename

            # Record full metadata even when the file is already on disk. A
            # re-run must be able to rebuild attribution for stills downloaded
            # by an earlier pass; "skipped" alone loses the source URL.
            record = {
                "filename": filename,
                "pexels_id": photo.get("id"),
                "url": photo.get("url"),
                "photographer": photo.get("photographer"),
                "width": photo.get("width"),
                "height": photo.get("height"),
                "size_label": best["label"],
            }

            if filepath.exists():
                print(f"  Skip (exists): {filename}")
                tracker[shot_id].append({**record, "skipped": True})
                continue

            print(f"  Downloading {filename} ({best['label']})")

            if download_image(url, filepath):
                tracker[shot_id].append(record)

        time.sleep(1)

    with open(tracker_path, "w") as f:
        json.dump(tracker, f, indent=2)

    print(f"\nDone. Tracker saved to: {tracker_path}")
    return tracker


def main():
    parser = argparse.ArgumentParser(description="Search and download stock still images from Pexels")
    parser.add_argument("--campaign", type=str, help="Path to campaign folder containing shot-list.md")
    parser.add_argument("--query", type=str, help="Single search query string")
    parser.add_argument("--config", type=str, help="Path to JSON config file with search entries")
    parser.add_argument("--out", type=str, default="skills/workflows/video-production/media-sourcing/stills", help="Output directory for downloads")
    parser.add_argument("--per-shot", type=int, default=3, help="Images to download per shot (default: 3)")
    parser.add_argument("--count", type=int, default=5, help="Images to download for --query mode (default: 5)")
    parser.add_argument("--orientation", type=str, default="landscape", choices=["landscape", "portrait", "square"])
    args = parser.parse_args()

    mode = sum(bool(x) for x in [args.campaign, args.query, args.config])
    if mode != 1:
        print("Error: Use exactly one of --campaign, --query, or --config")
        sys.exit(1)

    queries = []

    if args.campaign:
        campaign = Path(args.campaign)
        shot_list = campaign / "shot-list.md"
        out = campaign / "assets" / "stills"
        queries = parse_shot_list(shot_list)
        if not queries:
            print("No searchable shots found in shot-list.md")
            sys.exit(1)
        print(f"Parsed {len(queries)} shots from {shot_list}")
        search_and_download(queries, out, args.orientation, args.per_shot)
        return

    if args.query:
        queries = [{"shot_id": "query", "query": args.query, "count": args.count}]
        search_and_download(queries, args.out, args.orientation, args.count)
        return

    if args.config:
        config_path = Path(args.config)
        with open(config_path, "r", encoding="utf-8") as f:
            queries = json.load(f)
        if not queries:
            print("Config file is empty")
            sys.exit(1)
        search_and_download(queries, args.out, args.orientation, args.per_shot)
        return


if __name__ == "__main__":
    main()
