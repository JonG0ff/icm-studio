# Remotion Runtime

The shared, local Remotion render runtime. Video Production and Programmatic Animation both render here. The deliverable and its recipe decide which workspace owns the job. Work in this folder from your editor. It is not a hosted app.

## Start

```bash
cd remotion
npm install
npm run dev
```

Remotion Studio opens the registered compositions for preview and frame-by-frame editing.

## Agent Skill

The workspaces load Remotion's own `remotion-best-practices` skill for Remotion APIs. It isn't bundled here. Install it once from the repo root:

```bash
npx skills add remotion-dev/skills
```

Or with the GitHub CLI: `gh skill install remotion-dev/skills`. See the [Remotion Agent Skills docs](https://www.remotion.dev/docs/ai/skills). Without it, agents can still read the [Remotion docs](https://www.remotion.dev/docs) directly.

Source, timing data, and handoffs are tracked. Generated voice audio, SFX, music, and renders stay local. A fresh clone can list and render the compositions below. Your own productions need their local media in place before they render. Never commit downloaded media to fix a missing file.

## Commands

```bash
npm run typecheck
npm run compositions
npm run render:smoke
```

The smoke render is written to `out/smoke-test.mp4`. The `out/` folder is local only.

## What Ships

| Composition | Folder | What it shows |
|---|---|---|
| `script-to-animation-smoke-test` | `src/compositions/script-to-animation/smoke-test/` | The runtime renders |
| `programmatic-animation-look-swatches-v1` | `src/compositions/programmatic-animation/look-swatches/` | Four looks side by side |
| `video-production-hybrid-short-prototype` | `src/compositions/video-production/hybrid-short/` | Source cuts, phrase captions, and supporting cards from a JSON edit map |
| `video-production-selected-footage` | `src/compositions/video-production/selected-footage/` | Target of the footage-edit command. Needs your own footage |

Shared code:

- `src/compositions/programmatic-animation/_kit/`: the animation rig kit. Looks, shapes, mouth sets, sheet boards.
- `src/components/motion-graphics/`: the [motion graphics kit](src/components/motion-graphics/README.md).
- `src/lib/`: edit contracts and the open-edit and video-use adaptations. Each upstream folder keeps its license.
- `scripts/`: the [footage-edit command](scripts/FOOTAGE_EDIT.md) and footage analysis.

## Footage Edit

The [selected-footage command adapter](scripts/FOOTAGE_EDIT.md) connects inspection, local Whisper with a cache, editorial compilation, composition previews, and render dispatch. It is experimental.

The `video-production-selected-footage` composition needs your own footage. Opened on its own in Studio, it shows a blank frame. Run the footage-edit command on a clip first; it supplies the props and the source file.

## Hybrid Short Prototype

The prototype uses a JSON edit map, normal-speed source cuts, phrase captions, separate emphasis, supporting cards, and explicit source and output frame rates. It has fixed output metadata. Register a matching definition for another duration or size.

```bash
node scripts/create-hybrid-test-media.mjs
node src/compositions/video-production/hybrid-short/edit-map.test.mjs
npx remotion still src/index.ts video-production-hybrid-short-prototype out/hybrid-short/frame-45.png --frame=45 --scale=0.5
npx remotion render src/index.ts video-production-hybrid-short-prototype out/hybrid-short/prototype.mp4
```

Check stills around each cut before rendering. The fixture is a generated test pattern with a quiet tone. Its text is test labeling, not transcribed speech. FFmpeg must be on your PATH for the fixture generator.

This is a technical check, not a finished edit. Follow the [hybrid short recipe](../workspaces/video-production/shared/formats/hybrid-short.md) for a real job. The code uses Remotion's [OffthreadVideo API](https://www.remotion.dev/docs/offthreadvideo) and [Caption data format](https://www.remotion.dev/docs/captions/caption).

Before you call any export final, watch and listen to the whole file. Stills, transcripts, and a clean decode support that check. They don't replace it.

## Add a Composition

1. Create `src/compositions/<workspace>/<topic-slug>/`.
2. Export the React component and a typed definition made with `defineComposition()`.
3. Use a hyphenated ID with the workspace and topic slug.
4. Add the definition to `src/compositions/registry.ts`.
5. Put static files in `public/assets/<workspace>/<topic-slug>/`, voice audio in `public/audio/`.
6. Run `npm run typecheck` and `npm run compositions` before you open Studio or render.

## Licensing

This folder's code is MIT, like the rest of the repo. The adapted upstream code keeps its own license in its folder. The Remotion framework has separate terms: free for individuals and small teams, a company license for larger companies. Check the [Remotion license](https://www.remotion.dev/license) before you use it.
