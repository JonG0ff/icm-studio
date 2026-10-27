# Stage 01: Script Lock

Write or verify the spoken script, beat map, on-screen text, and runtime from the job's accepted brief or imported spec.

## Inputs

| Source | Location | Scope | Why |
|---|---|---|---|
| Brief | `../00-brief/output/[slug]/` | Brief or accepted entry/spec/route | Objective, angle, content direction, constraints |
| Format | `../../shared/formats/CONTEXT.md` | Selected recipe only | Opening, pacing, chapters, runtime |
| Business Memory | `../../../../libraries/business-memory/brand-vault/CONTEXT.md` | Selected brand voice rules | Voice and claim constraints |
| Short form only | `../../../../libraries/business-memory/sops/reel-hook-design.md` | Hook guidance when relevant | Hook pair and payoff |
| Reference | `references/locked-script-format.md` and `references/script-lock-checklist.md` | Full | Script structure and audit |

## Process

1. Read the accepted direction and prior job decisions. Preserve locked copy and VO; do not rewrite them because the repository moved.
2. Draft authored speech from the accepted direction. For recorded footage, inventory the source and verify selected words, original-file ranges, and surrounding context using the selected recipe. Keep factual source notes and separate recorded speech from authored text.
3. Build the beat map with timing, narration, viewer takeaway, and on-screen text. For long form, group beats by chapter and name transitions.
4. Keep overlays purposeful. Record whether full captions are separate from on-screen text.
5. Estimate runtime per chapter when applicable and for the whole video. Resolve mismatch against the brief.
6. Check brand rules, format guidance, and the script checklist. Mark unresolved lines and approvals explicitly.
7. Save the locked script, then continue to Stage 02. The script and scenes share a checkpoint.

## Split Test Runs

Skip unless the brief or accepted spec says `split-test-cell`.

- Lock the body and CTA as the spine, identical across packages.
- Mark beat one `hook slot, varies by package`; Stage 02 supplies hook packages.
- VO covers the body and CTA only unless an approved test design explicitly states otherwise.
- Preserve an accepted `all - screening cell` hook selection as the instruction to ship every pair.

## Audit

| Check | Pass Condition |
|---|---|
| Direction traced | Angle, key messages, offer, CTA, and accepted locks match the brief/spec |
| Opening and payoff | Opening promise and its delivery are identified using the selected recipe |
| Voice and claims | Brand constraints pass; claims have source notes |
| Runtime | Beat/chapter totals fit the brief |
| Recorded footage | Selected speech and original-file ranges are verified; omissions preserve meaning; authored overlays are identified separately |
| Coverage | Every beat has narration, takeaway, and overlay text or an explicit dash |
| Approval | Unresolved lines remain visible; no inferred acceptance |

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Locked script | `output/[slug]-locked-script.md` | `references/locked-script-format.md` |
