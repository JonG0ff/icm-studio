# Business Context Questionnaire

Read this file when the user types `setup` in Business Memory or asks to configure reusable business context.

Ask only the questions needed for the current brand or project. These answers configure reusable pointers for missing company, brand, SOP, offer, CTA, and project details.

Do not block downstream workspaces on unanswered questions. If a field is unknown, leave it out or mark it TBD in the approved file only when the user approves that.

### Q1: What brand should this configure?
- Placeholder: `{{BRAND_NAME}}`
- Files: `brand-vault/brands/[brand-slug]/identity.md`, `brand-vault/brands/[brand-slug]/voice-rules.md`
- Type: free text
- Default: none. Ask.
- Start: copy `brand-vault/brands/_template/` to `brand-vault/brands/[brand-slug]/`.
- Derived: `{{BRAND_SLUG}}` from the lowercase, hyphenated brand name.

### Q2: What is the one-sentence brand?
- Placeholder: `{{ONE_SENTENCE_BRAND}}`
- Files: `brand-vault/brands/[brand-slug]/identity.md`
- Type: free text
- Default: none. Ask.

### Q3: Who is the primary audience, what do they care about, and what do they already know?
- Placeholders: `{{TARGET_AUDIENCE}}`, `{{AUDIENCE_CARES_ABOUT}}`, `{{AUDIENCE_KNOWLEDGE_LEVEL}}`
- Files: `brand-vault/brands/[brand-slug]/identity.md`
- Type: free text
- Default: none. Ask.

### Q4: What is the positioning and content mission?
- Placeholders: `{{BRAND_POSITIONING}}`, `{{CONTENT_MISSION}}`
- Files: `brand-vault/brands/[brand-slug]/identity.md`
- Type: free text
- Default: Derive from the one-sentence brand and audience.

### Q5: What is the primary offer and default CTA?
- Placeholders: `{{PRIMARY_OFFERS}}`, `{{DEFAULT_CTA}}`
- Files: `brand-vault/brands/[brand-slug]/identity.md`
- Type: free text
- Default: Primary offer TBD. Default CTA TBD.

### Q6: Give two examples of copy that sounds right.
- Placeholders: `{{VOICE_RIGHT_EXAMPLE_1}}`, `{{VOICE_RIGHT_EXAMPLE_2}}`
- Files: `brand-vault/brands/[brand-slug]/voice-rules.md`
- Type: free text
- Default: Short, specific, concrete examples.

### Q7: Give two examples of copy that sounds wrong.
- Placeholders: `{{VOICE_WRONG_EXAMPLE_1}}`, `{{VOICE_WRONG_EXAMPLE_2}}`
- Files: `brand-vault/brands/[brand-slug]/voice-rules.md`
- Type: free text
- Default: Generic marketing language or abstract summaries.

### Q8: What should this brand never sound like?
- Placeholders: `{{VOICE_HARD_CONSTRAINT_1}}`, `{{VOICE_HARD_CONSTRAINT_2}}`, `{{VOICE_HARD_CONSTRAINT_3}}`, `{{VOICE_PACING_DESCRIPTION}}`, `{{VOICE_ANTI_PATTERN}}`, `{{VOICE_ANTI_PATTERN_DESCRIPTION}}`, `{{VOICE_STRATEGIC_RATIONALE}}`
- Files: `brand-vault/brands/[brand-slug]/voice-rules.md`
- Type: free text
- Default: No hype, no filler, no performative expertise.

### Q9: What visual defaults should apply?
- Placeholders: `{{PRIMARY_COLOR}}`, `{{ACCENT_COLOR}}`, `{{BACKGROUND_COLOR}}`, `{{TEXT_COLOR}}`, `{{TEXT_MUTED_COLOR}}`, `{{FONT_HEADING}}`, `{{FONT_BODY}}`
- Files: `brand-vault/tokens.md`, `brand-vault/themes/default.md`
- Type: free text
- Default: Keep current placeholders if unknown.

## After Onboarding

Create or update the brand folder under `brand-vault/brands/[brand-slug]/`. For a new brand, start from a copy of `brand-vault/brands/_template/`.

Add the brand to the Brand Routing table in `brand-vault/CONTEXT.md`.

Then scan the configured brand files for remaining `{{` placeholders. If any remain, ask only for the missing values needed now.

Do not write raw brainstorms, swiped references, or unapproved planning artifacts into Business Memory.
