# Query Patterns

How to turn one shot brief into search queries that return stills you can cut.

Read this before writing the query plan. The scripts validate the plan; they do not
write it. Query writing is the judgment part of this skill.

## The bar every still has to clear

A still is on screen for 1.3 to 2 seconds, behind a talking head, at reel speed.

- It must read in under one second.
- One subject. If you have to hunt for the subject, the still is wasted.
- Deep blacks, desaturated mid-tones, warm accents. Graded for contrast and mood.
- High-contrast cinematic colour. Not black and white.

## Route the brief before you write the query

| The brief is | Method | Why |
|---|---|---|
| A named person, film, or news moment | `web-still` | Pexels will miss. Find one direct image URL |
| Mood, object, place, plate | `pexels` | Theatres, desks, hallways, hands, rooms |
| A named subject with a deep free archive | `commons` | Category crawl returns far more than keyword search |
| Already in the media library | `library-reuse` | Check repository path `libraries/media/assets/index.md` first, every time |
| Cannot exist as a photograph | `generation` | Last resort. Needs a reason and the checkpoint |

## Query rules

**Search for the work, not the person.** A director at a monitor beats a portrait of a
director. A crew on location beats a headshot. The brief is almost always an action.

**One subject per query.** Two subjects returns neither.

**Add one light or framing word.** `backlit`, `silhouette`, `overhead`, `low angle`,
`dark room`, `single lamp`, `screen glow`. This is what separates a gradeable still from
a bright stock photo.

**Say the frame, not the feeling.** "Empty director's chair on a lit set" is a query.
"Loneliness of creative work" is not.

**Never search for these.** They come back as dead frames:

- Museum display cases, vitrines, plaques, framed artifacts
- Award ceremonies and red carpets, when you wanted the work
- Posed group photos with everyone facing the camera
- Anything with readable third-party titles, logos, or UI

## Three queries per brief

The scripts require at least three. They are not three tries at the same thing.

1. **Primary** — the brief, said plainly, with a light word. This one downloads.
2. **Angle change** — same subject, different framing or distance.
3. **Safety** — the generic plate that will definitely return something usable.

Only the primary runs on the first pass. Two and three are the swap pool when the
variety report flags a slot.

## Hook panels

Four panels become one 2x2 grid. They are judged together, not separately.

- One dominant colour per panel. Four panels, four colours.
- Same subject family across all four, so the grid reads as one idea.
- If two panels share a colour the grid reads as mush. The variety report flags this.

## Wikimedia thumbnails

Use allowed thumb widths only, or the URL 404s:

`120, 250, 330, 500, 960, 1280, 1920, 3840`

Commons rate-limits hard. Keep `--sleep` at 2s or higher. When keyword search
under-returns for a named subject, crawl the category instead — it is usually the
difference between a handful of files and over a hundred.

## Worked examples

From a movie-themed edition:

| Slot | Brief | Method | Primary query |
|---|---|---|---|
| shot-01 | Dark theater from behind, one viewer, screen glow | pexels | `dark cinema audience from behind screen glow` |
| shot-13 | Overhead, printed pages spread across a floor | pexels | `overhead printed pages scattered on floor` |
| shot-33 | Full film crew on location, 20+ people, cables, rigs | web-still | `film crew on location set rigs cables wide` |
| shot-35 | Scoring stage, orchestra, conductor | commons | `Category:Film scoring` |
| shot-40 | Cursor blinking on an empty page | pexels | `blank document cursor dark screen close up` |

Note shot-33: the brief is the work — a crew working — not a named person. It still
routes to `web-still` because real film sets are press and publicity photography, not
stock.
