# Motion Graphics: Source And Local Changes

`MaskReveal.tsx`, `Callout.tsx`, and the shared choreography separation are adapted from [Onda](https://github.com/degueba/onda), by Rodrigo Botelho, under MIT. The complete notice is in `LICENSE.onda`. The reviewed revision and source blobs are in `upstream.json`.

Local changes:

- Use seconds and the active composition FPS instead of fixed 30 FPS delays.
- Replace upstream placement, theme, Zod, and package dependencies with small typed props.
- Use a normalized SVG path for callout drawing, without adding a path package for this slice.
- Keep typography and visual tokens under the consuming job's control.
- Use explicit eased timing and local validation.
- Add an original process-diagram module.

This is a selected source adaptation, not a full Onda installation or a promise of upstream compatibility. Preserve notices, compare upstream changes deliberately, and do not overwrite local changes with its CLI.

These modules are experimental runtime code. They have not been promoted as approved Animation Library pieces. The first proof owns taste and delivery decisions.
