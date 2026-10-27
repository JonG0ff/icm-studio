# Stage 01: Brand Setup

Create or update one brand under `brand-vault/brands/`.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|---------------|---------------|-----|
| Questionnaire | `../../setup/questionnaire.md` | Full file | Collect reusable brand values |
| Brand vault | `../../brand-vault/CONTEXT.md` | Brand Routing | Avoid duplicate brand folders |
| Existing brand | `../../brand-vault/brands/[brand-slug]/` | Full files if present | Preserve approved values |

## Process

1. Ask the setup questions in one pass.
2. Derive the brand slug from the brand name.
3. Create or update `brand-vault/brands/[brand-slug]/identity.md`.
4. Create or update `brand-vault/brands/[brand-slug]/voice-rules.md`.
5. Update `brand-vault/CONTEXT.md` Brand Routing.
6. Scan the updated brand files for remaining placeholders.

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Brand identity | `../../brand-vault/brands/[brand-slug]/identity.md` | Markdown |
| Voice rules | `../../brand-vault/brands/[brand-slug]/voice-rules.md` | Markdown |
| Brand routing update | `../../brand-vault/CONTEXT.md` | Markdown table row |
