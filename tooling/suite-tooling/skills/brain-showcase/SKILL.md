---
name: brain-showcase
description: >
  Use to regenerate showcase.md — a textual snapshot of the brain's structure,
  content, and connectivity. Wraps `suite_core.nodes wiki-sync`, which regenerates
  index.md, llms.txt, and showcase.md together (idempotently). Trigger: "generate
  showcase", "/brain-showcase".
argument-hint: "[node-dir | --nearest start-dir]"
allowed-tools: Bash
---

# brain-showcase

Regenerate `showcase.md` — a static textual snapshot of the structure and
connectivity of a node’s `brain/`. It does not modify notes; it only reads
and reports aggregate metrics.

1. From `Life/packages/shared`, run:
   ```bash
   .venv/Scripts/python -m suite_core.nodes wiki-sync --nearest <start-dir>
   # or for a specific node:
   .venv/Scripts/python -m suite_core.nodes wiki-sync <node-dir>
   ```
2. The command regenerates **three derived files** together: `index.md` (folder
   folder), `llms.txt` (AI entry point — lists of notes with summaries),
   `showcase.md` (this file). Idempotent: it does not change files when their
   content is identical.
3. **Contents of `showcase.md`**: an overall snapshot of the network of notes
   in the brain. It contains: (1) counts — total notes / content notes /
   hub (`_index.md`) / link totali / componenti connesse; (2) tabella per
   cartella con conteggi; (3) list of hubs with their summaries;
   (4) network health indicators (orphans, broken links — reported in
   [`brain-audit`]).
4. **For an offline visual view**: use [[brain-dashboard]] (static HTML,
   readable in a browser, same engine, metrics + interactive interface).
   `showcase.md` is the text format for versioning and archiving.

   See [[brain-index]], [[brain-dashboard]].

## Instance specifics

Run `python -m suite_core.nodes skill-overlay brain-showcase` and apply what it prints (it may print nothing).
