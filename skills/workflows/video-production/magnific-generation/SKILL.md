---
name: magnific-generation
description: Generate short-form video clips, still frames, and visual hooks in Magnific without wasting credits. Use when a scene plan or split-test cell needs AI-generated footage, AI UGC performance clips, visual hook clips, product/metaphor shots, or storyboarded body sequences, and when choosing between Magnific models, Variations, Storyboard, voiceover, and lip-sync.
license: MIT
---

# Magnific Generation

Produce generated clips for short-form video without burning credits on work that could have been free.

Use this skill when the asset manifest calls for generated footage. Use `media-sourcing` first when stock or real footage would do the job. Use `elevenlabs-voiceover` for voice, not Magnific audio.

## The Credit Rule

> Unlimited in the Magnific app or a Magnific agent does not mean free through the MCP.

**Every MCP action consumes credits, including models that are unlimited in the app.** Generate in the Magnific app or a custom Magnific agent. Reserve the MCP for cases where the chat integration is genuinely worth paying for.

MCP actions that do not cost credits: checking balance, browsing existing creations, rendering past work in chat.

## Free On Plans With Unlimited Models

The tables below describe the Premium+ plan as of October 2026. Check your own plan and the vendor's current docs before you plan a batch. Stock downloads are capped per day and do not consume credits.

| Category | Free in app or agent |
|---|---|
| Image models | Auto, Classic, Flux.1 / 1.1 / 2 Klein / 2 Pro, GPT, Imagen 3 and 4, Nano Banana and Banana 2, Grok, Ideogram, Mystic 1.0 through 2.5, Recraft V4, Seedream 4 / 4.5 / 5 Lite, Z-Image |
| Video models | Kling 2.5 720p, Minimax Hailuo 2.3 768p, Wan 2.2 480p, Seedance 1.5 Pro draft mode |
| Editing | Auto, Qwen Edit, Seedream inpaint/outpaint/variations, Flux.2 re-render and restyle, Nano Banana edits, Sketch to Image, SVG export |
| Planning | AI Assistant, and agent Brainstorm mode |

Still costs credits: Kling 3.0, Seedance 2.0, Veo 3.1, higher resolutions, longer durations, upscalers, all audio tools, custom character/object/style training, new early-access models, and anything through the MCP.

## Video Credit Rates

| Model | Resolution | Credits/sec |
|---|---:|---:|
| Kling 2.5 | 720p | Free on plans with unlimited models |
| Kling 2.6 | 1080p | 45 |
| Kling 2.5 | 1080p | 65 |
| Kling 3.0 | 720p | 70 |
| Kling 3.0 | 1080p | 90 |
| Veo 3.1 Fast | 720p/1080p | 100 |
| Veo 3.1 | 720p/1080p | 200 |
| Seedance 2.0 | 1080p | 280 |

## The Default Path

```text
Plan in Brainstorm mode          (0 credits)
→ still frames, unlimited image model   (0 credits)
→ Variations for angles and expressions (0 credits)
→ Kling 2.5 720p motion test            (0 credits)
→ select winners
→ Kling 2.6 1080p final                 (45/sec)
```

Iterate for free. Pay only for approved finals.

Do not pay for an upscale when Kling 2.6 already produces a clean native 1080p. Use an upscaler only when the source is visibly soft.

## Keep Generated Clips Silent

The default is silent footage. Add VO, subtitles, music, and SFX in Final Cut Pro.

Silent clips are modular. The same visual supports many scripts, text hooks, VO takes, and edits, which is the whole point of a reusable bank.

Use model audio only when all of these are true: it adds no credit cost, it is genuinely useful for that shot, it saves editing time, and it survives the final mix. Otherwise skip it.

## Voiceover Versus Re-Lipping

These are two different operations with very different costs.

**Add VO without re-lipping.** Silent video → Voiceover node → Video Audio Mix. Adds audio without regenerating video. This is the default.

**Re-lip a clip.** Silent video → voiceover audio → lip-sync or Speak operation. This is an AI video transformation and consumes separate credits, roughly 100–500+ depending on duration and settings, with Speak listed around 400. For a 2–4 second clip that can cost as much as regenerating the clip.

Re-lip only when visible speech is the hook, mouth movement is essential to the idea, data shows silent performance is underperforming, or the clip is important enough to justify the cost.

## AI UGC

The default AI UGC format is silent performance footage with separate VO and subtitles.

The synthetic creator can look, react, demonstrate, point, grab or use the product, move through the scene, and show frustration, surprise, relief, focus, or curiosity.

```text
Synthetic creator reference
→ People / Expressions / Custom Variations
→ choose a strong frame
→ Kling 2.5 720p motion test
→ Kling 2.6 1080p final
```

Hold the same creator, wardrobe, set, lighting, and camera language across clips meant to read as the same person.

Avoid generating a separate talking-mouth clip for every variation. Lip-synced clips are harder to combine consistently and trigger another paid video operation.

Check the brand's on-camera rule in its project record under `libraries/business-memory/project-memory/projects/` before you generate a synthetic creator.

## Storyboard Versus Variations

**Use Variations** for alternate versions of one visual: camera angles, expressions, product views, compositions, and different actions from the same anchor image.

```text
Anchor image → Variations → split the strongest frames → Video Generator
```

**Use Storyboard** only when a sequence needs a beginning, middle, and end, when continuity matters, or when one approved character or core idea needs a reusable foundation. Storyboard is more expensive than building individual clips with Variations.

Budget roughly one Storyboard per approved UGC character or core visual idea, then remix its frames with Variation-generated clips. Do not storyboard every hook or every content idea.

Storyboard frames can be reordered and reused as start frames, end frames, or references. Reordering can cause jumps in pose or location, which sometimes reads as intentional fast-cutting and sometimes reads as a mistake. Check it.

Mixing is expected: a Storyboard clip establishes the character, then Variation clips cover product, metaphor, detail, and humanless B-roll.

## Generating For A Split-Test Cell

A cell shares one body and CTA across every package. That shapes what gets generated.

- **Body and CTA clips: generate once per cell.** They are the locked spine and are reused by every package.
- **Hook clips come from the bank first.** A hook is reused across about three cells with different text hooks before it is judged, so in steady state only about one new hook clip is needed per cell, not one per package.
- Test hooks at Kling 2.5 720p for free. Promote a clip to Kling 2.6 1080p only when it enters a cell.

Rough cost at 1080p finals, 3-package cells:

| | Clips | Credits |
|---|---:|---:|
| Body and CTA, once per cell | ~6 × 3s | ~810 |
| New hook clips, steady state | ~1 × 3s | ~135 |
| **Per cell** | | **~945** |

Multiply the per-cell figure by your planned cells per month. Budget higher at the start while the bank is built from empty.

At a steady cadence, hook-bank depth usually limits you more than credits. Build bank clips continuously at 720p while iterating.

See `libraries/business-memory/sops/reel-split-test.md`.

## Record Every Approved Clip

An approved silent clip is a reusable asset, not a one-off render. Write a record before moving on.

Visual hooks use `libraries/media/shared/visual-hook-record-format.md`. Other generated clips use the standard asset record. Both need the source prompt and the model, or the clip cannot be regenerated or varied later.

Keep raw generated media in ignored local-only paths. Records go in Git; files do not.

## Quality Gate

| Check | Pass Condition |
|---|---|
| Channel | Generation ran in the app or an agent, not the MCP |
| Iteration cost | Test passes used unlimited models |
| Final model | Paid model used only for approved finals |
| Upscale | No upscale purchased on an already-clean 1080p render |
| Audio | Clip is silent unless model audio met all four conditions |
| Continuity | Same creator clips hold wardrobe, set, lighting, and camera language |
| Record | Source prompt, model, and duration are captured |
| Rights | Clip marked `generated` in the asset manifest |

## Sources

- [Magnific Agents](https://www.magnific.com/ai/docs/custom-agents)
- [Getting Started with Spaces](https://www.magnific.com/ai/docs/getting-started-with-spaces)
- [Image Nodes and Variations](https://www.magnific.com/ai/docs/image-nodes)
- [Variations modes and Storyboard](https://www.magnific.com/ai/docs/other-image-tools)
- [Video Nodes and Video Combiner](https://www.magnific.com/ai/docs/video-nodes)
- [Audio Nodes](https://www.magnific.com/ai/docs/audio-nodes)
- [AI credits and limits](https://www.magnific.com/ai/docs/ai-credits-and-limits)
- [Video generator credits](https://www.magnific.com/de/ai/docs/ai-video-generator-credits)
- [Unlimited models](https://www.magnific.com/ai/docs/unlimited-models)
- [Magnific MCP](https://www.magnific.com/ai/docs/magnific-mcp)

Rates change. Re-check the credit tables before planning a large batch.
