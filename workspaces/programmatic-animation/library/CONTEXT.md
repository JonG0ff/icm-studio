# Library

Every piece, with its status. Production reads from here. Workshop stage 01 adds `workshop` rows when a piece starts; only workshop stage 05 sets `approved` or `archived` after owner sign-off.

## Files

| File | Holds |
|------|-------|
| `index.md` | One row per piece: slug, type, look, status (`approved`, `workshop`, `archived`), date |
| `entries/[type]/[slug].md` | One spec per approved piece, in the shape of `../shared/library-spec-format.md` |
| `personas/[persona-slug].md` | Canonical writing and behavior profile, linked from the character entry |

## How to Load

1. Read `index.md`.
2. Pick the rows the run needs: same look, status `approved` or `workshop`.
3. Load only those pieces: from `entries/[type]/[slug].md` when `approved`, or from the workshop stage outputs and `remotion/src/compositions/programmatic-animation/_workshop/[slug]/` while `workshop`. Never load the whole folder.
4. For scriptwriting or acting direction, follow each selected character's persona pointer. Use `../shared/persona-profile-format.md` for the profile and review contract.

## Rules

- Three statuses: `approved`, `workshop`, `archived`.
- Workshop 01 adds a `workshop` row to `index.md` when a piece starts.
- Only workshop 05 sets `approved` or `archived`, after owner sign-off (Canon stop; see Pattern 19 in `../../../_core/CONVENTIONS.md`).
- Production may load `approved` and `workshop` pieces. `archived` pieces stay listed but production never uses them.
- A piece belongs to one look.
- A persona can be shared across looks. Find it through the character entry; it has no separate piece row.
- Draft profiles stay in the workshop. Only workshop 05 publishes new profiles or changes to canon. Consolidated approved profiles retain their original source pointers.
- Code and art for each piece live in `remotion/`, at the paths in the entry (or `remotion/src/compositions/programmatic-animation/_workshop/[slug]/` while `workshop`).
