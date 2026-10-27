# Knowledge Layer Entry Format

Canonical structure for `knowledge-layer/entries/[slug]-reference.md`.

```markdown
# [Title]

- source: [url or path]
- source-type: image | webpage | pdf | audio | video | social-video
- type: ad | landing-page | email | brand-guide | social-post | ...
- saved: YYYY-MM-DD
- tags: [comma-separated]
- asset-manifest: knowledge-layer/assets/[slug]/manifest.json
- primary-context: knowledge-layer/assets/[slug]/[context artifact path]

## Why saved

(human note from intake)

## Visual

(colors, typography, layout notes)

## Animation style

(only for `animation-style` references: the trait list from extraction)

## Copy

(hook, body patterns, offer, CTA)

## Video Timeline

(timestamped scene, frame, motion, and on-screen text notes; use "none observed" for non-video)

## Audio

(transcript hook, voice/tone, music/sound, spoken CTA)

## Combined Patterns

(approved or edited notes tying visuals and audio together)

## Patterns worth reusing

(bullet list -- human-approved at curation)
```

This is the canonical home for this reference. Stage outputs are not authoritative after curation.
