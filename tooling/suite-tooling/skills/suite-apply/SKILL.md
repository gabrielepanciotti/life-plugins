---
name: suite-apply
description: >
  Use to (re)apply a suite node's tooling materialization: regenerate its
  node.config.resolved.json and .claude/agents/*.md from the inherited config +
  archetypes. Non-invasive (never touches settings or enables plugins). Wraps
  `suite_core.nodes apply`. The SessionStart hook runs this automatically for the
  nearest node; invoke manually after editing an ancestor node.config.
argument-hint: "[node-dir | --nearest start-dir]"
allowed-tools: Bash
---

# Apply suite node tooling

1. From the suite's `packages/shared` directory, run either:
   ```bash
   .venv/Scripts/python -m suite_core.nodes apply <node-dir>
   # or, from anywhere inside a node, find the nearest and apply it:
   .venv/Scripts/python -m suite_core.nodes apply --nearest <start-dir>
   ```
2. This regenerates `node.config.resolved.json` (gitignored) and the node's
   `.claude/agents/*.md` from its inherited archetypes — idempotently.
3. It is NON-INVASIVE: it never edits settings.json, never enables plugins, never
   touches ancestor nodes. Safe to run repeatedly. See [[suite-resolve-node]],
   [[suite-materialize-agents]].

## Instance specifics

Run `python -m suite_core.nodes skill-overlay suite-apply` and apply what it prints (it may print nothing).
