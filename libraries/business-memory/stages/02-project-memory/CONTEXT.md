# Stage 02: Project Memory

Save approved project facts, decisions, and small context pointers.

This stage does not create a general memory system.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|---------------|---------------|-----|
| Project catalog | `../../project-memory/index.md` | Full file | Avoid duplicate project records |
| Existing project memory | `../../project-memory/projects/[project-slug].md` | Full file if present | Preserve approved decisions |
| User approval | Current conversation | Explicit approval only | Draft notes are not memory |

## Process

1. Summarize proposed project facts, decisions, or pointers.
2. Ask for approval before writing.
3. If approved, append or update the project file.
4. Mark rejected ideas with `DO_NOT_RESURFACE` when the user clearly rejects them.
5. Update `project-memory/index.md`.
6. Do not save raw brainstorms, swiped references, every model observation, or unapproved route bundles.

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Project memory | `../../project-memory/projects/[project-slug].md` | Markdown |
| Index update | `../../project-memory/index.md` | Markdown table row |
