# Business Memory

Approved business, brand, offer, and project context for your work.

This library stores approved company details, brand rules, business standards, content SOPs, content-type templates, and project facts. Read selected records directly; maintenance stages are for creating or updating records. It is not a general-purpose conversation memory system.

## Folder Map

```
business-memory/
├── CLAUDE.md
├── CONTEXT.md
├── setup/
│   └── questionnaire.md
├── brand-vault/
│   ├── CONTEXT.md
│   ├── brands/
│   │   ├── _template/        (blank brand; copy it in setup)
│   │   │   ├── identity.md
│   │   │   └── voice-rules.md
│   │   └── acme-coffee/      (demo brand; replace with your own)
│   │       ├── identity.md
│   │       └── voice-rules.md
│   ├── themes/
│   │   ├── CONTEXT.md
│   │   └── default.md
│   └── tokens.md
├── sops/
│   ├── CONTEXT.md
│   ├── social-reel.md
│   ├── footage-short-quality.md
│   ├── reel-hook-design.md
│   ├── reel-retention-progression.md
│   ├── reel-split-test.md
│   └── instagram-publishing-safety.md
├── content-types/
│   ├── CONTEXT.md
│   ├── short-form-video.md
│   └── split-test-cell.md
├── offers/
│   ├── CONTEXT.md
│   └── acme-coffee-seasonal-blend.md
├── project-memory/
│   ├── CONTEXT.md
│   ├── index.md
│   └── projects/
└── stages/
    ├── 01-brand-setup/
    ├── 02-project-memory/
    └── 03-validation/
```

## Triggers

| Keyword | Action |
|---------|--------|
| `setup` | Configure a brand in `brand-vault/brands/` |
| `brand` | Read or update approved brand context |
| `sop` | Find or update a content SOP |
| `offer` | Read or update an offer record in `offers/` |
| `project` | Propose or approve project memory |
| `status` | Show brands, SOPs, project memory, and validation state |

## Routing

| Task | Go To |
|------|-------|
| Add or configure a brand | `stages/01-brand-setup/CONTEXT.md` |
| Read brand identity or voice | `brand-vault/CONTEXT.md` |
| Add or update a theme | `brand-vault/themes/CONTEXT.md` |
| Find or update a SOP | `sops/CONTEXT.md` |
| Find a content template | `content-types/CONTEXT.md` |
| Find an offer or affiliate compliance rule | `offers/CONTEXT.md` |
| Propose or approve project memory | `stages/02-project-memory/CONTEXT.md` |
| Check stale pointers or duplicated brand files | `stages/03-validation/CONTEXT.md` |

## What to Load

| Task | Load These | Do NOT Load |
|------|-----------|-------------|
| Write for a brand | `brand-vault/brands/[brand-slug]/identity.md`, `brand-vault/brands/[brand-slug]/voice-rules.md` | other brand folders, project-memory |
| Use visual rules | `brand-vault/tokens.md`, selected theme from `brand-vault/themes/` | project-memory |
| Find SOP | `sops/CONTEXT.md`, selected SOP | brand files unless the SOP asks for them |
| Design a split-test cell | `sops/reel-split-test.md`, `sops/instagram-publishing-safety.md`, `content-types/split-test-cell.md`, the brand's `text-hook-bank.md` if it has one, the project file if one exists | other brand folders, unrelated SOPs |
| Log project memory | `project-memory/index.md`, selected project file, `stages/02-project-memory/CONTEXT.md` | unrelated brand folders |
| Validate routing | `stages/03-validation/CONTEXT.md`, dependent workspace routing docs | project files unless checking a project link |

## Boundaries

- This library stores authored and approved business context.
- Use it to fill missing company, brand, SOP, offer, CTA, and project details.
- Offer records store partner terms and compliance. Partner compliance rules outrank our own format preferences.
- Do not use it to store raw brainstorms, every model observation, or swiped references.
- Swiped references stay in `../swipes/knowledge-layer/`.
- Do not copy brand files into dependent workspaces. Point them here.
