---
name: brain-reconcile
description: >
  Use to additively bring an existing brain/ to Standard Brain — creates missing
  per-folder _index.md hubs and backfills frontmatter on notes lacking it, without
  ever renaming, moving, or deleting. Strictly additive. Run --dry-run first to
  inspect, then apply. Vault→profile mapping is indicative and per-node; set in
  node.config by the node owner, not by Life. Trigger: /brain-reconcile, "reconcile",
  "adopt standard brain", "reconcile brain".
argument-hint: "[--nearest] [--dry-run] <node-dir>"
allowed-tools: Bash
---

# brain-reconcile

Bring an existing vault into Standard Brain in a **strictly additive** way: create
missing folder `_index.md` files (for every folder that contains `.md` notes but has no
hub), and prepend the minimal frontmatter (6 required fields) to notes that lack it. Never
rename, move, delete, or rewrite existing content. Idempotent: a second run makes no
changes.

## Usage

### 1. Preliminary inspection (dry-run)
```bash
cd /path/to/node
python -m suite_core.nodes brain-reconcile --nearest --dry-run .
```

Read the report: it lists the `_index.md` files it would create (`+`) and the notes it
would backfill (`~`). If everything looks right, proceed to step 2.

### 2. Apply
```bash
python -m suite_core.nodes brain-reconcile --nearest .
```

Creates the hubs and backfills the frontmatter. Then inspect the result:

```bash
# Check quality with the gate
python -m suite_core.nodes brain-gate --mode warn --nearest .

# Regenerate derived files (index.md, llms.txt, showcase.md)
python -m suite_core.nodes wiki-sync --nearest .
```

## Strictly additive behavior

- **Create `_index.md`**: one for each recursive folder under `brain/` that contains
  at least one `.md` file but has no `_index.md`. Minimal frontmatter with 6 fields
  (title, summary, tags: hub, status: stub, created, updated), and a body with a list of
  wikilinks to the notes in that folder.
- **Backfill frontmatter**: prepend the YAML block to notes that lack it
  (`parse_frontmatter(text) is None`). Preserve the body verbatim. Never modify notes that
  already have FM, even if it is partial/invalid (the gate reports them; rewriting them is
  not reconcile's job).
- **Exclusions**: skip the `sources/` and `workspace/` subtrees (transient, consistent with
  the gate) and the `brain/` root (use `index.md`, not `_index.md`). Do NOT exclude the
  `private/` folder.
- **Idempotent**: a second run does not touch the `_index.md` files already created or the
  notes already backfilled.

## Vault → profile mapping (indicative, per node)

Reconcile is profile-agnostic. **The mapping is INDICATIVE and is set in the node's
`node.config`** (fields `brain_profile` and `numbering`), by the node owner, NOT by Life.
Examples for reference:

| Node | Vault | Profile/numbering | Notes |
|------|-------|-------------------|------|
| **it-vault** | `it-vault/` | `business` | complaint areas, SLA, product roadmap |
| **product-b** | `brain/` | `product` | planning solver, internal backlog |
| **PersonalChef** / **Travelers** | respective vaults | `personal-life` | recipes, trip planning |
| **AcademicAssistant** | `brain/` | `research` + `johnny-decimal` | course archives, literature |
| **product-d** | to be verified | TBD | property analytics |

**Life never decides another node’s profile.** Each node determines its own
`brain_profile` in `node.config`. Reconcile reads that setting during conformance;
if it is absent, it uses a neutral default (and logs the omission).

## Reference commands (from `packages/shared`)
```bash
# Dry-run on a specific node
.venv/Scripts/python -m suite_core.nodes brain-reconcile --dry-run /path/to/node

# Apply to the nearest node (walk up CWD→root)
.venv/Scripts/python -m suite_core.nodes brain-reconcile --nearest /path/to/start

# Dry-run + apply + gate + wiki-sync (full pipeline)
.venv/Scripts/python -m suite_core.nodes brain-reconcile --dry-run .
.venv/Scripts/python -m suite_core.nodes brain-reconcile .
.venv/Scripts/python -m suite_core.nodes brain-gate --mode warn brain
.venv/Scripts/python -m suite_core.nodes wiki-sync .
```

## Integration with the brain workflow

- Complements **[[brain-gate]]** (which checks quality: complete frontmatter, length,
  wikilinks, no broken links, no orphans, one component). Run reconcile BEFORE the gate.
- Complements **[[brain-note]]** (skill for creating atomic notes with structured
  frontmatter). Reconcile backfills "orphaned" notes that lacked FM; brain-note creates
  well-formed new notes.
- Does not touch `sources/` (raw data) or `workspace/` (transient scratch space).

## Limitations and responsibilities

- Reconcile does NOT improve existing content. If a note’s body is wrong, the owner must
  rewrite it; reconcile only backfills its FM.
- Reconcile does NOT apply the profile to content (numbering, profile-specific tags, etc.).
  The profile can only be applied to new notes (brain-note) or during manual refactors.
- If the vault→profile mapping is wrong in `node.config`, reconcile does NOT fix it —
  the node owner is responsible for correcting it.

See [[suite-conform]] (full node provisioning) and [[brain-gate]] (quality audit).

## Instance specifics

Run `python -m suite_core.nodes skill-overlay brain-reconcile` and apply what it prints (it may print nothing).
