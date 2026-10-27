# Reference Intake Dependencies

Install these to enable full OCR and transcription during media acquisition.

## Required

- `ffmpeg` and `ffprobe` — video/audio probing and frame extraction
  - `brew install ffmpeg`
- `yt-dlp` — social video download
  - `brew install yt-dlp`

## Optional

- `tesseract` — OCR on sampled video frames
  - `brew install tesseract`
- `whisper` (OpenAI Whisper) — local audio transcription
  - `brew install pipx && pipx ensurepath && pipx install openai-whisper`
  - Make sure `~/.local/bin` is on your PATH.

If these are missing, the script records a warning and continues without OCR or transcription.
