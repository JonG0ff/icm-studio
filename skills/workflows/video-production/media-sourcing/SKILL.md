---
name: media-sourcing
description: Source footage, still images, music, and sound effects for short-form video production through Pexels, Wikimedia Commons, Pixabay, YouTube reference clips, web stills (named athletes, movie publicity, news/press), or manual source research. Use when a scene plan needs footage, stills, b-roll, event/topic images, roster/news stills, reference clips, music/SFX source options, rights notes, or fallback assets.
license: MIT
---

# Media Sourcing

Find source media for short-form video production. Route by source method, record rights status, and write enough source notes for the asset manifest before edit lock.

Use this skill for footage, stills, b-roll, reference clips, music/SFX source options, and source/fallback research. Use `audio-rip` after a source is selected when you need local audio extraction, temp rips, stems, or format conversion.

## Source Methods

| Method | Use For | Deliverable Risk |
|---|---|---|
| Pexels video | Licensed stock footage and b-roll | Low when source notes are recorded |
| Pexels photo | Licensed stills, plates, backgrounds, overlays; mood/object/place plates | Low when source notes are recorded |
| Wikimedia Commons | Free/publicly licensed event, sports, public-figure, archival, and topic stills | Medium; each file needs page URL, creator/credit, license, attribution, and context review |
| Web still | Named athletes, celebrities, movie publicity, news/press stills for organic reels when stock will miss | High; record source URL; `rights_note: unclear`; file on disk is usable in FCP |
| Pixabay music | Royalty-free music beds, loops, intros, and stingers | Low when Content License notes and source page are recorded |
| Pixabay sound effects | Royalty-free SFX, risers, whooshes, impacts, ambience, and foley | Low when Content License notes and source page are recorded |
| YouTube reference | Internal reference clips, pacing study, shot analysis; freeze a frame when the best hit is a highlight/trailer | High; never public deliverables without separate rights clearance |
| Manual source | Other libraries, client assets, public archives, screenshots, or unverified finds | Depends on rights; mark unclear assets `needs-approval` or `blocked` |

## Output Rule

Every external asset needs a manifest row with:

- source URL or local path
- asset type: `footage`, `still`, `music`, or `sfx`
- status: `ready`, `needs-approval`, or `blocked`
- rights note: public, owned, licensed, generated, pending, internal-reference-only, or unclear
- fallback when rights are risky or unclear

For Wikimedia Commons, do not treat search results as news-wire photos. Mark an asset `ready` only when the Commons file page, direct file URL, creator or credit line, license name or terms, license URL or terms evidence, attribution requirement, and delivery-context risks are recorded.

For web stills, require a direct source URL and local path. Use `rights_note: unclear`. File on disk is usable in FCP; keep the source URL so the still can be swapped if a reel gets pulled.

## Editor Delivery

Repo paths are for the system. The editor works from Finder, so any sourcing run that hands
media to a human also delivers a clean copy at `~/Desktop/[short-slug]-[stills|footage]/`:
numbered folders by beat, media files only, `PICK_` on recommendations, then `open` it in
Finder. For stills, use `../still-bank/scripts/build-editor-folder.py`.

## Pexels Video

Set the API key:

```bash
export PEXELS_API_KEY="your_key_here"
```

Search from a campaign shot list:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-pexels.py \
  --campaign /path/to/campaign \
  --per-shot 3 \
  --orientation portrait
```

Run a one-off search:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-pexels.py \
  --query "night city aerial skyline cinematic" \
  --count 5 \
  --out /path/to/campaign/assets/footage
```

Search from JSON:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-pexels.py \
  --config searches.json \
  --out /path/to/campaign/assets/footage
```

`searches.json`:

```json
[
  {"shot_id": "shot-07", "query": "neon sign flickering night rain", "count": 3},
  {"shot_id": "shot-12", "query": "empty subway tunnel light cinematic", "count": 3}
]
```

Outputs:

- `assets/footage/shot-{NN}_option-{N}.mp4`
- `assets/footage/download-tracker.json`

## Pexels Stills

Search from a campaign shot list:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-pexels-photos.py \
  --campaign /path/to/campaign \
  --per-shot 3 \
  --orientation portrait
```

Run a one-off search:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-pexels-photos.py \
  --query "night city skyline silhouette copy space" \
  --count 5 \
  --out /path/to/campaign/assets/stills
```

Search from JSON:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-pexels-photos.py \
  --config searches.json \
  --out /path/to/campaign/assets/stills
```

Outputs:

- `assets/stills/shot-{NN}_option-{N}.jpg`
- `assets/stills/download-tracker.json`

## Wikimedia Commons Event And Topic Stills

Use Wikimedia Commons for free/publicly licensed stills around public events, sports, public figures, places, organizations, and archival topics. Commons is not Getty or a live news-wire feed; search by topic and verify each file's license and attribution before use.

No API key is required. Set a clear user agent for live API searches:

```bash
export WIKIMEDIA_USER_AGENT="icm-studio-media-sourcing/1.0 (contact: your email or project URL)"
```

Search one topic:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-wikimedia-commons.py \
  --query "2026 FIFA World Cup Portugal Croatia" \
  --limit 5 \
  --out /path/to/campaign/assets/commons
```

Search from a campaign shot list:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-wikimedia-commons.py \
  --campaign /path/to/campaign \
  --per-shot 5
```

Search from JSON:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-wikimedia-commons.py \
  --config commons-searches.json \
  --out /path/to/campaign/assets/commons
```

`commons-searches.json`:

```json
[
  {"shot_id": "shot-03", "query": "Portugal Croatia football match", "limit": 5},
  {"shot_id": "shot-04", "query": "United States Belgium World Cup", "limit": 5}
]
```

Outputs:

- `commons-candidates.json`
- `commons-candidates.md`

The script searches the Commons file namespace through the MediaWiki API and writes metadata first. It does not download files unless you run selected-download mode:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-wikimedia-commons.py \
  --download-selected /path/to/campaign/assets/commons/commons-candidates.json \
  --selected-ids shot-03-commons-001 \
  --download-dir libraries/media/local-media/[project-slug]/commons
```

Source path:

1. Check `libraries/media/assets/index.md` before searching.
2. Search Commons with event/topic terms, including team names, event names, dates, venues, and public-figure names.
3. Review `commons-candidates.md` and open the Commons file page for any candidate you plan to use.
4. Record file page URL, direct file URL, creator or credit line, license, license URL or usage terms, attribution requirement, local path if downloaded, and fallback.
5. Download only selected files into an ignored local path, usually `libraries/media/local-media/[project-slug]/commons/`.
6. Mark the row `ready` only when source, license, creator/credit, and attribution evidence are recorded. Otherwise use `needs-approval` or `blocked`.

Rights note format:

```text
Wikimedia Commons file page and license metadata recorded. License: [license]. Creator/credit: [creator or credit]. Attribution required: [yes/no/unknown]. Check personality, trademark, event, and brand context before delivery.
```

Mark as `needs-approval` when the license or credit metadata is incomplete, the image includes recognizable people, team logos, sponsors, trademarks, sensitive news context, or the intended commercial/editorial use needs human review.

## Wikimedia Commons Category Crawl

Keyword search matches file *titles* and returns a thin slice — a few hits for a
subject that actually has dozens of files. Commons depth lives in **categories**.
Use this script when a named subject (person, film, work, event) is under-returning.

Measured on one still-first reel: keyword search found 20 stills across three subjects;
the category crawl found 130.

Discover which categories exist for a subject, with file counts:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-commons-categories.py \
  --discover "Andy Weir" "Sean Baker filmmaker"
```

Crawl categories from a config and download thumbnails:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-commons-categories.py \
  --config section-categories.json \
  --depth 1 --min-width 900 --per-section 6 \
  --out /path/to/candidates \
  --download-dir libraries/media/local-media/[project-slug]/commons-categories
```

`section-categories.json`:

```json
[
  {"section": "01-weir", "subject": "Andy Weir", "categories": ["Category:Andy Weir", "Category:The Martian"]}
]
```

Notes:

- `--depth 1` walks subcategories, which is where per-event photo sets live.
- Downloads use Wikimedia thumbnail widths only (120/250/330/500/960/1280/1920/3840).
  Custom widths return 400.
- Commons rate-limits hard. The script backs off on 429 and honours `Retry-After`;
  keep `--sleep` at 2s or higher.
- SVG, logos, maps, diagrams, and images under `--min-width` are dropped — they do
  not read at reel speed.
- One section per subject with a low `--per-section` gives range across many faces;
  one section with a high `--per-section` gives depth on one subject.

## Pixabay Music And Sound Effects

Use Pixabay for royalty-free music beds, ambience, foley, whooshes, risers, impacts, logo stingers, and short transition sounds.

Set the API key when an approved Pixabay tool or API flow is available:

```bash
export PIXABAY_API_KEY="your_pixabay_api_key_here"
```

The public Pixabay API docs currently describe image and video search. For music and sound effects, use the public Pixabay Music and Sound Effects pages unless a key-backed audio endpoint has been verified for the current task. Do not build mass-download or scraping flows around undocumented audio behavior.

For SFX maps, use the sound-effects helper to generate search links, local reuse checks, selected-download tracking, and manifest rows:

```bash
python3 skills/workflows/video-production/sound-effects-mix/scripts/source-pixabay-sfx.py \
  --config /path/to/sfx-map.json \
  --out /path/to/campaign/music/sfx/ \
  --project-slug campaign-slug
```

Source path:

1. Check `libraries/media/assets/index.md` before searching.
2. Search Pixabay Music or Pixabay Sound Effects with the scene's source terms, or generate the SFX search packet from `source-pixabay-sfx.py`.
3. Open the asset page and confirm the Content License summary.
4. Download only selected assets into an ignored local path, usually `libraries/media/local-media/[project-slug]/audio/`.
5. Add a manifest row with the Pixabay page URL, creator, asset title, duration, local path, and rights note.
6. Mark the row `ready` only when the Pixabay page URL and Content License note are recorded.

Rights note format:

```text
Pixabay Content License. Royalty-free use allowed; no attribution required, but credit appreciated. Source page, creator, title, and prohibited-use check recorded.
```

Mark as `needs-approval` when the asset includes recognizable people, brands, trademarks, unclear AI/personality references, or any use that could trigger third-party rights.

## YouTube Reference Clips

Use YouTube only for internal reference, study, and editorial practice unless rights are separately cleared. Ripped YouTube footage must not be used in client deliverables or public-facing content without clearance.

Search and score candidates:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/search-youtube-reference.py \
  --query "chicago navy pier winter ice waves" \
  --campaign /path/to/campaign \
  --cc-only
```

Rip a bounded reference segment:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/download-youtube-reference.py \
  "https://www.youtube.com/watch?v=..." \
  /path/to/campaign \
  --start 0:15 \
  --end 0:35
```

Outputs:

- `footage/YYYY-MM-DD-title.mp4`
- `footage/YYYY-MM-DD-title.json`

The sidecar marks the clip as `internal_use_only: true`.

## Web Stills

Use web stills when the brief needs a named athlete, celebrity, movie publicity frame, or news/press look that Pexels and Commons will miss.

Workflow:

1. Write a search packet: one row per still, with query and destination filename.
2. Find a **direct image URL** (browser, Wikipedia/Commons file URL, news image CDN, or a YouTube frame). Do not scrape Google Images in bulk.
3. Download only that URL into an ignored still-bank folder.
4. Write a sidecar with source URL, query, and local path so the file can be re-found.

Status: file on disk = usable in FCP. Record `rights_note: unclear` and keep the source URL. Do not block the download on license, personality, or trademark review.

Download one still:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/download-web-still.py \
  --url "https://example.com/photo.jpg" \
  --out libraries/media/local-media/still-bank/aug08-roster/ \
  --id aug08-messi-trophy \
  --query "Messi World Cup trophy celebration"
```

Batch from JSON:

```bash
python3 skills/workflows/video-production/media-sourcing/scripts/download-web-still.py \
  --config stills.json \
  --out libraries/media/local-media/still-bank/aug08-roster/
```

`stills.json`:

```json
[
  {"id": "aug08-messi-trophy", "url": "https://example.com/messi.jpg", "query": "Messi World Cup trophy celebration"},
  {"id": "aug08-ohtani-swing", "url": "https://example.com/ohtani.jpg", "query": "Ohtani swing stadium"}
]
```

Outputs:

- `[id].jpg` (or png/webp/gif from the response)
- `[id].json` sidecar (`url`, `query`, `filename`, `local_path`, `fetched_at`, `rights_note: unclear`)
- `web-still-download-tracker.json` for the batch

Default destination:

```text
libraries/media/local-media/still-bank/
  [pack-or-scene]/
```

When the best hit is a highlight or trailer rather than a photo, rip a bounded YouTube segment with `download-youtube-reference.py`, then extract one frame with ffmpeg into the same still-bank folder and write a matching sidecar by hand or via a follow-up `--url` of a hosted still if available.

Route:

- Named person / movie still / news-press look → web still (skip Pexels; it will miss).
- Mood / object / place (lamp room, theater, desk, car, mountains) → Pexels photo first.
- Commons remains useful when a free licensed file of the named person already exists and looks good enough.

## Manual Sources

Use manual source rows when a useful asset comes from a source this skill does not automate yet.

1. Save the URL, library name, creator, license page, or client-provided path.
2. Mark rights as `licensed`, `owned`, `public`, `pending`, `internal-reference-only`, or `unclear`.
3. If rights are unclear, use `needs-approval` or `blocked`.
4. Add at least one fallback source or generation option.

## Input Requirements

Campaign mode expects:

```text
campaign-folder/
|-- shot-list.md
`-- assets/
    |-- footage/
    `-- stills/
```

`shot-list.md` should include a `Stock Search Terms` column when available.

## Command Reference

| Script | Purpose |
|---|---|
| `search-pexels.py` | Search/download Pexels videos |
| `search-pexels-photos.py` | Search/download Pexels still images |
| `search-wikimedia-commons.py` | Search Commons event/topic files and write metadata-first candidates |
| `download-web-still.py` | Download a direct image URL into a still-bank folder with sidecar JSON |
| `../sound-effects-mix/scripts/source-pixabay-sfx.py` | Generate SFX search packets and download explicitly selected Pixabay audio |
| `search-youtube-reference.py` | Search/rank YouTube reference candidates |
| `download-youtube-reference.py` | Download a bounded YouTube reference segment |

## Rules

- Do not download full YouTube videos.
- Do not mark YouTube clips `ready` for public delivery unless separate rights clearance is documented.
- Do not treat Commons as a news-photo provider; verify each file page, license, creator/credit, and attribution need before use.
- Do not mass-download Commons results. Download only selected candidates into ignored local media paths.
- Do not scrape Google Images in bulk. Find one direct image URL per still, then download that URL.
- For web stills, require a source URL and local path; use `rights_note: unclear`. File on disk is enough to cut in FCP.
- Do not store API keys or paid-library credentials in repo files.
- Do not describe Pixabay assets as unlicensed. Use `royalty-free` and cite the Pixabay Content License.
- Do not mass-download Pixabay audio or rely on undocumented audio endpoints without task-specific verification.
- Keep original downloaded files intact.
- Record source and rights notes before edit lock.
