---
name: elevenlabs-voiceover
description: Author ElevenLabs v3 voiceover from a locked script. Derives voice filter criteria, writes tagged PASTE-block scripts, and validates a human-chosen voice against the spec. No API calls.
license: MIT
metadata:
  tags: elevenlabs, voiceover, tts, video-production, audio-tags
---

# ElevenLabs Voiceover Authoring

Turn a locked script into ElevenLabs-ready voiceover guidance: filter criteria for Voice Library search, a tagged v3 script to paste, and a validation pass when the human picks a voice.

This skill is **authoring only**. It does not call the ElevenLabs API, search voices programmatically, or generate audio files. For API calls and audio files, use `../elevenlabs-voice-generation/SKILL.md`.

## When to Use

- Production spec asset manifest marks voiceover as ElevenLabs TTS or `needs-generation`
- Locked voiceover script exists in the destination production workspace's script stage output
- You need voice filter criteria before browsing ElevenLabs Voice Library
- You need a v3 audio-tag script to paste into ElevenLabs Text to Speech
- The human picked a voice and wants a pass/fail check against the spec

## Prerequisites

- Approved `[slug]-locked-script.md` from `workspaces/video-production/stages/01-script-lock/output/`
- Upstream brief and marketing spec for tone, POV, and audio constraints
- Brand voice rules from `libraries/business-memory/brand-vault/brands/[brand]/voice-rules.md` when available

## Quick Start

1. Load inputs (see Step 1 below).
2. Derive voice criteria per [`references/voice-criteria-dimensions.md`](references/voice-criteria-dimensions.md).
3. Annotate the locked script with v3 tags per [`references/spec-to-tags.md`](references/spec-to-tags.md).
4. Save output to `workspaces/video-production/stages/03-asset-gathering/output/[slug]-elevenlabs-vo.md` using [`templates/tagged-vo-output.md`](templates/tagged-vo-output.md).
5. Human picks a voice in ElevenLabs UI and shares the name back.
6. Run voice validation (Step 5 below).

## Workflow

### Step 1 — Load inputs

| Source | Location | What to read |
|--------|----------|--------------|
| Locked script | `workspaces/video-production/stages/01-script-lock/output/[slug]-locked-script.md` | Locked Voiceover Script, Beat Map, delivery notes, runtime target |
| Job brief/spec | Destination workspace's approved brief artifact | Audience, Angle, Constraints.Audio |
| Brand voice | `libraries/business-memory/brand-vault/brands/[brand]/voice-rules.md` | Hard constraints, pacing, what the voice is NOT |

Do not rewrite locked copy unless the spec marks a line `[needs approval]`.

### Step 2 — Derive voice criteria

Output a **Voice Criteria** table. Use filter dimensions from [`references/voice-criteria-dimensions.md`](references/voice-criteria-dimensions.md).

Rules:

- Give **criteria and search phrases**, not voice IDs. ElevenLabs voices change over time.
- Include an explicit **Avoid** list from brand voice rules.
- Recommend **v3 stability** setting (Creative, Natural, or Robust) based on tag density.
- Add 3–5 plain-language Voice Library search phrases (e.g. "calm male narrator american documentary").

### Step 3 — Write tagged v3 script

1. Copy the Locked Voiceover Script verbatim.
2. Add one opening audio tag per beat from the Beat Map (not per sentence).
3. Follow tag rules in [`references/v3-audio-tags.md`](references/v3-audio-tags.md) and mapping rules in [`references/spec-to-tags.md`](references/spec-to-tags.md).
4. Wrap in a PASTE block (see PASTE block format below).
5. Always specify model `eleven_v3` and recommended stability in the blockquote header.

**PASTE block format** (for pasting into the ElevenLabs app):

```markdown
## ► PASTE THIS into ElevenLabs

> Model: eleven_v3. Stability: Natural. Copy everything between the two rules below.

---

[matter-of-fact] First beat narration here.

[shift] Next beat picks up on a tone change.

---
```

For per-line generation from a script, use `../elevenlabs-voice-generation/SKILL.md`.

### Step 4 — Write output artifact

Save to the active asset sourcing stage:

`workspaces/video-production/stages/03-asset-gathering/output/[slug]-elevenlabs-vo.md`

If the project is already routed into short-form production and Stage 03 asset gathering is active, use:

`workspaces/video-production/stages/03-asset-gathering/output/[slug]-elevenlabs-vo.md`

Use [`templates/tagged-vo-output.md`](templates/tagged-vo-output.md). Include:

- Voice Criteria table + search phrases + stability recommendation
- Tagged Script (PASTE block)
- Beat-to-tag audit table
- Empty Voice Validation section for the human to fill in

### Step 5 — Voice validation

When the human shares their chosen voice (name + optional preview notes), run a criteria audit:

| Check | Pass if |
|-------|---------|
| Gender / age / accent | Matches criteria or acceptable override with reason |
| Pace / energy / register | Preview aligns with spec delivery notes |
| Brand avoid list | Voice does not sound hypey, salesy, or off-brand |
| Tag compatibility | Voice character fits planned tag density |
| POV | Can carry second-person lift without sounding preachy |

Output one of:

- **PASS** — voice fits criteria; proceed to generate and export WAV
- **PASS WITH NOTES** — usable with minor caveats; list them
- **FAIL** — mismatches; list specific gaps and revised filter suggestions

## Rules

- Never commit ElevenLabs API keys or generated audio to git.
- Do not rewrite marketing copy during tagging unless explicitly asked.
- Voice choice matters more than tags. Tags cannot fix a mismatched voice.
- Prefer premade or IVC voices for v3 expressive short-form. PVC clones are less reliable on v3.
- v3 does not support SSML `<break>` tags. Use `[short pause]`, ellipses, and paragraph breaks instead.
- One tag per beat. Never stack tags on one line.
- Record chosen voice name and validation result in the output artifact.

## References

- [`references/voice-criteria-dimensions.md`](references/voice-criteria-dimensions.md) — filter axes and search phrase patterns
- [`references/v3-audio-tags.md`](references/v3-audio-tags.md) — tag vocabulary and anti-patterns
- [`references/spec-to-tags.md`](references/spec-to-tags.md) — beat-map to tag mapping
- [`templates/tagged-vo-output.md`](templates/tagged-vo-output.md) — output artifact template

## Related Skills

- `skills/workflows/video-production/sound-effects-mix/SKILL.md` — SFX and VO ducking after VO is generated
- `../elevenlabs-voice-generation/SKILL.md`: per-line ElevenLabs API generation with timestamps, used by `workspaces/programmatic-animation/`.
