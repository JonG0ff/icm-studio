# icm-studio

Folders that turn an idea into finished work. Every step is a file you can read and edit.

`AGENTS.md` is the source of truth for agents. `CLAUDE.md` points here.

## Vocabulary

- ICM is the method for navigating instructions, references, and job artifacts. Rules live in `_core/`.
- A workspace produces a deliverable. Its workflow is a set of stages with inputs, process, and outputs.
- A library keeps reusable context, references, or assets. Reading a record does not need its maintenance workflow.
- A skill is a reusable method. A tool runs an action.
- A template is a blank starter. A job is one piece of work; its files are artifacts.

## Start Here

Token rule: read indexes first. Then read only the closest doc or skill the task needs.

1. `workspaces/README.md`: which workspace makes what you want.
2. `libraries/README.md`: the shared libraries every workspace reads.
3. `skills/README.md`: the skill map.

## Choose The Owner

| Job | Owner |
|---|---|
| Make a deliverable | The workspace in `workspaces/README.md` |
| Keep brand, voice, offers, SOPs, and project facts | `libraries/business-memory/` |
| Save, extract, or curate references | `libraries/swipes/` (Swipe Engine) |
| Find, source, or register reusable media | `libraries/media/` |
| Build a new ICM workspace | `_core/workspace-builder/` |

- Start in the workspace that makes the deliverable. Its brief stage owns the plan.
- Read the owner's `CLAUDE.md`, then `CONTEXT.md`, then only the current stage's inputs.
- Read library records directly. Run maintenance stages only to add or change records.
- Handoffs follow `_core/handoff-checkpoint.md`.

## Business Memory

- Load one brand at a time from `libraries/business-memory/brand-vault/brands/`.
- The demo brand is Acme Coffee Co. (`acme-coffee`). Replace it with your own in setup.
- New brands start from `brand-vault/brands/_template/`. Setup fills every placeholder in it.

## Swipe Engine

- `acquire` creates a staged package only. Run `reference_intake.py finalize-save` after the user approves the save.
- Write stage Markdown with your file tool. Never use heredocs or Python write workarounds.
- Stage 03 promotion needs `promote --human-approved` after curation approval.
- Every stage writes `[slug]-handoff.md` and ends the turn while waiting for approval.
- Saved references are not cleared production assets.

## Media

- Check `libraries/media/assets/index.md` before sourcing anything new.
- Git stores metadata, not raw media. Raw files go in `libraries/media/local-media/`, which is ignored.
- Downloads do not grant rights. Record source and rights before reuse.

## Video Production

- New videos start at `workspaces/video-production/stages/00-brief/CONTEXT.md`. Pick one recipe in `shared/formats/`.
- Plan the edit before you build it: a storyboard or beat plan, then previews, then a full render.
- Finish full audio and video playback of the final export before you call it ready. If you cannot play it, say QA is blocked.
- Production approval never grants permission to post. Publishing is its own decision.
- A split-test cell keeps one body and CTA. Produce, QA, and ship the whole cell.

## Skills

- Read `skills/README.md`, then load the smallest matching `SKILL.md`.
- Video skills live in `skills/workflows/video-production/`.
- Paid generation and voice credits need approval first. Stage 03 shows the cost.

## Reviews And State

- Files on disk are the state. Follow Pattern 19 in `_core/CONVENTIONS.md` for review modes and the spend guardrail.
- Briefs, stage artifacts, and approval blocks own job state. No separate run card.

## Safety

- Never commit `.env`. Only `.env.example`, with blank values, belongs in Git.
- No audio or video files in Git.
- Use the demo brand in examples. Never add a real brand, client, or person.

## Writing Rule

Write for a tired teammate on a phone:

- Short sentences.
- Plain words.
- One idea per bullet.
- No em dashes.
