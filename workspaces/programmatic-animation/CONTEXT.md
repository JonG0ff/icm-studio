# Programmatic Animation

Two lanes: the workshop builds approved pieces, the production line makes videos from them.

This is a specialized production workflow using the shared Remotion runtime. Route by the deliverable and production recipe. Footage editing, repurposing, and mixed-media jobs start in `../video-production/`; using Remotion alone does not route them here.

## Task Routing

Routing tables are maps, not gates.

| Task Type | Go To | Description |
|-----------|-------|-------------|
| Brief | `stages/production/01-brief/CONTEXT.md` | Idea, format, look, cast, set |
| Script | `stages/production/02-script/CONTEXT.md` | Speaker-tagged lines and hooks |
| Voice | `stages/production/03-voice/CONTEXT.md` | One audio file per line |
| Timing | `stages/production/04-timing/CONTEXT.md` | Word times per speaker |
| Blocking | `stages/production/05-blocking/CONTEXT.md` | Cues: set, cast, camera, SFX, holds |
| Scene | `stages/production/06-scene/CONTEXT.md` | Remotion composition and contact sheet |
| Render | `stages/production/07-render/CONTEXT.md` | mp4 per variant and manifest |
| Missing piece | `stages/workshop/01-concept/CONTEXT.md` | Workshop subagent detour from the brief's beats |
| Piece concept | `stages/workshop/01-concept/CONTEXT.md` | Type, look, purpose for one piece |
| Design sheet | `stages/workshop/02-design-sheet/CONTEXT.md` | Views, palette, silhouette, or voice design |
| Rig | `stages/workshop/03-rig/CONTEXT.md` | Parts, pivots, mouths, poses in code |
| Motion test | `stages/workshop/04-motion-test/CONTEXT.md` | Approved test plan, then test render and contact sheet. Optional for characters, sets and props. |
| Approve | `stages/workshop/05-approve/CONTEXT.md` | Sign off and add to the library |

## Shared Resources

| Resource | Location | Contains |
|----------|----------|----------|
| Library | `library/CONTEXT.md` | Approved pieces and how to load them |
| Formats | `shared/formats/CONTEXT.md` | One recipe per video format |
| Looks | `shared/looks.md` | How a look is made from references, technique families, filters, look test |
| Style feasibility | `shared/style-feasibility.md` | Honest grading of a reference style, calibration log |
| Script format | `shared/script-format.md` | Line IDs, speaker tags, hook variants |
| Blocking cues | `shared/cue-grammar.md` | How `stages/production/05-blocking/output/[slug]/cues.md` is written |
| Bring intake | `shared/bring-intake.md` | How to ingest a file you bring |
| Library spec format | `shared/library-spec-format.md` | What each piece type must have |
| Persona profiles | `shared/persona-profile-format.md` | Character writing, behavior, lifecycle, and script consistency review |
| Rights rules | `shared/rights-rules.md` | Original work, no real voices, no reposts |
| Contact sheets | `shared/contact-sheets.md` | How Claude reviews its own frames |
| Platform specs | `shared/platform-specs.md` | Size, fps, length per platform |
| Tool setup | `shared/tool-setup.md` | ElevenLabs key, Whisper, ffmpeg, Node |
| Remotion skill | `remotion-best-practices`, installed from Remotion (see `../../remotion/README.md`) | Remotion APIs |
| Voice generation skill | `../../skills/workflows/video-production/elevenlabs-voice-generation/SKILL.md` | ElevenLabs per-line audio |
| Word timing skill | `../../skills/workflows/video-production/word-timing/SKILL.md` | Word times, Whisper fallback |
