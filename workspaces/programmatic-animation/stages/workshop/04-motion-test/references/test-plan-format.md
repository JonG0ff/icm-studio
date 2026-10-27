# Test Plan Format

The paper version of the motion test. Always write it before any audio, code or render. Rendering costs the most, so every choice gets made here first. Motion test stays optional for characters, sets and props when the piece goes straight into production; the first production render is the test. When workshop 04 runs, `test-plan.md` gets an approval line only in `plan` or `manual` mode (see Pattern 19 in `../../../../../../_core/CONVENTIONS.md`).

## Sections

### 1. Header

| Field | Value |
|---|---|
| Piece | slug, type, look |
| Length | target seconds |
| Voice | voice name and ID, model |
| Status | `draft`, or `approved` in `plan` and `manual` modes |

### 2. Full Script

Every voiced line, in order, with line IDs. Start from the concept's first-use story and the voice design text. Keep every line of the voice design text. If a line is cut or changed, list it under "Cuts" with the reason. The person has to agree to every cut.

```
[b-01] SPEAKER: [audio tag] Line text.
```

### 3. Sets

One block per set:

- **Name** and whether it's `library`, `stand-in` or `own run` (from the concept's needs table).
- **What's in it:** 4-8 items in plain words (bed, gaming desk, RGB strip, pizza boxes, front door).
- **Screens:** what any monitor or phone shows. Look-alike layouts only, no copied UI or logo marks.
- **Time of day and light:** one line.

### 4. Beat Table

One row per beat. A new beat every 3-8 seconds.

| # | Story beat | Quote or action | Set | On screen (pose, view, expression) | Props | Camera | SFX | Covers |
|---|---|---|---|---|---|---|---|---|
| 1 | Wake up | (no line) lying in bed, phone alarm | bedroom | lie, front, groggy | phone | hold | alarm buzz | must-do 1 |

- **Quote or action:** 3-6 words from the script, or the action for a silent beat.
- **Covers:** which must-do items the beat shows.
- Check every pose, expression and view against the rig. Check every action against `staging-limits.md`.

### 5. Coverage

- Each first-use story beat, and the beat number that shows it.
- Each must-do item, and the beat number that shows it, or "skipped" with a reason.

### 6. Open Questions

Choices the person should make, such as a joke's timing or what a screen says. Leave out anything with an obvious default.

### 7. Approval

Written only in `plan` or `manual` mode (see Pattern 19 in `../../../../../../_core/CONVENTIONS.md`).

```
Approved: YYYY-MM-DD, with markups: [none | list]
```

Only the person can fill this line in. It is written after their reply in `plan` or `manual` mode, and omitted in `taste` and `auto` modes.
