# Design Tokens

Human-readable visual constants for marketing workspaces.

Setup fills these values (questionnaire Q9). Until then, the demo brand's colors are in `brands/acme-coffee/identity.md`.

## Approved Tokens

| Token | Value | Notes |
|-------|-------|-------|
| Primary color | `{{PRIMARY_COLOR}}` | Main brand color |
| Accent color | `{{ACCENT_COLOR}}` | Emphasis and impact moments |
| Background color | `{{BACKGROUND_COLOR}}` | Default surface |
| Text color | `{{TEXT_COLOR}}` | Body text on the background |
| Muted text color | `{{TEXT_MUTED_COLOR}}` | Secondary text and captions |
| Font heading | {{FONT_HEADING}} | Titles and display moments |
| Font body | {{FONT_BODY}} | Captions, UI, body copy |
| Radius | `8px` | Buttons, cards, small panels |
| Max content width | `720px` | Blog, email, long copy |
| Social safe zone | `1080x1920` | Reels, TikTok, Shorts |

## Usage

- Use the accent color for emphasis, not as the whole palette.
- Do not invent new hex codes when an approved token exists.
- If a new token is needed, add it here first.
- Keep this Markdown until there is a real code consumer for structured tokens.
