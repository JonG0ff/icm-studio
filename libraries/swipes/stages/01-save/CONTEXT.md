# Stage 01: Save

Intake a marketing reference. URL, image path, PDF, audio, video, screenshot, or pasted copy. Human decides keep or skip before extraction.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User | (conversation) | URL, file path, upload, or pasted content | The reference to save |
| Shared | `../../shared/swipe-tags.md` | Common tags and fallback | Tag options for this reference |
| Reference | `references/intake-format.md` | Full file | Required intake fields |
| Shared | `../../shared/stage-handoff-format.md` | Full file | Required terminal checkpoint and handoff format |
| Skill | `../../../../skills/swipe-engine/reference-intake/SKILL.md` | Full file | Acquire and normalize the source |

## Process

1. Ask the user for the reference: URL, file, screenshot, or pasted content. If multiple, handle one at a time.
   - Animation style sets: when several images show one style, ask the reason and the style slug once. Save each image as its own entry (`[style-slug]-01`, `-02`, ...) with the tags `animation-style, style-[style-slug]`. One checkpoint covers the set.
2. Capture metadata: title (or derive from source), source URL/path, asset type (ad, landing-page, email, brand-guide, social-post, other).
3. Ask why they saved it. One or two sentences. This is taste, not extraction.
4. Propose a slug (lowercase, hyphenated). Confirm with user.
5. Propose tags from `swipe-tags.md`, approved project pointers if already loaded, or the user's stated reason. User confirms or edits.
6. Run `reference_intake.py acquire` to acquire the source into `output/assets/[slug]/`. Stop if acquisition fails; acquisition creates a staged package only.
7. Read `manifest.json` and confirm `status: staged`, `workflow_state: awaiting-save-approval`, a valid `primary_context`, and at least one acquired file. Surface every warning and `quality_status`.
8. **[Checkpoint]** Present intake summary plus acquisition warnings. User decides: save (continue to extract) or skip (no intake record).
9. If save: run the canonical `finalize-save` command with the user's reason, metadata, and `--human-approved`. Do not hand-write the intake file. If skip: do not finalize, and never promote the staged package.
10. Write `[slug]-handoff.md` using `../../shared/stage-handoff-format.md`. Return the Stage 01 checkpoint and end the turn. Do not keep loading while waiting for the user's save decision.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 8 | Title, source, type, why saved, slug, tags, acquired context, warnings | Save or skip |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Source captured | URL, path, or pasted content is recorded |
| Source acquired | Manifest status is `staged`, primary context exists, and `quality_status`/warnings were reviewed |
| Save handoff | `workflow_state` is `save-approved`, `ready_for_stage_02` is `true`, and `intake_record` resolves |
| Why saved | Human provided a reason (not agent-invented) |
| Slug valid | Lowercase, hyphenated, unique vs existing `knowledge-layer/index.md` slugs |
| Human gate | Output written only after explicit save confirmation |
| Terminal handoff | Handoff artifact exists and the user-facing checkpoint names artifacts, warnings, next action, and exact reply |
| No setup dependency | Missing default tags never blocks intake |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Intake record | `output/[slug]-intake.md` | Markdown per `references/intake-format.md` |
| Staged assets | `output/assets/[slug]/manifest.json` | Manifest plus ignored raw/context files |

Stage 02 reads the intake record and manifest from `output/`. It must stop unless `ready_for_stage_02: true`. It uses local context artifacts and does not refetch the original source.
