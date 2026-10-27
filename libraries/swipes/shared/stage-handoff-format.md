# Swipe Engine Stage Handoff

Every stage must leave a short handoff artifact and return a user-facing checkpoint. A checkpoint is terminal for the current turn.

## Write and tracking contract

- Stage handoffs, intake records, extractions, and curation logs are Markdown files under `stages/*/output/`. They are intentionally writable and tracked.
- Raw media, sampled frames, contact sheets, manifests, and other bulky package files remain ignored under `output/assets/`.
- Use the IDE file tool or `apply_patch` for Markdown outputs. Do not use `cat >`, heredocs, Python write workarounds, or long shell payloads.
- If a Markdown output is reported as ignored, treat that as a repository configuration error and stop with `state: blocked`; do not work around it by collapsing stages.
- Before returning, run the canonical `check-handoff` command from the reference-intake script. A handoff is not complete until that check passes.

## Required artifact

Write this file to the current stage's `output/` folder:

`[slug]-handoff.md`

```markdown
# Stage Handoff: [title]

- slug: [slug]
- stage: 01-save | 02-extract | 03-curate
- state: complete | ready-for-review | needs-approval | blocked | failed
- completed-at: YYYY-MM-DDTHH:MM:SSZ
- next-action: [one concrete action]
- user-response: [exact short reply that moves the workflow forward]

## Completed

- [what actually finished]

## Artifacts

- [absolute or repository-relative path]

## Visual inspection

[For image/video sources: list the contact sheet and sampled-frame paths opened with the local image viewer. Use "not applicable" for audio-only sources.]

## Warnings or blockers

- None, or the exact warning/blocker.

## Review / approval request

[Only include this section when the stage needs a user decision. State exactly what the user is approving or editing.]
```

## User-facing checkpoint

The final response for the stage must contain the same information in this order:

```text
STAGE: [01-save | 02-extract | 03-curate]
STATE: [complete | ready-for-review | needs-approval | blocked | failed]
COMPLETED: [one sentence]
ARTIFACTS: [paths]
WARNINGS/BLOCKERS: [none or exact issue]
NEXT ACTION: [one action]
REPLY WITH: [exact approval, edit, or unblock response]
```

Do not say only “done,” “waiting for approval,” or “processing.” Do not keep the task loading after this checkpoint. Return control to the user immediately. Do not poll, sleep, or continue silently while waiting for approval.

The exact reply in `user-response` is a checkpoint label, not permission to run later stages in the same turn. A Stage 01 handoff ends Stage 01. A Stage 02 handoff ends Stage 02. Stage 03 requires a separate human review of the extraction.

## Production job integration

When a production job requests a reference:

1. Read the requesting brief or stage artifact.
2. Keep its workspace and stage as the return destination in the handoff.
3. Point the job artifact to the approved reference when ready.
4. Follow `../../../_core/handoff-checkpoint.md` for the return. Keep the Swipe Engine stage checkpoint fields above intact.

Standalone reference intake starts here. No separate run card is required.

## Stage meanings

- `01-save`: `needs-approval` after acquisition, then `complete` only after the save checkpoint is approved and `finalize-save` succeeds.
- `02-extract`: `ready-for-review` after the extraction artifact and handoff exist. It must name the extraction paths and any uncertain fields.
- `03-curate`: `needs-approval` while the draft entry and pattern updates are presented; `complete` only after promotion, entry, index, and curation log are written.
- `blocked`: a concrete missing input, tool, permission, or user decision prevents progress. Name it; never disguise it as loading.
- `failed`: the stage did not complete. Include the command/error and the last valid artifact.
