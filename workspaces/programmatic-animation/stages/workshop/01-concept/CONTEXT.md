# Workshop 01: Concept

Pin down one piece: its type, its look, and what it must be able to do.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User | Chat, or `../../../input/[slug]/concept.md` | Full | The piece idea, or a brought concept |
| Production | `../../production/01-brief/output/[run-slug]/brief.md` | Story beats for this piece, only when started as a detour from production | Beats the piece must serve in the run |
| Shared | `../../../shared/bring-intake.md` | Full, only if a file was brought | Ingest steps |
| Shared | `../../../shared/looks.md` | "Rules for All Looks". Looks: also "Where a Look Comes From" and "Technique Families". | Fit the look |
| Shared | `../../../shared/style-feasibility.md` | Full, looks only | The honest feasibility read |
| Swipe engine | `../../../../../libraries/swipes/knowledge-layer/index.md` | Entries tagged `style-[slug]`, looks only, then those entries and their images | The reference images |
| Shared | `../../../shared/library-spec-format.md` | The piece type's section | Know what the piece must end up with |
| Shared | `../../../shared/persona-profile-format.md` | Full, characters only | Draft the recurring identity and writing rules |
| Shared | `../../../shared/rights-rules.md` | Full | Original work only |
| Shared | `../../../shared/staging-limits.md` | Full, characters and props only | The can't-do list |
| Library | `../../../library/index.md` | Rows for the chosen look. Looks: all `look` rows. | Avoid near duplicates |

## Process

0. If a file was brought, follow bring intake, add a `workshop` row to `../../../library/index.md` if not present, and skip to the audit.
1. Restate the piece: type (look, character, set, prop, voice), look, slug. When started as a detour from production, its input is the brief's beats for that piece.
2. Check `../../../library/index.md` for a near duplicate in the same look. Name it if found. On start, add a `workshop` row to `../../../library/index.md` for this piece.
   - Looks: go to "Looks" below for steps 3-7, then save.
3. Write the purpose. Characters: draft `persona.md` from the owner's notes using `persona-profile-format.md`, and link it from the concept. Mark new traits as proposed and unknowns as open. Silent characters still need behavior profiles. Sets and props: what scenes need them.
4. Write the must-do list: actions, expressions, or lines the piece must handle.
5. Characters, sets and props: write the first-use story. List every beat of the first skit or scene the piece is for, in order, using the user's words or the production brief's beats for this piece. Keep every beat named. Never merge or drop one.
6. Write the needs table: for each story beat, the set, props and screens it needs. Mark each one `library` (approved, exists), `stand-in` (built inside the motion test only) or `own run` (needs its own workshop run first).
7. Write the can't-do list from `staging-limits.md` that applies.
8. Save to `output/[slug]/concept.md`.

## Looks

A look starts from reference images, not a description.

1. Find the swipe entries tagged `style-[slug]`. If there are none, or fewer than 3, ask the person for images and save them through `../../../../../libraries/swipes/stages/01-save/CONTEXT.md` first.
2. Open every reference image with the image viewer. Never grade from the entry text alone.
3. Write the style read: one line per trait from `style-feasibility.md`, from what the images show.
4. Write the feasibility read in the format from `style-feasibility.md`. Lead with the hardest trait.
5. Write the must-do list: the 3-5 traits the look test render must show to count as this style.
6. Write the can't-do list from every Out of reach trait.

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|------------|---------------|---------------|------|
| 6 | Type, look, purpose, persona draft for characters, must-do list, first-use story, needs table | Build it, change it, or drop it. Stand-in or own run for each missing set and prop. | Taste |
| Looks 4 | Reference images, style read, feasibility read with the grade and "What you'll see" | Build as is, build the adapted option, or drop it | Taste |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Type and look set | Both present. Look is an approved `look` row in the library, or this run is building the look. Piece has a `workshop` row in `../../../library/index.md`. |
| No duplicate | No approved piece in the same look does the same job |
| Rights | Passes `rights-rules.md`. No real person parodied by name. |
| Must-do list | 3+ items, each testable in the motion test |
| First-use story | Characters, sets, props: every beat the user named is listed, in order |
| Persona | Characters: concept links to a draft profile with source pointers, writing or silence rules, reactions, relationships, boundaries, and reference examples |
| References | Looks: 3+ swipe entries tagged `style-[slug]`, every image opened |
| Feasibility | Looks: every trait graded, hardest trait named, overall grade matches the trait grades per `style-feasibility.md` |
| Needs table | Every story beat has a set. Every set, prop and screen is marked library, stand-in or own run. |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Concept | `output/[slug]/concept.md` | Header (type, look, slug), purpose, must-do list, first-use story, needs table, can't-do list. Looks: header, reference slugs, style read, feasibility read, must-do list, can't-do list. |
| Persona draft | `output/[slug]/persona.md` | Characters only, per `persona-profile-format.md` |
