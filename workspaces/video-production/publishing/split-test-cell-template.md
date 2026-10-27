# Cell: [cell-id]

- cell_id: ST-###-[slug]
- stage: screening | decomposition
- brand: [brand slug]
- status: queued | producing | on-hold | live | closed
- opened: YYYY-MM-DD
- closed: YYYY-MM-DD
- interleaved_with: [other cell id]

## Hypothesis

One line. What a win would prove.

## Locked Spine

- body: [pointer to the locked script]
- cta: [the CTA and its visual]
- runtime: [seconds]
- variant matrix: [pointer to the matrix in production output]

## Read Plan

- primary_metric:
- view_floor:
- close_condition:

## Packages

| Package | Visual hook | Text hook | Published | Views | 3s hold | Watch-through | Likes | Comments | Shares |
|---------|-------------|-----------|-----------|-------|---------|---------------|-------|----------|--------|
| P-A | VH-### | TH-### | YYYY-MM-DD | | | | | | |
| P-B | VH-### | TH-### | YYYY-MM-DD | | | | | | |
| P-C | VH-### | TH-### | YYYY-MM-DD | | | | | | |

- cell_median (primary metric):

## Decision

- outcome: breakout | tie | dud-cell | no-read
- winner: [package id, or none]
- reasoning: [why, in one or two lines]
- promoted_to_everyone: [date, or no]
- feeds: [the decomposition cell id, or the next screening cell id]

## Bank Updates

Confirm each was written back after close.

- [ ] `bank_status` updated on every visual hook used
- [ ] `bank_status` updated on every text hook used
- [ ] `used_in_cells` updated on every hook record
- [ ] `paired_text_hooks` and `paired_visuals` updated so the pairing cannot repeat

## Events

| Date | Event | Notes |
|------|-------|-------|

Record throttle events, extensions, and anything that would change how the numbers should be read.

## Notes

Anything that would mislead a future reader of this ledger. Holidays, an outage, a package published late, a caption typo, an unusual audience source.

---

## How To Use This Template

- Copy to `split-tests/[cell-id].md` at Stage 06, before the first package publishes.
- The read plan is filled in **before** publishing. Setting a success threshold after seeing the numbers is how false winners get made.
- Leave losing packages recorded. A losing package is data.
- Only a closed decomposition cell produces a learning for project memory. A screening breakout is a candidate.
