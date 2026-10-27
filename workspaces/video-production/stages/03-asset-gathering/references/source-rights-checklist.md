# Source Rights Checklist

Use this when marking asset status.

- Record where every external asset came from.
- Mark whether the asset is public, owned, licensed, generated, or pending.
- Do not assume public footage is safe for every platform or ad use.
- For Pixabay music or SFX, record the page URL, creator, title, duration, local path, and `Pixabay Content License` note.
- For selected Pixabay SFX downloads, keep raw files in `libraries/media/local-media/[project-slug]/audio/sfx/` or another ignored local-only path.
- Do not commit filled selection JSON if it contains direct download URLs.
- Do not call Pixabay assets unlicensed. Use `royalty-free` with the license note.
- Keep paid library account details out of repo files.
- If rights are unclear, mark the asset `needs-approval` or `blocked`.
- Add a fallback for every risky or missing asset.
