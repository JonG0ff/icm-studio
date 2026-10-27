# Production 01: Brief

Lock the idea, the format, the look and the cast for one video. Make it here or bring a brief you wrote elsewhere.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User | Chat, or `../../../input/[slug]/brief.md` | Full | The idea, or a brought brief |
| Shared | `../../../shared/bring-intake.md` | Full, only if a file was brought | Ingest steps |
| Reference | `references/brief-format.md` | Full | Brief fields |
| Shared | `../../../shared/formats/CONTEXT.md` | "Live Recipes" | Which formats exist |
| Shared | `../../../shared/formats/[format].md` | Full, the chosen format only | Length, structure, variants |
| Library | `../../../library/index.md` | Rows for the chosen look | What's in the library |
| Shared | `../../../shared/rights-rules.md` | Full | No real voices, no reposted clips |
| Business context | `../../../../../libraries/business-memory/CONTEXT.md` | Selected brand/project pointers, only when relevant | Approved audience, voice, claims, and offer |

## Process

0. Start directly from the request. If a brief was brought, follow bring intake and skip to step 4. Accepted legacy briefs/specs retain their recorded decisions and approval status.
1. Restate the idea in one sentence. Name the angle: why it's funny or useful. Capture audience, objective, platform, and relevant brand/project facts in the optional business/context fields. Use the request first and load selected library sections only.
2. Pick the format from Live Recipes.
3. Pick the look, then cast, set and props for that look.
4. Set `review:` (default `taste`, per Pattern 19 in `../../../../../_core/CONVENTIONS.md`) and optional `credit-cap:`.
5. Fill every brief field and the `## pieces` table. Mark each piece `library`, `workshop`, or `missing`.
6. For each `missing` piece, start a subagent through the workshop (`../../workshop/01-concept/CONTEXT.md`). Its input is the brief's beats for that piece. Keep going. Do not block.
7. Save to `output/[slug]/brief.md`.

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|------------|---------------|---------------|------|
| 5 | The brief and `## pieces` table | Go, or change the angle or pieces | Taste |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Format | Exists in Live Recipes |
| Library | Every piece is `approved` or `workshop`, or `missing` with a workshop subagent started |
| Rights | Passes `rights-rules.md` |
| One sentence | The idea fits in one sentence |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Brief | `output/[slug]/brief.md` | Fields from `brief-format.md` |
