# Brief Format

Every brief has these fields. A brought brief is mapped onto them; missing fields are flagged, not guessed.

```
# [slug] brief

slug: [lowercase-hyphen-slug]
review: taste
credit-cap: 5000
idea: One sentence.
angle: Why it's funny or useful.
format: skit-short
look: flash-cutout
cast:
  - HOST: [library slug] (voice: [voice slug])
  - GUEST: [library slug] (voice: [voice slug])
set: [library slug]
props: [library slugs, or none]
variants: [number, from the format unless overridden]
length target: [seconds]
references: [selected source pointers, sections, and use/rights limits, optional]
business context: [brand/project, objective, audience, offer/CTA if relevant, optional]
platform and delivery: [destination, aspect ratio, requested versions/captions, optional]
constraints: [must include/avoid, approved claims, rights, deadline, optional]
context gaps: [missing inputs, owner, and next action, optional]
accepted inputs: [brought brief/spec paths and exact prior decisions, optional]
notes: [anything else]
```

## Field Rules

| Field | Rule |
|---|---|
| slug | Lowercase with hyphens. Unique across runs. |
| review | `manual`, `plan`, `taste`, or `auto`. Missing means the workspace default (`taste`). |
| credit-cap | Optional. ElevenLabs credits per run. Missing means 5,000. |
| idea | One sentence. No "and also". |
| cast | Speaker names are UPPER_SNAKE. They become the script's speaker tags. |
| look | One look per video. Every piece must be in that look. |
| variants | 1 means no split test. |
| references | Record selected sections and use limits. Study only unless production rights are separately cleared. |
| business context | Approved facts stay in Business Memory. This brief records job decisions and pointers. |
| optional context | Add only fields relevant to this video. Existing briefs remain valid; never invent approval or reopen accepted locks to fill a new field. |

## Pieces

List every needed piece under a `## pieces` heading (replaces `## gaps`; free notes can follow it):

```
## pieces

| Piece | Type | Source |
|---|---|---|
| lead-host | character | library |
| suburban-walk-path | set | missing |
| phone | prop | workshop |
```

- `Source` is `library`, `workshop`, or `missing`.
- Old briefs with `## gaps` stay valid. Readers treat them as legacy.
