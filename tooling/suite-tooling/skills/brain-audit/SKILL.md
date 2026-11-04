---
name: brain-audit
description: >
  Use to run the brain quality audit in warn mode — read-only inspection
  that checks frontmatter completeness, note length (<=300 lines), >=3 outgoing
  wikilinks, no broken links, no orphans, and a single connected component.
  Wraps `suite_core.nodes brain-gate --mode warn`. Never modifies notes.
  Trigger: "brain audit", "/brain-audit", "check for broken notes".
argument-hint: "[node-dir | --nearest start-dir]"
allowed-tools: Bash
---

# brain-audit

Read-only audit of a brain: run the gate in warn mode to inspect note quality
without changing any notes. Useful for a quick check before making corrections
or for periodic validation.

1. From `Life/packages/shared`, run:
   ```bash
   .venv/Scripts/python -m suite_core.nodes brain-gate --mode warn --nearest <start-dir>
     # or target a specific node:
   .venv/Scripts/python -m suite_core.nodes brain-gate --mode warn <node-dir>
   ```

2. The six read-only checks are:
   - (1) Complete frontmatter (`title`/`summary`/`tags`/`status`/`created`/`updated`)
   - (2) Body has at most 300 lines
   - (3) At least three valid outgoing wikilinks (`_index.md` files are exempt)
   - (4) No broken links (wikilinks pointing to missing notes)
   - (5) No orphans (notes with no incoming links)
   - (6) One connected component per node (the brain is connected, not fragmented)

3. **Warn mode** (audit): prints violations and exits with status 0.
   Violations do not block; the report is informational. Use this for periodic
   audits and to diagnose the current state.

4. **Correction cycle** (until there are no errors):
   - Read the audit report and identify violations by category.
   - To correct them, use [[brain-gate]] in **block mode** to enforce the rules,
     or use [[brain-note]] to rewrite or split defective notes.
   - Validate the result by running `brain-audit` again until the report is clear.

5. **Deprecation**: this skill replaces `/vault-audit` (vault-core). Life's
   unified gate replaces the vault audit mechanism.

Vedi [[brain-gate]], [[brain-note]].

## Instance specifics

Run `python -m suite_core.nodes skill-overlay brain-audit` and apply the
instance appendix; it may be empty.
