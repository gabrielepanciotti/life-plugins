---
name: brain-dashboard
description: >
  Use to generate a static offline HTML dashboard of a Life node's brain — shows
  metric cards (total/content/hubs/links/components), per-folder table, and hub
  list. Wraps `suite_core.nodes brain-dashboard`. Idempotent; visual counterpart
  to [[brain-showcase]] (textual). Trigger: "generate the dashboard", "/brain-dashboard",
  "brain dashboard".
argument-hint: "[node-dir | --nearest start-dir]"
allowed-tools: Bash
---

# brain-dashboard

Generate a static offline HTML dashboard of a node's `brain/`: visual metrics,
per-folder table, and hub list. No external resources (opens in a browser
without a connection).

1. From `Life/packages/shared`, run:
   ```bash
   .venv/Scripts/python -m suite_core.nodes brain-dashboard --nearest <start-dir>
   # or for a specific node:
   .venv/Scripts/python -m suite_core.nodes brain-dashboard <node-dir>
   ```
2. Writes `brain/dashboard.html` (offline, complete, no HTTP/HTTPS).
3. Displays: (1) metric cards (total notes, content, hubs, links, connected
   components); (2) a table with note counts per folder; (3) a hub list with
   summaries.
4. Idempotent: rewrites only when the content differs.
5. It is the **visual** counterpart to `/brain-showcase` (text report): use this
   for an interactive browser view, and showcase for a Markdown snapshot.

   See [[brain-showcase]], [[brain-audit]].
