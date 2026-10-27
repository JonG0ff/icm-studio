# Locked Script Format

Use this format for `output/[slug]-locked-script.md`. Metadata paths in completed artifacts are repository-relative unless explicitly stated otherwise.

```markdown
# Locked Script: [title]

- slug: [slug]
- output_intent: [video | short-form-video | split-test-cell]
- format: [short-form | long-form]
- source_brief: workspaces/video-production/stages/00-brief/output/[slug]/brief.md
- accepted_imports: [existing spec/entry/route paths if applicable]
- created: YYYY-MM-DD
- runtime_target: [brief target]
- runtime_estimate: [spoken estimate with pauses]

## Opening And Payoff

Opening promise, selected hook when applicable, and the beat/chapter that pays it off.

## Locked Voiceover Script

Final spoken script and delivery direction. Group by chapter for long form.
Mark unresolved lines `[needs approval]`.

## Beat Map

| Chapter / sequence | Beat | Time | Narration | Viewer takeaway | On-screen text |
|---|---|---|---|---|---|

## Runtime Estimate

Word count, spoken pace, pause allowance, chapter totals when applicable, total, and fit against target.

## Unresolved Lines

Every unresolved line and claim/source question, or `None`.
```

## Rules

- Trace content to the accepted brief/spec. Keep prior script and VO approvals intact.
- On-screen emphasis and full captions are distinct deliverables; specify both when required.
- Every beat has text or an explicit dash. Stage 02 owns shots, cuts, and asset needs.
- Runtime stays an estimate until recorded/generated VO exists. Adjust pauses before changing locked copy.
- Short-form hook pairs and long-form chapter structure follow the selected recipe.
