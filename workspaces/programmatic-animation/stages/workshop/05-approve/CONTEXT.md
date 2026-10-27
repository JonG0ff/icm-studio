# Workshop 05: Approve

Sign the piece off into the library, send it back a stage, or archive it.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stages | `../01-concept/output/[slug]/` through `../04-motion-test/output/[slug]/` | Full | Everything about this piece |
| Shared | `../../../shared/library-spec-format.md` | "Every Entry", the type's section, "Checklist Per Type" | The entry shape |
| Shared | `../../../shared/persona-profile-format.md` | Full, characters only | Publish the persona with its approval sources |
| Library | `../../../library/index.md` | Full | Where the row goes |

## Motion Test Skipped and Promotion After Ship

Promotion happens after ship. When a piece was built for a production run or skipped workshop 04, approve it only after the first production run that uses the piece ships. That shipped render is the test evidence: name it in `decision.md`. Until then the piece stays `workshop` in `../../../library/index.md` and in `remotion/src/compositions/programmatic-animation/_workshop/`, and production loads it from there.

This stage is a `Canon` stop (see Pattern 19 in `../../../../../_core/CONVENTIONS.md`). It flips the piece's status in `../../../library/index.md` from `workshop` to `approved` or `archived`. It is never written by the agent alone in `auto` mode.

## Process

1. Check the piece against the type's checklist.
2. Draft the library entry from the run's files. Characters: include the persona draft and its reference examples in the review. Separate established material from proposed traits.
3. Present the entry and the checklist result.
4. On sign-off:
   - Move code from `remotion/src/compositions/programmatic-animation/_workshop/[slug]/` to `remotion/src/compositions/programmatic-animation/_library/[look]/[slug]/` with `git mv`. Drop its `test` folder.
   - Move art to `remotion/public/assets/programmatic-animation/_library/[look]/[slug]/`.
   - Save the entry to `library/entries/[type]/[slug].md` with status `approved`.
   - Characters: link an existing approved persona when reusing it in another look. For a new or revised persona, publish the signed-off profile to `../../../library/personas/[persona-slug].md`, with revision and approval source, and link it from the entry. Move a new draft to the canonical path and update its relative links and the workshop concept/design pointers. Do not overwrite a shared profile unless its change was part of the sign-off. Keep one current profile, not two competing copies.
   - Flip the piece's row in `../../../library/index.md` from `workshop` to `approved` and set the entry path.
5. On send-back: note the stage and the reason. Keep status `workshop` in `../../../library/index.md`.
6. On archive: flip the index row in `../../../library/index.md` from `workshop` to `archived`. Leave code in `remotion/src/compositions/programmatic-animation/_workshop/`.
7. Save the decision to `output/[slug]/decision.md`.

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|------------|---------------|---------------|------|
| 3 | Draft entry and checklist result | Approve, send back (which stage), or archive | Canon |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Checklist | Every item for the type is met |
| Paths | Code and art paths in the entry resolve |
| Index | The row matches the entry's slug, type, look and status |
| Persona | Characters: profile link resolves, approved content matches the sign-off, revision and sources are recorded, and workshop pointers use the canonical path |
| Typecheck | Passes after the move |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Library entry | `../../../library/entries/[type]/[slug].md` | Per `library-spec-format.md` |
| Persona profile | `../../../library/personas/[persona-slug].md` | Characters only, per `persona-profile-format.md` |
| Index row | `../../../library/index.md` | One row |
| Decision | `output/[slug]/decision.md` | Approved, sent back, or archived, with the reason |
