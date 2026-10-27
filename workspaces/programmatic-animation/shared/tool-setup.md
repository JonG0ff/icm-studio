# Tool Setup

What each stage needs installed. Check once per machine.

## Tools

| Tool | Stages | Required | Check |
|------|--------|----------|-------|
| Node 20+ and `remotion/` deps | workshop 03-04, production 06-07 | Yes | `node -v`, then `npm install` in `remotion/` |
| Python 3 | production 03-04, workshop 04 (voice) | Yes | `python3 --version` |
| ffmpeg and ffprobe | production 03-04, 06-07 | Yes | `ffmpeg -version` |
| ElevenLabs API key | workshop 04 (voice), production 03 | Yes | See below |
| Whisper | production 04 (brought audio only) | Optional | `whisper --help` |

- Install ffmpeg on macOS with `brew install ffmpeg`.
- Install Whisper with `pipx install openai-whisper`. Default model: medium.en.

## ElevenLabs Key

- Put `ELEVENLABS_API_KEY=` in the repo's `.env`. Never commit `.env`.
- Never print or read `.env` in a session. Pass the key through:
  ```
  env $(grep -h '^ELEVENLABS_API_KEY=' .env) python3 [script] ...
  ```
- Get a key: ElevenLabs dashboard, profile menu, API Keys. One key per project.

## Voice IDs

- Voice IDs are not secrets. They live in each voice's library entry.
- Production 03 builds `cast-voices.json` from those entries.

## Remotion Checks

Run from `remotion/` before any render:

```
npm run typecheck
npm run compositions
```
