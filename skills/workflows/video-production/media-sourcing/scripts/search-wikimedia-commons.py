#!/usr/bin/env python3
"""
Search Wikimedia Commons for event/topic media and write metadata-first candidates.

Uses only Python standard library. No API key is required.

Search modes:
    --query       Single Commons search query
    --config      JSON array of {shot_id, query, limit} objects
    --campaign    Read shot-list.md from a campaign folder

Download mode:
    --download-selected commons-candidates.json --download-dir /ignored/local/path

By default this script does not download files. It records file page, license,
creator/credit, attribution, and direct file metadata so asset manifests can be
reviewed before edit lock.
"""

import argparse
import json
import os
import re
import ssl
import sys
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

API_BASE = "https://commons.wikimedia.org/w/api.php"
DEFAULT_USER_AGENT = (
    "icm-studio-media-sourcing/1.0 "
    "(local workflow; set WIKIMEDIA_USER_AGENT for contact)"
)


def user_agent():
    return os.environ.get("WIKIMEDIA_USER_AGENT", DEFAULT_USER_AGENT)


def api_get(params):
    full_params = {
        "format": "json",
        "formatversion": "2",
        **params,
    }
    url = f"{API_BASE}?{urlencode(full_params)}"
    req = Request(
        url,
        headers={
            "User-Agent": user_agent(),
            "Accept": "application/json",
        },
    )
    ctx = ssl.create_default_context()
    with urlopen(req, context=ctx, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def clean_text(value):
    if value is None:
        return ""
    if isinstance(value, dict):
        value = value.get("value", "")
    text = str(value)
    text = re.sub(r"(?i)<br\s*/?>", "; ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def ext_value(extmetadata, *keys):
    for key in keys:
        value = clean_text(extmetadata.get(key))
        if value:
            return value
    return ""


def commons_page_url(title):
    return "https://commons.wikimedia.org/wiki/" + quote(title.replace(" ", "_"), safe="/:")


def slugify(value, fallback="commons-file"):
    slug = re.sub(r"[^\w.-]+", "-", value.lower()).strip("-._")
    return slug[:90] or fallback


def normalize_shot_id(value, idx):
    value = clean_text(value)
    if not value:
        return f"shot-{idx:02d}"
    if value.isdigit():
        return f"shot-{int(value):02d}"
    return slugify(value, fallback=f"shot-{idx:02d}")


def media_kind(mime):
    if mime.startswith("image/"):
        return "still"
    if mime.startswith("video/"):
        return "footage"
    if mime.startswith("audio/"):
        return "audio"
    return "source-proof"


def allowed_by_mime(mime, allowed):
    if "all" in allowed:
        return True
    if "image" in allowed and mime.startswith("image/"):
        return True
    if "video" in allowed and mime.startswith("video/"):
        return True
    if "audio" in allowed and mime.startswith("audio/"):
        return True
    return False


def parse_allowed_media_types(raw):
    allowed = {part.strip().lower() for part in raw.split(",") if part.strip()}
    valid = {"image", "video", "audio", "all"}
    bad = sorted(allowed - valid)
    if bad:
        raise ValueError(f"Unsupported media type(s): {', '.join(bad)}")
    return allowed or {"image"}


def build_rights_note(candidate):
    license_name = candidate["license_short_name"] or candidate["usage_terms"] or "license metadata missing"
    creator_credit = candidate["creator"] or candidate["credit"] or "creator/credit missing"
    attribution = candidate["attribution_required"] or "unknown"
    if candidate["manifest_status"] == "ready":
        return (
            "Wikimedia Commons file page and license metadata recorded. "
            f"License: {license_name}. Creator/credit: {creator_credit}. "
            f"Attribution required: {attribution}. "
            "Check personality, trademark, event, and brand context before delivery."
        )
    return (
        "Wikimedia Commons candidate; mark needs-approval until file page, "
        "creator/credit, license, and attribution details are reviewed. "
        f"Current license: {license_name}. Current creator/credit: {creator_credit}."
    )


def candidate_from_page(page, query, shot_id, rank):
    imageinfo = (page.get("imageinfo") or [{}])[0]
    extmetadata = imageinfo.get("extmetadata") or {}
    title = page.get("title", "")
    mime = imageinfo.get("mime", "")

    creator = ext_value(extmetadata, "Artist", "Author", "Creator")
    credit = ext_value(extmetadata, "Credit", "Attribution", "CreditLine")
    license_short_name = ext_value(extmetadata, "LicenseShortName", "License")
    license_url = ext_value(extmetadata, "LicenseUrl")
    usage_terms = ext_value(extmetadata, "UsageTerms")
    attribution_required = ext_value(extmetadata, "AttributionRequired")

    has_required_rights = bool(
        title
        and commons_page_url(title)
        and (license_short_name or usage_terms)
        and (license_url or usage_terms)
        and (creator or credit)
    )
    manifest_status = "ready" if has_required_rights else "needs-approval"

    candidate = {
        "id": f"{shot_id}-commons-{rank:03d}",
        "source": "wikimedia-commons",
        "query": query,
        "shot_id": shot_id,
        "rank": rank,
        "title": title,
        "commons_page_url": commons_page_url(title) if title else "",
        "direct_file_url": imageinfo.get("url", ""),
        "mime": mime,
        "asset_type": media_kind(mime),
        "width": imageinfo.get("width"),
        "height": imageinfo.get("height"),
        "size_bytes": imageinfo.get("size"),
        "upload_timestamp": imageinfo.get("timestamp", ""),
        "commons_description": ext_value(extmetadata, "ImageDescription", "ObjectName"),
        "date_metadata": ext_value(extmetadata, "DateTimeOriginal", "DateTime"),
        "creator": creator,
        "credit": credit,
        "license_short_name": license_short_name,
        "license_url": license_url,
        "usage_terms": usage_terms,
        "attribution_required": attribution_required,
        "manifest_status": manifest_status,
        "selected": False,
    }
    candidate["rights_note"] = build_rights_note(candidate)
    candidate["manifest_row_hint"] = (
        f"{candidate['commons_page_url']} | {candidate['manifest_status']} | "
        f"{candidate['rights_note']}"
    )
    return candidate


def search_commons(query, shot_id, limit, allowed_media_types):
    params = {
        "action": "query",
        "generator": "search",
        "gsrnamespace": "6",
        "gsrsearch": query,
        "gsrlimit": str(min(limit, 50)),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iimetadataversion": "latest",
        "iiextmetadatalanguage": "en",
    }
    data = api_get(params)
    pages = data.get("query", {}).get("pages", [])
    pages = sorted(pages, key=lambda page: page.get("index", 999999))

    candidates = []
    for page in pages:
        imageinfo = (page.get("imageinfo") or [{}])[0]
        mime = imageinfo.get("mime", "")
        if not allowed_by_mime(mime, allowed_media_types):
            continue
        candidates.append(candidate_from_page(page, query, shot_id, len(candidates) + 1))
    return candidates


def read_config(path, default_limit):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("queries", [])
    if not isinstance(data, list):
        raise ValueError("Config must be a JSON array or an object with a queries array")

    queries = []
    for idx, item in enumerate(data, 1):
        if isinstance(item, str):
            queries.append({"shot_id": f"query-{idx:02d}", "query": item, "limit": default_limit})
            continue
        if not isinstance(item, dict) or not item.get("query"):
            raise ValueError("Each config item must be a string or an object with a query field")
        queries.append(
            {
                "shot_id": item.get("shot_id") or f"query-{idx:02d}",
                "query": item["query"],
                "limit": int(item.get("limit") or item.get("count") or default_limit),
            }
        )
    return queries


def table_cells(line):
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return [clean_text(cell) for cell in cells]


def is_separator_row(line):
    compact = line.strip().replace("|", "").replace(":", "").replace("-", "").strip()
    return compact == ""


def parse_campaign_shot_list(campaign, per_shot):
    shot_list = Path(campaign) / "shot-list.md"
    if not shot_list.exists():
        raise FileNotFoundError(f"Shot list not found: {shot_list}")

    headers = []
    rows = []
    with open(shot_list, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line.startswith("|"):
                continue
            if is_separator_row(line):
                continue
            cells = table_cells(line)
            lowered = [cell.lower() for cell in cells]
            if not headers and any("search" in cell or "shot" in cell for cell in lowered):
                headers = cells
                continue
            if headers and len(cells) >= 2:
                row = {headers[i]: cells[i] for i in range(min(len(headers), len(cells)))}
                rows.append(row)

    query_columns = [
        "Wikimedia Search Terms",
        "Commons Search Terms",
        "Stock Search Terms",
        "Search Terms",
        "Description",
        "Need",
    ]
    shot_columns = ["Shot ID", "Shot", "Asset ID", "Scene", "Beat"]

    queries = []
    for idx, row in enumerate(rows, 1):
        query = ""
        for col in query_columns:
            query = row.get(col, "")
            if query:
                break
        if not query:
            continue

        shot_label = ""
        for col in shot_columns:
            shot_label = row.get(col, "")
            if shot_label:
                break

        queries.append(
            {
                "shot_id": normalize_shot_id(shot_label, idx),
                "query": query,
                "limit": per_shot,
            }
        )
    return queries


def markdown_escape(value):
    return clean_text(value).replace("|", "\\|")


def write_outputs(candidates, out_dir, query_entries, args):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "created": created,
        "endpoint": API_BASE,
        "mode": "metadata-only",
        "user_agent": user_agent(),
        "media_types": sorted(args.allowed_media_types),
        "queries": query_entries,
        "candidates": candidates,
    }

    json_path = out_dir / "commons-candidates.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    md_path = out_dir / "commons-candidates.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Wikimedia Commons Candidates\n\n")
        f.write(f"- created: {created}\n")
        f.write(f"- endpoint: {API_BASE}\n")
        f.write("- mode: metadata-only; no files downloaded\n")
        f.write("- note: Commons is free/publicly licensed media, not a news-wire feed.\n\n")

        f.write("## Query Summary\n\n")
        f.write("| Shot ID | Query | Candidates |\n")
        f.write("|---|---|---|\n")
        for entry in query_entries:
            count = len([item for item in candidates if item["shot_id"] == entry["shot_id"]])
            f.write(
                f"| {markdown_escape(entry['shot_id'])} | "
                f"{markdown_escape(entry['query'])} | {count} |\n"
            )

        f.write("\n## Candidates\n\n")
        for item in candidates:
            creator_credit = item["creator"] or item["credit"] or "missing"
            license_label = item["license_short_name"] or item["usage_terms"] or "missing"
            f.write(f"### {markdown_escape(item['id'])}\n\n")
            f.write(f"- title: {markdown_escape(item['title'])}\n")
            f.write(f"- query: {markdown_escape(item['query'])}\n")
            f.write(f"- type: {markdown_escape(item['asset_type'])} ({markdown_escape(item['mime'])})\n")
            f.write(f"- status: {markdown_escape(item['manifest_status'])}\n")
            f.write(f"- Commons page: {item['commons_page_url']}\n")
            f.write(f"- direct file: {item['direct_file_url']}\n")
            f.write(f"- license: {markdown_escape(license_label)}\n")
            f.write(f"- license URL: {item['license_url']}\n")
            f.write(f"- creator/credit: {markdown_escape(creator_credit)}\n")
            f.write(f"- attribution required: {markdown_escape(item['attribution_required'] or 'unknown')}\n")
            f.write(f"- rights note: {markdown_escape(item['rights_note'])}\n\n")

    return json_path, md_path


def load_candidates(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return data.get("candidates", [])


def filename_for_candidate(candidate):
    file_url = candidate.get("direct_file_url", "")
    ext = Path(urlparse(file_url).path).suffix
    title = candidate.get("title", "commons-file").replace("File:", "", 1)
    return f"{slugify(candidate.get('id', 'commons'))}-{slugify(title)}{ext or '.media'}"


def download_file(url, path):
    req = Request(url, headers={"User-Agent": user_agent()})
    ctx = ssl.create_default_context()
    with urlopen(req, context=ctx, timeout=90) as resp:
        with open(path, "wb") as f:
            while True:
                chunk = resp.read(1024 * 64)
                if not chunk:
                    break
                f.write(chunk)


def download_selected(args):
    if not args.download_dir:
        print("Error: --download-dir is required with --download-selected")
        return 2

    selected_ids = {
        value.strip()
        for value in (args.selected_ids or "").split(",")
        if value.strip()
    }
    candidates = load_candidates(args.download_selected)
    selected = []
    for item in candidates:
        if selected_ids and item.get("id") in selected_ids:
            selected.append(item)
        elif not selected_ids and item.get("selected") is True:
            selected.append(item)

    if not selected:
        print("Error: No selected candidates found. Set selected=true in JSON or pass --selected-ids.")
        return 2

    out_dir = Path(args.download_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tracker = []
    for item in selected:
        file_url = item.get("direct_file_url")
        if not file_url:
            tracker.append({"id": item.get("id"), "downloaded": False, "error": "missing direct_file_url"})
            continue

        path = out_dir / filename_for_candidate(item)
        if path.exists():
            tracker.append({"id": item.get("id"), "downloaded": False, "skipped": True, "local_path": str(path)})
            continue

        print(f"Downloading {item.get('id')}: {path.name}")
        try:
            download_file(file_url, path)
            tracker.append(
                {
                    "id": item.get("id"),
                    "downloaded": True,
                    "source_page": item.get("commons_page_url"),
                    "direct_file_url": file_url,
                    "local_path": str(path),
                    "license": item.get("license_short_name"),
                    "rights_note": item.get("rights_note"),
                }
            )
        except Exception as exc:
            tracker.append({"id": item.get("id"), "downloaded": False, "error": str(exc)})
        time.sleep(args.sleep)

    tracker_path = out_dir / "commons-download-tracker.json"
    with open(tracker_path, "w", encoding="utf-8") as f:
        json.dump(tracker, f, indent=2, ensure_ascii=False)
    print(f"Tracker saved to: {tracker_path}")
    return 0


def build_query_entries(args):
    if args.query:
        return [{"shot_id": args.shot_id or "query", "query": args.query, "limit": args.limit}]
    if args.config:
        return read_config(args.config, args.limit)
    return parse_campaign_shot_list(args.campaign, args.per_shot)


def main():
    parser = argparse.ArgumentParser(
        description="Search Wikimedia Commons files and write manifest-ready metadata candidates."
    )
    parser.add_argument("--query", help="Single Commons search query")
    parser.add_argument("--shot-id", help="Optional shot/asset ID for --query mode")
    parser.add_argument("--config", help="JSON config with search entries")
    parser.add_argument("--campaign", help="Campaign folder containing shot-list.md")
    parser.add_argument("--download-selected", help="Download selected candidates from commons-candidates.json")
    parser.add_argument("--download-dir", help="Local-only output directory for selected downloads")
    parser.add_argument("--selected-ids", help="Comma-separated candidate IDs to download from --download-selected")
    parser.add_argument("--out", default="./commons-candidates", help="Output folder for candidate metadata")
    parser.add_argument("--limit", "--count", dest="limit", type=int, default=10, help="Results per one-off/config query")
    parser.add_argument("--per-shot", type=int, default=5, help="Results per campaign shot")
    parser.add_argument("--media-types", default="image", help="Comma-separated: image, video, audio, all")
    parser.add_argument("--sleep", type=float, default=1.0, help="Seconds between serial API/download requests")
    args = parser.parse_args()

    try:
        args.allowed_media_types = parse_allowed_media_types(args.media_types)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 2

    search_modes = [args.query, args.config, args.campaign]
    if args.download_selected:
        if any(search_modes):
            print("Error: Use --download-selected separately from search modes")
            return 2
        return download_selected(args)

    if sum(bool(mode) for mode in search_modes) != 1:
        print("Error: Use exactly one of --query, --config, --campaign, or --download-selected")
        return 2

    try:
        query_entries = build_query_entries(args)
    except Exception as exc:
        print(f"Error: {exc}")
        return 2

    if not query_entries:
        print("Error: No search queries found")
        return 2

    all_candidates = []
    for entry in query_entries:
        print(f"Searching Commons: {entry['query']} ({entry['shot_id']})")
        try:
            candidates = search_commons(
                entry["query"],
                entry["shot_id"],
                int(entry.get("limit") or args.limit),
                args.allowed_media_types,
            )
        except Exception as exc:
            print(f"  Search failed: {exc}")
            candidates = []
        all_candidates.extend(candidates)
        time.sleep(args.sleep)

    json_path, md_path = write_outputs(all_candidates, args.out, query_entries, args)
    print(f"Done. JSON saved to: {json_path}")
    print(f"Done. Markdown saved to: {md_path}")
    print("No files downloaded. Use --download-selected after choosing candidates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
