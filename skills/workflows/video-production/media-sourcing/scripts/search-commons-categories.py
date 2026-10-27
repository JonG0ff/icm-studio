#!/usr/bin/env python3
"""
Crawl Wikimedia Commons *categories* for named-subject stills.

Keyword search (`search-wikimedia-commons.py`) matches file titles and returns a
thin slice. Commons depth lives in categories, so this script resolves a subject
name to its category, walks subcategories, and returns every file underneath.

Modes:
    --discover "Andy Weir"        List candidate categories for a subject
    --category "Category:X"       Crawl one category (repeatable)
    --config categories.json      Crawl a list of {section, subject, categories}

Downloads use Wikimedia thumbnail widths only; full originals are never fetched.
Standard library only. No API key required.
"""

import argparse
import json
import re
import ssl
import sys
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

API_BASE = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "icm-studio-media-sourcing/1.1 (local video workflow)"

# Wikimedia only renders these thumbnail widths reliably. Custom widths 400 out.
ALLOWED_THUMB_WIDTHS = (120, 250, 330, 500, 960, 1280, 1920, 3840)

# Titles that never read as a b-roll still at reel speed.
# Derivative and meta files dominate top-level celebrity categories on Commons.
# None of these read as a b-roll still at reel speed.
TITLE_REJECT = re.compile(
    r"(?i)(\b(logo|icon|map|signature|coat of arms|diagram|chart|graph|barcode|"
    r"qr code|screenshot|spectrum|waveform|plaque|nuvola|commons-logo|timeline|"
    r"statistics|infographic|fan art|fanart|impersonator|wax figure|madame tussauds|"
    r"album cover|book cover|poster|mural|graffiti|sketch|caricature|cartoon|"
    r"exhibit|museum|memorial|grave|tombe|tomb|headstone|protest|rally|"
    r"collection|interface|mockup|net worth|views between|activity of)\b"
    r"|\.(svg|webm|ogv)$)"
)
MIME_REJECT = ("image/svg+xml", "image/x-xcf", "application/pdf", "image/tiff")


def api_get(params, retries=5):
    """GET the Commons API, backing off on 429/5xx rather than dying on them."""
    url = f"{API_BASE}?{urlencode({'format': 'json', 'formatversion': '2', **params})}"
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    delay = 2.0
    for attempt in range(retries):
        try:
            with urlopen(req, context=ssl.create_default_context(), timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries - 1:
                raise
            wait = float(exc.headers.get("Retry-After") or delay)
            print(f"  ... {exc.code} from Commons, waiting {wait:.0f}s")
            time.sleep(wait)
            delay *= 2
        except URLError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2
    raise RuntimeError("Commons API retries exhausted")


def clean(value):
    if isinstance(value, dict):
        value = value.get("value", "")
    text = re.sub(r"(?i)<br\s*/?>", "; ", str(value or ""))
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def slugify(value, fallback="commons-file"):
    return re.sub(r"[^\w.-]+", "-", str(value).lower()).strip("-._")[:80] or fallback


def page_url(title):
    return "https://commons.wikimedia.org/wiki/" + quote(title.replace(" ", "_"), safe="/:")


def snap_width(width):
    for allowed in ALLOWED_THUMB_WIDTHS:
        if allowed >= width:
            return allowed
    return ALLOWED_THUMB_WIDTHS[-1]


def discover_categories(subject, limit=10):
    """Find the Commons categories that match a subject name."""
    data = api_get({
        "action": "query",
        "list": "search",
        "srnamespace": "14",
        "srsearch": subject,
        "srlimit": str(limit),
    })
    return [hit["title"] for hit in data.get("query", {}).get("search", [])]


def category_members(title, member_type):
    """Page through one category's members of a given type (file or subcat)."""
    members, cont = [], None
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": title,
            "cmtype": member_type,
            "cmlimit": "500",
        }
        if cont:
            params["cmcontinue"] = cont
        data = api_get(params)
        members.extend(data.get("query", {}).get("categorymembers", []))
        cont = data.get("continue", {}).get("cmcontinue")
        if not cont:
            return members


def crawl_category(root, depth, sleep, seen_cats):
    """Collect file titles under a category, walking subcategories to `depth`."""
    files, frontier = [], [(root, 0)]
    while frontier:
        title, level = frontier.pop(0)
        if title in seen_cats:
            continue
        seen_cats.add(title)
        try:
            files.extend(member["title"] for member in category_members(title, "file"))
            if level < depth:
                subcats = category_members(title, "subcat")
                frontier.extend((sub["title"], level + 1) for sub in subcats)
        except (HTTPError, URLError) as exc:
            print(f"  ! category failed {title}: {exc}")
        time.sleep(sleep)
    return files


def fetch_imageinfo(titles, thumb_width, sleep):
    """Batch imageinfo lookups (50 titles per request) with thumbnail URLs."""
    pages = []
    for start in range(0, len(titles), 50):
        batch = titles[start:start + 50]
        data = api_get({
            "action": "query",
            "titles": "|".join(batch),
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
            "iiurlwidth": str(thumb_width),
            "iimetadataversion": "latest",
            "iiextmetadatalanguage": "en",
        })
        pages.extend(data.get("query", {}).get("pages", []))
        time.sleep(sleep)
    return pages


def build_candidate(page, section, subject, min_width, name_pattern=None):
    info = (page.get("imageinfo") or [{}])[0]
    meta = info.get("extmetadata") or {}
    title = page.get("title", "")
    mime = info.get("mime", "")
    width, height = info.get("width") or 0, info.get("height") or 0

    if mime in MIME_REJECT or not mime.startswith("image/"):
        return None
    if TITLE_REJECT.search(title) or width < min_width:
        return None
    # For a named person, the subject's name must appear in the file title.
    # Category membership alone lets in crowd shots, venues, and merchandise.
    if name_pattern and not name_pattern.search(title):
        return None

    creator = clean(meta.get("Artist")) or clean(meta.get("Credit"))
    license_name = clean(meta.get("LicenseShortName")) or clean(meta.get("UsageTerms"))
    attribution = clean(meta.get("AttributionRequired")) or "unknown"
    ready = bool(title and license_name and creator)

    return {
        "id": f"{slugify(section)}-{slugify(Path(title.replace('File:', '', 1)).stem)}",
        "source": "wikimedia-commons",
        "section": section,
        "subject": subject,
        "title": title,
        "commons_page_url": page_url(title),
        "thumb_url": info.get("thumburl", ""),
        "thumb_width": info.get("thumbwidth"),
        "thumb_height": info.get("thumbheight"),
        "direct_file_url": info.get("url", ""),
        "mime": mime,
        "width": width,
        "height": height,
        "orientation": "portrait" if height > width else "landscape",
        "description": clean(meta.get("ImageDescription"))[:300],
        "date": clean(meta.get("DateTimeOriginal")),
        "creator": creator,
        "license_short_name": license_name,
        "license_url": clean(meta.get("LicenseUrl")),
        "attribution_required": attribution,
        "manifest_status": "ready" if ready else "needs-approval",
        "rights_note": (
            f"Wikimedia Commons. License: {license_name or 'missing'}. "
            f"Creator/credit: {creator or 'missing'}. Attribution required: {attribution}. "
            "Check personality and brand context before delivery."
        ),
        "selected": False,
    }


def download_thumb(candidate, out_dir, sleep):
    url = candidate.get("thumb_url") or candidate.get("direct_file_url")
    if not url:
        return {"id": candidate["id"], "downloaded": False, "error": "no url"}

    suffix = ".png" if candidate["mime"] == "image/png" else ".jpg"
    path = Path(out_dir) / f"{candidate['id']}{suffix}"
    if path.exists():
        return {"id": candidate["id"], "downloaded": False, "skipped": True, "local_path": str(path)}

    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, context=ssl.create_default_context(), timeout=90) as resp:
            path.write_bytes(resp.read())
    except (HTTPError, URLError, OSError) as exc:
        return {"id": candidate["id"], "downloaded": False, "error": str(exc)}
    finally:
        time.sleep(sleep)

    return {
        "id": candidate["id"],
        "downloaded": True,
        "local_path": str(path),
        "source_page": candidate["commons_page_url"],
        "thumb_url": url,
        "license": candidate["license_short_name"],
        "creator": candidate["creator"],
        "rights_note": candidate["rights_note"],
    }


def read_config(path):
    with open(path, "r", encoding="utf-8") as f:
        entries = json.load(f)
    if not isinstance(entries, list):
        raise ValueError("Config must be a JSON array of {section, subject, categories}")
    for entry in entries:
        if not entry.get("categories"):
            raise ValueError(f"Entry missing categories: {entry}")
    return entries


def write_outputs(candidates, out_dir, args):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endpoint": API_BASE,
        "mode": "category-crawl",
        "thumb_width": args.thumb_width,
        "depth": args.depth,
        "candidates": candidates,
    }
    json_path = out / "commons-category-candidates.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return json_path


def run_discover(args):
    for subject in args.discover:
        print(f"\n### {subject}")
        for title in discover_categories(subject):
            try:
                count = len(category_members(title, "file"))
                subs = len(category_members(title, "subcat"))
            except (HTTPError, URLError) as exc:
                print(f"  ?      {title} ({exc})")
                continue
            print(f"  {count:4d} files / {subs:2d} subcats   {title}")
            time.sleep(args.sleep)
    return 0


def run_crawl(args):
    if args.config:
        entries = read_config(args.config)
    else:
        entries = [{
            "section": args.section or "unsorted",
            "subject": args.subject or (args.category[0] if args.category else ""),
            "categories": args.category,
        }]

    seen_cats, seen_titles, candidates = set(), set(), []
    for entry in entries:
        section = entry.get("section", "unsorted")
        subject = entry.get("subject", "")
        titles = []
        for category in entry["categories"]:
            print(f"Crawling {category} -> {section}")
            titles.extend(crawl_category(category, args.depth, args.sleep, seen_cats))

        fresh = [t for t in dict.fromkeys(titles) if t not in seen_titles]
        seen_titles.update(fresh)
        if not fresh:
            print(f"  no new files for {section}")
            continue

        tokens = entry.get("title_must_match") or []
        name_pattern = (
            re.compile("|".join(re.escape(t) for t in tokens), re.I) if tokens else None
        )
        for page in fetch_imageinfo(fresh, args.thumb_width, args.sleep):
            candidate = build_candidate(page, section, subject, args.min_width, name_pattern)
            if candidate:
                candidates.append(candidate)
        print(f"  {section}: {len([c for c in candidates if c['section'] == section])} usable candidates")

    json_path = write_outputs(candidates, args.out, args)
    print(f"\nCandidates: {len(candidates)} -> {json_path}")

    if args.download_dir:
        Path(args.download_dir).mkdir(parents=True, exist_ok=True)
        per_section, tracker = {}, []
        for candidate in candidates:
            section = candidate["section"]
            if per_section.get(section, 0) >= args.per_section:
                continue
            record = download_thumb(candidate, args.download_dir, args.sleep)
            tracker.append(record)
            if record.get("downloaded") or record.get("skipped"):
                per_section[section] = per_section.get(section, 0) + 1
                print(f"  [{section} {per_section[section]}/{args.per_section}] {record.get('local_path')}")

        tracker_path = Path(args.download_dir) / "commons-category-tracker.json"
        with open(tracker_path, "w", encoding="utf-8") as f:
            json.dump(tracker, f, indent=2, ensure_ascii=False)
        print(f"Tracker: {tracker_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Crawl Wikimedia Commons categories for named-subject stills.")
    parser.add_argument("--discover", nargs="+", help="List candidate categories for these subject names")
    parser.add_argument("--category", action="append", help="Category to crawl (repeatable)")
    parser.add_argument("--section", help="Section label for --category mode")
    parser.add_argument("--subject", help="Subject label for --category mode")
    parser.add_argument("--config", help="JSON array of {section, subject, categories}")
    parser.add_argument("--depth", type=int, default=1, help="Subcategory recursion depth")
    parser.add_argument("--min-width", type=int, default=800, help="Reject images narrower than this")
    parser.add_argument("--thumb-width", type=int, default=1280, help="Thumbnail width to download")
    parser.add_argument("--out", default="./commons-candidates", help="Folder for candidate metadata")
    parser.add_argument("--download-dir", help="Download thumbnails here (local-only path)")
    parser.add_argument("--per-section", type=int, default=6, help="Max downloads per section")
    parser.add_argument("--sleep", type=float, default=2.0, help="Seconds between requests")
    args = parser.parse_args()

    args.thumb_width = snap_width(args.thumb_width)

    if args.discover:
        return run_discover(args)
    if not (args.category or args.config):
        print("Error: use --discover, --category, or --config")
        return 2
    return run_crawl(args)


if __name__ == "__main__":
    sys.exit(main())
