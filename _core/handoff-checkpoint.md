# Agent Handoff And Delivery Rule

Use this format at a real workspace boundary or final delivery. Stop only when the job's review mode keeps a stop; see [Pattern 19](CONVENTIONS.md#pattern-19-files-are-the-state).

## Before Returning

1. Finish and audit the current artifact.
2. Save decisions, approvals, blockers, and context pointers in the owning job artifact.
3. Name the next owner and entry stage. Point to canonical files.
4. Reveal the output per Pattern 21 when applicable.
5. Present the checkpoint and end the turn if a stop applies. Otherwise continue and report the handoff in the final response.

No separate tracking card is required.

## User-Facing Format

```text
COMPLETED: [one sentence]
ARTIFACTS: [canonical paths]
WARNINGS/BLOCKERS: [none or exact issue]
NEXT OWNER: [workspace, library, delivery, or unavailable]
NEXT ACTION: [one concrete action]
REPLY WITH: [exact short reply, only if a stop applies]
```

Do not leave a task loading while awaiting a reply. When no live route exists, name the missing lane, preserve completed artifacts, and ask for a destination decision.
