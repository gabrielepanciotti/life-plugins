# How to write an effective skill

Index: Three levels · Description · Tone · Length and structure · Where files live · Examples · Keywords · Final checklist

The full standard is the 12 rules in `~/.claude/docs/controllo-skill.md`; this file
provides a practical version for authors.

## Three levels

1. **Name and description**: always in context. Claude reads them to choose which skill to open.
2. **SKILL.md body**: loaded when the skill starts.
3. **Linked files** (`references/`, `scripts/`): opened only when needed.

So SKILL.md stays short and serves as an index; material needed for some tasks belongs in a
separate file linked directly from SKILL.md.

## Description

Form: «What it does. Use it when <conditions and trigger phrases>.» In Italian, third person
(«Prepares estimates», never «I’ll help you with…»).

- Says what it does and when to use it. Do not describe the steps: if it summarizes them, Claude may follow the
  description instead of reading the body.
- Include phrases the user would actually say, in quotation marks. They are also used by the router
  (`hooks/skill-inneschi.tsv`).
- A vague description or one without a «when» may trigger the skill randomly or never.
- `allowed-tools`: only those used.

Example:

```yaml
description: Create FastAPI endpoints using the project's standard patterns (RBAC, soft delete, CRUD). Use when asked for a new endpoint, route, or API in a FastAPI project.
```

## Tone

- Use the imperative or infinitive: «Read the file», not «You should read».
- A rule with its reason beside it is more effective than a rule in all caps. With newer
  models, repeated capitalized words (such as shouted «never» or «always») worsen results: the skill becomes rigid.
- Write only what Claude cannot know: internal rules, names, paths through
  variables, and commands. Do not explain what an invoice is.
- Do not ask Claude to transcribe its reasoning; ask for the answer and a brief
  explanation.
- Use one term for each thing and one default solution instead of five alternatives.
- No dates that expire in the body: state the current method clearly and keep history in
  `references/storia.md`.

## Length and structure

- Keep SKILL.md under **500 lines** (excluding the header). Move anything longer to `references/`.
- Put instructions that must not be lost at the top: after a long conversation Claude Code
  keeps only the beginning of the skill.
- A file over 100 lines starts with `Index:`.
- Add sections only when needed: decision path, `## Serve`, steps, output template,
  final review, linked files. No section is mandatory.
- For more than 3–4 ordered steps: use numbered steps, a «Copy and check off» list, and say under each
  check where to return if it fails.
- Where quality matters, include a final check and «Finish only when…». Where style matters,
  include two or three request-result pairs.
- Use a flowchart (graphviz) only for non-obvious decisions; number linear lists and use tables for
  reference material.

## Where files live

```
skill-name/
├── SKILL.md
├── references/   details, each linked from SKILL.md; names describe their contents
├── scripts/      state whether Claude runs or reads them
├── evals/        prove.md and, if needed, evals.json / val.json
└── assets/       files used in the output
```

Claude does not know a file exists unless SKILL.md names it.

## Examples

One complete, real example is better than three mediocre ones: drawn from real work, annotated
with why it works rather than what it does, and ready to adapt.

## Keywords

Help with selection: verbatim error messages, symptoms («flaky test», «failed
migration»), synonyms («endpoint / route / API»), and tool names (Alembic, FastAPI).

## Final checklist

Structure
- [ ] Frontmatter with `name` and `description`; description in Italian, third person, with a «when»
- [ ] SKILL.md under 500 lines; index in files over 100 lines
- [ ] Every linked file exists and is named in SKILL.md
- [ ] `## Serve` with installation commands; no personal or Windows paths
- [ ] Full names of MCP tools

Quality
- [ ] Decision path at the top if the route changes; templates identified as identical or adaptable
- [ ] «Copy and check off» list with a «go back» direction and final check
- [ ] Script error messages say what is missing and what is present
- [ ] No expiring dates or excessive capitalization

Tests
- [ ] `evals/prove.md` with at least 3 real requests, tried with and without the skill in a
      new conversation
- [ ] Automated evals (8–12 cases, at least 60% robust assertions) only for skills with
      many branches or for the loop in step 5
