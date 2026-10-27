---
name: reference-intake
description: Acquire and normalize marketing references for the swipe-engine reference loop. Use when a user asks to save, swipe, ingest, or reference an image, screenshot, webpage, PDF, audio file, local video, Instagram post, TikTok, YouTube video, or compatible social URL for later extraction and curation.
license: MIT
---

# Swipe Engine Reference Intake

Acquire the source before writing the Stage 01 intake record. Produce local, inspectable context artifacts so Stage 02 never has to refetch the original URL.

The CLI has two different operations. `acquire` creates a staged package only. `finalize-save` writes the Stage 01 intake record after the user approves the save checkpoint. Never treat an acquisition manifest as a completed swipe.

Every stage must use `libraries/swipes/shared/stage-handoff-format.md`. A stage checkpoint is terminal: write the handoff, send the user-facing summary, and end the current turn. Never leave the task loading while waiting for approval.

Stage Markdown outputs are intentionally unignored and writable: use the IDE file tool or `apply_patch`. Never use `cat >`, a heredoc, or a Python write workaround for an intake, extraction, handoff, or curation file. Raw media and derived assets under `output/assets/` remain ignored; that does not block local reading or the `finalize-save`/`promote` scripts.

After writing a handoff, validate it with the short command below before returning the checkpoint:

```bash
python3 skills/swipe-engine/reference-intake/scripts/reference_intake.py check-handoff \
  libraries/swipes/stages/<stage>/output/<slug>-handoff.md \
  --stage "<stage>" --slug "<slug>" --state "<state>"
```

## Workflow

1. Read `libraries/swipes/stages/01-save/CONTEXT.md` and its intake format.
2. Propose the slug and tags, then acquire the reference:

   ```bash
   python3 skills/swipe-engine/reference-intake/scripts/reference_intake.py acquire \
     "<url-or-local-path>" --slug "<slug>"
   ```

3. For a webpage, capture a full-page screenshot with the available browser or Playwright tool, then pass it to the same command:

   ```bash
   python3 skills/swipe-engine/reference-intake/scripts/reference_intake.py acquire \
     "https://example.com" --slug "<slug>" --captured-file "/path/to/full-page.png"
   ```

4. Read the emitted `manifest.json`. Confirm `status: staged`, `workflow_state: awaiting-save-approval`, `next_action: present-save-checkpoint`, and inspect every warning. Do not write an intake record if acquisition failed.
5. Present the normal Stage 01 save checkpoint. Do not write the intake file with `cat`, a heredoc, or an invented human note. On explicit approval, run:

   ```bash
   python3 skills/swipe-engine/reference-intake/scripts/reference_intake.py finalize-save \
     libraries/swipes/stages/01-save/output/assets/<slug>/manifest.json \
     --title "<title>" \
     --type social-post \
     --tags "inspiration,hook" \
     --why-saved "<the user's reason>" \
     --human-approved
   ```

   This writes `[slug]-intake.md` and changes the manifest to `workflow_state: save-approved`.
6. Run Stage 02 from the acquired files in the manifest. Do not refetch the source. Do not proceed unless `ready_for_stage_02: true`. Write the Stage 02 extraction and `[slug]-handoff.md` before returning the stage summary. Stop at the Stage 02 checkpoint; do not draft or promote Stage 03 in the same turn.
7. After Stage 03 approval, promote persistent context artifacts and include the explicit approval flag:

   ```bash
   python3 skills/swipe-engine/reference-intake/scripts/reference_intake.py promote \
     libraries/swipes/stages/01-save/output/assets/<slug>/manifest.json \
     --human-approved
   ```

8. Write the promoted manifest and primary-context paths into the knowledge-layer entry. Never promote rejected references.

## Acquisition Behavior

- Copy images and screenshots directly into the context package.
- Capture webpages as full-page screenshots before acquisition.
- Preserve a PDF in ignored staging; render its pages and extract text for context.
- Preserve video in ignored staging; generate probe metadata, timestamped frames, a labeled contact sheet, frame index, scene index, motion index, audio profile, media timeline, and media-analysis draft.
- Preserve audio in ignored staging; generate probe metadata, audio profile, media timeline, transcript artifacts when available, and media-analysis draft.
- Download Instagram, TikTok, YouTube, and compatible social video with `yt-dlp`.
- For social posts that require a logged-in session, pass either `--cookies-from-browser chrome` or `--cookies /path/to/cookies.txt` to the acquire command. Use only sessions you are authorized to access, and never commit cookie files.
- If `yt-dlp` still fails, the user can download the visible post manually with a trusted Chrome extension and ingest that local file as the fallback. Record the failed URL, failed tool, reason, and error with `--fallback-source`, `--fallback-tool`, `--fallback-reason`, and `--fallback-error`.
- Run the existing `info-rip` script for YouTube metadata and transcripts when available.
- Use `--transcript-file` when the user already has a transcript. Otherwise attempt local Whisper transcription when a `whisper` command is installed. Treat its absence as a warning, not an acquisition failure.
- Attempt OCR on sampled video frames when `tesseract` is installed. Treat its absence as a warning, not an acquisition failure.
- Stage 02 must open the local `primary_context`/contact sheet and representative sampled frames with the image viewer. Gitignored staging files remain readable from the filesystem; do not use Git tracking state as an access test.

Read [manifest-schema.md](references/manifest-schema.md) when changing the manifest or stage handoff.

## Guardrails

- Keep every recorded path relative to the repository root.
- `status: staged` means acquisition only. It never means the reference is saved, extracted, or curated.
- `workflow_state` and `next_action` are the handoff contract. Follow them instead of inferring progress from file existence.
- `quality_status: degraded` or a nonzero `warning_count` must be shown at the Stage 01 checkpoint. Warnings may be non-blocking, but they may never be silently omitted.
- Use `finalize-save` to create the intake record. Manual heredocs and Python write workarounds are not accepted for any stage output.
- Every stage must write a handoff artifact and return a terminal checkpoint with completed work, artifact paths, warnings/blockers, next action, and the exact reply needed from the user.
- A media extraction is not visually complete until the contact sheet and representative frames have been opened. Transcript/OCR/motion metadata is supporting evidence, not a substitute for viewing frames.
- The promotion gate rejects a media extraction that lacks `## Visual inspection` or claims that gitignored frames are not viewable.
- Approval is a user decision, not a background wait. End the turn immediately after asking for it.
- Treat raw PDF, video, and audio as staging-only. Promote only context artifacts marked `persist: true`.
- Check content hashes before creating a duplicate package.
- If social download fails because the source is private, deleted, or rate-limited, request a screenshot or local file fallback.
- When a fallback file is used, document why. The manifest must preserve what failed and the fallback note must be available to Stage 02.
- Report the exact missing command when a required capability is unavailable.
- Do not bypass the Stage 01 save gate or Stage 03 curation gate.
