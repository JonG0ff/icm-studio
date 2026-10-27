# Contributing

Thanks for helping. Small, focused pull requests are easiest to review.

## One Pull Request Per Piece

Open one PR for each of these:

- **A new workspace.** Build it with the workspace builder in `_core/workspace-builder/`. It must pass its own validation stage.
- **A new skill.** Put it under `skills/`, add a `skills/registry.yml` entry with its owner and license, and route to it from `skills/README.md`.
- **A fix to a library or stage.** Keep the stage contract: inputs, process, checkpoints, outputs.

## Rules

- Follow `_core/CONVENTIONS.md`. Keep `CONTEXT.md` files under 80 lines.
- Write for a tired reader on a phone: short sentences, plain words, one idea per bullet.
- No em dashes.
- Use the demo brand, Acme Coffee Co., in examples. Never add a real brand, client, or person.
- No audio or video files in Git. No `.env` files.
- Only add code you wrote, or code with a known, compatible license. Keep the upstream license and notice.

## Before You Open The PR

- Every path in a `CONTEXT.md` you touched points to a file that exists.
- Every placeholder you added is asked for in a `setup/questionnaire.md`. See `_core/placeholder-syntax.md`.
- Tests for any script you changed pass.

## Questions

Open a discussion or an issue. Say which workspace or library it is about.
