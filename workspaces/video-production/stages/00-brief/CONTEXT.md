# Stage 00: Brief

Turn a direct video request into a brief and plan inside Video Production.

## Inputs

| Source | Location | Scope | Why |
|---|---|---|---|
| User | Current request or supplied brief | Full | Outcome and constraints |
| Template | `../../../../_core/templates/content-brief/brief-format.md` | Full | Shared capture and planning fields |
| Format | `../../shared/formats/CONTEXT.md` | One selected recipe | Format-specific production needs |
| Libraries | `../../../../libraries/` | Relevant indexes and selected entries only | Approved facts, references, existing media |
| Existing job | `output/[slug]/` and `../../jobs/[slug]/` | Accepted imports and decisions, when present | Preserve ongoing work |

## Process

1. Choose one slug and identify the deliverable and production recipe. Keep footage editing, repurposing, mixed media, and motion graphics here, including Remotion renders. Route jobs using Programmatic Animation's production recipes to `../../../programmatic-animation/`; route copy-only to `../../../copywriting/`.
2. Capture objective, audience, angle, platform, duration, aspect ratio, delivery files, and constraints from the request.
3. Select short-form or long-form guidance. Load only relevant brand/project facts and reference entries. Check the media catalog.
4. Capture content direction, visual/audio direction, references, success criteria, missing assets, and the stage plan using the brief format.
5. Record review mode and optional budget cap. Keep unknowns and pending decisions explicit. No setup questionnaire is required.
6. For an existing job, use accepted spec/entry/route files already in `output/[slug]/`. Preserve their approvals, script locks, and decisions. Add a brief only if missing context requires one; do not repeat completed stages.
7. For a new job, save `output/[slug]/brief.md`. Present the plan at the applicable checkpoint, then continue to Stage 01 under the job's review mode.

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|---|---|---|---|
| 7 | Brief, context gaps, format, and production plan | Approve direction or revise | Taste, plan |

## Audit

| Check | Pass Condition |
|---|---|
| Owner | Video Production owns the deliverable and plan |
| Context | Facts and references have selected pointers; no invented approvals |
| Format | Duration, aspect ratio, chapters if needed, and delivery are specified |
| Existing job | Accepted decisions remain authoritative and pending approvals remain pending |
| Readiness | Missing inputs have owners and concrete next actions |

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Brief and plan, new job | `output/[slug]/brief.md` | Shared content brief format |
| Accepted imports, existing job | `output/[slug]/[original-filename].md` | Preserved original entry/spec/route |
