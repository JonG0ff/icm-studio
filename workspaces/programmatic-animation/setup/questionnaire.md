# Onboarding Questionnaire: Programmatic Animation

Read this file when the user types `setup`. Ask all questions in one pass. The user can answer everything in one message, or reply "defaults".

These configure the system once. Looks are not picked here. Each one is built from reference images in the workshop. Per-video details (slug, idea, format, look, cast) are collected by `stages/production/01-brief/` at the start of each run. Per-piece details are collected by `stages/workshop/01-concept/`.

Brand voice lives in `../../../libraries/business-memory/`. If the brand is missing, use `../../../libraries/business-memory/setup/questionnaire.md` to configure reusable context.

Never write an API key into any file. The ElevenLabs key goes in the repo's `.env`. See `shared/tool-setup.md`.

---

### Q1: Which brand do these videos belong to?
- Placeholder: `{{BRAND_SLUG}}`
- Files: `stages/production/01-brief/CONTEXT.md`, `stages/production/02-script/CONTEXT.md`
- Type: selection
- Options: the folder names in `../../../libraries/business-memory/brand-vault/brands/`
- Default: `{{BRAND_SLUG}}`

### Q2: Where will most videos be posted?
- Placeholder: `{{PRIMARY_PLATFORM}}`
- Files: `shared/platform-specs.md`, `shared/formats/skit-short.md`
- Type: selection
- Options: Instagram Reels, TikTok, YouTube Shorts
- Default: Instagram Reels
- Derived: `{{DEFAULT_FPS}}` in `shared/platform-specs.md` = `30`. Ask only if the user names another frame rate.

### Q3: How many hook versions should each skit get?
- Placeholder: `{{SKIT_VARIANT_COUNT}}`
- Files: `shared/formats/skit-short.md`
- Type: number
- Default: `1` (no split test). Use 3-5 when split testing.

### Q4: How should captions look?
- Placeholder: `{{CAPTION_STYLE}}`
- Files: `shared/formats/skit-short.md`
- Type: selection
- Options:
  - Word by word, key word in an accent color, speaker name tab
  - One line at a time, speaker name tab
  - No captions
- Default: word by word, key word in an accent color, speaker name tab

### Q5: What should the optional end card say?
- Placeholder: `{{END_CARD_TEXT}}`
- Files: `shared/formats/skit-short.md`
- Type: free text
- Example: `@marlolabs`
- Default: `none` (the skit ends on the button)

### Q6: How should word timing work?
- Placeholder: `{{TIMING_ENGINE}}`
- Files: `stages/production/04-timing/CONTEXT.md`
- Type: selection
- Options:
  - ElevenLabs alignment, Whisper only for brought audio
  - Whisper for everything
- Default: ElevenLabs alignment, Whisper only for brought audio
- Derived: `{{WHISPER_MODEL}}` in `shared/tool-setup.md` = `medium.en`. Ask only if the user wants a smaller, faster model (`small.en`).

---

## After Onboarding

1. Replace every placeholder above in the listed files.
2. Scan the workspace for remaining `{{` patterns. If any remain, ask for the missing answer.
3. Ask the user to confirm `ELEVENLABS_API_KEY` is in the repo's `.env`. Don't read or print `.env`.
4. Run the tool checks in `shared/tool-setup.md`.
5. Tell the user what was set, then point them to the first job: bring 3-10 reference images of a style, save them in `../../../libraries/swipes/` with the tag `animation-style`, then run a look through `stages/workshop/01-concept/CONTEXT.md`.
