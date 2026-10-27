# Stage 03: Validation

Check that production workspaces and shared libraries point to canonical Business Memory.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|---------------|---------------|-----|
| Business Memory | `../../CLAUDE.md`, `../../CONTEXT.md` | Full files | Check expected routes |
| Brand vault | `../../brand-vault/CONTEXT.md` | Full file | Check brand routing |
| Dependent workspaces | `../../../swipes/`, `../../../../workspaces/` | Routing docs only | Find stale local brand pointers |

## Process

1. Search dependent routing docs for local `brand-vault/` references.
2. Confirm brand work points to repository path `libraries/business-memory/brand-vault/brands/[brand-slug]/` with the correct traversal from the consumer.
3. Confirm SOP references point to repository path `libraries/business-memory/sops/CONTEXT.md` where needed.
4. Check links and relative paths.
5. Report any stale duplicates that should become pointers.

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Validation notes | `output/[date]-validation.md` | Markdown |
