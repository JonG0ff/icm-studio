# Stage 02: Register Asset

Add or update a reusable media record after a useful asset has been sourced or approved.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|---------------|---------------|-----|
| Candidate asset | User-provided path, source package, asset manifest, or stage output | Source URL, local path, status, rights note | Identify what to register |
| Library | `../../assets/index.md` | Full file | Avoid duplicate asset records |
| Shared | `../../shared/asset-record-format.md` | Full file | Use the required record schema |
| Shared | `../../shared/local-media-policy.md` | Full file | Keep raw files local-only |
| Reference | `references/registration-checklist.md` | Full file | Validate source and rights fields |
| Skill | `../../../../skills/workflows/video-production/media-sourcing/SKILL.md` | Source Methods and Output Rule | Apply source and rights status rules |

## Process

1. Confirm the asset is worth reusing across projects.
2. Check `assets/index.md` for an existing record with the same source URL, title, local path, or hash when available.
3. Create or update one record in `assets/[asset-id].md`.
4. Add or update the row in `assets/index.md`.
5. Keep raw media in `local-media/` or another ignored local-only path.
6. Save a registration note to `output/` when useful.

## Audit

| Check | Pass Condition |
|-------|----------------|
| Required fields | Asset record includes every field from the shared format |
| Source clarity | Source URL, local path, or source note is present |
| Rights honesty | Status matches the rights note |
| Duplicate check | Existing index and records were checked first |
| Git safety | Raw media is ignored; metadata is trackable |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Asset record | `../../assets/[asset-id].md` | Markdown |
| Index update | `../../assets/index.md` | Markdown table row |
| Registration note | `output/[asset-id]-registration.md` | Markdown when needed |
