# Persona Profiles

The writing and behavior reference for a recurring character. Load it before outlining or reviewing a script.

## Ownership

| Record | Owns |
|---|---|
| Persona profile | Identity, motivations, dialogue, reactions, relationships, boundaries, examples |
| Character entry | Look, rig, poses, expressions, animation limits, persona and voice pointers |
| Voice entry | Audible sound, voice ID, model, settings, tested tags, reference audio |
| Run script and consistency review | This story's dialogue, arc, profile revisions, approved deviations |

One persona can have several visual versions. Link each character entry to the same profile. Do not copy its writing rules into every rig or voice entry.

## Paths and Lifecycle

- Workshop draft: `stages/workshop/01-concept/output/[character-slug]/persona.md`.
- Canonical profile: `library/personas/[persona-slug].md`, linked from the approved character entry.
- A profile is a companion to a character, not a new library piece type. Find it through the character entry; no separate index row is needed.
- Workshop 01 drafts it. Workshop 02 refines it. Test and script notes supply evidence. Workshop 05 publishes it with the character after sign-off.
- A shared rig can have one profile with named variants. Split the profiles when the variants acquire distinct identities or speaking styles.
- Consolidating existing approved material keeps its approval source. Label extrapolated traits and new example lines `proposed`; they are not established canon.
- Revisions that change canon go through workshop 05. Increment `revision` when published content changes, and record what changed and the approval source.
- Do not change a locked script when its profile changes. Record which revision that run used. Apply later revisions to new or explicitly revised scripts.

## Profile Template

```markdown
# [persona-slug] persona
kind: fictional
status: draft | approved | archived
revision: 1
updated: YYYY-MM-DD
approval source: [decision or approved source; pending for drafts]
character: [character entry or workshop concept link]
voice: [voice entry or workshop voice-design link; none for silent characters]

## Sources

- [Source link]: what it establishes. Distinguish owner notes, approved scripts, and proposals.

## Identity

- Role, self-image, and the story function. Record known facts; leave unknown history open.

## Worldview and Motivation

- What they want, believe, fear, and misunderstand. What creates recurring conflict?

## Speaking Style

- Vocabulary, sentence shape, slang, profanity, recurring habits, and humor.
- Silent characters: say so. Describe physical communication instead; do not invent dialogue.

## Reactions

- How they respond to conflict, embarrassment, success, rejection, or reassurance.
- Define recognizable tendencies, not one emotion that every line must repeat.

## Relationships

- How behavior changes with named cast members or audiences. Leave unknown relationships open.

## Boundaries

- What would break the character, plus established story restrictions.
- A new story can develop the character. Record an approved change rather than silently rewriting canon.

## Reference Examples

- Good: sourced dialogue or silent beats, with why each fits and its approval state.
- Misses: clearly labeled counterexamples, with why they fail. Never treat them as dialogue to reuse.
- Examples show the pattern. Do not paste a catchphrase into every script.

## Performance Link

- Acting intent and voice pointer. Read tested tags and settings from the voice entry.
- Keep descriptive acting notes out of spoken text unless expressed as supported audio tags.

## Open Questions and Proposed Changes

- Missing context or new traits needing a decision. Do not fill gaps with invented permanent lore.
```

This rollout covers fictional characters. A future real-person profile can use the same writing sections, but facts and examples need that person's validation. Cloning remains a separate voice workflow governed by the rights rules; a profile does not authorize it.

## Script Review

Write `character-consistency.md` beside `script.md`:

```markdown
# [run-slug] character consistency

## Cast Sources

| Speaker or silent role | Character | Persona path | Revision | Status / approval source |
|---|---|---|---|---|
| [speaker] | [slug] | [path relative to this file] | [revision] | [source] |

## Review

| Character | Dialogue / physical behavior | Motivation and reactions | Relationships and boundaries | Result |
|---|---|---|---|---|
| [slug] | [line IDs or beats and evidence] | [evidence] | [evidence] | pass / needs decision |

## Deviations and Decisions

- [Line ID or beat]: conflict, proposed resolution, and explicit owner decision if supplied.
- Write `None` when there are no deviations.
```

- Check vocabulary, motivation, emotional progression, relationships, and behavior, including silent roles.
- Use specific line IDs or beats. Mark unknown traits as open; do not invent them to produce a pass.
- Brought scripts get the same review. Preserve their wording and beats; surface conflicts before lock.
- Approved temporary deviations belong to the run review. Permanent changes belong to a profile revision.
- Profiles and review headings are local context. The voice generator receives only its supported request fields, including spoken text and inline audio tags.
