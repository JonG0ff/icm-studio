# Library Audit Checklist

- Confirm each index row points to an asset record.
- Confirm each asset record has the required fields.
- Confirm every external source has a rights note.
- Flag records marked `ready` without a clear license, owned asset note, or generation note.
- Flag YouTube or social clips that are not marked `internal-reference-only`, `needs-approval`, or `blocked`.
- Check whether local paths still exist when local files are expected.
- Run `git status --short --ignored libraries/media` before finalizing.
