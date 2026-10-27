# Workshop 03: Rig

Turn the design into a moving piece in code: parts, pivots, mouths, expressions and poses. Voices skip this stage.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../02-design-sheet/output/[slug]/` | Full | The art to rig |
| Previous stage | `../01-concept/output/[slug]/concept.md` | Must-do list | What the rig must support |
| Reference | `references/rig-conventions.md` | Full | Folder shape, props, mouth map |
| Shared | `../../../shared/looks.md` | The chosen look's section | Motion style |
| Shared | `../../../shared/library-spec-format.md` | The piece type's section | Required parts |
| Skill | the `remotion-best-practices` skill (install: `remotion/README.md`) | Index, then rules as needed | Remotion APIs |

## Process

1. Split the art into parts. Set each pivot.
2. Characters: build the mouth set (6-8 shapes), expressions and poses from the concept.
3. Looks: build the kit (shared constants file) and a quick test host.
4. Write the component to `remotion/src/compositions/programmatic-animation/_workshop/[slug]/`. Import the look's kit for colors and timing.
5. Run `npm run typecheck` in `remotion/`.
6. Render a pose sheet still: every expression and pose side by side.
7. Save to `output/[slug]/rig.md`.

## Checkpoints

No stops. See Audit.

## Audit

| Check | Pass Condition |
|-------|---------------|
| Typecheck | Passes |
| No hardcoded colors | All colors come from the look's kit |
| Coverage | Every mouth, expression and pose listed renders on the pose sheet |
| Pose sheet | Every part moves cleanly |
| Must-do support | Every must-do item has the parts it needs |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Rig notes | `output/[slug]/rig.md` | Parts, pivots, mouth map, expressions, poses, code path |
| Pose sheet | `output/[slug]/pose-sheet.png` | One still |
| Component | `remotion/src/compositions/programmatic-animation/_workshop/[slug]/` | React component plus parts |
