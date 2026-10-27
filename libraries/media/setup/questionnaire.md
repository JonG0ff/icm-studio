# Media Library Setup

Use this only when configuring reusable media defaults.

1. Where should raw reusable media live by default?
   - Default: `libraries/media/local-media/`

2. Which external storage should records point to when local storage is not enough?
   - Default: local path only for now
   - Examples: Google Drive, Dropbox, Supabase Storage, Cloudflare R2

3. Which asset statuses require human approval before reuse?
   - Default: `internal-reference-only`, `needs-approval`, and `blocked`

4. Should small previews be committed?
   - Default: no. Keep previews local unless a specific preview exception is approved.

5. Which tag groups matter most?
   - Default: subject, brand, emotion, source type, visual motif, rights status
