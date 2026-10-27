# Stage 03: Curate

Human approves extraction and merges it into the persistent knowledge layer.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../02-extract/output/` | `[slug]-extraction.md` | Extracted fields to curate |
| Previous stage | `../01-save/output/` | `[slug]-intake.md` | Why saved, tags, source |
| Previous stage | `../01-save/output/assets/[slug]/manifest.json` | Staged context artifacts | Assets to promote after approval |
| Knowledge layer | `../../knowledge-layer/index.md` | Full file | Avoid duplicate slugs; update catalog |
| Reference | `references/entry-format.md` | Full file | Canonical entry structure |
| Reference | `references/curation-rules.md` | Full file | Merge and pattern update rules |
| Shared | `../../shared/stage-handoff-format.md` | Full file | Required terminal checkpoint and handoff format |

## Process

1. Read intake and extraction for the current slug.
2. Confirm the manifest has `workflow_state: save-approved`, `ready_for_stage_02: true`, and that the Stage 02 extraction file exists. Stop if the reference is still only staged.
3. Draft knowledge layer entry from both files. Merge "why saved" from intake with extraction fields, including media sections when present.
4. **[Checkpoint]** Present draft entry to human. They approve, edit, or reject.
5. If rejected: do not write to knowledge layer. Stop.
6. If approved: run `reference-intake promote --human-approved` on the staged manifest. This copies only files marked `persist: true` into `knowledge-layer/assets/[slug]/`. The explicit flag is required; never promote from Stage 01 alone.
7. Write `knowledge-layer/entries/[slug]-reference.md` with the promoted manifest and primary-context paths.
8. Add row to `knowledge-layer/index.md`.
9. Update `knowledge-layer/patterns/visual-patterns.md`, `knowledge-layer/patterns/copy-patterns.md`, and/or `knowledge-layer/patterns/media-patterns.md` if human confirms patterns worth aggregating.
10. Write curation log to stage output.
11. Run audit checks.
12. Write `[slug]-handoff.md` using `../../shared/stage-handoff-format.md`. If approval is pending, state `needs-approval`, list the draft entry and proposed pattern updates, and end the turn immediately. If approved, state `complete` and list the promoted assets, entry, index update, and curation log.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 3 | Full draft entry + proposed pattern updates | Approve, edit, or reject |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Human gate | Entry written only after explicit approval |
| Asset gate | Rejected references create no files under `knowledge-layer/assets/` |
| Durable context | Entry paths point to the promoted manifest and primary context |
| Canonical entry | One file at `knowledge-layer/entries/[slug]-reference.md` |
| Index updated | New row in `index.md` matches entry slug |
| No duplication | Extracted content lives in entry; not copied into patterns verbatim |
| Reject path | Rejection produces no knowledge layer write |
| Terminal handoff | Handoff artifact exists and the user-facing checkpoint names the decision, artifacts, blockers, and exact reply |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Curation log | `output/[slug]-curation.md` | Approved/rejected, date, pattern updates made |
| Knowledge entry | `../../knowledge-layer/entries/[slug]-reference.md` | On approval only |
| Knowledge assets | `../../knowledge-layer/assets/[slug]/` | Promoted context artifacts on approval only |
| Index update | `../../knowledge-layer/index.md` | On approval only |

The knowledge layer entry is the persistent product. Stage output is a log only.
