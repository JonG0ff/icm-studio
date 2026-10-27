#!/usr/bin/env python3
"""
Build a Pixabay SFX sourcing packet and download explicitly selected audio.

This script is metadata-first by default. It turns an SFX map JSON file into:

1. pixabay-sfx-sourcing.md - search links, local reuse checks, and manifest hints
2. pixabay-sfx-selection-template.json - selected asset fields to fill in

After a human or agent selects assets on Pixabay, use --download-selected with
the filled template. The download URL is used only for the download run and is
not written back into the tracker.

Usage:
    python3 source-pixabay-sfx.py --config sfx-map.json --out ./sfx-source --project-slug campaign-slug
    python3 source-pixabay-sfx.py --download-selected ./sfx-source/pixabay-sfx-selection-template.json --out ./sfx-source
"""

import argparse
import json
import re
import ssl
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

RIGHTS_NOTE = (
    "Pixabay Content License. Royalty-free use allowed; no attribution "
    "required, but credit appreciated. Source page, creator, title, and "
    "prohibited-use check recorded."
)
USER_AGENT = "icm-studio-sound-effects-mix/1.0 (local SFX sourcing workflow)"
ALLOWED_PAGE_PREFIXES = (
    "https://pixabay.com/sound-effects/",
    "https://pixabay.com/music/",
)
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aif", ".aiff"}


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for path in [here, *here.parents]:
        if (path / "skills").exists() and (path / "workspaces").exists():
            return path
    return Path.cwd()


def resolve_repo_path(path_value: str, repo_root: Path) -> Path:
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path
    return repo_root / path


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def slugify(value: str, fallback: str = "sfx") -> str:
    slug = re.sub(r"[^\w.-]+", "-", str(value).lower()).strip("-._")
    return slug[:90] or fallback


def clean_cell(value) -> str:
    text = str(value or "")
    text = text.replace("|", "/")
    return re.sub(r"\s+", " ", text).strip()


def as_list(value) -> list:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def fmt_time(seconds, frame_rate: int = 24) -> str:
    try:
        seconds = float(seconds)
    except (TypeError, ValueError):
        return "N/A"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    frames = int((seconds - int(seconds)) * frame_rate)
    return f"{minutes:02d}:{secs:02d}:{frames:02d}"


def source_terms_for(sfx: dict) -> list:
    terms = as_list(sfx.get("source_terms"))
    if terms:
        return terms
    fallback = " ".join(
        part
        for part in [
            sfx.get("name", ""),
            sfx.get("description", ""),
            sfx.get("visual", ""),
        ]
        if part
    )
    return [fallback.strip()] if fallback.strip() else [sfx.get("id", "sound effect")]


def pixabay_sound_effect_url(query: str) -> str:
    return f"https://pixabay.com/sound-effects/search/{quote(query.strip(), safe='')}/"


def pixabay_music_url(query: str) -> str:
    return f"https://pixabay.com/music/search/{quote(query.strip(), safe='')}/"


def item_wants_music(sfx: dict) -> bool:
    haystack = " ".join(as_list(sfx.get("suggested_sources")) + [sfx.get("name", ""), sfx.get("description", "")])
    return "music" in haystack.lower() or "stinger" in haystack.lower()


def local_media_candidates(index_path: Path, terms: list, limit: int = 4) -> list:
    if not index_path.exists():
        return []

    tokens = {
        token
        for term in terms
        for token in re.findall(r"[a-z0-9]+", term.lower())
        if len(token) >= 4
    }
    if not tokens:
        return []

    candidates = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or set(stripped) <= {"|", "-", " "}:
            continue
        low = stripped.lower()
        if " asset id " in low or ("| type |" in low and "| title |" in low):
            continue
        audio_bonus = 2 if ("| sfx " in low or "| audio " in low or "sfx" in low) else 0
        score = sum(1 for token in tokens if token in low) + audio_bonus
        if score > audio_bonus:
            candidates.append((score, stripped))

    candidates.sort(key=lambda item: item[0], reverse=True)
    return [line for _, line in candidates[:limit]]


def default_media_dir(project_slug: str) -> str:
    return f"libraries/media/local-media/{project_slug}/audio/sfx"


def build_sourcing_packet(args) -> None:
    repo_root = find_repo_root()
    config_path = Path(args.config)
    config = load_json(config_path)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    sourcing_path = out_dir / "pixabay-sfx-sourcing.md"
    template_path = out_dir / "pixabay-sfx-selection-template.json"
    script_path = Path(__file__).resolve()

    project_name = config.get("project_name", config_path.stem)
    project_slug = args.project_slug or slugify(project_name, "sfx-project")
    media_dir = args.media_dir or default_media_dir(project_slug)
    media_index = (
        resolve_repo_path(args.media_index, repo_root)
        if args.media_index
        else repo_root / "libraries/media/assets/index.md"
    )
    frame_rate = int(config.get("frame_rate", 24))
    created = datetime.now(timezone.utc).isoformat()

    selection_template = {
        "project_name": project_name,
        "project_slug": project_slug,
        "created": created,
        "media_dir": media_dir,
        "rights_note": RIGHTS_NOTE,
        "selections": [],
    }

    lines = [
        f"# Pixabay SFX Sourcing - {project_name}",
        "",
        f"- created: {created}",
        f"- project_slug: {project_slug}",
        f"- media_library_index: {media_index}",
        f"- selected_download_dir: {media_dir}",
        "",
        "## Rules",
        "",
        "- Check local media candidates before downloading new audio.",
        "- Use Pixabay asset pages, not raw search-result snippets, for source proof.",
        "- Record page URL, creator, title, duration, local path, and `Pixabay Content License`.",
        "- Paste direct download URLs only into the local selection JSON used for the download run.",
        "- Do not commit raw audio or tokenized/private download URLs.",
        "",
        "## Download Selected Assets",
        "",
        "After filling `pixabay-sfx-selection-template.json`, run:",
        "",
        "```bash",
        f"python3 {script_path} \\",
        f"  --download-selected {template_path.resolve()} \\",
        f"  --out {out_dir.resolve()}",
        "```",
        "",
        "## SFX Source Queue",
        "",
    ]

    for sfx in config.get("sfx", []):
        sfx_id = sfx.get("id", slugify(sfx.get("name", "sfx")))
        terms = source_terms_for(sfx)
        local_hits = local_media_candidates(media_index, terms)
        start = fmt_time(sfx.get("timestamp_start"), frame_rate)
        end = fmt_time(sfx.get("timestamp_end"), frame_rate)
        output_filename = f"{slugify(sfx_id)}.mp3"

        sfx_searches = [pixabay_sound_effect_url(term) for term in terms]
        music_searches = [pixabay_music_url(term) for term in terms] if (args.include_music or item_wants_music(sfx)) else []

        selection_template["selections"].append(
            {
                "id": sfx_id,
                "name": sfx.get("name", ""),
                "pixabay_page_url": "",
                "direct_download_url": "",
                "title": "",
                "creator": "",
                "duration": "",
                "output_filename": output_filename,
                "rights_note": RIGHTS_NOTE,
                "status": "needs-source",
            }
        )

        lines.extend(
            [
                f"### `{sfx_id}` - {clean_cell(sfx.get('name', 'Unnamed SFX'))}",
                "",
                f"- time: {start} - {end}",
                f"- scene: {clean_cell(sfx.get('scene', 'N/A'))}",
                f"- visual: {clean_cell(sfx.get('visual', 'N/A'))}",
                f"- mix: {sfx.get('mix_level_db', 'N/A')}dB peak ({clean_cell(sfx.get('mix_level_percent', 'N/A'))})",
                f"- output filename: `{output_filename}`",
                "",
                "Source terms:",
            ]
        )
        lines.extend(f"- {term}" for term in terms)
        lines.extend(["", "Pixabay Sound Effects searches:"])
        lines.extend(f"- {url}" for url in sfx_searches)
        if music_searches:
            lines.extend(["", "Pixabay Music searches:"])
            lines.extend(f"- {url}" for url in music_searches)

        lines.extend(["", "Local media candidates:"])
        if local_hits:
            lines.extend(f"- {hit}" for hit in local_hits)
        else:
            lines.append("- none found in the current media-library index")

        lines.extend(
            [
                "",
                "Manifest row hint:",
                "",
                "| Asset ID | Scene / Beat | Type | Need | Source path / URL / prompt | Status | Rights note | Fallback | Next action |",
                "|----------|--------------|------|------|----------------------------|--------|-------------|----------|-------------|",
                f"| {clean_cell(sfx_id)} | {clean_cell(sfx.get('scene', ''))} | sfx | {clean_cell(sfx.get('name', ''))} | [Pixabay page URL or local reuse path] | needs-source | {RIGHTS_NOTE} | self-record or no-SFX edit | select source and fill download template |",
                "",
            ]
        )

    sourcing_path.write_text("\n".join(lines), encoding="utf-8")
    write_json(template_path, selection_template)

    print("Generated:")
    print(f"  - {sourcing_path}")
    print(f"  - {template_path}")


def valid_pixabay_page(url: str) -> bool:
    return any(url.startswith(prefix) for prefix in ALLOWED_PAGE_PREFIXES)


def content_ext(content_type: str, url: str) -> str:
    path_ext = Path(urlparse(url).path).suffix.lower()
    if path_ext in AUDIO_EXTENSIONS:
        return path_ext
    content_type = (content_type or "").split(";", 1)[0].strip().lower()
    return {
        "audio/mpeg": ".mp3",
        "audio/mp3": ".mp3",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        "audio/mp4": ".m4a",
        "audio/ogg": ".ogg",
        "audio/flac": ".flac",
    }.get(content_type, ".mp3")


def download_audio(url: str, target_base: Path, overwrite: bool) -> tuple:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "audio/*,*/*"})
    ctx = ssl.create_default_context()
    with urlopen(req, context=ctx, timeout=90) as resp:
        ext = target_base.suffix.lower()
        if ext not in AUDIO_EXTENSIONS:
            ext = content_ext(resp.headers.get("Content-Type", ""), url)
            target = target_base.with_suffix(ext)
        else:
            target = target_base
        if target.exists() and not overwrite:
            return target, "skipped-exists"
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as f:
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                f.write(chunk)
    return target, "downloaded"


def safe_output_filename(selection: dict) -> str:
    raw = selection.get("output_filename") or selection.get("filename") or selection.get("id") or selection.get("title")
    name = Path(str(raw)).name
    if not name or name in {".", ".."}:
        name = f"{slugify(selection.get('id', 'pixabay-sfx'))}.mp3"
    return name


def load_selections(path: Path) -> tuple:
    data = load_json(path)
    if isinstance(data, list):
        return {}, data
    selections = data.get("selections") or data.get("items") or []
    if not isinstance(selections, list):
        raise ValueError("Selection JSON must contain a list under `selections`.")
    return data, selections


def manifest_row(item: dict) -> str:
    return (
        "| {id} | {title} | sfx | {page_url} | {status} | {rights_note} | {local_path} | {fallback} |"
    ).format(
        id=clean_cell(item.get("id", "")),
        title=clean_cell(item.get("title") or item.get("name", "")),
        page_url=clean_cell(item.get("pixabay_page_url", "")),
        status=clean_cell(item.get("status", "needs-source")),
        rights_note=clean_cell(item.get("rights_note", RIGHTS_NOTE)),
        local_path=clean_cell(item.get("local_path", "")),
        fallback=clean_cell(item.get("fallback", "self-record or no-SFX edit")),
    )


def download_selected(args) -> None:
    repo_root = find_repo_root()
    selected_path = Path(args.download_selected)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    meta, selections = load_selections(selected_path)
    media_dir_raw = args.media_dir or meta.get("media_dir") or default_media_dir(meta.get("project_slug", "sfx-project"))
    media_dir = resolve_repo_path(media_dir_raw, repo_root)
    created = datetime.now(timezone.utc).isoformat()

    tracker = {
        "created": created,
        "source_selection": str(selected_path),
        "media_dir": display_path(media_dir, repo_root),
        "rights_note": RIGHTS_NOTE,
        "items": [],
    }

    for selection in selections:
        item_id = selection.get("id") or slugify(selection.get("title", "pixabay-sfx"))
        page_url = str(selection.get("pixabay_page_url") or selection.get("page_url") or "").strip()
        download_url = str(selection.get("direct_download_url") or selection.get("download_url") or "").strip()
        filename = safe_output_filename(selection)
        target_base = media_dir / filename

        record = {
            "id": item_id,
            "name": selection.get("name", ""),
            "title": selection.get("title", ""),
            "creator": selection.get("creator", ""),
            "duration": selection.get("duration", ""),
            "pixabay_page_url": page_url,
            "local_path": "",
            "rights_note": selection.get("rights_note") or RIGHTS_NOTE,
            "attribution_note": selection.get("attribution_note", ""),
            "fallback": selection.get("fallback", "self-record or no-SFX edit"),
            "status": "needs-source",
        }

        if page_url and not valid_pixabay_page(page_url):
            record["status"] = "needs-approval"
            record["error"] = "Pixabay page URL is not under /sound-effects/ or /music/."
            tracker["items"].append(record)
            continue

        if not page_url or not download_url:
            record["status"] = "needs-source"
            record["error"] = "Missing Pixabay page URL or direct download URL."
            tracker["items"].append(record)
            continue

        try:
            target, status = download_audio(download_url, target_base, args.overwrite)
            record["local_path"] = display_path(target, repo_root)
            record["status"] = "ready" if status == "downloaded" else status
            record["download_host"] = urlparse(download_url).netloc
        except HTTPError as exc:
            record["status"] = "needs-source"
            record["error"] = f"HTTP {exc.code}: {exc.reason}"
        except (URLError, TimeoutError, OSError) as exc:
            record["status"] = "needs-source"
            record["error"] = str(exc)

        tracker["items"].append(record)

    tracker_path = out_dir / "pixabay-sfx-download-tracker.json"
    manifest_path = out_dir / "pixabay-sfx-manifest-rows.md"
    write_json(tracker_path, tracker)

    manifest_lines = [
        "# Pixabay SFX Manifest Rows",
        "",
        "| Asset ID | Need | Type | Source path / URL | Status | Rights note | Local path | Fallback |",
        "|----------|------|------|-------------------|--------|-------------|------------|----------|",
    ]
    manifest_lines.extend(manifest_row(item) for item in tracker["items"])
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    print("Generated:")
    print(f"  - {tracker_path}")
    print(f"  - {manifest_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Pixabay SFX source packets or download selected SFX assets.")
    parser.add_argument("--config", help="SFX map JSON config used to build the sourcing packet")
    parser.add_argument("--download-selected", help="Filled selection JSON with chosen Pixabay page and download URLs")
    parser.add_argument("--out", default=".", help="Output directory for source packet or tracker files")
    parser.add_argument("--project-slug", help="Project slug for default local media paths")
    parser.add_argument("--media-dir", help="Local-only directory for selected raw audio downloads")
    parser.add_argument("--media-index", help="Media library index path for local reuse checks")
    parser.add_argument("--include-music", action="store_true", help="Also include Pixabay Music search links for every SFX row")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing downloaded files")
    args = parser.parse_args()

    mode_count = sum(bool(value) for value in [args.config, args.download_selected])
    if mode_count != 1:
        print("Error: Use exactly one of --config or --download-selected", file=sys.stderr)
        sys.exit(1)

    if args.config:
        build_sourcing_packet(args)
    else:
        download_selected(args)


if __name__ == "__main__":
    main()
