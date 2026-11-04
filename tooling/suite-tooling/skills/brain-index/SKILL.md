---
name: brain-index
description: >
  Use to regenerate llms.txt (and other derived indexes) by invoking the
  already-shipped wiki-sync engine. Wraps `suite_core.nodes wiki-sync`. Runs
  idempotently to resync index.md, llms.txt, and showcase.md. Trigger: "regenerate
  llms.txt", "/brain-index", "sync the index".
argument-hint: "[node-dir | --nearest start-dir]"
allowed-tools: Bash
---

# brain-index

Regenerate the AI-facing index (`llms.txt`) and derived files for a node's brain
(spec §5). Idempotent: creates or updates only when content changes.

1. From `Life/packages/shared`, run:
   ```bash
   .venv/Scripts/python -m suite_core.nodes wiki-sync --nearest <start-dir>
   # or for a specific node:
   .venv/Scripts/python -m suite_core.nodes wiki-sync <node-dir>
   ```
2. The command regenerates these together:
   - `brain/index.md` — text summary of notes by folder
   - `brain/llms.txt` — structured index for LLMs (list of `- [[name]] -- summary` per folder)
   - `brain/showcase.md` — snapshot with metrics (total notes, links, components, hubs)
3. **llms.txt** is the brain's "gateway document" for LLMs: it contains only note
   names and their summaries, never full text. Never edit it by hand — it is
   regenerated automatically from the brain content.
4. This skill is for **on-demand** regeneration. Regeneration already happens
   automatically in the Stop hook at every session (there is no need to invoke it
   routinely). Use it when adding or removing significant notes and you want an
   immediate sync, or when repairing a brain note and you want the index to
   reflect the change before handing off the work.

   See [[brain-showcase]], [[brain-note]].
