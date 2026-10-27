# Curation Rules

How to merge intake and extraction into the knowledge layer.

## Merge rules

- "Why saved" always comes from intake (human voice)
- Visual, Copy, Video Timeline, Audio, and Combined Patterns sections come from extraction, edited by human at checkpoint
- "Patterns worth reusing" must be human-approved; agent proposes, human confirms
- Remove `(uncertain)` fields unless human confirms them

## Pattern aggregation

Update `patterns/visual-patterns.md`, `patterns/copy-patterns.md`, or `patterns/media-patterns.md` when:

- Human explicitly marks a pattern for aggregation, OR
- The same structural pattern appears in 2+ curated entries (note both slugs)

Format for new pattern entries:

```markdown
### [Pattern name]
- seen in: [slug-a], [slug-b]
- note: (one line description)
```

Use `patterns/media-patterns.md` for recurring audio/visual timing patterns, motion patterns, spoken CTA structures, and hook-to-frame relationships.

Do not aggregate competitor-specific copy verbatim. Aggregate structure, not wording.

## Rejection

If human rejects: write curation log with status `rejected`. Do not touch knowledge layer files.

## Editing existing entries

If curating an update to an existing slug, overwrite the entry file only after human approval. Update index row if metadata changed.
