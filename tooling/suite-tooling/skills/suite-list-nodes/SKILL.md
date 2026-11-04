---
name: suite-list-nodes
description: >
  Use to list every node in the Life monorepo tree with its resolved type and
  inherited tooling counts. Wraps `suite_core.nodes list`.
argument-hint: "[root-dir]"
allowed-tools: Bash
---

# List Life nodes

1. From `Life/packages/shared`, run:
   ```bash
   .venv/Scripts/python -m suite_core.nodes list <root-dir>
   ```
   (root-dir is usually the Life repo root.)
2. Each line shows `<relpath>  [<resolvedType>]  caps=N agents=N toolsets=N`.
3. Use this to audit the tree and spot nodes missing a type or tooling.
