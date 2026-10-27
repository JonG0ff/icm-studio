# Script Format

How `script.md` is written. The voice and timing scripts parse it, so the line shape is strict.

## Header

```
# [slug] script
format: skit-short
look: flash-cutout
cast: HOST, GUEST
variants: 3
```

## Spoken Lines

One spoken line per row:

```
[b-01] HOST: Good evening. I'm standing in the eye of the storm. [whispering]
```

- `[id]` comes first. Then the speaker, a colon, and the text.
- Speaker names are UPPER_SNAKE and match the brief's cast.
- ElevenLabs audio tags go in square brackets inside the text. Tag rules live in the `elevenlabs-voiceover` skill.
- Everything else (headings, notes, blank rows) is ignored by the scripts.

## Line IDs

| ID | Meaning |
|---|---|
| `b-01`, `b-02` ... | Body lines, in order |
| `h1-01`, `h1-02` ... | Hook lines for variant 1 |
| `h2-01` ... | Hook lines for variant 2 |

- IDs are two digits and never reused in one script.
- Variant N plays hook lines `hN-*`, then every body line.
- No hook lines means one variant: the body.
- Change a line's text, keep its ID. Re-roll only that line.

## Sections

Use headings so a person can read it:

```
## hook v1
[h1-01] HOST: ...

## hook v2
[h2-01] HOST: ...

## body
[b-01] HOST: ...
[b-02] GUEST: ...
```

## Stage Directions

- Put action notes on their own row in parentheses: `(HOST spins the chair)`.
- They aren't voiced. Blocking reads them.

## Brought Scripts

- If a brought script has no IDs, bring intake adds them in order.
- If a line has no speaker, bring intake flags it. It doesn't guess.
