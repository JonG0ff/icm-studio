# Production 07: Render

Render every variant to mp4, check it end to end, and write the manifest.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../06-scene/output/[slug]/build.md` | Full | Composition IDs and known issues |
| Previous stage | `../04-timing/output/[slug]/timing-report-v[N].md` | Length, every variant | Runtime target |
| Previous stage | `../02-script/output/[slug]/script.md` | Hook sections | What differs per variant |
| Reference | `references/render-checklist.md` | Full | Pre-flight, render, post-render, loop-back |
| Shared | `../../../shared/formats/[format].md` | "Settings", "Render" | Variants and captions |
| Shared | `../../../shared/platform-specs.md` | The format's row | Size and fps |
| SOP | `../../../../../libraries/business-memory/sops/reel-split-test.md` | Full, only if variants > 1 | Split-test handoff |

## Process

1. Run pre-flight from the checklist.
2. Render each variant to `remotion/out/programmatic-animation/[slug]/v[N].mp4`. Cap: three full renders per run, then stop and ask (see Pattern 19 in `../../../../../_core/CONVENTIONS.md`).
3. Make a phone copy of each.
4. Watch each variant end to end. Check runtime against the timing report and verify that every voiced line, beat, and set in the approved script plays in the render.
5. Write the manifest: one row per variant, what differs, file paths.
6. Suggest a title, cover frame and caption per the format. Then reveal `v1.mp4` and the manifest in Finder (Pattern 21).
7. On owner ship approval, record the `## Approval` block in `output/[slug]/manifest.md`:
   ```
   ## Approval

   Approved to ship: YYYY-MM-DD, v1 as rendered. sha256 v1.mp4: 3f9a0c12e4b7
   ```
8. After ship, offer W05 promotion (`../../workshop/05-approve/CONTEXT.md`) for `workshop` pieces (Canon; never by the agent alone in `auto`).

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|------------|---------------|---------------|------|
| 6 | Renders and manifest revealed in Finder; title, cover, caption | Ship, re-render, or loop back | Ship |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Pre-flight build | `npm run typecheck` and `npm run compositions` pass in `remotion/`; every variant's composition is registered |
| Pre-flight preview | Studio preview plays end to end with no console errors, no black frames between sections, and fonts loaded |
| Pre-flight audio and frame | Each variant's audio mounts once and plays the whole way; size, fps, and safe areas match the platform row |
| Beat audit | Every voiced line, beat, and set in the approved script plays in the render |
| Exit code | 0 for every variant |
| Runtime | Within 5% of the timing report |
| Sync | Mouths and cues on the words at the end of the video |
| Manifest | Lists every variant and what differs |

A failed check uses the loop-back table in `render-checklist.md`.

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Videos | `remotion/out/programmatic-animation/[slug]/` | `v[N].mp4` and `v[N]-phone.mp4`, local only |
| Manifest | `output/[slug]/manifest.md` | Variant, hook lines, file, runtime, title, cover, caption |
