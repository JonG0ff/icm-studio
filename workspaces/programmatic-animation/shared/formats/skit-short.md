# Format: Skit Short

A short multi-character comedy sketch. Laugh first.

## Settings

| Field | Value |
|-------|-------|
| Platform | Instagram Reels, 9:16 |
| Length | Story sets it. No cap; a longer skit runs the same process (owner, 2026-10-19). 20 s minimum. |
| Speakers | 1-3 on screen. Every line has a speaker. |
| Variants | 1 hook variants. 1 means no split test. |
| Captions | Word by word, key word in accent color, ink stroke, no background pill |

## Structure

| Section | Length | Job |
|---------|--------|-----|
| cold-open | 0-3 s | Drop straight into the bit. No intro, no "hey guys". |
| setup | 3-12 s | Who, where, what's wrong. One setting. |
| escalation | 12 s to the button | Two or more beats, each bigger than the last. |
| button | last 3-6 s | One final joke or hold. Then cut. |

## Hook Rules

- The first line is the hook. It's a voiced line, not a title card.
- The first frame shows the setting and a character mid-action.
- Hook variants change only the hook lines. The body stays the same.
- Follow `libraries/business-memory/sops/reel-hook-design.md` for hook craft.
- Split-test variants follow `libraries/business-memory/sops/reel-split-test.md`.

## Writing Rules

- One setting per skit.
- Lines are short. Most under 12 words.
- A joke every 5-8 seconds.
- Use holds and silence for timing. Mark them in blocking, not the script.
- Physical comedy must be in the "easy in code" list in `../staging-limits.md`.

## Ending

- End on the button, not a call to action.
- Optional end card: none.

## Render

- One mp4 per variant: `v1`, `v2`, ...
- The manifest says which hook each variant uses.
