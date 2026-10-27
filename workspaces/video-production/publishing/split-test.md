# Run Daily Split Tests

Use this workflow for continuous daily split testing.

This is a loop, not a project. It has no end date. Cells open and close inside it.

For a single reel, start directly at [Video Production’s brief](../stages/00-brief/CONTEXT.md).

## The Shape

```text
two cells always in flight
→ publish one package per day, alternating cells
→ read each package at ~24 hours
→ close a cell when its decision rule fires
→ promote the winner, log the result
→ open the next cell before the current one runs dry
```

Cell length varies. Boundaries land wherever the data puts them, not on a weekly calendar.

## Why Two Cells

Every package inside a cell shares an identical body and CTA. Publishing them on consecutive days is the closest this system gets to uploading the same video twice.

Running two cells and alternating them means consecutive uploads never share a spine:

```text
Mon  Cell A, package 1
Tue  Cell B, package 1
Wed  Cell A, package 2
Thu  Cell B, package 2
Fri  Cell A, package 3
```

It also gives you the buffer that makes daily publishing survivable. When Cell A closes, Cell B is mid-flight and the next cell is already in production.

Cells are different lengths, so boundaries land wherever the data puts them. Two weeks with cells of 3, 4, 3, 5, and 3 packages:

```text
Mon  Cell A 1      Mon  Cell B 4
Tue  Cell B 1      Tue  Cell C 2
Wed  Cell A 2      Wed  Cell D 1   <- D opens midweek
Thu  Cell B 2      Thu  Cell C 3
Fri  Cell A 3      Fri  Cell D 2
Sat  Cell B 3      Sat  Cell E 1   <- E opens on a Saturday
Sun  Cell C 1      Sun  Cell D 3
```

Fourteen slots filled, no two consecutive days sharing a spine, and no cell waiting on a Monday to start. That is the point: the loop runs on data, not on the week.

## Produce A Cell

A cell is produced as one batch, through the normal production chain.

1. Design the cell using [`../../../libraries/business-memory/sops/reel-split-test.md`](../../../libraries/business-memory/sops/reel-split-test.md).
2. Start at [the video brief](../stages/00-brief/CONTEXT.md), then follow the production stages. The production workspace has a Split Test Runs section in stages 02, 03, 04, and 06.
3. Stage 02 approves the test design: packages, rotation, and publish slots.
4. Stage 03 generates the spine once and the hook clips per package.
5. Stage 04 exports every package from one project.
6. Stage 06 runs the cell gates and opens the ledger.

Do not publish a cell until every package clears QA. A cell ships whole or not at all.

## Run The Daily Loop

Each day:

1. Publish the queued package as a **trial reel**. Never as a normal post.
2. Read yesterday's package at about 24 hours. Record views, watch-through, likes, comments, and shares on the cell ledger.
3. Compare it to the cell median, using the primary metric on the ledger.
4. Check the queue. If fewer than three published-ready packages remain across both cells, start producing the next cell today.

Do not read a package below the cell's view floor. Below the floor there is no result, only noise.

## Close A Cell

Close when the decision rule fires. See the split-test SOP for the full table.

| Outcome | What to do |
|---|---|
| Breakout | Share the winner with everyone. Open a decomposition cell on it. |
| Tie | Close with no winner. Open a fresh screening cell with new packages. |
| Dud cell | The spine is the problem. Open a new cell with a new body and CTA. |
| No read | Extend the cell. Do not guess. |

On close:

1. Write the decision and reasoning on the cell ledger.
2. Update `bank_status`, `used_in_cells`, and `paired_text_hooks` on every hook used, in both banks.
3. If a decomposition cell confirmed which half carried a win, graduate that learning into the brand's project record under `../../../libraries/business-memory/project-memory/projects/`.

A screening breakout is a candidate. Only a closed decomposition cell produces a learning worth writing into project memory.

## Queue Rules

The queue lives at [`split-tests/queue.md`](split-tests/queue.md).

- Never leave a day empty. An empty slot is the one failure mode that breaks the cadence.
- Never put two packages from the same cell on consecutive days.
- Keep at least three published-ready packages queued across both cells.
- When the queue drops below three, producing the next cell is the priority over everything else in this loop.

## Follower Feed Floor

Every test package is a trial reel, so followers see nothing unless a winner is promoted.

If fewer than two packages are shared with everyone in any rolling two-week window, publish approved non-test content directly. The main feed should not go quiet while the tests run.

## If Reach Drops

Stop the affected cell and follow the throttle response in [`../../../libraries/business-memory/sops/instagram-publishing-safety.md`](../../../libraries/business-memory/sops/instagram-publishing-safety.md).

Do not push more variants into a throttle, and do not delete the posts.

## Artifacts

| Artifact | Location | Owner |
|---|---|---|
| Cell design and packages | `../stages/02-shot-and-scene-plan/output/[cell-id]-variant-matrix.md` | Production |
| Cell exports | `../stages/04-edit-package/output/[cell-id]-edit-package.md` | Production |
| Cell ledger | `split-tests/[cell-id].md` | Video Production publishing |
| Publish queue | `split-tests/queue.md` | Video Production publishing |
| Visual hook bank | `../../../libraries/media/assets/index.md` | Media library |
| Text hook bank | `../../../libraries/business-memory/brand-vault/brands/[brand-slug]/text-hook-bank.md` | Business Memory |
| Graduated learnings | `../../../libraries/business-memory/project-memory/projects/[project-slug].md` | Business Memory |

Production status lives in the cell's brief, production artifacts, and QA record. Publishing state lives in the ledger and queue. No run card is required. Explicit holds and closed decisions remain effective until the owner changes them.
