---
name: audio-rip
description: Download reference or cleared audio from YouTube and extract drum/instrument/vocal stems for short-form videos, trailers, and campaigns. Use when temp music, study audio, licensed audio, or local stem extraction is needed.
license: MIT
---

# Audio Rip

Download reference or cleared audio from YouTube and extract stems (drums, vocals, bass, etc.) for video projects. Built for trailer campaigns that need layered audio, such as an ambient base track plus a drum transition.

## When to Use

- You need temp, reference, licensed, or otherwise cleared audio from YouTube for a video project
- You want to extract stems (drums, vocals, bass) to layer under other audio
- You're building a trailer with a transition: slow ambient into industrial drums
- You need local stem extraction without uploading audio to a third-party service
- **You need sound effects, foley, or room tone that the media library doesn't have** — use `--no-stems --section`

## Ripping SFX and Foley

Stem separation is meaningless on a pencil scratch or a room tone. For SFX, skip it and pull only the seconds you need:

```bash
python3 skills/workflows/video-production/audio-rip/scripts/audio-rip.py \
  "https://www.youtube.com/watch?v=..." \
  libraries/media/local-media/[project-slug]/audio/sfx-source/rips \
  --no-stems --section "0:01-0:13"
```

Find candidates first with `media-sourcing/scripts/search-youtube-reference.py --query "..." --cc-only`, which ranks results and flags Creative Commons mentions. Then feed the rips into `sound-effects-mix/scripts/build-sfx-layers.py` to produce levelled stems with a rights column.

Never leave a run holding an SFX checklist when the audio can be ripped.

## Beat Map for Music Visuals

For a composition that moves with a song, bake the music into data:

```bash
python3 skills/workflows/video-production/audio-rip/scripts/beat_map.py \
  song.mp3 remotion/src/compositions/.../beat-map.ts \
  --start 27.36 --bars 8 --bpm 70.86 --clip remotion/public/audio/.../clip.mp3
```

- `--start` is the first downbeat. Find it from the bass jump at the drop.
- Measure BPM from snare spacing. Don't guess it.
- Output: per-frame `low`, `mid`, `high` (0-1) and hit frames per band.
- Needs ffmpeg, numpy and scipy. No librosa.

## Prerequisites

- **yt-dlp** installed (via Homebrew: `brew install yt-dlp`)
- **Demucs** (auto-installed in skill venv on first run)

## Quick Command

```bash
python3 skills/workflows/video-production/audio-rip/scripts/audio-rip.py \
  "https://youtube.com/watch?v=..." \
  /path/to/campaign/music/
```

**Output:**
- `music/temp-tracks/Track_Title.mp3` — original MP3
- `music/Track_Title__beat.mp3` — instrumental (no vocals)
- `music/Track_Title__vocals.mp3` — vocals only

## Workflow

### Step 1: Download from YouTube

The skill downloads the audio as a high-quality MP3:

```bash
yt-dlp --no-playlist --extractor-args "youtube:player_client=android_vr" -x --audio-format mp3 --audio-quality 0 -o "temp-tracks/%(title)s.%(ext)s" "<url>"
```

The YouTube client argument avoids browser-cookie and Keychain access. Do not use `--cookies-from-browser`, request Keychain credentials, or upgrade packages in response to a transient HTTP 403.

### Step 2: Extract Stems (Local Demucs)

Demucs runs locally to split into **vocals** + **no_vocals** (beat/instrumental):

```bash
python -m demucs.separate --two-stems vocals --mp3 -o stems/ <mp3>
```

No upload to third-party services required. First run downloads the model (~100 MB).

### Step 3: Layer in Editor

Import both files into your video editor:

| Track | File | Volume Automation |
|-------|------|-------------------|
| 1 | Base instrumental (ambient/slow) | Constant |
| 2 | Extracted drum stem | Silent → 15% → 40% → 100% → Cut |

Example automation for a 48-sec trailer with drums entering at 0:18:

```
0:00–0:18   → 0%   (drums silent, base track only)
0:18–0:22   → 15%  (fade in under VO)
0:22–0:27   → 40%  (noticeable, building)
0:27–0:42   → 100% (full industrial beat under montage)
0:42        → Cut  (hard cut to silence)
```

## Free Base Track Sources

If you need a clean ambient/instrumental base layer:

| Source | URL | Search Terms |
|--------|-----|--------------|
| Mixkit | https://mixkit.co/free-stock-music/ | `ambient`, `cinematic`, `tension`, `drone` |
| Pixabay | https://pixabay.com/music/ | `dark cinematic`, `piano tension`, `ambient` |
| YouTube Audio Library | https://www.youtube.com/audiolibrary | `cinematic`, `tension`, `ambient` |

Confirm each track's current license before public or commercial use.

## File Structure

```
campaign-folder/
├── music/
│   ├── temp-tracks/       # raw downloads from YouTube
│   ├── stems/             # extracted drums, vocals, etc.
│   ├── licensed-tracks/   # final purchased tracks (if any)
│   └── sfx/               # sound effects
```

## Commands

| Command | Purpose |
|---------|---------|
| `download-youtube <url> <output-dir>` | Download YouTube audio as MP3 |
| `download-youtube --playlist <url> <output-dir>` | Download entire playlist |

## Rules

- Never commit raw MP3s to git. Use `.gitignore` in `music/`.
- Always check if you already have the file before re-downloading.
- For public or commercial projects, document rights clearance or replace temp audio with a licensed track.
- Stem quality varies by tool. If drums sound muddy, try Lalal.ai instead of Moises.

## Common Issues

| Issue | Fix |
|-------|-----|
| "yt-dlp not found" | `brew install yt-dlp` |
| Download is video not audio | Script uses `--extract-audio --audio-format mp3` |
| Stem sounds low quality | Try a different splitter, or buy the lossless track |
| Drums have bleed from vocals | Use Lalal.ai (higher quality) or accept some bleed |

## Example: Full Trailer Audio Stack

| Time | Layer 1 (Base) | Layer 2 (Drums) | Layer 3 (SFX) |
|------|----------------|-----------------|---------------|
| 0:00–0:03 | Ambient drone | — | Room tone |
| 0:03–0:08 | Ambient drone | — | Rain, thunder |
| 0:08–0:13 | Ambient drone | — | Pencil, paper |
| 0:13–0:18 | Ambient drone | — | — |
| 0:18–0:22 | Ambient drone | 15% | — |
| 0:22–0:27 | Ambient drone | 40% | — |
| 0:27–0:42 | Ambient drone | 100% | Jet, keyboard, hammer |
| 0:42–0:58 | Cut to silence | Cut to silence | Cut to silence |
