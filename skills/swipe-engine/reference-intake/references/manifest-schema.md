# Manifest Schema

`manifest.json` is the machine-readable handoff between swipe-engine stages.

## Required fields

| Field | Meaning |
|---|---|
| `schema_version` | Manifest contract version. Current version is `3`; v1/v2 manifests remain readable as legacy manifests. |
| `slug` | Lowercase, hyphenated reference identifier. |
| `status` | `staged` for acquisition, `curated` after promotion. `complete` is a legacy v1/v2 value and must not be treated as a finished swipe. |
| `workflow_state` | Explicit handoff state: `awaiting-save-approval`, `save-approved`, or `curated`. |
| `next_action` | The next required human/agent action. Agents must follow this instead of guessing from file presence. |
| `ready_for_stage_02` | `true` only after `finalize-save` has written the intake record. |
| `ready_for_promotion` | Reserved for a future extraction/curation finalizer; never infer it from acquisition alone. |
| `source` | Original URL, repository-relative source path, or scrubbed `external-file:[name]`. |
| `source_type` | `image`, `webpage`, `pdf`, `audio`, `video`, or `social-video`. |
| `source_hash` | SHA-256 of the acquired source used for duplicate detection. |
| `acquired_at` | UTC ISO-8601 acquisition time. |
| `primary_context` | Repository-relative path to the main inspectable artifact. |
| `files` | Acquired and derived file records. |
| `tools` | Commands or built-in handlers used during acquisition. |
| `warnings` | Non-fatal missing capabilities or partial results. |
| `quality_status` | `ok` when no warnings were emitted; otherwise `degraded`. |
| `warning_count` | Count of entries in `warnings`. |

Each file record contains `path`, `role`, `mime_type`, `sha256`, `bytes`, and `persist`. Stage 03 copies only records where `persist` is `true`.

## Optional fields

| Field | Meaning |
|---|---|
| `fallback` | Present when the acquired source is a manual/local fallback for a failed original source. Contains `original_source`, `fallback_source`, `failed_tool`, `reason`, and optional `error`. |

## Roles

- `primary-context`: Main image or screenshot.
- `image-reference`: Additional image in a social carousel.
- `pdf-page`: Rendered PDF page.
- `extracted-text`: PDF text from v1/v2 manifests.
- `transcript`: User-provided or Whisper-generated transcript artifact.
- `video-frame`: Sampled frame.
- `contact-sheet`: Video overview image.
- `probe`: Technical audio/video metadata.
- `frame-index`: Timestamped sampled-frame table.
- `scene-index`: Scene-change candidate table.
- `motion-index`: Sample-to-sample motion table.
- `audio-profile`: Technical audio stream, volume, and silence profile.
- `media-timeline`: Combined timestamp handoff for video/audio review.
- `media-analysis`: Draft Video, Audio, and Combined Patterns summary for Stage 02 review.
- `ocr-text`: Optional on-screen text detected from sampled frames.
- `fallback-note`: Human-readable note explaining why a fallback file was used and what failed.
- `source-media`: Raw PDF, video, or audio. Never promote.
- `metadata`: Supporting source metadata.

Stage 02 must use `primary_context` plus relevant `files`; it must not depend on the original source remaining reachable. A staged manifest is not a Stage 02 handoff until `ready_for_stage_02` is `true` and the manifest names an intake record.
