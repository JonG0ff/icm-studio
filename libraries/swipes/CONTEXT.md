# Swipe Library

Saved references and reusable patterns. Swipe Engine is this library's save, extract, and curate maintenance workflow.

Read existing records directly. To make a deliverable, choose its production workspace in `../../workspaces/README.md` and establish the brief there.

## Task Routing

| Task Type | Go To | Description |
|-----------|-------|-------------|
| Save a reference | `stages/01-save/CONTEXT.md` | Intake URL, image, PDF, audio, video, or screenshot |
| Extract patterns | `stages/02-extract/CONTEXT.md` | Pull visual, copy, and layout fields from intake |
| Curate into library | `stages/03-curate/CONTEXT.md` | Human approves merge into knowledge layer |
| Read existing references | `knowledge-layer/CONTEXT.md` | Load selected entries and patterns without running maintenance stages |
| Create an output using references | `../../workspaces/README.md` | The destination workspace owns the brief and production decisions |

## Shared Resources

| Resource | Location | Contains |
|----------|----------|----------|
| Business Memory | `../business-memory/CONTEXT.md` | Approved brand, company, SOP, and project details |
| Reference library | `knowledge-layer/CONTEXT.md` | Routes to curated entries and patterns |
| Swipe tags | `shared/swipe-tags.md` | Suggested tags for organizing saved references |

## No Setup Requirement

This library is usable immediately.

Do not block `save`, `extract`, or `curate` because setup was not run.

Use this fallback order:

1. Current user input.
2. Approved pointers in `../business-memory/`.
3. One small question at the current stage.
4. A harmless default, only when the reference record will still be accurate.

## Philosophy

- The human provides the taste.
- The human decides what gets saved.
- Swipe Engine maintains this library. The production workspace owns each deliverable's plan.
- Business Memory fills missing brand, company, SOP, and project details.
- Return reference pointers to the requesting job artifact after the required checkpoint. No separate run card is required.
