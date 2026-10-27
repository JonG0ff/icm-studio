# Production 02: Script

Write the dialogue with a speaker on every line, plus hook variants if the format asks. Or bring a script.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-brief/output/[slug]/brief.md` | Full | Idea, cast, format |
| User | `../../../input/[slug]/script.md` | Full, only if brought | A brought script |
| Shared | `../../../shared/bring-intake.md` | Full, only if a file was brought | Ingest steps |
| Shared | `../../../shared/script-format.md` | Full | Line IDs and speaker tags |
| Shared | `../../../shared/formats/[format].md` | "Structure", "Hook Rules", "Writing Rules" | Shape of the script |
| Shared | `../../../shared/staging-limits.md` | Full | Don't write what can't be animated |
| Shared | `../../../shared/persona-profile-format.md` | "Script Review" | The consistency check and source record |
| Library | `../../../library/entries/character/[slug].md` | "Persona", "Voice", "Can't do", for the brief's cast only | Find the writing profile and animation limits |
| Library | `../../../library/personas/[persona-slug].md` | Full, following the cast's character pointers, including silent roles | Identity, dialogue, reactions, relationships, and examples |
| Brand | `../../../../../libraries/business-memory/brand-vault/brands/{{BRAND_SLUG}}/identity.md` | Core Principles and Brand Lines (or the brand's voice rules when present) | Brand voice |
| SOP | `../../../../../libraries/business-memory/sops/reel-hook-design.md` | Full, only if variants > 1 | Hook craft |
| Skill | `../../../../../skills/workflows/video-production/elevenlabs-voiceover/SKILL.md` | Tag rules | Audio tags in lines |

## Process

0. Load each cast member's persona profile before writing or reviewing. Record the path, revision, and approval source in `character-consistency.md`. If one is missing, route to the character workshop for a sourced profile. If an existing run has an explicit workshop-use exception, cite that decision and its draft profile; do not call it approved library content.
1. If a script was brought, follow bring intake and skip to step 6. Preserve its wording and story beats.
2. Outline the sections from the format's structure. One line per beat. Use the characters' motivations and relationships to drive the conflict.
3. Write the body. Every line gets an ID and a speaker. Follow each persona's vocabulary and sentence habits without repeating its reference examples by default.
4. Write hook variants (`h1-*`, `h2-*` ...) if the format asks.
5. Punch-up pass: cut words, sharpen the button, check a joke lands every 5-8 seconds.
6. Check dialogue and silent behavior against each persona. Write line IDs or beat evidence in `character-consistency.md`. Flag conflicts in brought scripts without silently rewriting them. Record approved deviations; permanent changes go through a profile revision in the workshop.
7. Read it at 160 words per minute and check the length against the format. Present unresolved persona conflicts with the full script before lock.
8. Save `script.md` and `character-consistency.md` to `output/[slug]/`. Script lock requires each conflict to be resolved or explicitly accepted by the owner.

## Checkpoints

| After Step | Agent Presents | Human Decides | Kind |
|------------|---------------|---------------|------|
| 2 | Beat outline | The shape of the bit | Taste |
| 7 | Full script with estimated length and character consistency review | Lock, rewrite lines, or explicitly accept a named deviation | Taste, plan |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Line shape | Every spoken line matches `script-format.md` |
| Speakers | Every speaker is in the brief's cast |
| Persona sources | Every cast member, including silent roles, has a profile path and revision; any workshop-use exception cites its owner decision |
| Character consistency | Dialogue, reactions, relationships, and silent beats fit the profiles; every deviation is resolved or has an explicit owner decision |
| Length | Estimated length is within the format's range |
| Hooks | Hook variant count matches the brief |
| Staging | No action outside `staging-limits.md` without its workaround |
| Style | No em dashes |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Script | `output/[slug]/script.md` | Per `script-format.md` |
| Character consistency | `output/[slug]/character-consistency.md` | Per `persona-profile-format.md`; sources, revisions, checks, and decisions |
