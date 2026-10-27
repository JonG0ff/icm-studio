# Asset Record Format

Use this format for `assets/[asset-id].md`.

```markdown
# Asset: [title]

- asset_id: [lowercase-hyphen-id]
- title: [plain title]
- type: footage | still | audio | sfx | logo | overlay | generated-video | generated-image
- status: ready | internal-reference-only | needs-approval | blocked
- date_added: YYYY-MM-DD
- tags: tag-one, tag-two, tag-three
- source_url: [source URL or source note]
- local_path: [local-only path to raw file, if present]
- rights_note: [public, owned, licensed, generated, pending, internal-reference-only, or unclear]
- reuse_notes: [where this asset fits]
- used_in: [project-slug, project-slug]
- fallbacks: [fallback source or generation option]

## Description

What the asset shows or provides.

## Source And Rights

License, ownership, creator, attribution, approval limits, takedown notes, or clearance gaps.

For Wikimedia Commons assets, record the Commons file page URL, direct file URL, creator or credit line, license name, license URL or usage terms, attribution requirement, and any personality, trademark, event, or brand-context approval risk.

For web stills (named athletes, movie publicity, news/press grabs), record the direct source URL, local path, search query if known, and `rights_note: unclear`. File on disk is enough to cut in FCP.

For Pixabay music or SFX assets, record the Pixabay asset page URL, creator, title, duration, local path, `Pixabay Content License` note, and any third-party rights concern from the asset page or intended use.

## Reuse Guidance

Best uses, bad fits, edit notes, framing notes, and search terms.

## Usage History

| Project | Use | Date | Notes |
|---------|-----|------|-------|
```

## Field Rules

- `asset_id` is stable once created.
- `local_path` should point to `local-media/` or another approved local-only folder. Stage output paths are temporary and should be moved before a reusable asset is registered.
- Do not put API keys, paid-library credentials, cookies, or private download tokens in records.
- Register approved Wikimedia Commons assets only after source and rights evidence is recorded. Raw downloads still belong in `local-media/` or another ignored local-only path.
- Register approved Pixabay SFX/music assets only after source page, creator, title, duration, local path, and Content License notes are recorded.
- For poke-style / web-still bank grabs, require a source URL and local path. `rights_note: unclear` is allowed for organic reel grabs. Keep the source URL so a still can be swapped if a reel gets pulled.
- Use `internal-reference-only` for YouTube, social, or documentary clips without delivery rights.
- Use `needs-approval` when the human must approve legal or brand risk before reuse.
- Use `blocked` when the asset should not be used.
