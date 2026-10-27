# Video Publishing And Results

Video Production owns the publish queue, experiment history, and performance reads here. The owner makes publishing decisions and supplies platform results. These records stay live after a production job finishes.

| Need | Start here |
|------|------------|
| Check planned publishing and readiness | [Publish queue](split-tests/queue.md) |
| Run the daily test loop | [Split-test workflow](split-test.md) |
| Start a cell ledger | [Cell template](split-test-cell-template.md) |
| Produce a new video | [Video Production](../CONTEXT.md) |

Production approval never grants permission to post. Publishing is a separate, explicit decision.

## Experiment History

Each cell gets a ledger at `split-tests/[cell-id].md`, copied from the [cell template](split-test-cell-template.md).

The ledger owns the hypothesis, read plan, measurements, and decision. The queue owns scheduling. Check the ledger before adding a package to the queue. A held cell needs an explicit decision to resume.

## Performance Reads

New performance reads use `performance/[job-slug].md`. Link the published artifact, brand or project, source evidence, read time, and any approved follow-up.

Keep measurements, source notes, caveats, and losing packages. Do not archive a ledger when its cell closes. Promote confirmed findings into the project record in [Business Memory](../../../libraries/business-memory/project-memory/index.md) through its approval workflow. Raw reads stay here.
