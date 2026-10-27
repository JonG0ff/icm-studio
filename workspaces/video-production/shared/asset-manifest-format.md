# Asset Manifest Format

Use this format for `stages/03-asset-gathering/output/[slug]-asset-manifest.md`. Metadata paths in completed artifacts are repository-relative unless explicitly stated otherwise.

```markdown
# Asset Manifest: [title]

- slug: [slug]
- scene_plan: workspaces/video-production/stages/02-shot-and-scene-plan/output/[slug]-scene-plan.md
- locked_script: workspaces/video-production/stages/01-script-lock/output/[slug]-locked-script.md
- source_brief: workspaces/video-production/stages/00-brief/output/[slug]/brief.md
- accepted_imports: [existing spec/entry/route paths if applicable]
- media_library: libraries/media/assets/index.md

## Source Readiness Summary

- ready:
- needs approval:
- needs generation:
- needs source:
- blocked:

## Asset Table

| Asset ID | Scene / Beat | Type | Need | Library ID | Source path / URL / prompt | Status | Rights note | Fallback | Next action |
|----------|--------------|------|------|------------|----------------------------|--------|-------------|----------|-------------|

For long form, group rows by chapter/sequence and include duration, resolution, crop, reuse, and backup coverage in the need/source notes.

Status values:
- `ready`
- `queued-generation`
- `needs-source`
- `needs-generation`
- `needs-shoot`
- `needs-approval`
- `blocked`

Types:
- footage
- still
- generated-image
- generated-video
- screen-capture
- brand-asset
- client-asset
- audio
- voiceover
- music
- sfx
- logo
- overlay
- template
- source-proof

## Generation Queue

| Asset ID | Prompt / script | Tool | Specs | Approval needed | Output path / status |
|----------|-----------------|------|-------|-----------------|----------------------|

Delete this section only if no generated assets are needed.

## Voiceover And Audio

- voiceover source:
- voice criteria or chosen voice:
- music source:
- stems:
- SFX source map:
- mix notes:

## Source And Rights Notes

List licenses, ownership notes, public-domain evidence, paid-library status, internal-reference-only limits, attribution needs, and approval risks.

For Wikimedia Commons rows, include the Commons file page URL, direct file URL or local-only path, creator or credit line, license name, license URL or usage terms, attribution requirement, and any personality, trademark, event, or brand-context risk. Do not mark a Commons row `ready` until those details are recorded.

For web-still rows, include the direct source URL and local path. Use `rights_note: unclear`. A local file does not establish publication rights; keep the source URL and approved use conditions.

## Gaps

| Gap | Blocks the edit? | Owner | Next action |
|-----|------------------|-------|-------------|

## Media Library Promotions

List reusable new assets that should be added to `libraries/media/assets/` after approval.

## Edit Readiness Gate

- [ ] Every scene asset need has a row.
- [ ] The media library was checked before new sourcing.
- [ ] Every external asset has a source and rights note.
- [ ] Wikimedia Commons rows include file page URL, creator/credit, license, attribution note, context-risk review, and fallback.
- [ ] Pixabay music/SFX rows include page URL, creator, title, duration, local path when downloaded, and `Pixabay Content License` note.
- [ ] Required SFX have source metadata and usable local files, or an explicit pending blocker/fallback/no-SFX decision. Search packets alone do not establish readiness.
- [ ] YouTube clips are marked internal-reference-only unless clearance is documented.
- [ ] Paid or unclear assets are marked `needs-approval` or `blocked`.
- [ ] Generated assets have prompts, tool names, and approval status.
- [ ] Required voiceover, music, and SFX needs are either ready or queued.
- [ ] Blockers are named before the edit package is built.
```

## Rules

- This manifest is the canonical selection record for the job. Reusable records remain in the media library.
- Do not put secrets, account keys, paid-library credentials, private cookies, or tokenized download links in the manifest.
- Do not commit raw media files. Use local-only paths for clips, stills, audio, and generated media.
- Do not commit filled Pixabay SFX selection JSON if it contains direct download URLs.
- Wikimedia Commons assets need file page, creator/credit, license, attribution, and context-risk notes before `ready`.
- YouTube assets are internal reference only unless separate rights clearance is documented.
- Generated assets need prompt, tool, date, and approval status before they can be marked `ready`.
- If a source is useful but risky, mark it `needs-approval` or `blocked` and provide a fallback.
