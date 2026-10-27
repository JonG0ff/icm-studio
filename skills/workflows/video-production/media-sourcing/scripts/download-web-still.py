#!/usr/bin/env python3
"""
Download a single web still from a direct image URL into an ignored local folder.

Writes the image plus a sidecar JSON (url, query, filename, fetched_at) so the
file can be re-found. Stdlib only.

Usage:
    python3 download-web-still.py \\
      --url "https://example.com/photo.jpg" \\
      --out libraries/media/local-media/still-bank/aug08-roster/ \\
      --id aug08-messi-trophy \\
      --query "Messi World Cup trophy celebration"

Batch mode (JSON array of {id, url, query} objects):
    python3 download-web-still.py \\
      --config stills.json \\
      --out libraries/media/local-media/still-bank/aug08-roster/
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import ssl
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

DEFAULT_USER_AGENT = (
    "icm-studio-media-sourcing/1.0 "
    "(local workflow; web-still grab)"
)

IMAGE_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/avif": ".avif",
    "image/tiff": ".tiff",
    "image/bmp": ".bmp",
}


def user_agent():
    return os.environ.get("WEB_STILL_USER_AGENT", DEFAULT_USER_AGENT)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "still"


def extension_from_url(url: str) -> str:
    path = unquote(urlparse(url).path)
    ext = Path(path).suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".tiff", ".tif", ".bmp"}:
        if ext == ".jpeg":
            return ".jpg"
        if ext == ".tif":
            return ".tiff"
        return ext
    guessed, _ = mimetypes.guess_type(path)
    if guessed in IMAGE_CONTENT_TYPES:
        return IMAGE_CONTENT_TYPES[guessed]
    return ""


def extension_from_content_type(content_type: str | None) -> str:
    if not content_type:
        return ""
    ctype = content_type.split(";")[0].strip().lower()
    return IMAGE_CONTENT_TYPES.get(ctype, "")


def is_image_content_type(content_type: str | None) -> bool:
    if not content_type:
        return False
    ctype = content_type.split(";")[0].strip().lower()
    return ctype.startswith("image/")


def download_image(url: str, dest: Path) -> dict:
    req = Request(
        url,
        headers={
            "User-Agent": user_agent(),
            "Accept": "image/*,*/*;q=0.8",
        },
    )
    ctx = ssl.create_default_context()
    with urlopen(req, context=ctx, timeout=90) as resp:
        content_type = resp.headers.get("Content-Type")
        if not is_image_content_type(content_type):
            # Some CDNs omit or mis-set Content-Type; sniff by magic bytes after read
            data = resp.read()
            if not looks_like_image(data):
                raise ValueError(
                    f"Response is not an image (Content-Type: {content_type or 'missing'})"
                )
        else:
            data = resp.read()

        if not data:
            raise ValueError("Empty response body")

        ext = extension_from_content_type(content_type) or extension_from_url(url)
        if not ext:
            ext = sniff_extension(data) or ".jpg"

        final_path = dest if dest.suffix else dest.with_suffix(ext)
        if dest.suffix and dest.suffix.lower() != ext and extension_from_url(url):
            # Keep caller-chosen suffix when URL already had one
            final_path = dest

        final_path.parent.mkdir(parents=True, exist_ok=True)
        with open(final_path, "wb") as f:
            f.write(data)

        return {
            "local_path": str(final_path),
            "content_type": content_type,
            "bytes": len(data),
            "final_url": resp.geturl(),
        }


def looks_like_image(data: bytes) -> bool:
    if len(data) < 12:
        return False
    signatures = (
        b"\xff\xd8\xff",  # jpeg
        b"\x89PNG\r\n\x1a\n",  # png
        b"GIF87a",
        b"GIF89a",
        b"RIFF",  # webp starts RIFF....WEBP
        b"BM",  # bmp
        b"II*\x00",  # tiff le
        b"MM\x00*",  # tiff be
    )
    if any(data.startswith(sig) for sig in signatures[:4]):
        return True
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return True
    if data.startswith(b"BM") or data.startswith(b"II*\x00") or data.startswith(b"MM\x00*"):
        return True
    # AVIF / HEIF often start with ftyp box
    if len(data) >= 12 and data[4:8] == b"ftyp":
        return True
    return False


def sniff_extension(data: bytes) -> str:
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return ".gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    if data.startswith(b"BM"):
        return ".bmp"
    if data.startswith(b"II*\x00") or data.startswith(b"MM\x00*"):
        return ".tiff"
    if len(data) >= 12 and data[4:8] == b"ftyp":
        return ".avif"
    return ""


def write_sidecar(path: Path, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def process_one(
    *,
    still_id: str,
    url: str,
    query: str,
    out_dir: Path,
    force: bool,
) -> dict:
    still_id = slugify(still_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    url_ext = extension_from_url(url)
    image_path = out_dir / f"{still_id}{url_ext or ''}"
    sidecar_path = out_dir / f"{still_id}.json"

    existing = None
    if image_path.suffix:
        if image_path.exists() and not force:
            existing = image_path
    else:
        for candidate in out_dir.glob(f"{still_id}.*"):
            if candidate.suffix.lower() in {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
                ".gif",
                ".avif",
                ".tiff",
                ".bmp",
            }:
                if not force:
                    existing = candidate
                break

    if existing is not None:
        sidecar = {
            "id": still_id,
            "url": url,
            "query": query,
            "filename": existing.name,
            "local_path": str(existing),
            "fetched_at": None,
            "skipped": True,
            "rights_note": "unclear",
        }
        if sidecar_path.exists():
            try:
                prior = json.loads(sidecar_path.read_text(encoding="utf-8"))
                sidecar["fetched_at"] = prior.get("fetched_at")
            except json.JSONDecodeError:
                pass
        write_sidecar(sidecar_path, sidecar)
        return {**sidecar, "downloaded": False}

    try:
        result = download_image(url, image_path if image_path.suffix else out_dir / still_id)
    except (HTTPError, URLError, ValueError, TimeoutError, OSError) as exc:
        return {
            "id": still_id,
            "url": url,
            "query": query,
            "downloaded": False,
            "error": str(exc),
            "rights_note": "unclear",
        }

    final_path = Path(result["local_path"])
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sidecar = {
        "id": still_id,
        "url": url,
        "final_url": result.get("final_url", url),
        "query": query,
        "filename": final_path.name,
        "local_path": str(final_path),
        "content_type": result.get("content_type"),
        "bytes": result.get("bytes"),
        "fetched_at": fetched_at,
        "skipped": False,
        "rights_note": "unclear",
    }
    write_sidecar(sidecar_path, sidecar)
    return {**sidecar, "downloaded": True}


def load_config(path: str) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Config must be a JSON array of {id, url, query} objects")
    entries = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Config item {i} must be an object")
        still_id = item.get("id")
        url = item.get("url")
        if not still_id or not url:
            raise ValueError(f"Config item {i} requires id and url")
        entries.append(
            {
                "id": still_id,
                "url": url,
                "query": item.get("query") or "",
            }
        )
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download a web still from a direct image URL into a local still-bank folder."
    )
    parser.add_argument("--url", help="Direct image URL")
    parser.add_argument("--id", dest="still_id", help="Still ID / filename stem")
    parser.add_argument("--query", default="", help="Search query used to find the still")
    parser.add_argument("--config", help="JSON array of {id, url, query} objects")
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory (ignored local-media still-bank folder)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if the image already exists",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.5,
        help="Seconds between batch downloads",
    )
    args = parser.parse_args()

    out_dir = Path(args.out)
    tracker = []

    if args.config:
        if args.url or args.still_id:
            print("Error: Use --config alone, or --url/--id together", file=sys.stderr)
            return 2
        try:
            entries = load_config(args.config)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
    else:
        if not args.url or not args.still_id:
            print("Error: Provide --url and --id, or --config", file=sys.stderr)
            return 2
        entries = [{"id": args.still_id, "url": args.url, "query": args.query}]

    for i, entry in enumerate(entries):
        print(f"Fetching {entry['id']}...")
        result = process_one(
            still_id=entry["id"],
            url=entry["url"],
            query=entry.get("query") or "",
            out_dir=out_dir,
            force=args.force,
        )
        tracker.append(result)
        if result.get("downloaded"):
            print(f"  Saved {result['local_path']}")
        elif result.get("skipped"):
            print(f"  Skipped (exists): {result.get('local_path')}")
        else:
            print(f"  Failed: {result.get('error')}", file=sys.stderr)
        if i < len(entries) - 1:
            time.sleep(args.sleep)

    tracker_path = out_dir / "web-still-download-tracker.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(tracker_path, "w", encoding="utf-8") as f:
        json.dump(tracker, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Tracker saved to: {tracker_path}")

    failures = [t for t in tracker if not t.get("downloaded") and not t.get("skipped")]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
