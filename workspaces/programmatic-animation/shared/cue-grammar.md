# Cues Grammar

How `cues.md` is written. It's the storyboard, timed to the voice.

## Shape

```
music: news-bed 0.2

# cold-open

## cold-open.reveal "standing in the eye" [sfx: wind-gust]
set: hurricane-beach. on: HOST (center, mic-hold, worried).
Camera pushes in slowly. Rain gets heavier.
```

- `# name` is a section. It becomes one scene block and, in long form, one chapter.
- `## section.beat "quote"` is a beat. The quote is 3-6 words copied from the script.
- `[sfx: name]` tags are optional. Several are fine.
- The line under a beat says what's on screen in plain words.

## Beat Fields

Put these on the first row under a beat. Leave out what doesn't change.

| Field | Example | Rule |
|---|---|---|
| `set:` | `hurricane-beach` | A library set slug |
| `on:` | `HOST (center, mic-hold, worried)` | Speaker, then position, pose, expression |
| `prop:` | `umbrella-inverted` | A library prop slug |
| `camera:` | `push-in`, `whip-pan`, `smash-cut`, `hold` | One move per beat |
| `fx:` | `rain-heavy`, `speed-lines` | Code effects |
| `hold:` | `0.8s` | A silent beat after the line, for timing jokes |

## Rules

- Change the beat every 3-8 seconds.
- Every quote must match words in `words.json`.
- Poses, expressions, sets and props must exist in the library entry for that piece.
- Cues never name a look. The same cues render in any look.
- No frame numbers, no component names, no pixel positions. That's the scene stage's job.
- A button joke or hold at the end gets its own beat.

## Music

- One `music:` line at the top sets the bed and level.
- A section can override it with its own `music:` line.
- Every music and SFX file needs a rights note in `sfx-map.md`.
