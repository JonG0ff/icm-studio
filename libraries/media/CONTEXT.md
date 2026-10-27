# Media Library

Catalog reusable media so future projects can find existing clips, stills, audio, overlays, and references before sourcing new ones.

## Task Routing

| Task Type | Go To | Description |
|-----------|-------|-------------|
| Find reusable media | `stages/01-find-reusable/CONTEXT.md` | Search existing records by tags, rights, source, and usage fit |
| Read existing records | `assets/index.md` and matching records | Load only the assets needed by the job; no maintenance workflow required |
| Find media from a job brief | `stages/01-find-reusable/CONTEXT.md` | Search for clips, stills, audio, overlays, or references named by production |
| Register asset | `stages/02-register-asset/CONTEXT.md` | Add or update an approved reusable asset record |
| Review library | `stages/03-review-library/CONTEXT.md` | Audit records, rights notes, duplicate sources, and local paths |

## Shared Resources

| Resource | Location | Contains |
|----------|----------|----------|
| Asset index | `assets/index.md` | Searchable catalog of reusable assets |
| Asset record format | `shared/asset-record-format.md` | Required fields for each reusable asset |
| Visual hook record format | `shared/visual-hook-record-format.md` | Extra fields for split-test opening clips, plus pairing history |
| Local media policy | `shared/local-media-policy.md` | Raw media storage and Git safety rules |
| Media sourcing skill | `../../skills/workflows/video-production/media-sourcing/SKILL.md` | Source method and rights guidance |
| Magnific generation skill | `../../skills/workflows/video-production/magnific-generation/SKILL.md` | Credit-safe generation for hook clips and generated footage |

## Rules

- Git stores metadata, not raw media.
- Put raw media under `local-media/` or another local-only ignored path.
- Do not mark an asset reusable unless it has source and rights notes.
- Keep reference patterns in `../swipes/`. Keep production media reuse records here.
- Update `used_in` when an asset is reused in a project.
- Visual hooks are an asset class here. Update `used_in_cells` and `paired_text_hooks` every time a hook ships, or the rotation rule in the split-test SOP cannot be enforced.
- The production job owns asset selection, timing, and its manifest. Return the relevant record pointer there after library work.
