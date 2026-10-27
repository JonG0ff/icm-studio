# Swipe Library

Saved references and reusable patterns. Its Swipe Engine maintenance workflow saves, extracts, and curates references.

## Folder Map

```
swipes/
├── CLAUDE.md              (you are here)
├── CONTEXT.md             (start here for task routing)
├── setup/
│   └── questionnaire.md   (optional pointer to Business Memory setup)
├── knowledge-layer/       (SWIPED references -- grows forever)
│   ├── CONTEXT.md
│   ├── index.md
│   ├── entries/
│   ├── assets/            (approved context artifacts)
│   └── patterns/
│       ├── visual-patterns.md
│       ├── copy-patterns.md
│       └── media-patterns.md
├── shared/
│   └── swipe-tags.md      (suggested organization tags)
└── stages/
    ├── 01-save/           (intake a reference)
    ├── 02-extract/        (structured extraction)
    └── 03-curate/         (human approve -> knowledge layer)
```

Each stage has `CONTEXT.md`, `output/`, and `references/`.

## One Job

This library owns the Swipe Engine reference loop:

`01-save -> 02-extract -> 03-curate`

Read existing entries and patterns directly. Reading a record does not require a save, extract, or curate pass. When creating a deliverable, start its production workspace through `../../workspaces/README.md`; that workspace owns the brief and plan.

## Triggers

| Keyword | Action |
|---------|--------|
| `setup` | Open Business Memory setup for reusable brand, company, SOP, and project details |
| `save` | Enter reference intake at `stages/01-save/CONTEXT.md` |
| `brief` | Choose the destination workspace in `../../workspaces/README.md` |
| `status` | Show reference loop state and knowledge-layer count |

## No Setup Requirement

The swipe engine must work without setup.

Saving references, extracting patterns, and curating entries cannot block on missing setup placeholders.

Fallback order:

1. Use what the user just said.
2. Load approved brand, company, SOP, or project pointers from `../business-memory/` only when reference context needs them.
3. Ask one small missing-content question at the active stage.
4. Use a harmless default only when it will not distort the output.

Default tags are conveniences. They are not prerequisites.

### How `status` works

Scan `stages/*/output/` for files other than `.gitkeep`. Count entries in `knowledge-layer/index.md`. Render:

```
Swipe Engine Status

Reference loop:
  [01-save]     [02-extract]     [03-curate]
     STATUS          STATUS           STATUS

Knowledge layer: N curated entries
```

## Routing

| Task | Go To |
|------|-------|
| Save a new reference | `stages/01-save/CONTEXT.md` |
| Save a reference named in a job brief | `stages/01-save/CONTEXT.md` |
| Extract from saved reference | `stages/02-extract/CONTEXT.md` |
| Curate into knowledge layer | `stages/03-curate/CONTEXT.md` |
| Create an output using references | `../../workspaces/README.md` |
| Configure reusable marketing context | `../business-memory/setup/questionnaire.md` |

## What to Load

| Task | Load These | Do NOT Load |
|------|-----------|-------------|
| Save reference | user request or selected job brief, `stages/01-save/references/*`, `shared/swipe-tags.md` | unrelated knowledge-layer entries |
| Extract | `stages/01-save/output/`, `stages/02-extract/references/*` | unrelated Business Memory brands and knowledge-layer entries |
| Curate | `stages/02-extract/output/`, `knowledge-layer/index.md`, `stages/03-curate/references/*` | unrelated Business Memory brands |

## Stage Handoffs

Reference loop: each stage writes to its own `output/`. Stage 03 also writes to `knowledge-layer/` on human approval.

If you edit any output file between stages, the next stage picks up your edits.

## Handoff Guardrail

`acquire` creates a staged package only. Follow the manifest's `workflow_state` and `next_action`. After the user approves the Stage 01 checkpoint, use `reference_intake.py finalize-save` with `--human-approved`; do not create intake or handoff files with a shell heredoc or Python write workaround. Stage Markdown outputs are intentionally writable/tracked; raw media and derived assets remain ignored. Stage 03 promotion requires `--human-approved` after the curation checkpoint.

If an IDE file tool reports that a stage Markdown output is ignored, stop and report a repository configuration error. Do not switch to a long heredoc, keep the turn loading, or combine multiple stages into one approval.

Every stage must write `[slug]-handoff.md` using `shared/stage-handoff-format.md`. The handoff is a terminal checkpoint for the current turn. Never keep the task loading while waiting for approval; return the summary and the exact reply needed from the user.
