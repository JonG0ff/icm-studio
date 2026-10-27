# Library Spec Format

What every library entry holds. Workshop stages 02-05 build toward this. Production reads it.

## Every Entry

```
# [slug]
type: character | set | prop | voice | look
look: [approved look slug]
status: approved | archived
approved: YYYY-MM-DD
code: remotion/src/compositions/programmatic-animation/_library/[look]/[slug]/
art: remotion/public/assets/programmatic-animation/_library/[look]/[slug]/
workshop run: [slug]
```

Then the type's sections below. A voice has no `code` or `art`.

## character

- **Persona:** link to `library/personas/[persona-slug].md`. Writing and behavior follow `persona-profile-format.md`.
- **Personality:** optional one-line navigation summary. The persona profile owns the full rules.
- **Voice:** the voice entry slug, or `none` for a silent character.
- **Views:** front, three-quarter. No back or side.
- **Mouths:** list of shape names (6-8), mapped to sounds.
- **Expressions:** list of names, for example `neutral, angry, shocked, smug, dead-inside`.
- **Poses:** list of names, for example `idle, point, shrug, mic-hold`.
- **Can't do:** known limits, so blocking doesn't ask for them.

## set

- **Layers:** back to front.
- **Spots:** named places a character can stand, for example `desk-center`.
- **Graphics:** lower thirds, tickers, banners that come with it.
- **Camera:** moves it supports (pan range, zoom limits).

## prop

- **Grip:** how a character holds it, and which poses support it.
- **Actions:** what it can do, for example `flip`, `break`, `fly-off`.

## voice

- **ElevenLabs voice ID:** the ID.
- **Model and settings:** model, stability, similarity, speed.
- **Character fit:** who it's for and the type it parodies. Never a real person.
- **Test lines:** file paths to the approved test lines.
- **Tag notes:** audio tags that work well, and ones that break it.

## look

- **References:** swipe entry slugs tagged `style-[slug]`.
- **Technique:** the technique families from `looks.md` it uses.
- **Kit:** path to the look's shared constants (palette, line weight, fps-on-twos, filters).
- **Feasibility:** predicted grade, Match score, and the traits that were Workaround or Out of reach.
- **Scores:** the seven look test scores from `looks.md`.
- **Rules:** what this look always does and never does.
- **Can't do:** traits and actions this look can't render, so blocking doesn't ask for them.

## Checklist Per Type

| Type | Must have before approve |
|---|---|
| character | Persona profile reviewed with source examples and boundaries, voice pointer or explicit silence, both views, all mouths, 4+ expressions, 4+ poses, motion test passed (or, if the owner skipped it, the first production render passed) |
| set | All layers, 2+ spots, camera test passed |
| prop | Art, grip points, hold test passed |
| voice | Voice ID, settings, 5+ approved test lines |
| look | 3+ references, feasibility read, kit file, look test render, side-by-side sheet, all seven scores, calibration row |
