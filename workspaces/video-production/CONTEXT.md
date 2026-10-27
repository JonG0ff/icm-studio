# Video Production

Make a video from a direct request or resume from accepted job artifacts.

## Task Routing

| Task | Go To | Result |
|---|---|---|
| Start or clarify a video | `stages/00-brief/CONTEXT.md` | Workspace-owned brief and plan |
| Lock script | `stages/01-script-lock/CONTEXT.md` | Script, beat map, runtime, text |
| Plan scenes | `stages/02-shot-and-scene-plan/CONTEXT.md` | Shots, timing, cuts, continuity |
| Gather assets | `stages/03-asset-gathering/CONTEXT.md` | Asset manifest and source files |
| Build edit packet | `stages/04-edit-package/CONTEXT.md` | Editor-ready decisions and delivery targets |
| Close blockers | `stages/05-open-items-closeout/CONTEXT.md` | Use/skip decisions and readiness |
| Review delivery | `stages/06-qa-delivery/CONTEXT.md` | QA notes and acceptance decision |
| Operate a split test | `publishing/split-test.md` | Publish queue, reads, and decisions |
| Configure defaults | `setup/questionnaire.md` | Optional editor/tool preferences |

## Shared Resources

| Resource | Location |
|---|---|
| Brief format | `../../_core/templates/content-brief/brief-format.md` |
| Format selection | `shared/formats/CONTEXT.md` |
| Motion graphic design | `../../skills/ai-capabilities/design/motion-graphic-design/SKILL.md` |
| Business facts and brands | `../../libraries/business-memory/CONTEXT.md` |
| Reference examples | `../../libraries/swipes/CONTEXT.md` |
| Media catalog | `../../libraries/media/assets/index.md` |
| Asset manifest | `shared/asset-manifest-format.md` |
| Edit packet | `shared/edit-package-format.md` |
| Variant matrix | `shared/variant-matrix-format.md` |
| Experiments and results | `publishing/` |
| Sourcing methods and tools | `../../skills/workflows/video-production/` |

## Rules

- New requests start at the brief. No separate intake or planning workspace is required.
- Existing jobs resume from their accepted outputs and decision history under `jobs/[slug]/`.
- Imported briefs/specs/routes under `stages/00-brief/output/[slug]/` retain their original approval status.
- Load only the chosen format recipe and relevant library entries.
- Check the media catalog before sourcing; keep job selections in the job manifest.
- Do not start QA while Stage 05 has unresolved blockers.
- Keep raw media local and source/rights records tracked.
- Preserve review modes and explicit approvals. Never infer approval from a migration.
- Footage editing, repurposing, mixed media, and motion graphics stay here, including Remotion renders. Jobs using Programmatic Animation's production recipes go to `../programmatic-animation/`. The rendering runtime alone does not determine ownership.
- Record an editorial and visual plan before assembly or rendering. Review the storyboard or equivalent beat plan and composition previews under the job's review mode.
- Unsupported output types need an explicit destination. Copy-only work goes to `../copywriting/`.
