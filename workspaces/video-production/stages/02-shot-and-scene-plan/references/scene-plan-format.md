# Scene Plan Format

Use this format for `output/[slug]-scene-plan.md`. Metadata paths are repository-relative unless explicitly stated otherwise.

```markdown
# Scene Plan: [title]

- slug: [slug]
- locked_script: workspaces/video-production/stages/01-script-lock/output/[slug]-locked-script.md
- source_brief: workspaces/video-production/stages/00-brief/output/[slug]/brief.md
- accepted_imports: [existing spec/entry/route paths if applicable]
- format: [short-form | long-form]
- created: YYYY-MM-DD
- runtime_target: [brief target]

## Scene Table

| Chapter / sequence | Scene | Time | Narration | Visual | Shot / crop | Cut / transition | Pacing / hold reason | Overlay text | Motion / VFX | Asset need |
|---|---|---|---|---|---|---|---|---|---|---|

## Rhythm And Continuity

Pacing, pauses, hard cuts, holds, transitions, and momentum shifts. Long form also tracks people, props, location, screen state, grade, and ambience across sequences.

## Missing Assets

Assets to source, generate, shoot, or approve, with fallbacks.
```

## Rules

- Follow the selected format recipe and brief. A short-form reset rule is not a universal rule for interviews, tutorials, or demonstrations.
- Short-form reset values can be `aesthetic`, `angle`, `subject`, `overlay`, or `deliberate-hold`.
- The job's scene table is canonical. Stage 03 owns source paths, prompts, rights, and selections.
- Existing accepted tables remain valid; new columns do not require rewriting their history.
