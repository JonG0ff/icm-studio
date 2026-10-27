---
name: still-bank
description: Source the full still-image bank for one still-first PiP reel edition from its locked script — 40 unique body stills behind the talking head plus the 4 hook-grid panels. Use when a locked script ships a numbered, timecoded shot brief and the edit needs a repeatable, no-repeats still bank with a map, an inventory, and asset-manifest rows. Covers hobby-edition reels and poke-style UGC packs.
license: MIT
---

# Still Bank

Turn one edition's locked script into a complete, checked still bank.

Per edition this delivers 40 unique body stills, 4 hook-grid panels, a human map, a
variety report, and the rows for the asset manifest. The product-beat screen is out of
scope.

This skill does not search or download anything itself. It parses the brief, plans the
queries, calls `../media-sourcing/` to do the work, then checks and packages the result.
Source methods and rights handling are defined there. Do not duplicate them.

## When to use it

- A locked script has a `## B-Roll` section of numbered, timecoded briefs and a
  `## Hook Grid` table.
- The format is still-first: hard-cut stills under a keyed talking-head PiP.
- The run is at Stage 03 of `workspaces/video-production/`.

For a single plate, one clip, or a footage-led reel, use `../media-sourcing/` directly.

## Inputs

| Input | Where |
|---|---|
| Locked script | `workspaces/video-production/stages/01-script-lock/output/[slug]-locked-script.md` |
| Format constants | `../../../../libraries/business-memory/content-types/still-first-reel.md` |
| Media library | `../../../../libraries/media/assets/index.md` |
| Manifest format | `../../../../workspaces/video-production/shared/asset-manifest-format.md` |
| Query rules | `references/query-patterns.md` |
| Output shapes | `references/bank-output-format.md` |

Set the shared paths once:

```bash
SLUG=movie-edition-01
STAGE=workspaces/video-production/stages
OUT=$STAGE/03-asset-gathering/output
BANK=libraries/media/local-media/still-bank/$SLUG
CONF=$BANK/_configs
SKILL=skills/workflows/video-production
```

## Run order

### 1. Check the media library first

```bash
rg -i 'theater|cinema|film crew|projector' libraries/media/assets/index.md
```

Mandatory, every time, before any search. Note every reusable hit and its asset ID. Those
slots route to `library-reuse` in the query plan.

### 2. Parse the locked script

```bash
python3 $SKILL/still-bank/scripts/parse-shot-brief.py \
  --script $STAGE/01-script-lock/output/$SLUG-locked-script.md \
  --out $OUT/$SLUG-shot-brief.json
```

Expect 40 body stills and 4 hook panels. A warning about the count means the script
drifted from the locked format — stop and check the script, not the parser.

### 3. Write the query plan

Read `references/query-patterns.md`. Then write
`$CONF/$SLUG-queries.json` — one entry per slot, at least three queries each:

```json
[
  {"slot": "shot-01", "method": "pexels",
   "queries": ["dark cinema audience from behind screen glow",
               "movie theater seats silhouette projector light",
               "cinema interior dark wide"]},
  {"slot": "shot-33", "method": "web-still",
   "queries": ["film crew on location set rigs cables wide", "...", "..."]},
  {"slot": "shot-35", "method": "commons", "subject": "Film scoring",
   "categories": ["Category:Film scoring"], "queries": ["...", "...", "..."]}
]
```

Methods: `pexels`, `web-still`, `commons`, `library-reuse`, `generation`.

### 4. Build the configs

```bash
python3 $SKILL/still-bank/scripts/build-search-configs.py \
  --shot-brief $OUT/$SLUG-shot-brief.json \
  --queries $CONF/$SLUG-queries.json \
  --out $CONF
```

This fails loudly on a slot with no plan, thin query sets, a commons entry with no
categories, or a generation entry with no reason. Fix the plan and re-run.

### 5. Download — free sources only

Pexels, one call per beat folder:

```bash
for f in $CONF/pexels/*.searches.json; do
  beat=$(basename "$f" .searches.json)
  python3 $SKILL/media-sourcing/scripts/search-pexels-photos.py \
    --config "$f" --out "$BANK/$beat" --orientation portrait
done
```

Web stills — fill the direct image URLs in the packet first, then:

```bash
python3 $SKILL/media-sourcing/scripts/download-web-still.py \
  --config $CONF/web-stills/$SLUG-web-stills.json \
  --out $BANK/[beat-folder]
```

Wikimedia Commons:

```bash
python3 $SKILL/media-sourcing/scripts/search-commons-categories.py \
  --config $CONF/commons/section-categories.json \
  --depth 1 --min-width 900 --per-section 3 --sleep 2 \
  --out $CONF/commons --download-dir $BANK/[beat-folder]
```

Target roughly 3 candidates per slot, about 120 for a 44-slot edition. That is the 3x
overshoot, and it is what makes a swap free later.

Free downloads happen **before** the checkpoint. The human reviews real files, not URLs.

### 6. Check variety

```bash
python3 $SKILL/still-bank/scripts/check-variety.py \
  --bank-root $BANK \
  --out $OUT/$SLUG-still-bank-variety-report.md
```

Exit 1 means a repeat: the same image landed in two slots. That breaks the no-repeats
rule. Swap one of the pair for a sibling candidate, or run its alternate query, then
re-run the check until it exits 0.

Advisories are judgment calls: overlapping frames, stills too dark or too flat to read,
and beats where three stills share a dominant colour. Fix what will show at reel speed.

### 7. Build the outputs

```bash
python3 $SKILL/still-bank/scripts/build-bank-outputs.py \
  --shot-brief $OUT/$SLUG-shot-brief.json \
  --bank-root $BANK \
  --search-plan $CONF/$SLUG-still-bank-search-plan.json \
  --picks $CONF/$SLUG-picks.json \
  --out $OUT --write-manifest
```

`--picks` is optional: `{"shot-13": "b"}` overrides the default first candidate.
`--write-manifest` writes a full manifest only when none exists; it never overwrites one.
When a manifest is already there, merge the rows from
`$SLUG-still-bank-manifest-rows.md` by hand.

Then write `$OUT/$SLUG-still-bank-sourcing-log.md`: date, method mix, rate-limit notes,
and any still you know is weak so the next person does not re-find the problem.

### 8. Build the editor's Finder folder

The bank is laid out for agents. The editor works from Finder beside Final Cut, so every
delivery also gets a clean copy on the Desktop: one numbered folder per beat, images only,
`PICK_` on the stills you recommend, and a labelled `00-PREVIEW.jpg` of everything.

```bash
python3 $SKILL/still-bank/scripts/build-editor-folder.py \
  --bank-root $BANK \
  --dest ~/Desktop/[short-slug]-stills \
  --pick [image-stem] --pick [image-stem] \
  --open
```

It copies, never moves, so the bank paths stay valid. `--replace` rebuilds a folder it made
earlier and refuses any folder it didn't make. Re-run it after any swap in the bank.

### 9. Checkpoint — stop here

Stage 03 is a human checkpoint and asset spend is gated behind it. Present:

- **The Desktop folder first**, already open in Finder, with counts per beat and what is
  marked `PICK_`. Then the bank path for the system.
- The variety report: repeats at zero, advisories named.
- Coverage: which slots are `ready`, which are `needs-source`.
- The generation queue with its cost, and why tiers 1-3 cannot serve those slots.
- Rights risks: any Commons row missing creator or licence.

Then stop and wait. Do not generate, license, or buy anything before approval.

## After approval

1. Generate only approved rows. Load `../magnific-generation/SKILL.md` first.
2. Record prompt, tool, date, and approval on every generated row before it goes `ready`.
3. Promote reusable stills into the media library with
   `../../../../libraries/media/shared/asset-record-format.md`, and add the pack
   to the Still Bank table in `assets/index.md`.
4. Add the approved map, manifest, and library record pointers to the production job's asset artifact.

## Outputs

See `references/bank-output-format.md` for shapes. Summary:

- Raw stills: `libraries/media/local-media/still-bank/[slug]/[beat]/` — Gitignored
- Editor folder: `~/Desktop/[short-slug]-stills/` — clean copy for Finder and Final Cut
- Map, inventory, variety report, manifest rows, sourcing log: stage 03 output
- Asset manifest: `stages/03-asset-gathering/output/[slug]-asset-manifest.md`

## Rules

- Check the media library before any search. Every time.
- No still repeats inside an edition. The variety report is the check, not a vibe.
- Every still must read in under one second at reel speed.
- Search for the work, not the person.
- No museum display cases, plaques, or framed-artifact shots.
- Overshoot 3x. Forty finals means roughly 120 candidates.
- Free sources download before the checkpoint. Generation waits for approval.
- Hook panels: one dominant colour each, or the 2x2 reads as mush.
- Deliver four hook panels. The 2x2 is assembled in Final Cut, not here.
- Raw media stays in ignored local-only paths. Never commit stills.
- Wikimedia thumbnails: allowed widths only, or the URL 404s.
- Markdown tracks the run. JSON is script I/O, not a status ledger.
- Never hand over only a repo path. Every delivery ends with the Desktop editor folder open
  in Finder.

## Command reference

| Script | Purpose |
|---|---|
| `scripts/parse-shot-brief.py` | Locked script to structured 44-slot brief |
| `scripts/build-search-configs.py` | Validate the query plan, write media-sourcing configs |
| `scripts/check-variety.py` | Repeats, dark/flat frames, colour clustering |
| `scripts/build-bank-outputs.py` | Map, on-disk inventory, asset-manifest rows |
| `scripts/build-editor-folder.py` | Clean Desktop copy by beat for Finder and Final Cut |
| `scripts/test_still_bank.py` | `python3 -m unittest discover -s scripts` |
