# Visual Hook Record Format

Use this format for `assets/vh-[###]-[slug].md`.

A visual hook is a short silent clip, 2 to 4 seconds, built to open a reel. It is an asset record like any other, with extra fields for hook type and pairing history.

Read `asset-record-format.md` first. This format extends it; it does not replace it.

## Record

```markdown
# Visual Hook: [name]

- asset_id: [vh-###-slug]
- hook_id: VH-###
- title: [plain name]
- type: generated-video
- status: ready | needs-approval | blocked
- date_added: YYYY-MM-DD
- tags: tag-one, tag-two
- source_url: generated
- local_path: [local-only path to the raw clip]
- rights_note: generated
- reuse_notes: [which topics and pillars this fits]
- used_in: [project-slug]

## Hook Fields

- hook_type: scroll-stopper | head-scratcher
- visual_premise: [one line, what the viewer sees]
- emotion: [what it should make the viewer feel]
- subject: [person, product, object, environment, or metaphor]
- motion_action: [the action across the clip]
- duration: [seconds]
- aspect_ratio: 9:16
- target_resolution: 1080x1920
- model: [generation model and resolution]
- source_prompt: [exact prompt, so the clip can be regenerated or varied]
- references: [reference images or swipe pointers used]

## Test History

- bank_status: untested | live | winner | flat | retired
- used_in_cells: [ST-###, ST-###]
- paired_text_hooks: [TH-###, TH-###]

## Description

What the clip shows.

## Reuse Guidance

Best uses, bad fits, edit notes, and search terms.

## Usage History

| Cell | Paired text hook | Result | Date | Notes |
|------|------------------|--------|------|-------|
```

## Field Rules

- `hook_id` is stable once created and is never reused, even after retirement.
- `source_prompt` and `model` are required. Without them the clip cannot be regenerated or varied, and the bank stops compounding.
- Clips stay silent. VO, music, and SFX are added in the edit, never baked into a bank clip.
- `paired_text_hooks` is the rotation record. Check it before building a cell and never repeat a pairing.
- `used_in_cells` grows every time the hook ships. A hook with three entries and no breakout is `flat`.
- A visual hook is judged at about three appearances with three different text hooks. Do not retire it after one showing; a single result is an anecdote, and this clip cost credits to make.
- Leave at least three cells between reappearances so the same opening clip never runs close to itself.
- Raw clips stay in `local-media/` or another ignored local-only path. The record goes in Git; the file does not.
- Generate and iterate at a low resolution, then promote to 1080p when the clip enters a cell.

## Bank Status Values

| Status | Meaning |
|---|---|
| `untested` | Approved, never published |
| `live` | Currently in a cell |
| `winner` | Broke out in a decomposition cell as the carrying half |
| `flat` | Ran three or more times, never broke out |
| `retired` | Brand, claims, or quality problem |

A `flat` hook is still useful as a control in a decomposition cell. Do not delete it.

## Depth Target

At one package per day, this bank is the bottleneck on publishing, not credits.

Hold at least fifteen `untested` visual hooks across a spread of hook types and subjects.

The math: a pool of nine visual hooks and nine text hooks fills nine three-package cells, gets every hook to three appearances, and never repeats a pairing. That is about a month of daily publishing from one bank load. Fifteen gives headroom for retirements.

Because hooks are reused about three times rather than consumed once, the bank does not need to grow by one clip per publish. Build steadily at low resolution and promote to 1080p only when a clip enters a cell.

## Related

- Test design: `../../business-memory/sops/reel-split-test.md`
- Text hook bank: the brand's `text-hook-bank.md` in `../../business-memory/brand-vault/brands/[brand-slug]/`
