# Local Media Policy

Git stores the catalog. It does not store raw media.

## Default Local Folder

Use this folder for reusable local media files:

```text
libraries/media/local-media/
```

This folder is ignored by Git except for `.gitkeep`.

## What Stays Out Of Git

- Stock footage exports
- YouTube or social reference clips
- Paid library downloads
- Large stills or screenshots
- Audio, music, stems, and SFX files
- Generated video or image outputs
- Zip exports and project archives

## What Can Be Tracked

- Markdown asset records
- JSON metadata without secrets
- Source and rights notes
- Search tags
- Usage history
- Small preview files only after an explicit file-size check and intentional `.gitignore` exception

## Before Adding Media

1. Put raw media in `local-media/` or another ignored local path.
2. Add or update the Markdown asset record.
3. Record source URL, rights note, and status.
4. Run `git status --short --ignored libraries/media`.
5. Confirm raw media is ignored and metadata is trackable.
