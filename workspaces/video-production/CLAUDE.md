# Video Production

Start a video request here. This workspace owns the brief, script, scenes, asset selection, edit packet, closeout, and delivery QA.

Use `CONTEXT.md` for routing. New jobs enter `stages/00-brief/CONTEXT.md`. Existing jobs resume at their current stage using accepted artifacts. Setup is optional.

## Boundaries

- Use the shared `../../remotion/` runtime for code-rendered video. Jobs using Programmatic Animation's production recipes belong in `../programmatic-animation/`; its workshop builds reusable animation pieces.
- Use `../copywriting/` for copy-only deliverables.
- Read reusable facts from `../../libraries/business-memory/`.
- Read references from `../../libraries/swipes/` and media records from `../../libraries/media/`.
- The job owns media needs, selections, timing, placement, and its asset manifest.
- Check the media catalog before sourcing. Promote reusable assets only through the library's approval workflow.

## Load Only What The Stage Needs

Load the job's brief or accepted imported spec, its selected format recipe, the current stage, and the inputs that stage names. Do not load every brand, recipe, or past job.

Short form and long form share stages. Their pacing, chapters, aspect ratio, and delivery needs come from the brief and one recipe under `shared/formats/`.

## Existing Jobs

Accepted entry packets, specs, and route bundles are preserved in `stages/00-brief/output/[slug]/` with their original filenames. They remain authoritative for their original decisions. Do not create a new brief approval or rewrite an accepted script because paths changed.

Legacy decisions and handoff history live under `jobs/[slug]/`. Read them when resuming that job. Status comes from job artifacts and approvals, not a separate tracking card.

## Checkpoints

Use the review mode from the first job artifact and Pattern 19 in `../../_core/CONVENTIONS.md`. An imported job keeps its recorded approvals and pending decisions.

- Brief: show objective, angle, constraints, context gaps, and production plan.
- Stage 02: review script and scenes together. Stage 01 continues into it.
- Stage 03: review assets, rights, generation queue, and blockers.
- Stage 05: review edit package and closeout together. Stage 04 continues into it.
- Stage 06: review delivery and any publishing decision.

## Tool And Rights Rules

- Use the smallest matching skill under `../../skills/workflows/video-production/`.
- Raw media remains local and ignored by Git.
- Record source, rights, attribution, and use constraints before edit lock.
- A downloaded file is not approval to publish or catalog it.
- Keep editing choices in the edit package and approved business facts in Business Memory.
- A split-test cell keeps one body and CTA. Produce and QA the whole cell together.
- Publishing operations and results live under `publishing/`; production approval never implies permission to post.
