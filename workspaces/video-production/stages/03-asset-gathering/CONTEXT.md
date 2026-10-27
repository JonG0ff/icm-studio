# Stage 03: Asset Sourcing

Source every asset the approved scene plan needs. Keep source, rights, local files, fallbacks, and costs visible.

## Inputs

| Source | Location | Scope | Why |
|---|---|---|---|
| Scenes and script | `../02-shot-and-scene-plan/output/` and `../01-script-lock/output/` | This job | Approved asset needs and VO |
| Brief | `../00-brief/output/[slug]/` | References, visual direction, constraints | Style and use limits |
| Swipes | `../../../../libraries/swipes/knowledge-layer/` | Listed entries and pattern sections only | Visual language to study |
| Media | `../../../../libraries/media/assets/index.md` | Relevant rows and selected records | Existing sources, rights, paths |
| Format | `../../shared/formats/CONTEXT.md` | Selected recipe | Coverage and candidate targets |
| Shared | `../../shared/asset-manifest-format.md` | Full | Job selection records |
| References | `references/sourcing-rules.md` and `references/source-rights-checklist.md` | Full | Source priority and safety |
| Skills | `../../../../skills/workflows/video-production/` | Smallest matching sourcing, still-bank, audio, VO, SFX, or generation skill | Procedures and executable tools |
| Split test only | `../02-shot-and-scene-plan/output/` | Variant matrix | Spine and per-package needs |

## Process

1. Read the accepted brief/spec references and their selected swipe entries. Save a visual-direction summary; if no swipes apply, name the approved direction source.
2. Read the locked script and scene plan. Do not reopen their accepted decisions.
3. Make manifest rows for visuals, VO, music, SFX, graphics, templates, and source proofs.
4. Check the media catalog for every need. Reuse only when visual fit, rights, status, and local path fit this job.
5. Source gaps with the appropriate skill/tools and `references/sourcing-rules.md`. Download authorized free-source candidates before review. Organize by chapter/scene.
6. For SFX, complete the skill's selected-download workflow and record actual files and metadata, not search links alone.
7. Record type, status, source URL/path, attribution, rights, fallback, and expected cost. Queue paid licenses and generation; do not spend before approval.
8. Audit and save the manifest and conditional outputs below.
9. Present actual candidate files, source/rights notes, gaps, costs, and promotion candidates for review.
10. Execute only approved paid/generation rows with their matching skill and spend rules. Update usable paths and rights status honestly.
11. List reusable assets for promotion through the media library's approval workflow. Downloading or selecting an asset never approves promotion.

## Split Test Runs

Skip for a single video.

- Check both hook banks before generating. Source body, CTA, and VO once; source hooks per package.
- Show total cost as shared spine plus per-package hooks.
- Follow the Magnific skill's generation channel and model rules.
- Approved hook records require source prompt/model plus pairing/use history. Update library records only through their approval workflow.

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|---|---|---|---|
| 9 | Downloaded candidates, manifest, rights, gaps, and promotion candidates | Select assets or revise | Taste |
| 9 | Paid/generation rows and expected costs, before execution | Approve named spend or use fallbacks | Spend |

## Audit

| Check | Pass Condition |
|---|---|
| Direction | Summary exists and selections fit the accepted direction |
| Coverage | Every scene need has a row, fallback, and format-appropriate candidates |
| Reuse | Catalog checked before sourcing; reference-only media is not cleared for release |
| Sources | Applicable source priority followed using skill tools; free-source files downloaded |
| Audio | Required SFX have candidate files and complete source metadata |
| Honesty | Ready assets have usable paths and rights notes; blockers stay visible |
| Spend | Paid/generation costs visible and required approval retained |
| Safety | Raw media ignored, no secrets written, promotion approval separate |
| Cell | Shared spine sourced once and hook pairing history checked |

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Visual direction summary | `output/[slug]-swipe-derived-visual-direction.md` | Source-derived summary |
| Asset manifest | `output/[slug]-asset-manifest.md` | Shared manifest format |
| Conditional supporting packets | `output/[slug]-generation-queue.md`, `[slug]-media-library-promotions.md`, `[slug]-elevenlabs-vo.md`, `[slug]-sfx-source-map.md` | Create each only when needed |
