# Project Memory

Approved context pointers for active marketing projects.

Keep this small. This is not a full memory system.

## What Belongs Here

- Campaign positioning approved by the user.
- Default CTA for a project.
- Audience constraints for a project.
- Decisions that should persist across future work.
- Pointers that help another workspace fill missing company, brand, SOP, offer, CTA, or routing details.
- Rejected ideas marked so agents do not resurface them.

## What Does Not Belong Here

- Raw brainstorms.
- Full research dumps.
- Swiped references.
- Every model observation from a session.
- Unapproved route bundles.
- Draft copy.
Those references live in `../../swipes/knowledge-layer/`.

## Files

| File | Use |
|------|-----|
| `index.md` | Catalog of project memory files |
| `projects/[project-slug].md` | Approved facts and decisions for one project |

## Approval Rule

Future agents may rely only on approved project memory.

If new information comes from a conversation, route it through `../stages/02-project-memory/CONTEXT.md` before saving it here.

When a downstream workspace is missing context, prefer this order:

1. Use current user input.
2. Load the smallest approved project pointer.
3. Ask one focused question.
4. Use a harmless default only when accuracy is not at risk.
