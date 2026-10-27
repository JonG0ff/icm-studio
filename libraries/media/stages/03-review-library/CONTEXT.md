# Stage 03: Review Library

Audit media records for stale paths, duplicate entries, rights gaps, and Git safety.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|---------------|---------------|-----|
| Library | `../../assets/index.md` | Full file | Review catalog coverage |
| Records | `../../assets/` | Asset records in scope | Check individual metadata |
| Shared | `../../shared/asset-record-format.md` | Full file | Validate required fields |
| Shared | `../../shared/local-media-policy.md` | Full file | Verify local-only raw media policy |
| Reference | `references/library-audit-checklist.md` | Full file | Audit criteria |

## Process

1. Review the index and asset records in scope.
2. Find missing fields, stale local paths, duplicate source URLs, and unclear statuses.
3. Check for raw media files that Git might track.
4. Update records or list required fixes.
5. Save the audit report to `output/`.

## Audit

| Check | Pass Condition |
|-------|----------------|
| Field completeness | Records follow the shared format |
| Rights clarity | Every record has a clear status and rights note |
| Duplicate risk | Duplicate source URLs or titles are flagged |
| Path clarity | Missing or stale local paths are marked |
| Git safety | Raw media files are ignored |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Library audit | `output/[date]-library-audit.md` | Markdown |
