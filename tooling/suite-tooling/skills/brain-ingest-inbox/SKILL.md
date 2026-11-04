---
name: brain-ingest-inbox
description: >
  Use to drain the normative inbox queue of a Life node's brain — turns the raw
  PDFs/HTML that the watcher (scripts/watcher/watch_fonti.py) downloaded into
  atomic brain notes conforming to the Standard Brain, then ticks the queue
  rows. Complements the deterministic watcher (fetch+diff+dedup) with the LLM
  quality step. Trigger: "ingest updates", "clear the regulatory inbox",
  "/brain-ingest-inbox".
argument-hint: "[node-dir, default .]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# brain-ingest-inbox — from watcher queue to brain notes

The deterministic watcher (`scripts/watcher/watch_fonti.py`, scheduled twice a day)
downloads regulatory updates (ARERA resolutions/DCOs, updated integrated texts,
GSE news, filtered Official Gazette items) to `brain/sources/` and queues one row
per item in `brain/sources/_inbox-queue.md`. This skill performs the quality step:
PDF → note.

## Procedure

1. Read `brain/sources/_inbox-queue.md`: process ONLY unchecked rows (`- [ ]`).
2. For each row: read the downloaded file (path in the row; PDFs with the Read tool).
3. Choose the domain from the taxonomy: `eel` sector → 01/03/05/07/12 by topic;
   `gas` → 02/07; `com` → by topic (Offers Portal→06, SII→04, quality→08,
   unbundling→10); GSE news on CER/efficiency/GO → 13; tax/excise → 09.
4. Write the atomic note in the domain (Standard Brain rules, see [[brain-note]]):
   - complete frontmatter (`status: review`, tag `normativa` + sector);
   - what the act establishes, who it applies to, effective dates;
   - potential impact for an electricity/gas seller ONLY if inferable from the text,
     otherwise `[TO DEFINE]`;
   - resolution reference + URL + source path at the end;
   - >=3 resolvable wikilinks (integrated-text spines: [[tiv]], [[tiqv]],
     [[timoe]]…, or related notes); backlink from the domain's `_index.md`.
   - If the act amends an integrated text, update the related spine
     ("Updates" section + possible `status: superseded` on the old note).
5. Act outside seller scope (waste, water, local distribution concessions):
   do NOT create the note; check the row with `(skip: outside seller scope)`.
6. Check off processed rows (`- [x]`).
7. Finish with: `.venv/Scripts/python -m suite_core.nodes wiki-sync <node>` and
   `.venv/Scripts/python -m suite_core.nodes brain-gate <node> --mode warn`;
   fix any violations introduced.

## Notes

- Never invent: content comes from the downloaded PDF, not memory.
- Zero PII (also applies to cases mentioned inside resolutions: generalize).
- The queue is idempotent: rows already marked `- [x]` are not processed again.
