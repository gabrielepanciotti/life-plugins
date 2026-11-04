---
name: suite-resolve-node
description: >
  Use to resolve a Life node's effective configuration — walk its inherits chain,
  compose tooling/capabilities/agents/mcp (additive arrays, nearest-wins scalars),
  and materialize node.config.resolved.json. Wraps `suite_core.nodes resolve`.
argument-hint: "[node-dir]"
allowed-tools: Bash
---

# Resolve a Life node

1. From `Life/packages/shared`, run:
   ```bash
   .venv/Scripts/python -m suite_core.nodes resolve <node-dir>
   ```
2. The command prints the resolved config and writes `<node-dir>/node.config.resolved.json`
   (gitignored — generated, never committed).
3. Use the resolved `agents.archetypes`, `mcp.toolsets`, and `tooling` to understand
   what this node inherits. Re-run after editing any ancestor `node.config`.
