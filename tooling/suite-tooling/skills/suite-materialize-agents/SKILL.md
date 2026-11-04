---
name: suite-materialize-agents
description: >
  Use to (re)generate a Life node's subagents from its type + inherited archetypes.
  Writes <node>/.claude/agents/<slug>-<archetype>.md from the suite archetype templates.
  Run after creating a node or changing its type/archetypes. Wraps `suite_core.nodes agents`.
argument-hint: "[node-dir]"
allowed-tools: Bash
---

# Materialize a Life node's agents

1. From `Life/packages/shared`, run:
   ```bash
   .venv/Scripts/python -m suite_core.nodes agents <node-dir>
   ```
2. This resolves the node, computes its effective archetypes (declared + type defaults),
   and writes one `.claude/agents/<slug>-<archetype>.md` per archetype that has a template.
3. The generated agents are discovered by Claude Code via directory walk-up when working
   inside the node. Re-run after editing ancestor `node.config` or the node's type.
   See [[suite-resolve-node]] and [[suite-create-node]].
