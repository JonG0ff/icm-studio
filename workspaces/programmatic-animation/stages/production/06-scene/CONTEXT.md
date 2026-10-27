# Production 06: Scene

Build the Remotion composition from the cues and word times. This stage waits only for the pieces it needs and imports from `remotion/src/compositions/programmatic-animation/_workshop/` until promotion.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../05-blocking/output/[slug]/cues.md` | Full | What happens when |
| Previous stage | `../05-blocking/output/[slug]/sfx-map.md` | Full | Sounds and levels |
| Previous stage | `../04-timing/output/[slug]/words-v[N].json` | Full, every variant | Exact times, mouth driving |
| Previous stage | `../01-brief/output/[slug]/brief.md` | "look", "cast", "set", "props" | Which pieces to import |
| Reference | `references/scene-conventions.md` | Full | Folder shape, timing, gap-fill |
| Shared | `../../../shared/contact-sheets.md` | Full | Self-review |
| Shared | `../../../shared/looks.md` | "Finishing Filters" | Look polish |
| Shared | `../../../shared/platform-specs.md` | The format's row, "Safe Areas" | Size and safe zones |
| Library | `../../../library/entries/[type]/[slug].md` | Code path and prop tables, for the brief's pieces only | How to drive each piece |
| Skill | the `remotion-best-practices` skill (install: `remotion/README.md`) | Index, then rules as needed | Remotion APIs |

## Process

1. Wait only for the pieces this video needs. Import `approved` pieces from `remotion/src/compositions/programmatic-animation/_library/` and `workshop` pieces from `remotion/src/compositions/programmatic-animation/_workshop/` until promotion. Build `remotion/src/compositions/programmatic-animation/[slug]/timing.ts` from the word times and cues.
2. Write one section component per top-level cue section. Beats use section-local time.
3. Drive mouths from word times through the `_kit` mouth driver.
4. Build one master composition per variant. Register each as `programmatic-animation-[slug]-v[N]` in `registry.ts`.
5. Run `npm run typecheck` and `npm run compositions` in `remotion/`.
6. Make a contact sheet for each variant and review it. Fix and re-sheet.
7. Save build notes to `output/[slug]/build.md`.

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|------------|---------------|---------------|------|
| 7 | Studio preview command, contact sheets, known issues | Preview works, or send back to blocking | Taste |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Cues covered | Every cue beat appears in the composition |
| Library untouched | No file under `remotion/src/compositions/programmatic-animation/_library/` or `remotion/src/compositions/programmatic-animation/_kit/` was edited for this video |
| Kit colors | No hardcoded colors. Look constants imported. |
| No black frames | Gap-fill sequencing and a background underlay in place |
| Contact sheet | Reviewed, no open problems |
| Typecheck | Passes |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Composition | `remotion/src/compositions/programmatic-animation/[slug]/` | `timing.ts`, section components, one master per variant |
| Registry rows | `remotion/src/compositions/registry.ts` | One per variant |
| Build notes | `output/[slug]/build.md` | Composition IDs, files, contact sheet paths, known issues |
