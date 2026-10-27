# Stage 01: Find Reusable Media

Search the media library before sourcing new footage, stills, audio, overlays, or reference clips.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|---------------|---------------|-----|
| User request or upstream package | Current task, scene plan, or asset manifest | Asset needs and search terms | Define what media is needed |
| Library | `../../assets/index.md` | Full file | Find candidate reusable assets |
| Records | `../../assets/` | Matching asset records only | Check source, rights, paths, and reuse guidance |
| Shared | `../../shared/local-media-policy.md` | Full file | Keep raw media local-only |
| Reference | `references/search-checklist.md` | Full file | Verify search quality |

## Process

1. Translate the asset need into tags, subject terms, visual motifs, and rights constraints.
2. Search `assets/index.md` and matching asset records.
3. Compare candidate status, rights note, local path, and prior usage.
4. Mark candidates as reusable, reference-only, risky, or no match.
5. Save a reuse recommendation to `output/`.

## Audit

| Check | Pass Condition |
|-------|----------------|
| Search coverage | Tags, subject terms, source type, and rights constraints were checked |
| Rights fit | Recommended assets have compatible status and rights notes |
| Path clarity | Every recommended asset has a local path or source URL |
| No raw media | No raw media was copied or committed |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Reuse recommendation | `output/[slug]-reuse-recommendation.md` | Markdown |
