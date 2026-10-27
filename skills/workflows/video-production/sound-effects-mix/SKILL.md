---
name: sound-effects-mix
description: Plan, source, and document sound effects mixes for short-form videos, trailers, reels, and cinematic brand edits. Use when Codex needs SFX timing, Pixabay search links, selected SFX downloads, source/license tracking, mix levels, EQ notes, ducking, ambience, foley, or editor-ready sound design notes.
license: MIT
---

# Sound Effects Mix

Build an editor-ready SFX map for a short-form video. Map effects to footage, time them to music and VO, and provide per-effect mix metadata so each layer supports the edit without overpowering it.

## When to Use

- A trailer, reel, montage, or brand film needs sound design.
- The edit has VO, music, footage, or scene timing.
- You need SFX source terms, file naming, and placement notes.
- You need mix levels, EQ, ducking, and hard-cut instructions.

## Quick Start

```bash
cd skills/workflows/video-production/sound-effects-mix/scripts
pip install -r requirements.txt
python3 generate-sfx-map.py \
  ../templates/trailer-campaign-01-sfx.json \
  /path/to/campaign/music/sfx/
```

Build the Pixabay sourcing packet from the same map:

```bash
python3 source-pixabay-sfx.py \
  --config ../templates/trailer-campaign-01-sfx.json \
  --out /path/to/campaign/music/sfx/ \
  --project-slug campaign-slug
```

After selected Pixabay assets are approved, fill `pixabay-sfx-selection-template.json` with the asset page URL, creator, title, duration, and direct download URL. Then download only those selected assets:

```bash
python3 source-pixabay-sfx.py \
  --download-selected /path/to/campaign/music/sfx/pixabay-sfx-selection-template.json \
  --out /path/to/campaign/music/sfx/
```

Output:

- `sfx-timeline.md` - editor-friendly placement guide with timecodes
- `sfx-download-checklist.md` - sourcing checklist with search terms
- `sfx-processing-notes.md` - per-clip EQ, filter, and ducking instructions
- `pixabay-sfx-sourcing.md` - Pixabay search links, local reuse checks, and manifest row hints
- `pixabay-sfx-selection-template.json` - selected asset fields to fill in before download
- `pixabay-sfx-download-tracker.json` - selected download results without storing raw download URLs
- `pixabay-sfx-manifest-rows.md` - asset manifest rows ready to paste into a production packet

## Mix Rules

1. Put SFX under the music unless a visible action needs emphasis.
2. Keep background and support effects subtle: usually 5-15% perceived loudness.
3. High-pass ambient SFX below 80-120Hz to avoid fighting music bass.
4. Duck SFX 2-4dB when the music hit or VO needs the pocket.
5. At hard cuts, cut effects cleanly unless the edit specifically calls for a tail.
6. Use one dominant sound idea per visual beat.

## SFX Map Format

Every project is defined by a JSON config:

```json
{
  "project_name": "Example Campaign Trailer 01",
  "frame_rate": 24,
  "music_bpm": 120,
  "hard_cut_seconds": 42,
  "sfx": [
    {
      "id": "01_ambient_room",
      "name": "Ambient Room Tone",
      "description": "Near silence, distant city hum, subtle tension",
      "timestamp_start": 0.0,
      "timestamp_end": 3.0,
      "scene": "Opening",
      "visual": "Black frame, film grain",
      "mix_level_db": -30,
      "mix_level_percent": "5%",
      "eq": { "high_pass_hz": 80, "low_pass_hz": 8000, "shelf_boost_db": 0 },
      "processing": ["high-pass at 80Hz", "very light compression 2:1"],
      "duck_to_music": false,
      "source_terms": ["room tone subtle hum cinematic tension"],
      "suggested_sources": ["Pixabay Sound Effects", "Freesound", "Storyblocks"],
      "file_format": "48kHz / 24-bit WAV",
      "placement": "Stereo, low and wide",
      "notes": "Keep it felt more than heard"
    }
  ]
}
```

## Field Reference

| Field | Description |
|---|---|
| `id` | File-name-friendly ID, prefix with scene number |
| `name` | Human-readable SFX name |
| `timestamp_start` / `timestamp_end` | Timeline placement in seconds |
| `scene` | Narrative scene or visual beat |
| `visual` | Footage or on-screen action |
| `mix_level_db` | Target peak level |
| `mix_level_percent` | Approximate perceived loudness vs music |
| `eq` | High-pass, low-pass, and shelf settings |
| `processing` | Processing instructions |
| `duck_to_music` | Whether this SFX ducks against the music |
| `source_terms` | Search keywords for libraries |
| `suggested_sources` | Where to look first |
| `file_format` | Delivery spec |
| `placement` | Panning or stereo width note |
| `notes` | Director/editor intent |

## Mix Levels Guide

| Context | dBFS Peak | Perceived % | Example |
|---|---:|---:|---|
| Near-silence open | -30 to -24 | 3-5% | Room tone, distant hum |
| Ambient bed | -24 to -18 | 5-10% | Rain, city rumble |
| Foley detail | -20 to -15 | 10-15% | Pencil, paper, keyboard |
| Subtle punch | -18 to -12 | 10-15% | Jet, hammer, car pass |
| Music peak | -6 to -3 | 80-90% | Main track |
| VO | -12 to -9 | 60-70% | Voiceover |

## Processing Defaults

| Type | Default |
|---|---|
| Ambient / room tone | High-pass 80Hz, low-pass 8kHz, light compression, stereo spread |
| Foley | High-pass 120Hz, small 2-4kHz presence boost, pan toward visual |
| Mechanical | High-pass 60Hz, low-pass 12kHz, optional sidechain compression |
| Nature / organic | High-pass 100Hz, moderate compression, wide stereo |

## File Naming

```text
{NN}_{scene_slug}_{sfx_slug}.{ext}
```

Examples:

- `01_opening_ambient_room.wav`
- `02_waiting_rain_window.wav`
- `07_build_rocket_engine.wav`

## Sourcing Priority

1. Existing media library assets with matching rights and local paths
2. Pixabay Sound Effects for royalty-free SFX, risers, whooshes, impacts, ambience, and short stingers
3. Pixabay Music for royalty-free music beds, loops, and logo-style audio when the edit needs simple cleared music
4. Storyblocks Audio
5. Artlist SFX
6. Epidemic Sound
7. Freesound.org, filtered for usable license
8. Self-recorded room tone, foley, or environment sounds

## Sourcing And Download Flow

Use `source-pixabay-sfx.py` when the SFX map needs actual source options or selected downloads.

1. Generate the SFX map with `generate-sfx-map.py`.
2. Run `source-pixabay-sfx.py --config ...` to create a Pixabay sourcing packet.
3. Open the generated search links and pick only assets that match the visual beat.
4. Confirm the asset page says it is covered by the Pixabay Content License.
5. Fill `pixabay-sfx-selection-template.json` with the page URL, title, creator, duration, and direct download URL.
6. Run `source-pixabay-sfx.py --download-selected ...` to download selected files into `libraries/media/local-media/[project-slug]/audio/sfx/` by default.
7. Copy rows from `pixabay-sfx-manifest-rows.md` into the asset manifest or edit package.

The script does not scrape search pages or mass-download results. It creates search links and downloads only selected direct audio URLs. Do not commit a filled selection JSON if it contains direct download URLs.

### Never end a stage with markdown and no audio

Steps 3-5 above are manual, because Pixabay tokenises sound-effects downloads per browser session. If nobody performs them, the run is left holding a checklist instead of stems. That is a stage failure, not a completed stage.

When the Pixabay loop has not been walked, get real audio another way — Pixabay is one source, not the only one:

1. **Local library first.** Check `libraries/media/assets/index.md` for cleared whooshes, impacts, risers, keyboard, and mouse clicks. The public studio includes no starter audio pack. If the catalog is empty, continue to the sourcing step below.
2. **Rip it.** Anything the library lacks — room tone, foley, ambience — is on YouTube in free-SFX uploads. Use the `audio-rip` skill:
   ```bash
   python3 skills/workflows/video-production/audio-rip/scripts/audio-rip.py \
     "<youtube-url>" [project]/audio/sfx-source/rips --no-stems --section "0:01-0:13"
   ```
   Find candidates with `media-sourcing/scripts/search-youtube-reference.py --query "..."`, which ranks results and flags Creative Commons mentions. Prefer known foley creators (InspectorJ and similar) — their licensing is documented.
3. **Synthesis last.** Only for beds where it is genuinely standard practice, and only when 1 and 2 came up empty.

Then assemble every layer into deliverable stems:

```bash
python3 build-sfx-layers.py \
  --config [project]/audio/sfx-source/sfx-layers.json \
  --library libraries/media/local-media \
  --out [project]/audio/sfx
```

Each stem is written at the config's sample rate and bit depth and normalised to one reference peak, so the mix column in the timeline stays a fader value rather than being baked into the file. Record a `rights` string on every layer; anything left unrecorded or marked for confirmation lands in a **Confirm licence before publishing** section of the generated report.

Stems that stand in for a real recording must be marked `"grade": "placeholder"`. They land in a **Replace before final mix** section and must not ship without being swapped.

## Pixabay Notes

Use `PIXABAY_API_KEY` only in local `.env` or exported shell state. Do not write the real key into skill docs, asset records, or project packets.

Pixabay's public API docs cover image and video search. For Sound Effects and Music, use the public Pixabay asset pages and selected-download workflow unless a stable audio API is verified for the current task.

For each selected Pixabay SFX or music asset, record:

- Pixabay page URL
- asset title and creator
- duration
- local path if downloaded
- rights note: `Pixabay Content License`
- attribution note if the editor chooses to credit the creator

Use `needs-approval` instead of `ready` if the asset page or intended use raises third-party rights concerns.

## Command Reference

| Script | Purpose |
|---|---|
| `generate-sfx-map.py` | Generate the editor SFX timeline, download checklist, and processing notes from a JSON SFX map |
| `source-pixabay-sfx.py --config` | Generate Pixabay search links, local media reuse checks, and a selection template |
| `source-pixabay-sfx.py --download-selected` | Download explicitly selected Pixabay audio and write tracker/manifest rows |
| `build-sfx-layers.py` | Build every layer into a delivered WAV stem from local library audio plus synthesis, with a provenance report |

## Rules

- Never commit raw SFX files to git.
- Never commit filled selection JSON if it contains direct download URLs.
- Download only selected SFX assets. Do not mass-download Pixabay search results.
- Always keep stems separate.
- Label every file with a scene prefix.
- Record source and license notes for every external SFX file.
- If a sourced SFX clip is longer than needed, trim inside the editor and keep the original file intact.
