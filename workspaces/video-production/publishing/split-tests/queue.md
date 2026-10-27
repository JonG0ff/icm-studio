# Publish Queue

One row per publish slot. Fill it from each cell's variant matrix.

Rules live in [the split-test workflow](../split-test.md#queue-rules). No two slots in a row come from the same cell.

| Date | Cell | Package | Export file | Status | Notes |
|------|------|---------|-------------|--------|-------|

Status values: `queued`, `ready`, `published`, `read`, `held`.

Nothing is queued yet.
