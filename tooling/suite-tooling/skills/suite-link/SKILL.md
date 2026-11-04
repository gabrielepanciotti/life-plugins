---
name: suite-link
description: Use to install the suite's shared packages in development into a Life node, reading its suite.lock.json (after suite conform wrote it). Trigger: "link the packages", "suite link", "/suite-link".
---

# suite-link

Install the suite's shared packages in a node for development, reading `suite.lock.json`.

## When to use it
After `suite conform` (which writes the lock), to actually link the packages:
- `suite-backend-core` → `pip install -e` in the node backend venv.
- `@suite/design-system` → `npm link` in the node frontend.

## Commands
```
cd packages/shared
.venv/Scripts/python -m suite_core.nodes link <node_dir>     # one node
.venv/Scripts/python -m suite_core.nodes link --all <root>   # all nodes under root
```

## Notes
- Development only on this machine (where `Life` exists on the filesystem): does not touch Docker/prod or server-1.
- Idempotent: rerunning does not reinstall packages that are already linked (states `linked|skipped|na|error`).
- `na` = prerequisite missing (no backend venv or no `frontend/package.json`): this is not an error.
- Vault (nodes without packages) → no-op.
