# ElevenLabs v3 Audio Tags

Condensed reference for Eleven v3 (`eleven_v3`) audio tags. Full docs: [ElevenLabs v3 best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices).

## Requirements

- Model must be `eleven_v3`. Older models ignore or mishandle audio tags.
- Tags are `[bracketed]` natural-language cues. They are **not spoken**.
- A tag affects all following text until the next tag.
- Voice choice matters more than tags. Pick a voice that already matches the delivery, then tag for fine control.

## Tag format

```
[tag] Sentence or paragraph that follows this delivery.
```

Place tags at the start of a beat or paragraph where the tone shifts. Do not stack multiple tags on one line.

## Tag families

### Delivery and emotion (voice-related)

| Tag | Use for |
|-----|---------|
| `[matter-of-fact]` | Default narration. Neutral, even pace. |
| `[whispers]` | Intimate or quiet moment |
| `[sighs]` | Weight, resignation, breath before a hard truth |
| `[curious]` | Questioning or exploratory tone |
| `[thoughtful]` | Reflective. Slightly slower with more breath. |
| `[pointed]` | Single line landing for weight. Slower, clear. |
| `[warm]` | Closing or invitation. Less clipped, friendlier. |
| `[shift]` | Tonal turn. Pivot from problem to solution or story to viewer. |
| `[conversational]` | Lighter mode. Anecdotes, direct address. |
| `[sarcastic]` | Ironic distance (use sparingly; often off-brand) |
| `[excited]` | Enthusiasm (rare unless the spec or brand voice asks) |
| `[mischievously]` | Playful tilt (rare unless the brand voice asks) |

Official v3 tags also include: `[laughs]`, `[laughs harder]`, `[chuckles]`, `[exhales]`, `[crying]`, `[snorts]`, `[whispers]`.

### Pacing

| Technique | Use for |
|-----------|---------|
| `[short pause]` | Brief rest between phrases |
| `[long pause]` | Beat boundary, dramatic weight |
| `[pause]` | General rest (workspace-proven; use sparingly) |
| Ellipses `...` | Hesitation, trailing thought, weight |
| Paragraph break | Natural breath between beats |
| Em dash or comma | Short rhythm shift |

v3 does **not** support SSML `<break time="1.5s" />`. Use tags, ellipses, and paragraph breaks instead.

### Reactions (non-verbal)

| Tag | Use for |
|-----|---------|
| `[laughs]` / `[chuckles]` | Light human reaction (usually off-brand for marketing VO) |
| `[clears throat]` | Transition or reset |
| `[exhales]` | Release after tension |

Use reactions sparingly in marketing VO. Most marketing short-form pieces avoid audible laughs.

### Sound effects (usually skip for marketing VO)

Tags like `[applause]`, `[gunshot]` exist in v3. Do not use in standard short-form marketing voiceover unless the spec explicitly calls for diegetic sound in the VO track.

## Anti-patterns

| Do not | Why |
|--------|-----|
| Stage directions `(sighs)`, `(grins)` | Ignored by v3 |
| Long descriptive tags `[in a voice that feels both confident and inviting]` | Ignored or treated as noise |
| Stacked tags `[matter-of-fact] [pause]` on one line | Only the first tag wires through |
| Tag every sentence | Flattens contrast; delivery sounds robotic |
| Tag once per minute on a 45s piece | Delivery drifts to default |
| Hype tags on blunt brand copy | Violates brand voice even if v3 executes them |
| `[whispers]` on a naturally loud voice | Voice and tag mismatch; poor results |
| SSML break tags | Not supported on v3 |

## Tag density

- Target: **one tag per beat** from the locked script beat map (~40–80 words per tag).
- Short punchy lines (e.g. "They laughed." / "It did.") rely on paragraph breaks, not tags.
- Reframe and lift beats get tags. Setup beats often stay neutral with `[matter-of-fact]` only at the open.

## Punctuation as delivery

v3 responds to punctuation beyond tags:

- **Ellipses** add pauses and weight: `The company was days from dead...`
- **CAPS** increase emphasis: `It was SO close.`
- Standard punctuation provides natural rhythm.

Use punctuation lightly. Over-CAPSing reads as shouty.

## Stability and tags

| Stability | Effect on tags |
|-----------|----------------|
| Creative | Most responsive to tags; more variable output |
| Natural | Balanced; default for moderate tag density |
| Robust | Resists directional prompts; tags have less effect |

Recommend stability in the PASTE block header based on tag density (see `voice-criteria-dimensions.md`).

## Brand-safe tag palette for short-form

Prefer these for direct, grounded brand voices:

- `[matter-of-fact]` — story setup, factual beats
- `[thoughtful]` — reframe, philosophical turn
- `[shift]` — story to viewer bridge, POV change
- `[pointed]` — landing a single hard truth
- `[warm]` — final lift or CTA (not salesy)
- `[conversational]` — direct second-person address

Avoid unless spec explicitly asks:

- `[excited]`, `[laughs]`, `[mischievously]`, `[sarcastic]`, `[whispers]` (ASMR)
