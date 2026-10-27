---
name: motion-graphic-design
description: Plan and build motion graphic videos with deliberate typography, composition, and scene choreography. Use for graphic explainers, kinetic type, product demos, animated diagrams, and editorial graphics.
license: MIT
metadata:
  upstream: https://github.com/iart-ai/motion-design-skills
  upstream_commit: 3c129f769d90a1328c209c386492333c9ac62312
---

# Motion Graphic Design

Translate a message into graphic scenes with one coherent motion language.

## Enter The Existing Job

Use the producing workspace's brief and accepted decisions. Video Production owns general motion-graphics videos. Programmatic Animation keeps jobs using its specialized recipes. Both use the shared Remotion runtime. Do not introduce a separate intake or planning workspace.

## Design Before Code

Define the audience, one message, intended feeling, exact text, platform, and audio direction. Reuse known brand context. Label creative defaults as proposals.

Plan each beat as a composition: focal point, supporting information, graphic relationship, movement, and reading hold. Motion should reveal, connect, compare, transform, or demonstrate the idea. A series of unrelated entrances does not establish a visual story.

Set a small motion language: type hierarchy, spacing, palette, easing, timing scale, transition family, and motion intensity. Let exceptions serve a named story beat. For deeper direction and review, read [references/craft.md](references/craft.md).

## Implement The Selected Treatment

Load the `remotion-best-practices` skill (install: `remotion/README.md`) for API guidance, then only relevant rules. Use the shared `remotion/` runtime. Start with existing local modules before importing more code.

The experimental kit is `remotion/src/components/motion-graphics/`. Its [runtime guide](../../../../remotion/src/components/motion-graphics/README.md) describes the three modules, limits, provenance, and first proof. They are runtime components, not automatically approved library pieces.

Keep content, brand, and timing in the owning job. Shared modules accept typed props and do not import a job's plan. Use seconds and actual FPS. Keep frame evaluation deterministic and independent of playback order. Load fonts before capture.

For external source, pin the reviewed revision, retain notices, and record local changes. Import the dependency closure, not an entire project. Follow `skills/registry.yml` when adding a skill. Existing review and promotion rules apply.

## Verify The Actual Result

Inspect start, settled, transition, and ending frames before a full render. Check phone-size readability, clipping, hierarchy, timing, and aspect-ratio fit. Check repeated-frame determinism when changing animation mechanics.

Complete full audiovisual playback QA before calling a rendered video ready. Record unperformed playback as blocked. Keep creative acceptance and publishing decisions explicit in job artifacts.

See [NOTICE.md](NOTICE.md) for source scope and adaptations.
