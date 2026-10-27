# Voice Criteria Dimensions

Filter axes for ElevenLabs Voice Library search. Output criteria, not voice IDs. Voices are added and removed over time; these dimensions stay stable across projects.

## How to use

1. Read the locked script, the marketing spec, and brand voice rules.
2. Fill one row per dimension in the output artifact.
3. Add 3–5 plain-language search phrases the human can type into Voice Library.
4. When the human shares a chosen voice back, audit against this table.

## Dimensions

| Dimension | Options | Notes |
|-----------|---------|-------|
| Gender presentation | male / female / androgynous / no preference | Match narrator POV and audience expectation from brief |
| Perceived age | young adult (20s) / mid (30s–50s) / mature (50s+) / elder | Avoid teen/youthful for authority pieces; avoid elder unless story calls for it |
| Accent / locale | General American / British RP / Australian / neutral international / other | Default to audience locale unless story is region-specific |
| Pace | measured / conversational / brisk | From spec delivery notes and swipe audio patterns |
| Energy | low / medium-low / medium / high | Low–medium for documentary; medium for explainer; high only when spec explicitly wants hype (rare for brand marketing VO) |
| Register | documentary narrator / direct-address coach / warm explainer / authoritative founder / news anchor / conversational peer | One primary register; note if POV shifts mid-script |
| Emotional range | stable neutral / moderate expression / highly expressive | Drives v3 stability setting and tag density |
| POV fit | third-person story narrator / second-person direct address / mixed | Flag beats where POV shifts (e.g. story → viewer bridge) |
| v3 suitability | prefer v3-compatible premade or IVC | PVC clones are less reliable on v3 |
| Avoid | free text | Explicit anti-criteria from brand voice and spec |

## v3 stability recommendation

| Tag density | Emotional range | Recommended stability |
|-------------|-----------------|----------------------|
| Light (1 tag per 60+ words) | Stable neutral | Robust or Natural |
| Moderate (1 tag per beat) | Moderate expression | Natural |
| Heavy (multiple shifts per beat) | Highly expressive | Creative or Natural |

Robust resists directional prompts. Creative is more expressive but less consistent. Natural is the default for most short-form marketing VO.

## Search phrase patterns

Combine 2–4 traits into plain-language phrases for Voice Library search:

- `[pace] [gender] [register] [accent]` — e.g. "calm male narrator american documentary"
- `[energy] [register] [locale]` — e.g. "measured british storyteller"
- `[avoid inverse] [register]` — e.g. "serious not upbeat corporate narrator"

Write 3–5 phrases. Vary wording so the human can try different filter combinations.

## Deriving criteria from specs

| Spec signal | Criteria implication |
|-------------|---------------------|
| "Calm, measured voiceover" | Pace: measured. Energy: low–medium. Register: documentary narrator |
| "Single speaker energy" | One voice. Avoid multi-character or dialogue voices |
| Second-person direct address in final beats | POV: mixed. Register must handle direct address without preachy tone |
| Brand voice: blunt, self-assured, no hype | Avoid: sales announcer, upbeat influencer, cartoonish |
| Brand voice: not performative | Avoid: credential-heavy, overly warm coach, ASMR whisper |
| Swipe reference: sparse text, message-led | Energy stays low; voice carries the reel |
| Runtime 45–60s short-form | Conversational pace OK but not rushed; room for beat pauses |
| Constraints.Audio: voiceover-driven | VO is primary; voice must be clear at -16 LUFS dialogue target |

## Avoid list patterns

Pull explicit avoids from brand `voice-rules.md` **What The Voice Is Not** section. Common short-form avoids:

- Hype announcer / infomercial energy
- Upbeat influencer / TikTok hype voice
- Cartoonish or mascot comedy delivery
- ASMR whisper or breathy intimacy (unless spec asks)
- Generic SaaS explainer monotone
- Overly performative "motivational speaker" cadence
- Sales close / hard CTA delivery

## Validation checklist

When the human shares a voice choice, score each dimension:

| Dimension | Match | Notes |
|-----------|-------|-------|
| Gender presentation | yes / partial / no | |
| Perceived age | yes / partial / no | |
| Accent / locale | yes / partial / no | |
| Pace | yes / partial / no | |
| Energy | yes / partial / no | |
| Register | yes / partial / no | |
| Avoid list | clear / borderline / fails | |
| Tag compatibility | yes / partial / no | |
| POV fit | yes / partial / no | |

**PASS:** all core dimensions yes or acceptable partial with reason.
**PASS WITH NOTES:** one partial that does not block production.
**FAIL:** any core dimension fails or avoid list is borderline/fails.
