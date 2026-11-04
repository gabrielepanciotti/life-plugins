---
name: brain-note
description: >
  Procedural skill for creating and splitting atomic notes in a node’s brain/.
  Complete required frontmatter (title/summary/tags/status/created/updated),
  hub-first (create the folder index.md first, ≥3 outgoing wikilinks per note, ≤300 lines
  in the body), domain-prefixed naming (self-…, cliente-…, kpi-…, concetto-…,
  persona-…). Absorbs vault-core types (decision/feature/postmortem/edit)
  as note tags `type/...`, not separate systems. Deprecates /vault-edit|feature|decision|postmortem.
  After writing, suggest wiki-sync and /brain-gate. Trigger: "write a note
  in the brain", "/brain-note", "document X in the brain".
argument-hint: "[node-dir | --nearest start-dir] [type: decision|feature|postmortem|edit]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# brain-note

Create and organize atomic notes in a node’s `brain/` using the company-brain model
(spec §2). Notes are the foundation of distributed knowledge: hard facts, decisions,
people, areas, and KPIs. Well-written notes keep the system reliable.

## Required frontmatter (6 fields)

Every note MUST have this frontmatter — see [[brain-gate]] for the six rules:

```yaml
---
title: Titolo della nota
summary: Una riga, riassunto dell'idea
tags: [tag1, tag2, type/decision]  # tags liberi; type/... per vault-legacy
status: draft|active|archived
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Status meanings:**
- `draft` — note in progress, not yet consolidated
- `active` — operational note, established knowledge
- `archived` — superseded or no longer relevant note

**Tags — model:**
- Free-form: `kpi`, `person-chiave`, `problema`, `soluzione`, etc.
- **Absorb vault-core types**: when writing a decision/feature/postmortem/edit note,
  add the matching tag: `type/decision`, `type/feature`, `type/postmortem`, `type/edit`.
  Do not create separate systems; a note can have the tag `type/decision` and be an ordinary note.

## Hub-first: the brain’s sensory organs

The brain works through hubs (`_index.md` in each folder). Before writing a content note,
write its folder’s hub:

```
brain/
├── self/                    # who I am (hub: who I am as a company)
│   ├── _index.md           # hub — write this FIRST
│   ├── self-id.md          # concrete notes
│   └── self-vision.md
├── clienti/                 # hub: portfolio
│   ├── _index.md           # hub
│   ├── cliente-acme.md
│   └── cliente-globex.md
└── kpi/
    ├── _index.md           # hub
    ├── kpi-mrr.md
    └── kpi-churn.md
```

**Rule:** every `_index.md` is a hub — the note’s point of contact with the outside world.
- Summarize the folder in 2-3 lines
- List the notes below with a brief summary (`[[nota-name]]` — brief summary)
- Link to external sources where relevant (doc, api, spec)

## Naming — domain-prefixed kebab-case

Avoid generic names. Give every note a **domain prefix** that makes its context clear:

| Prefix     | Meaning | Examples |
|---|---|---|
| `self-…` | Organizational identity | `self-id`, `self-vision`, `self-valori` |
| `cliente-…` | External person or organization | `cliente-acme`, `cliente-bob-sales` |
| `kpi-…` | Metrics and measures | `kpi-mrr`, `kpi-churn-rate`, `kpi-ltv` |
| `concetto-…` | Technical or domain abstractions | `concetto-monorepo`, `concetto-fractal-network` |
| `persona-…` | Internal role or user type | `persona-product-manager`, `persona-developer` |

**Unique-name rule:** the name (without the `.md` extension) must be **unique across the entire brain**.
If you find an accidental duplicate, add a note explaining the intent (merge, rename, or deliberate choice).

## Body: at least 3 outgoing wikilinks, at most 300 lines

Every note must:
- **Link to at least three other notes** (`[[nome-nota]]` — free text; the wiki is intelligent)
- **Stay under 300 lines** — if it grows, split it into atomic notes
- Have strong backlinks: if a note X links to Y, Y must link back to X (or to a hub)

Write **natural prose**, not lists. LLM readers handle continuous prose better.

## Absorb vault-core types

The six `/vault-*` skills are consolidated here. **Do NOT create duplicate systems.**

Usage model:
- A **decision** → note with `tags: [..., type/decision]`, `status: active` (until revoked)
- A **feature/epic** → note with `type/feature`, link to the roadmap
- A **postmortem** → `type/postmortem`, include the date and root cause, linking relevant notes
- An **edit/refactor** → `type/edit`, state what changes and why

Deprecation: the skills `/vault-edit`, `/vault-feature`, `/vault-decision`, `/vault-postmortem`
continue to work as a fallback until you adopt Standard Brain. The Life network uses
this engine; legacy vaults become inactive.

## Creation workflow

1. **Plan**: what to document, where in the brain (which folder), type/prefix.
2. **Hub first**: if the folder has no `_index.md`, write one. It must have ≥3 links to notes below.
3. **Atomic note**: complete frontmatter, body of 50–250 lines (natural prose), ≥3 wikilinks.
4. **Backlink**: ensure a hub or broader note links back to it.
5. **Validation**: afterward, run [[brain-gate]] to report issues; `/brain-audit` for a full report.
6. **Regenerate derivatives**: run `wiki-sync` to regenerate `index.md`/`llms.txt`/`showcase.md` automatically.

## After writing

Run (from Life/packages/shared):

```bash
# Regenerate indexes + AI port
.venv/Scripts/python -m suite_core.nodes wiki-sync --nearest <start-dir>

# Validation — full report
.venv/Scripts/python -m suite_core.nodes brain-gate --mode warn --nearest <start-dir>
```

In block mode (corrective cycle):
```bash
.venv/Scripts/python -m suite_core.nodes brain-gate --mode block <node-dir>
```

If a violation appears, return here, fix the frontmatter/wikilinks/length, and validate again.

See [[brain-gate]], [[brain-canon]], [[brain-index]].

## Instance specifics

Run `python -m suite_core.nodes skill-overlay brain-note` and apply what it prints (it may print nothing).
