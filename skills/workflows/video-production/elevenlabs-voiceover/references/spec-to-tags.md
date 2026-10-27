# Spec to Tags Mapping

Rules for annotating a locked voiceover script with Eleven v3 audio tags using the locked script beat map.

## Inputs

From `[slug]-production-spec.md`:

- **Locked Voiceover Script** — copy to annotate (verbatim)
- **Beat Map** — beat name, time range, narration, viewer takeaway
- Delivery notes above the script (e.g. "Read calmly and measured, with natural pauses at the end of beats")

From upstream brief and spec:

- Audio constraints (voiceover-driven, calm, etc.)
- Narrator POV (second person, third person, mixed)
- Swipe audio patterns (measured, single speaker)

## Mapping rules

### 1. One tag per beat, not per sentence

Each beat in the Beat Map gets one opening tag at the first narration line of that beat. Short fragment lines within the same beat inherit the tag.

Example beat groupings for fragment-style scripts:

| Beat | Lines grouped under one tag |
|------|----------------------------|
| Hook | "Your morning coffee can taste better." |
| Setup | "Start with fresh beans." + "Weigh one serving." |
| Setup | "Heat the water and let it settle." |
| Middle | "Pour slowly over the grounds." |
| Middle | "Give the coffee time to bloom." |
| Middle | "Taste it before adding milk." + "Adjust tomorrow." |

### 2. Beat type to tag

| Beat type (from beat name or takeaway) | Primary tag | Secondary options |
|----------------------------------------|-------------|-------------------|
| Hook / setup (story facts) | `[matter-of-fact]` | — |
| Middle (tension, cost) | `[matter-of-fact]` or `[thoughtful]` | `[sighs]` only if beat is emotionally heavy |
| Turn / pivot | `[shift]` | paragraph break before the turn line |
| Reframe (concept reveal) | `[thoughtful]` or `[shift]` | — |
| Bridge (story → viewer) | `[shift]` then `[conversational]` | Split tags only if beat spans distinct POV sections |
| Lift / CTA | `[warm]` or `[pointed]` | `[warm]` for identity lines; `[pointed]` for single hard truths |
| Direct address (second person) | `[conversational]` | — |

### 3. Delivery notes to tags

| Spec delivery note | Tag approach |
|--------------------|--------------|
| "Calm and measured" | `[matter-of-fact]` default; avoid `[excited]` |
| "Natural pauses at end of beats" | Paragraph breaks between beats; `[short pause]` only at major turns |
| "Single speaker energy" | One consistent register; minimal tag variety |
| "Motivational lift" | `[warm]` on final beat, not `[excited]` |
| "Documentary" | `[matter-of-fact]` + `[thoughtful]` on reframe |
| "Direct address to viewer" | `[conversational]` on bridge and lift beats |

### 4. POV shifts

When the script moves from third-person story to second-person viewer:

1. Keep `[matter-of-fact]` through the story beats.
2. Use `[shift]` at the first second-person line ("You're already in the middle...").
3. Use `[conversational]` or `[warm]` for the bridge and lift if the shift tag alone is not enough.

Do not add a new tag for every sentence after the POV shift. One tag per beat still applies.

### 5. Fragment lines

Short declarative fragments ("They laughed." / "It did.") do not need their own tags. They inherit the beat tag and gain impact from paragraph breaks and pacing.

Optional: ellipses before a fragment for weight (`The fourth launch had to work.\n\nIt did.`) — no extra tag needed.

### 6. Brand voice guardrails

Before finalizing tags, check brand voice rules:

- No hype tags on copy that is deliberately blunt
- No `[laughs]` or `[excited]` unless swipe reference or spec explicitly uses humor or high energy
- `[warm]` on CTA must not sound salesy — if the line is identity ("Make something worth keeping"), warm not excited

### 7. PASTE block assembly

1. Copy annotated script into PASTE block between two `---` rules.
2. Add header blockquote: `Model: eleven_v3. Stability: [Natural|Creative|Robust].`
3. Strip beat markers, scene notes, and on-screen text — narration only.
4. Keep tone tags in `[brackets]`.

## Beat-to-tag audit table

Include this table in the output artifact:

| Beat | Time | Tag | Rationale |
|------|------|-----|-----------|
| Hook | 0:00–0:04 | `[matter-of-fact]` | Story setup; calm documentary open |
| ... | ... | ... | ... |

One row per beat from the locked script beat map (skip end card if narration is "None").

## Do not

- Rewrite locked copy while tagging
- Add tags inside brand name or CTA attribution ("— Brand Name")
- Tag the end card beat when narration is none
- Use more than one tag per beat unless POV clearly splits within the beat (rare)
