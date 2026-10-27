# ICM Conventions

The rules for building and maintaining ICM workspaces and libraries. ICM is also known as the Model Workspace Protocol (MWP). This is the live canonical source. Historical upstream documents are under `history/icm/`.

---

## Five-Layer Routing Architecture

Agents read down the layers. They stop as soon as they have what they need.

```
Layer 0: CLAUDE.md           -> "Where am I?"            (always loaded, ~800 tokens)
Layer 1: CONTEXT.md          -> "Where do I go?"          (read on entry, ~300 tokens)
Layer 2: Stage CONTEXT.md    -> "What do I do?"            (read per-task, ~200-500 tokens)
Layer 3: Reference material  -> "What rules apply?"        (loaded selectively, varies)
Layer 4: Working artifacts   -> "What am I working with?"  (loaded selectively, varies)
```

**Layer 0 -- CLAUDE.md** is auto-loaded by Claude Code into every conversation. It contains the folder map, naming conventions, and a routing table that points to workspace-level files. One per workspace.

**Layer 1 -- Top-level CONTEXT.md** is the first thing an agent reads when entering the workspace. It contains a task routing table that maps task types to specific stage folders. One per workspace.

**Layer 2 -- Stage CONTEXT.md files** live inside each stage folder. They contain the scope definition, what-to-load tables, and step-by-step process. One per stage. Layer 2 is the control point of the system -- its Inputs table determines exactly which files from Layers 3 and 4 the agent loads.

**Layer 3 -- Reference material** is the persistent context: design systems, voice rules, build conventions, style guides, domain knowledge bundled as skill files. These files are configured once during workspace setup and remain stable across every run of the pipeline. They live in `references/` folders within stages, in workspace-level configuration folders (like `brand-vault/` or `design-system/`), in `shared/`, and in `skills/`. Larger reference collections can include their own CONTEXT.md routing files to help agents navigate within the collection.

**Layer 4 -- Working artifacts** are the per-run context: previous stage outputs, user-provided source material, anything specific to this particular run. These files are produced and consumed during execution and change every time the pipeline runs. They live in `output/` folders.

The distinction between Layers 3 and 4 matters because they require different things from the model. Layer 3 material needs to be internalized as constraints and patterns -- write like this, use these colors, follow these conventions. Layer 4 material needs to be processed as input -- transform this research into a script, convert this script into a specification. Layer 3 is the factory. Layer 4 is the product.

A rendering agent might only need Layers 0 through 2. A script-writing agent reads down to Layer 4 to access both voice rules (Layer 3) and source material (Layer 4). No agent reads everything.

Every token of irrelevant context is a token of diluted attention. Workspace CLAUDE.md files should explicitly map each task to its minimal required files. Loading more context does not make output better. It makes it worse.

---

## Pattern 1: Stage Contracts

Every stage CONTEXT.md follows the same three-section shape:

```markdown
## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| ... | ... | ... | ... |

## Process

1. Step one
2. Step two
3. Step three

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| ... | ... | ... |
```

This is the contract. It is simple enough that a non-technical user can read it and understand what is happening. It is structured enough that an agent can follow it reliably. Every stage follows this exact shape. No exceptions.

---

## Pattern 2: Stage Handoffs via Output Folders

Every stage has an `output/` subfolder. The agent writes its artifact there. The next stage reads from the previous stage's `output/` folder.

The convention:
- Stage N produces: `stages/0N-name/output/artifact-name.md`
- Stage N+1's CONTEXT.md says: "Read `../0N-name/output/artifact-name.md` as your input"

This is the handoff. A human can open the output file, edit it, and the next stage picks up the edited version. No state management. No orchestration layer. Just files in predictable places.

File naming in output folders: `[topic-slug]-[stage-artifact].md`
- Example: `hello-world-script.md`, `hello-world-spec.md`

---

## Pattern 3: One-Way Cross-References

Every folder points outward to what it needs. No folder points back.

If Stage 03 references Stage 02's component registry, Stage 02 does NOT reference anything in Stage 03. If the brand-vault is referenced by multiple stages, the brand-vault does NOT reference any stage.

This prevents reference growth from going N-squared as the system scales. When adding a new reference, check: "Does the target file already reference my folder?" If yes, restructure.

---

## Pattern 4: Selective Section Routing

CONTEXT.md Inputs tables do not just say "read voice-rules.md." They say "read the Voice Rules section of voice-rules.md."

This keeps token cost low. A 150-line file might have only 60 lines of actionable rules for a specific stage. The other 90 lines of strategic rationale stay unloaded.

Format in CONTEXT.md Inputs tables:

```
| File | Section to Load | Why |
|------|----------------|-----|
| voice-rules.md | "Voice Rules" through "What the Voice Is NOT" | Tone guidance |
| identity.md | "One-Sentence Brand" and "Audience" sections | Audience context |
```

When a full file is needed, write "Full file" in the Section/Scope column.

---

## Pattern 5: Canonical Sources

Every piece of information has ONE home. Other files point there. They do not duplicate it.

If you need to update a rule, you update it in one place. Every other file has a pointer. If you find the same information in two files, one of them should be replaced with a reference to the other.

Smell test: search the repo for a specific phrase. If it appears in more than one file and both instances are meant to be authoritative, one needs to become a pointer.

---

## Pattern 6: CONTEXT.md = Routing, Not Content

CONTEXT.md files answer three questions:
1. What is this folder?
2. What do I load?
3. What is the process?

They never contain the actual reference material. No definitions. No rules. No extended examples. No voice guidelines. This keeps them small (25-80 lines) and prevents them from going stale when the content they would otherwise duplicate gets updated.

If you find yourself writing more than a one-sentence description in a CONTEXT.md, that content belongs in a separate file that the CONTEXT.md points to.

---

## Pattern 7: Tool Prerequisites

Some stages require external tools (Node.js, LibreOffice, ffmpeg, etc.). Setup guides for these tools live in the `references/` folder of the stage that uses them (e.g., `stages/03-build/references/remotion-setup.md`).

Setup guides are written for someone who has never installed the tool: what it is (one sentence), installation steps, how to verify it works, and how the workspace uses it.

If a tool is needed by multiple stages, it can live in `shared/` instead. The `setup` onboarding process should check which tools are needed based on the user's answers and point them to the right setup guide.

Note: When a workspace bundles skills (Pattern 9), many tools that would have needed separate prerequisites (scripts, libraries, utilities) come bundled inside the skill folder. Only tools that require system-level installation (Node.js, Python, LibreOffice) still need setup guides.

---

## Trigger Keywords

Every workspace recognizes these triggers:

**`setup`** -- Starts the onboarding questionnaire. The agent reads `setup/questionnaire.md`, asks the questions conversationally, collects answers, replaces placeholders across the workspace, and verifies no placeholders remain.

**`status`** -- Shows pipeline completion. The agent scans all `stages/*/output/` folders and renders an ASCII pipeline diagram:

```
Pipeline Status: [workspace-name]

  [01-stage-name]  ------>  [02-stage-name]  ------>  [03-stage-name]
     COMPLETE                  PENDING                  PENDING
  (artifact.md)              (empty)                  (empty)
```

For each stage: if the output folder contains files (other than .gitkeep), the stage is COMPLETE and the filenames are listed. If the output folder is empty or contains only .gitkeep, the stage is PENDING.

Workspaces can define additional trigger keywords in their own CLAUDE.md.

---

## Naming Conventions

- Folders and files: `lowercase-with-hyphens`
- Stage folders: zero-padded numbers prefix: `01-`, `02-`, `03-`
- Placeholders: `{{SCREAMING_SNAKE_CASE}}`
- Output artifacts: `[topic-slug]-[artifact-type].md`
- No spaces in file or folder names

---

## Pattern 8: Questionnaire Design

Onboarding questionnaires configure the production system, not a specific run. They follow these rules:

1. **Flat structure.** No category groupings. Just a numbered list of questions.
2. **All at once.** Every question appears in one pass. The user should be able to answer everything in a single message.
3. **System-level only.** Questions configure things that stay the same across runs: identity, brand, design, tool preferences, default workflow. Per-run details (project name, topic, audience, scope) are collected conversationally at the start of each pipeline run by the entry stage.
4. **Derive, do not ask.** If a field can be inferred from another answer, the agent fills it in. List derived fields under the question they depend on. Do not add a separate question.
5. **Sensible defaults.** Every question should have a default or example so the user can skip what they do not care about.
6. **Ask once, never again.** After setup, the user should never see these questions again. The answers are baked into the workspace files permanently.

The questionnaire template at `_core/templates/questionnaire-template.md` encodes these rules.

---

## Pattern 9: Canonical Skills

Full skill definitions live once under the repository-level `skills/` directory. `skills/README.md` routes agents and `skills/registry.yml` records provenance, visibility, export status, owner, and license.

Workspaces reference canonical skills from their stage input tables. They do not copy full `SKILL.md`, `rules/`, or `scripts/` trees into product folders.

```text
repository/
├── skills/[lane]/[domain]/[skill-name]/SKILL.md
└── workspaces/[workspace]/stages/[stage]/CONTEXT.md
```

Use the relative path from the stage to the canonical skill:

```text
| Skill | `../../../../skills/[lane]/[domain]/[name]/SKILL.md` | Index, then load rules as needed | [What it provides] |
```

During discovery, search the live map and registry before looking outside the repository. Import an external skill into the canonical library once, record its source and license, then point every workspace at that copy.

Workspace-specific behavior stays in local references or a product-local skill only when it is genuinely unique to that workspace. Export tooling may bundle canonical skills into a standalone package later; exported copies are generated artifacts, not source-of-truth definitions.

---

## Pattern 10: Specs Are Contracts

Specification stages define WHAT the output should achieve and WHEN things happen. They do not prescribe HOW to implement. The build stage has creative freedom within the quality floor defined by the design system.

A spec contains:
- **Beat map** with approximate durations, narration, and mood
- **Visual philosophy** describing what a muted viewer should understand
- **Key moments** that MUST land, and why each matters
- **Audio sync points** mapping narration words to visual events
- **Color flow** with per-scene dominant color and mood

A spec does NOT contain: frame numbers, component names, pixel positions, spring configs, or prop definitions. These are implementation decisions that belong to the build stage.

---

## Pattern 11: Checkpoints

Creative stages should include at least one checkpoint where the agent pauses and the human steers. The agent completes a full unit of work, presents options or a draft, and the human redirects before the next unit begins. Checkpoints go between process steps, not within them.

Not every stage needs checkpoints. Linear stages (extract, render, validate) often run straight through. Creative stages (writing, design, ideation) benefit from at least one.

The Checkpoints section in a stage CONTEXT.md is a table:

```
| After Step | Agent Presents | Human Decides | Kind |
|------------|---------------|---------------|------|
| [step #] | [what to show] | [what to choose] | [Taste \| Spend \| Canon \| Ship] |
```

See Pattern 19 for review modes, `Kind` values, and the `, plan` flag. "Agent Presents" means shown on screen per Pattern 21, not just listed as paths.

---

## Pattern 12: Stage Audits

Creative and build stages should include an Audit section: a checklist the agent runs after completing the process but before writing to output/. Audits catch quality issues before they propagate downstream. Each check should be specific enough that pass/fail is unambiguous. Checks that used to be QA stops go here.

Not every stage needs an audit. Data extraction or file conversion stages may not benefit. Creative and build stages almost always do.

The Audit section in a stage CONTEXT.md is a table:

```
| Check | Pass Condition |
|-------|---------------|
| [Check name] | [What "passing" looks like] |
```

If any check fails, the agent revises before saving to output/.

---

## Pattern 13: Value Validation

Content-producing stages should define what types of value their output can deliver. Before the main creative work begins (ideally at a checkpoint), the agent and human should agree on which value types this specific piece will hit. This prevents "interesting but doesn't DO anything" output.

Value types are workspace-specific. A content workspace might use NOVEL, USABLE, QUESTION-GENERATING, INTERESTING. A course workspace might use TEACHES, PRACTICES, CHALLENGES. The framework is defined once in a reference file and used at every checkpoint.

---

## Pattern 14: Docs Over Outputs

Reference docs (design system, build conventions, skill rules) are the authoritative source for how to build. Previous stage outputs in `output/` folders are artifacts, not templates. Agents should not read other outputs to learn patterns.

This prevents copying from older, lower-quality work and ensures docs remain the single source of truth for quality standards. Early outputs are the worst outputs. If future agents learn from them, quality never improves.

---

## Pattern 15: Shared Constants

Workspaces that produce code should define a constants pattern. Configurable values (colors, fonts, timing, layout) live in shared files that all build outputs import from. The questionnaire populates these files once during onboarding. Change a value once, it updates everywhere.

This is Pattern 5 (Canonical Sources) applied to code values. Without shared constants, the same hex code or font name is hardcoded in every output file. Changing the brand color means a find-and-replace across every file ever built.

For non-code workspaces (content writing, course design), this pattern does not apply. Shared values live in reference docs instead.

---

## Pattern 16: Knowledge Layer

Some shared libraries and domain-specific workspace libraries maintain a **persistent reference library** across jobs. Unlike `stages/*/output/` (per-job handoffs), the knowledge layer is maintained reusable context and should be committed to version control.

Use a workspace-level `knowledge-layer/` folder with its own `CONTEXT.md` for selective section routing (same pattern as `brand-vault/CONTEXT.md`).

Canonical structure:

```
knowledge-layer/
├── CONTEXT.md              (routes to index, entries, patterns)
├── index.md                (catalog: slug, type, source, date, tags)
├── entries/                (one file per curated reference)
│   └── [slug]-reference.md
└── patterns/               (aggregated cross-reference insights)
    ├── visual-patterns.md
    └── copy-patterns.md
```

Rules:

- **Curation stage writes here.** A stage (typically after human approval) writes to `knowledge-layer/entries/` and updates `index.md` and `patterns/`. It does not treat the library as a transient handoff folder.
- **One entry per reference.** Each saved asset gets one canonical file. Other files point to it; do not duplicate extracted content.
- **Human taste gate.** Nothing enters the knowledge layer without explicit human approval at a checkpoint. The agent proposes; the human decides what gets saved.
- **Separate from brand-vault.** `brand-vault/` holds your authored identity (configured once at setup). `knowledge-layer/` holds swiped or collected references (grows forever).

Stage CONTEXT.md files that read from the knowledge layer should specify exact entry slugs or pattern sections in their Inputs table, not "load everything."

---

## Pattern 17: Direct Entry And Ownership

A request enters the workspace that makes the deliverable. Its brief stage captures the request, required context, constraints, format, and plan. Separate intake or planner workspaces are not required.

- Production owns job briefs, scripts, selections, edits, approvals, and delivery artifacts.
- Shared libraries own reusable records. Reading records does not require their maintenance workflow.
- Skills own reusable methods; tools and runtimes own executable implementation.
- Use pointers for facts owned elsewhere. Keep one job slug across related artifacts.
- A real cross-workspace handoff names the destination, entry stage, canonical inputs, and next action. A route bundle is optional when it helps that handoff.
- Existing accepted entry packets, specs, and bundles remain valid inputs. Moving them does not reopen locked decisions.
- Unsupported outputs need an explicit destination. Do not invent a replacement planning workspace.

The root `workspaces/README.md` selects production owners. `libraries/README.md` selects shared context owners. Starting guidance lives in the workspace map; shared handoff rules live in `_core/handoff-checkpoint.md`. Publishing procedures stay with their production owner. The builder under `_core/workspace-builder/` is an authoring utility.

---

## Pattern 18: Archive Boundaries

Archives keep inactive material available without letting it look like active guidance.

Use `_archive/` for tracked historical docs. Use `local-archive/` for old local files that should stay out of Git. Do not use archives as working folders.

Before archiving stage output, search for live references and confirm the file is not part of an active handoff. If a later stage still reads it, leave it in place.

Rules:

- **Tracked history lives in `_archive/`.** Superseded planning docs, retired workspace docs, and historical decision notes go here when they are safe to commit.
- **Local files live in `local-archive/`.** Bulky exports, renders, zips, temporary downloads, and non-reusable working files go here when they should not be committed.
- **Reusable media stays in media-library.** Raw media worth reusing belongs in `libraries/media/local-media/` with metadata in `libraries/media/assets/`.
- **Archive moves are recorded.** Add tracked moves to `_archive/index.md` with the original path, archive path, reason, and restore note.
- **Archives are not routing sources.** Agents should not load archive files unless the user asks for historical context.

---

## Pattern 19: Files Are the State

The files on disk are the state. Every fact has one home.

### One Home per Fact

| Fact | One home |
|---|---|
| What an artifact says | Its stage `output/[slug]/` file |
| A stage is done | Its output file exists |
| A piece is approved for reuse | Its row in `library/index.md` |
| A deliverable shipped | The approval block in its final render `manifest.md` |
| Job context and handoffs | The owning brief and relevant stage artifacts |
| Experiment history and publishing state | Video Production `publishing/` ledgers and queue |

### Review Modes

Host permission mode (what the agent may touch) and ICM review mode (when the agent stops to show work) are independent.

| Mode | Like | Agent stops at |
|---|---|---|
| `manual` | Ask every time | Every checkpoint in the stage files |
| `plan` | Plan mode | Once on the plan (and spend stops), then runs to the end |
| `taste` | Auto-accept edits | Taste, canon, and ship stops only |
| `auto` | Bypass | Nowhere. Present the finished work. |

- Default mode: `taste`.
- The owner can override per run in plain words (for example, "make the launch skit, auto").
- Record the mode in the run's first artifact (in animation: `review: taste` and optional `credit-cap: 5000` in `brief.md`).

### Stop Kinds

Each row in a stage `Checkpoints` table has a `Kind` column:

| Kind | Question | What happens |
|---|---|---|
| `Taste` | Do you like it? | Stops in `manual` and `taste`. Stops in `plan` only when flagged `, plan`. |
| `Spend` | Does it cost credits or render time? | Stops in `manual` and `plan`. Covered by the spend guardrail otherwise. |
| `Canon` | Does it change every future run? | Stops in every mode except `auto`. |
| `Ship` | Ready to post? | Stops in every mode except `auto`. |

- Add `, plan` when the stop is the run's plan (workspace docs state which stops carry `, plan`).
- There are no QA checkpoint rows. QA checks ("did the agent do it right?") belong in the stage's `Audit` table.
- A missing `Kind` column or a value outside the list reads as `unknown`.

### Mode Matrix

| Kind | `manual` | `plan` | `taste` | `auto` |
|---|---|---|---|---|
| Taste | stop | stop only if `plan` | stop | no |
| Spend | stop | stop | no (guardrail only) | no (guardrail only) |
| Canon | stop | stop | stop | no |
| Ship | stop | stop | stop | no |
| unknown | stop | stop | stop | no |

- `auto` stops nowhere. It never writes a canon or ship record on its own; it presents the finished work and lists the open canon and ship decisions.
- Audits run in every mode. In animation, the beat audit (every voiced line, beat, and set in the approved script plays in the render) is never skipped.
- A workspace with no `Kind` columns behaves like `manual`, except in `auto`.

### Spend Guardrail

Applies in every mode:

| Limit | Value | When hit |
|---|---|---|
| ElevenLabs credits per run | 5,000 | Stop before the call that would pass it. Show credits used and what is left to make. |
| One ElevenLabs call | 1,500 credits | Stop and show the dry run first. |
| Re-rolls of one line | 3 | Stop and ask. The script line may be the problem. |
| Full renders per run | 3 | Stop and ask. Use contact sheets and stills between renders. |

- Before any paid voice call, run the dry run and log credits in the `## Spend` section of `voice-manifest.md` ending with `Credits used: N of M`.
- The owner can raise a limit per run in plain words.
- Never run paid AI image or video generation without asking, in any mode.

### Progress from Files

- A stage is done for a slug when every declared output for that slug exists. Some exist: partial. None: not started.
- A run waits at a stop when a stage is done, the next stage in its lane has not started, and the done stage has a stop the run's mode keeps.
- A run is shipped when its final `manifest.md` contains an `## Approval` block (`Approved to ship: YYYY-MM-DD, ...`, with optional `sha256 <file>: <12-hex>`). If the hash is present and the file's hash differs, the run reads "changed since approval, review again".
- Only the owner creates canon rows (`approved` or `archived` in `library/index.md`) and ship approval blocks.
- No file proves an agent is running. Show file change times, never "agent working".
- Mid-stage stops leave no file. Readers list them but cannot detect them.

### Run Cards

- No separate run card is required. Preserve unique legacy decisions in owning job records; current state and approvals stay in stage artifacts.
- Publishing ledgers and performance reads remain canonical operational history. Approved reusable learning belongs in Business Memory.

### Not Used

- No `icm.yaml`.
- Agents do not need `.icm-workbench.json`. The app may read it for sidebar links.
- `VIEWS.md` is not workflow state. It holds layout and pointers only (Pattern 20).

---

## Pattern 20: Views Files

A workspace can declare how a viewer app lays it out. The declaration lives in one `VIEWS.md`, beside the workspace's `CONTEXT.md`. A workspace without one still works: the app shows a generic view of its folders, docs, media, and stage contracts.

`VIEWS.md` holds layout and source pointers only. Never put instructions, status, progress, or decisions in it. Those keep their homes under Pattern 19, and views point at them.

```markdown
# Views: Programmatic Animation

## Workshop

| Collection | Items from | Key | View | Detail |
|---|---|---|---|---|
| Characters | `library/index.md` where Type = character | Slug | gallery | Character |

### Character detail

| Panel | Source | View |
|---|---|---|
| Design sheet | `stages/workshop/02-design-sheet/output/{key}/*.png` | media |
| Pose sheets | `stages/workshop/03-rig/output/{key}/*.png` | compare |
| Rig notes | `stages/workshop/03-rig/output/{key}/rig.md` | document |

### Actions

| Action | Scope | Runs |
|---|---|---|
| Request revision | item: Character | `stages/workshop/03-rig/CONTEXT.md` |
```

Rules:

- **Sections.** Each `## Heading` is a section. Sections appear in file order, and the first one leads.
- **Items from.** A folder glob ending in `/` (each matching folder is an item, and its name is the key), or a Markdown table file with an optional `where Column = value` filter.
- **Key.** The table column that identifies an item. Leave it blank for folder globs.
- **View.** One of `gallery`, `table`, `document`, `media`, `compare`. Nothing else.
- **Detail.** Names a `### <Name> detail` heading. Its panels show in order. A gallery card's thumbnail is the first image in the first `media` panel.
- **Sources.** `{key}` becomes the item's key. Globs are allowed, and a glob with several matches shows all of them. Paths are relative to the workspace folder. A path starting with `/` is relative to the repo root, for media in `remotion/public/` and similar. No path may leave the repo.
- **Actions.** Scope is `workspace`, `collection: <name>`, or `item: <detail name>`. **Runs** points at the instruction file the agent should follow. An action prepares a prompt for the agent. It never runs anything by itself.
- **Gaps show.** A missing file shows as missing, with its path. An unknown view or column shows as unsupported, with the line it came from. Neither reads as empty.
- **Status comes from records.** Item status comes from its owning record (for example, the `Status` column in `library/index.md`), never from `VIEWS.md` and never from file presence alone.
- **Browsing changes nothing.** Opening a view never approves, promotes, ships, or catalogs anything.

Agents may edit `VIEWS.md` like any other ICM file, for example to add a collection or a panel. The app refreshes when it changes.

---

## Pattern 21: Show the Output

When a stage writes something the human should see, the agent opens it on their Mac. Paths in chat alone are not enough.

When:
- At every checkpoint the run's mode keeps, before asking the question.
- When a stage writes media: renders, contact sheets, design sheets, pose sheets, audio takes.
- When a brought file is ingested. Reveal where it landed.
- In `auto`, once at the end, on the finished work.

How:
- One main file: `open -R "<absolute path>"`. Finder opens with it selected.
- Several files: `open "<output folder>"`.
- A render to watch now: `open "<file>.mp4"`.
- At most three Finder windows per checkpoint. Prefer the folder over many files.
- Also list absolute paths in chat as links. Embed PNG and JPG stills inline with `![alt](path)`.
- A workspace's `VIEWS.md` panel sources are a good list of what to show.

Rules:
- Opening a file never approves, ships, promotes, or catalogs anything.
- A missing file is reported with its path. Do not open the parent folder as a fallback.
- macOS only. On another OS, list the paths and say the reveal was skipped.

---

## Quality Guardrails

- CONTEXT.md files: under 80 lines
- Reference files: under 200 lines (if longer, split into multiple files)
- Use plain English. Avoid jargon. If a term needs explaining, it is too specialized.
- No em dashes anywhere in the repo
- Every folder that should persist but starts empty gets a `.gitkeep` file
- Every markdown file should be readable by someone who understands markdown and git basics but does not have a deep engineering background
