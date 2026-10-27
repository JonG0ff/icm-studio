# Workshop 02: Design Sheet

Turn the concept into the piece's design: views, palette and silhouette, or a voice design.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-concept/output/[slug]/concept.md` | Full | What to design |
| Previous stage | `../01-concept/output/[slug]/persona.md` | Full, characters only | Identity and behavior to express in the design |
| User | `../../../input/[slug]/` | Art files, only if brought | Art made in another tool |
| Shared | `../../../shared/bring-intake.md` | Full, only if a file was brought | Ingest steps |
| Shared | `../../../shared/looks.md` | "Technique Families" | Build technique |
| Library | `../../../library/entries/look/[look].md` | Full. Looks: the concept's feasibility read instead. | Style rules and technique |
| Shared | `../../../shared/library-spec-format.md` | The piece type's section | Required views and fields |
| Skill | `../../../../../skills/workflows/video-production/magnific-generation/SKILL.md` | Index | Roughs only, characters and sets |
| Skill | `../../../../../skills/workflows/video-production/elevenlabs-voiceover/SKILL.md` | Voice criteria section | Voice type only |

## Process

0. If art was brought, follow bring intake, then check it against the look and skip to step 4.
1. Pick the sheet for the type:
   - look: style sheet (palette, line weight, texture, motion rules) built from the concept's style read. Hang the reference images beside it.
   - character: front and three-quarter views, palette, silhouette. Link to the concept's persona draft; refine that same file as choices are made, without copying it into the design sheet.
   - set: layout sheet with spots and broadcast graphics.
   - prop: prop sheet with grip points.
   - voice: voice design (ElevenLabs voice ID shortlist, settings, character fit).
2. Make 2-3 roughs. AI roughs are allowed. They never ship as is.
3. Build the clean version with the look's technique family: SVG for a vector rig, paths for procedural line, sprites for pixel, PNG layers for cutouts, shaders for texture, a Three.js scene for 3D.
4. Render one still of the sheet at phone size.
5. Save to `output/[slug]/`.

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|------------|---------------|---------------|------|
| 2 | Roughs side by side | Which direction to clean up | Taste |
| 4 | Clean sheet still. Looks: next to 3 reference images, with a re-graded feasibility if the still changed it. | On-model and fits the look, or redo | Taste |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Required views | Every view or field the type needs is present |
| Palette | Colors come from the look's palette only |
| Silhouette | Reads at phone size in solid black |
| Rights | No traced or copied reference art |
| Persona fit | Characters: expressions and poses support the persona's reactions; new traits remain marked as proposals |
| Honest re-grade | Looks: if the still is weaker than the feasibility read predicted, the grade is lowered and the person told |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Design sheet | `output/[slug]/design-sheet.md` | Views list, palette, notes, file list |
| Art files | `output/[slug]/` | Clean art in the look's technique, plus the sheet still |
