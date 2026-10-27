# Experimental Motion Graphics Kit

Three reusable modules for the shared runtime. Use them inside your own composition. Creative acceptance and full playback QA belong to the job that uses them.

| Export | Inputs | Timing and limits |
|---|---|---|
| `MaskReveal` | Children, style, direction, delay, duration | Seconds; uses local sequence time. Caller owns wrapping, type, and placement. |
| `Callout` | Label, normalized anchor and label position, type/color, delay, duration | Seconds. Coordinates are fractions of the composition. Caller keeps label and elbow connector inside safe areas. |
| `ProcessDiagram` | Two to six uniquely identified nodes, labels, optional details, size, colors, font, optional initial visible node | Vertical SVG. Seconds per step. Long labels and aspect adaptation require preview. |

Pass content and brand choices from the consuming composition. Shared code must not import a job's beat map. A Sequence gives its children a local frame origin, so module delays are relative to that sequence.

`MaskReveal`, `Callout`, and choreography organization adapt selected MIT Onda source. The process diagram is original. See [NOTICE.md](NOTICE.md), [LICENSE.onda](LICENSE.onda), and [upstream.json](upstream.json). No upstream CLI, full registry, or service is installed.

## Use

From `remotion/`:

```bash
npm run typecheck
node --test src/components/motion-graphics/motion.test.mjs
```

Import from `src/components/motion-graphics/index.ts`. Register your composition in `src/compositions/registry.ts`, then preview it in Studio with `npm run dev`.

The [motion graphic design skill](../../../../skills/ai-capabilities/design/motion-graphic-design/SKILL.md) explains when to pick these pieces. The [motion graphics format](../../../../workspaces/video-production/shared/formats/motion-graphics.md) is the production recipe.
