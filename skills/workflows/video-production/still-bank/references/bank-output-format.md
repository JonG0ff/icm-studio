# Bank Output Format

What a still-bank run writes, and where.

## Local files

Raw stills are Gitignored. They live under:

```text
libraries/media/local-media/still-bank/[edition-slug]/
  hook-grid/
  01-[beat]/
  02-[beat]/
  ...
```

One folder per beat, named by `parse-shot-brief.py`. Never a flat dump: at the
checkpoint a human opens a beat folder and has to see that beat's options at once.

## Slot and asset IDs

| Thing | Shape | Example |
|---|---|---|
| Slot | `shot-NN`, global, script order, hook panels last | `shot-13`, `shot-41` |
| Filename (Pexels) | written by `search-pexels-photos.py` | `shot-13_option-2.jpg` |
| Filename (web still) | written by `download-web-still.py` | `shot-13a.jpg` |
| Filename (Commons) | written by `search-commons-categories.py` | `shot-13-commons-001.jpg` |
| Asset ID | `ST-NN` plus an option letter | `ST-13b` |

Option letters are assigned in sorted filename order inside a slot. The filename in the
map is authoritative; the letter is a label.

Alternate-query files carry `-alt1` in the slot (`shot-13-alt1_option-1.jpg`) and still
count as the same slot, so they never register as repeats.

## Tracked outputs

All under `workspaces/video-production/stages/03-asset-gathering/output/`.

| File | Written by | What it is |
|---|---|---|
| `[slug]-shot-brief.json` | `parse-shot-brief.py` | The 44 briefs, parsed from the locked script |
| `[slug]-still-bank-search-plan.json` | `build-search-configs.py` | Routing and queries per slot |
| `[slug]-still-bank-on-disk.json` | `build-bank-outputs.py` | Every candidate on disk |
| `[slug]-still-bank-map.md` | `build-bank-outputs.py` | Human map, one table per beat |
| `[slug]-still-bank-variety-report.md` | `check-variety.py` | Repeats, dark/flat frames, colour clustering |
| `[slug]-still-bank-manifest-rows.md` | `build-bank-outputs.py` | Rows to merge into the asset manifest |
| `[slug]-still-bank-sourcing-log.md` | you | What happened, method mix, known-weak stills |
| `[slug]-asset-manifest.md` | you (or `--write-manifest`) | The canonical asset record |

JSON is script I/O. Job state lives in Markdown — the map, manifest, and sourcing log
under the production workspace. Do not add a status field to JSON and treat it as a ledger.

## Map columns

```text
| ID | Brief | Search query | Method | Source URL | Local path | Pick |
```

One table per beat. Every candidate gets a row. The pick is marked, and the rest stay on
disk as the swap pool.

## Manifest rows

The manifest carries the picks only — 40 body stills plus 4 hook panels. The overshoot
lives in the map and the Fallback column.

```text
| Asset ID | Scene/Beat | Type | Need | Library ID | Source path/URL/prompt | Status | Rights note | Fallback | Next action |
```

Type is `still`, or `generated-image` for an approved generation row.

## Status and rights by method

| Method | Rights note | Status |
|---|---|---|
| Pexels | `licensed` — Pexels License, source page and photographer recorded | `ready` |
| Web still | `unclear` — source URL recorded, file on disk cuts in FCP | `ready` |
| Wikimedia Commons | `public` — only with file page, creator, licence, licence URL, attribution | `ready`, else `needs-approval` |
| Media library reuse | carried from the record | `ready` |
| Generation | `generated` — needs prompt, tool, date, approval | `queued-generation` |
| Nothing on disk | `pending` | `needs-source` |

This splits rights by method. An earlier bank marked every row `unclear`,
including Pexels. Method-specific notes are what the manifest format and the
`media-sourcing` skill already ask for.
