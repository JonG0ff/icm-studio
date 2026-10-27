# SOP: Reel Split Test

Standard process for testing reel creative in cells instead of one-offs.

## When To Use

- Any organic reel run that exists to learn, not just to publish.
- Loaded by the production workspace when the brief calls for a split-test cell.
- Called at scene planning, before shots are locked.

Pair this SOP with `instagram-publishing-safety.md`. Test design and publishing safety are one job.

## The Cell

A **cell** is one locked body and CTA plus several hook packages that ride on top of it.

A **hook package** is one visual hook plus one text hook, treated as a single unit.

```text
Package A   VH-012 + TH-004  ┐
Package B   VH-018 + TH-009  ├─ same body, same CTA
Package C   VH-021 + TH-002  ┘
```

The body and CTA are the **spine**. The spine never changes inside a cell. That is what makes packages comparable, and it is why body clips get generated once and reused.

One package publishes per day. See the workflow at `../../../workspaces/video-production/publishing/split-test.md`.

## Two Stages

### Stage 1: Screening

The default. Both hook layers change on every package.

- You are hunting outliers, not margins.
- A screening cell answers which package broke out. It does not answer whether the visual or the text did it.
- Small gaps are noise at this sample size. Read them as ties.

Screening is the right default because one trial reel per day against a cold audience cannot resolve a text-only difference. Spending a week of slots on a difference the data cannot see is a week lost.

### Stage 2: Decomposition

Runs only after a screening breakout. Splits the winner to find which half carried it.

```text
Package A   winning VH + winning TH   (control)
Package B   winning VH + new TH
Package C   new VH + winning TH
```

If A and B both win, the visual carried it. If A and C both win, the text carried it. If only A wins, the pairing carried it, and the pairing is the asset.

Decomposition earns its slots because a real candidate already exists.

## The Rotation Rule

Both hook layers rotate. Never weld one text hook to one visual, and never burn a visual hook after a single showing.

Three rules:

1. **Judge at three appearances.** A hook is readable once it has run in about three cells with three different partners. If VH-012 holds up beside TH-004, TH-019, and TH-027, that is the visual carrying weight. One appearance is an anecdote.
2. **Never repeat a pairing.** Check `paired_text_hooks` on the visual record and `paired_visuals` on the text record.
3. **Leave at least three cells between reappearances.** A hook returns with a different partner, a different spine, and real distance in time. Back-to-back reuse of the same opening clip is the near-duplicate profile publishing safety exists to prevent.

Rotation must be symmetric. Rotating only text hooks across always-new visuals gives text hooks three data points and every visual hook exactly one, which is backwards: visual hooks cost generation credits and are the primary iteration asset, so they are the layer that most needs accumulating signal.

A worked schedule. Nine visual hooks, nine text hooks, three packages per cell:

```text
C-01  VH-01+TH-01  VH-02+TH-02  VH-03+TH-03
C-02  VH-04+TH-04  VH-05+TH-05  VH-06+TH-06
C-03  VH-07+TH-07  VH-08+TH-08  VH-09+TH-09
C-04  VH-01+TH-04  VH-02+TH-05  VH-03+TH-06
C-05  VH-04+TH-07  VH-05+TH-08  VH-06+TH-09
C-06  VH-07+TH-01  VH-08+TH-02  VH-09+TH-03
C-07  VH-01+TH-07  VH-02+TH-08  VH-03+TH-09
C-08  VH-04+TH-01  VH-05+TH-02  VH-06+TH-03
C-09  VH-07+TH-04  VH-08+TH-05  VH-09+TH-06
```

Every hook in both banks reaches three appearances, no pairing repeats, and nothing returns sooner than three cells later. Nine cells is roughly a month at this cadence.

Rotation is what turns screening into a system instead of a guess.

## Metric By Stage

| Stage or variable | Primary metric |
|---|---|
| Screening, hook package | 3-second hold rate, then watch-through |
| Decomposition, visual vs text | 3-second hold rate |
| Body or progression | Average watch time, completion |
| CTA, soft vs hard | Link clicks to product views, via `utm_content` in PostHog |

Match the metric to what the variable controls. A hook controls the first 3 seconds. Judging a hook on likes measures the body.

## Decision Rule

Read a package only after it clears the view floor set on the cell. Below the floor there is no result, only noise.

| Outcome | Condition | Action |
|---|---|---|
| Breakout | One package is far ahead of the cell median on the primary metric and is not last on the secondary | Promote it to followers. Open a decomposition cell. |
| Tie | All packages land in a narrow band | Close the cell. No winner. Open a new screening cell with new packages. |
| Dud cell | Every package is below the account's trailing baseline | The spine is the problem, not the hooks. Open a new cell with a new body and CTA. |
| No read | Packages have not cleared the view floor after 48 hours | Extend the cell. Do not guess. |

Default the margin to roughly 1.5x the cell median on the primary metric. Treat that as a starting heuristic and recalibrate once ten cells are logged.

Prefer extending a cell over declaring a winner. A false winner gets promoted, gets copied into the next cell, and poisons everything downstream.

The dud-cell outcome matters. Without it a team will test hooks forever on a body nobody watches.

## Inputs Required

1. Brand slug.
2. The one key message the cell must land.
3. The audience.
4. The stage: screening or decomposition.
5. Available visual hooks from `../../media/assets/index.md`.
6. Available text hooks from the brand's `text-hook-bank.md`.
7. Pairing history, so rotation can be checked.

## Process

1. Load the brand voice rules and the project memory file.
2. Pick the stage. Screening unless a breakout is waiting to be decomposed.
3. Write the hypothesis in one line. Name what a win would prove.
4. Lock the spine: body beats and CTA. This is the control.
5. Build the packages.
   - Screening: pull 3 to 5 visual hooks and pair each with a different text hook. Use `reel-hook-design.md` to draft and type each pair.
   - Decomposition: build the three-package control structure above.
6. Check rotation. Reject any pairing that already ran.
7. Set the primary metric, the view floor, and the close condition.
8. Write the variant matrix. See `../../../workspaces/video-production/shared/variant-matrix-format.md`.
9. Assign publish slots on the interleave. See `instagram-publishing-safety.md`.
10. Pass the cell to production.

Three packages is the minimum for screening. Two packages cannot separate a winner from a coin flip.

## Quality Gate

| Check | Pass Condition |
|---|---|
| Spine locked | Body and CTA are identical across every package in the cell |
| Package complete | Every package has one visual hook and one text hook, both typed |
| Rotation | No visual/text pairing repeats an earlier cell |
| Stage named | The cell is labeled screening or decomposition |
| Hypothesis | One line, stating what a win would prove |
| Metric | Primary metric matches the variable under test |
| View floor | A minimum read threshold is set before publishing |
| Close condition | The cell states what ends it |
| Slots | Packages are assigned to non-consecutive days, interleaved with the other live cell |
| Voice | No hard-constraint violation from the brand voice file |
| Claims | No medical, disease, guaranteed-performance, or unsupported clinical claim |

## Output Contract

The calling workspace decides the output path.

The SOP output should include:
- cell id and stage
- the hypothesis
- the locked spine
- the package table, with visual hook id and text hook id per package
- rotation check result
- primary metric, view floor, and close condition
- publish slots
- brand voice file loaded
- any swiped references used

## Not Adopted

- **Single-variable purism.** Textbook A/B design says change exactly one thing. At one trial reel per day against a cold audience the sample cannot support it, and it produces the near-duplicate profile Instagram penalizes hardest. Attribution is bought in decomposition cells instead, after screening finds something worth attributing.
- **"Change at least one additional variable" as written.** The source guide is right that variants must differ. It is wrong to leave the extra change undefined, because a change that tracks the test condition biases the result. Extra variation belongs in the rotated differentiation layer in `instagram-publishing-safety.md`.
- **Deleting posts that underperform.** A losing package is data. It stays up unless it violates brand or claims rules.

## Source

Adapted from working notes and a third-party Instagram split-testing guide. Neither is included in this repository.

Only the sections adopted here are binding.
