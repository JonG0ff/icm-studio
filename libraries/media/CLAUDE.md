# Media Library

Reusable stock, reference, and production media catalog for production work.

This library stores source, rights, location, and reuse records. Raw media belongs in `local-media/` or another approved local-only location that is ignored by Git.

## When to Use This Library

Use this when you need to find, register, audit, or reuse footage, stills, audio, overlays, generated media, or internal reference clips across multiple content pieces.

Read `assets/index.md` and matching records directly when looking for existing assets. Start a maintenance stage only when finding, registering, or auditing records needs its own artifact.

Use `../swipes/` for saved references and pattern extraction. The destination production workspace owns the job's brief, selections, timing, and asset manifest.

## Folder Map

```text
media/
|-- CLAUDE.md
|-- CONTEXT.md
|-- assets/
|   `-- index.md
|-- local-media/
|   `-- .gitkeep
|-- setup/
|   `-- questionnaire.md
|-- shared/
|   |-- asset-record-format.md
|   |-- visual-hook-record-format.md
|   `-- local-media-policy.md
`-- stages/
    |-- 01-find-reusable/
    |-- 02-register-asset/
    `-- 03-review-library/
```

Each stage has `CONTEXT.md`, `output/`, and `references/`.

## Triggers

| Keyword | Action |
|---------|--------|
| `find media` | Open `stages/01-find-reusable/CONTEXT.md` |
| `register asset` | Open `stages/02-register-asset/CONTEXT.md` |
| `review library` | Open `stages/03-review-library/CONTEXT.md` |
| `setup` | Open `setup/questionnaire.md` |
| `status` | Show stage output state |

## Routing

| Task | Go To |
|------|-------|
| Find reusable clips or stills for a new project | `stages/01-find-reusable/CONTEXT.md` |
| Find media named in a job brief | `stages/01-find-reusable/CONTEXT.md` |
| Add a reusable asset record after sourcing | `stages/02-register-asset/CONTEXT.md` |
| Audit rights, duplicates, paths, or stale records | `stages/03-review-library/CONTEXT.md` |
| Confirm the asset record schema | `shared/asset-record-format.md` |
| Register or read a split-test visual hook | `shared/visual-hook-record-format.md` |
| Confirm raw media storage rules | `shared/local-media-policy.md` |

## Rules

- Keep raw media out of Git.
- Store source, rights, tags, local path, and reuse history in Markdown.
- Mark risky YouTube, social, or unclear assets `internal-reference-only`, `needs-approval`, or `blocked`.
- Search this library before downloading new production media.
- Return approved records to the requesting job artifact. No separate run card is required.
- Promote new reusable assets only after human approval.
