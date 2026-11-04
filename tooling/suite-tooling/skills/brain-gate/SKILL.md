---
name: brain-gate
description: >
  Use to run the 6-rule brain quality gate on a Life node — checks frontmatter
  completeness, note length (<=300 lines), >=3 outgoing wikilinks, no broken
  links, no orphans, and a single connected component. Wraps
  `suite_core.nodes brain-gate`. Warn mode reports without blocking; block mode
  exits non-zero on violations. Trigger: "check the brain", "brain gate",
  "/brain-gate".
argument-hint: "[--mode warn|block] [node-dir | --nearest start-dir]"
allowed-tools: Bash
---

# brain-gate

Validate a node's `brain/` notes against the 6 company-brain rules
(spec §4). Read-only: never modifies notes. Skips `sources/` and `workspace/`
and managed files (`index.md`, `CHANGELOG.md`, `_README.md`); `_index.md` files
are exempt from minimum wikilink and orphan counts.

1. From `Life/packages/shared`, run:
   ```bash
   .venv/Scripts/python -m suite_core.nodes brain-gate --nearest <start-dir>
   # or for a specific node, in block mode:
   .venv/Scripts/python -m suite_core.nodes brain-gate --mode block <node-dir>
   ```
2. The 6 rules: (1) complete frontmatter `title/summary/tags/status/created/updated`;
   (2) body <=300 lines; (3) >=3 valid outgoing wikilinks; (4) no broken links;
   (5) no orphans; (6) a single connected component per node.
3. **Warn mode** (default): prints the report, exit 0 — this is what runs in the
   Stop hook at every session. **Block mode**: exit 1 if there are violations,
   for final cleanup of a node.
4. The gate complements **lifegate** (which guards the public/private boundary):
   this checks note quality, not visibility.

   See [[suite-conform]] (brain scaffold) and [[suite-resolve-node]].
