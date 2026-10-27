# Skills

Reusable methods the workspaces and libraries call.

## Source Of Truth

- This file routes agents to skills.
- `registry.yml` lists every shipped skill with its owner and license.

Do not load the whole folder. Read this index, pick the smallest matching `SKILL.md`, then open only the files that skill asks for.

## Skills

| Skill | Path | Called by |
|---|---|---|
| Reference intake | `swipe-engine/reference-intake/SKILL.md` | Swipe Engine stage 01: acquire and normalize a reference |
| Copywriting | `ai-capabilities/sales-marketing/copywriting/SKILL.md` | Copywriting stages 01 and 02 |
| Motion graphic design | `ai-capabilities/design/motion-graphic-design/SKILL.md` | Video Production motion-graphics jobs, stage 02 |
| Media sourcing | `workflows/video-production/media-sourcing/SKILL.md` | Video Production stage 03, Media Library: footage, stills, music, SFX, reference clips |
| Still bank | `workflows/video-production/still-bank/SKILL.md` | Video Production stage 03: a whole still bank from a numbered shot brief |
| Audio rip | `workflows/video-production/audio-rip/SKILL.md` | Video Production stages 03 and 05: temp or cleared audio and stems |
| Sound effects mix | `workflows/video-production/sound-effects-mix/SKILL.md` | Video Production stages 03 to 05: SFX maps, sourcing, mix notes |
| ElevenLabs voiceover | `workflows/video-production/elevenlabs-voiceover/SKILL.md` | Video Production stages 03 and 05: voice criteria and tagged VO scripts |
| Magnific generation | `workflows/video-production/magnific-generation/SKILL.md` | Video Production stage 03, Media Library: credit-safe AI clips and visual hooks |

Paid steps say so first. Magnific and ElevenLabs use credits. Stage 03 shows the cost and waits for approval before it spends.

## Adding A Skill

1. Check this file and `registry.yml` first.
2. Make one folder with `SKILL.md` plus only the `scripts/`, `references/`, or `assets/` it needs.
3. Add frontmatter: `name`, `description`, and `license`.
4. Add a `registry.yml` entry with owner and license.
5. Add a row to the table above.

Only add code you wrote, or code with a known license. Keep the upstream license and notice.
