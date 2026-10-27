# Variant Matrix Format

Use this format for `stages/02-shot-and-scene-plan/output/[cell-id]-variant-matrix.md`.

The variant matrix is the production side of a split-test cell. It says what gets built, what stays identical, and when each package publishes.

Write one only when the run is a split test. A normal single-reel run does not need it.

Read `../../../libraries/business-memory/sops/reel-split-test.md` before filling this in.

## Matrix

```markdown
# Variant Matrix: [cell-id]

- cell_id: ST-###-[slug]
- stage: screening | decomposition
- brand: [brand slug]
- hypothesis: [one line, what a win would prove]
- interleaved_with: [the other live cell id]

## Locked Spine

Identical across every package. Built once, reused by all.

- body_beats: [pointer to the locked script beat map]
- cta: [the exact CTA and its visual]
- runtime: [seconds]
- vo_track: [pointer to the VO asset]

## Packages

| Package | Visual hook | Text hook | Differentiation delta | Publish slot | utm_content | Export | Result |
|---------|-------------|-----------|----------------------|--------------|-------------|--------|--------|
| P-A | VH-### | TH-### | music, cover, b-roll order | YYYY-MM-DD | [value] | [filename] | pending |
| P-B | VH-### | TH-### | music, cover, b-roll order | YYYY-MM-DD | [value] | [filename] | pending |
| P-C | VH-### | TH-### | music, cover, b-roll order | YYYY-MM-DD | [value] | [filename] | pending |

## Rotation Check

| Package | Pairing | Ran before? |
|---------|---------|-------------|
| P-A | VH-### + TH-### | no |

## Read Plan

- primary_metric: [3-second hold rate, watch time, or link clicks]
- view_floor: [minimum views before a package is read]
- close_condition: [what ends the cell]
```

## Field Rules

- `cell_id` is stable. Every artifact for the cell uses it, including the ledger in `../publishing/split-tests/`.
- The locked spine is the control. If any spine field differs between packages, the cell is invalid and the results mean nothing.
- Every package needs both a `visual_hook_id` and a `text_hook_id`. A package missing one is not a package.
- `differentiation_delta` is assigned by rotation, never by preference. Never give the expected winner the better music. See `../../../libraries/business-memory/sops/instagram-publishing-safety.md`.
- Publish slots must be non-consecutive and interleaved with the other live cell.
- `utm_content` is unique per package, so PostHog can separate downstream behavior.
- `result` stays `pending` until the 24-hour read. Results are recorded on the cell ledger, and copied here only as a summary.

## Rotation Rule

Reject any pairing that has already run. Check `paired_text_hooks` on the visual hook record and `paired_visuals` on the text hook record.

A repeated pairing is not just a weak test. It is the closest this system gets to republishing the same creative, which is the exact thing publishing safety is trying to avoid.

## Decomposition Matrix

A decomposition cell has exactly three packages and a fixed shape:

| Package | Visual hook | Text hook | Role |
|---------|-------------|-----------|------|
| P-A | winning VH | winning TH | control |
| P-B | winning VH | new TH | tests the visual |
| P-C | new VH | winning TH | tests the text |

Read it as: A and B win means the visual carried it. A and C win means the text carried it. Only A wins means the pairing is the asset.

## Related

- Test design: `../../../libraries/business-memory/sops/reel-split-test.md`
- Publishing safety: `../../../libraries/business-memory/sops/instagram-publishing-safety.md`
- Cell template: `../../../libraries/business-memory/content-types/split-test-cell.md`
- Cell ledger and queue: `../publishing/split-tests/`
