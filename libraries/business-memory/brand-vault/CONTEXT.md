# Brand Vault

Approved brand identity, voice rules, visual tokens, and themes.

## Brand Routing

| Brand | Load | Use For |
|-------|------|---------|
| Acme Coffee Co. (demo) | `brands/acme-coffee/identity.md`, `brands/acme-coffee/voice-rules.md` | The made-up demo brand every example uses. Replace it with your own in setup. |
| New brand | `brands/_template/` | Copy this folder to `brands/[brand-slug]/` during setup. Never write into the template. |

Add one row here for each brand you configure.

Before a brand's first split test, copy `brands/_template/text-hook-bank.md` into
its brand folder if missing. Draft and approve hooks through Business Memory.
The demo brand starts with no approved text hooks.

## Shared Visual Context

| File | Section/Scope | Use For |
|------|---------------|---------|
| `tokens.md` | Full file | Visual constants shared across marketing workspaces |
| `themes/CONTEXT.md` | Full file | Choosing the smallest theme file |

## Rules

- Load one brand at a time.
- Brand files are authored truth, not swiped references.
- Swiped references stay in `../../swipes/knowledge-layer/`.
- If a downstream workspace needs voice or identity, point it here.
- Do not duplicate brand rules into downstream workspaces.
