# Intake Format

Required fields for `output/[slug]-intake.md`.

```markdown
# Intake: [title]

- slug: [slug]
- source: [url or file path]
- source-type: image | webpage | pdf | audio | video | social-video
- type: ad | landing-page | email | brand-guide | social-post | screenshot | pdf | other
- saved: YYYY-MM-DD
- tags: [comma-separated]
- asset-manifest: output/assets/[slug]/manifest.json
- primary-context: output/assets/[slug]/[context artifact path]
- acquisition-status: complete
- status: pending-extraction

## Why saved

(human note -- required)

## Raw notes

(optional: user observations before extraction)

## Source content

(URL, path, or pasted text/screenshot description)
```

Rules:

- `status` starts as `pending-extraction`. Stage 03-curate sets `curated` in the knowledge layer entry.
- `asset-manifest` and `primary-context` must resolve to files produced by `reference-intake`.
- Do not write the intake record unless `acquisition-status` is `complete`.
- Prefer the `reference_intake.py finalize-save` command. It requires explicit `--human-approved`, preserves the manifest handoff state, and prevents empty or invented `why saved` notes.
- Do not extract patterns here. Intake is metadata and human intent only.
