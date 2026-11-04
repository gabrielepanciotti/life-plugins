---
name: node-forge
description: Forge a new, live Life node that meets the 9/9 DoD, including deep hierarchies (e.g. Health → Yoga → FaceYoga). An orchestrator on top of suite-new: the deterministic part uses `nodes forge`, and the judgment-based part uses the node-architect subagent. Triggers: "/node-forge", "forge a node", "create a tree of nodes", "bring a node to 9/9 DoD".
---

# /node-forge — forge a node (or tree) to a live 9/9 DoD

Extends `/suite-new`: after deterministic scaffolding, closes the gap to the **9
DoD dimensions** and can create **deep node trees**. Two parts:
**deterministic** (CLI commands, GUI-ready) + **judgment-based** (subagent `node-architect`).

## 0. Choose the shape
- **Type by level**: domain with UI → `fastapi-react-app`; specific leaf →
  `leaf` (brain-only, promotable). Use bridge/cli/fastapi-app/react-app as needed.
- **Hierarchy**: the tree lives in the **logical graph** (`life.graph.json`, parent→children);
  physical inheritance remains **flat** toward Life. Create **top-down** (parent first).
- **New top-level domain** (e.g. Health): forge it with `--new-cluster` (creates the cluster
  in the graph). Attach children with `--parent <graphId-del-parent>`.

## 1. Forge (deterministic)

```
cd packages/shared
.venv/Scripts/python -m suite_core.nodes forge "<DisplayName>" "<slug>" "<Cluster>" \
    --type <type> --dest "<path>" [--parent <graphId>] [--new-cluster]
```

Runs: `new` (scaffold+graph+ports+git+conform+link) → `docs-scaffold`, writes
`<repo>/forge.status.json` with judgment-based stages set to `pending` and the
`manifest`. Prints status for each stage. Safety: fail-fast validation before writes;
no rollback on late failure (check `git status` in `$SRV_ROOT/Life`).

Examples (Health tree):
```
# 1) top-level Health domain (new cluster)
forge "Health" "health" "Health" --type fastapi-react-app --dest "$SRV_ROOT/Health" --new-cluster
# 2) subdomain with UI
forge "Yoga" "yoga" "Health" --type fastapi-react-app --dest "$SRV_ROOT/Yoga" --parent health
# 3) brain-only leaf
forge "FaceYoga" "faceyoga" "Health" --type leaf --dest "$SRV_ROOT/FaceYoga" --parent yoga
```

## 2. Bring it to 9/9 (judgment) — delegate to the subagent

Run the **`node-architect`** subagent on each forged node. Complete, in the order given by the
`manifest`: **tooling grants** (+`apply`) → **true brain skeleton** (gate block exit 0)
→ **go-live** (DB+docker+HTTP200; `leaf` skip) → **`dod-whichck` loop** until 9/9.

## 3. Verify by running, not by assumption

```
.venv/Scripts/python -m suite_core.nodes dod-whichck --json "<path>"   # 9/9, no 🔴/🟡 (N/A OK on leaf)
.venv/Scripts/python -m suite_core.nodes brain-gate --mode block "<path>"   # exit 0
.venv/Scripts/python -m suite_core.nodes go-live --dry-run "<path>"          # docker/health plan
```

To show nodes in the galaxy, you need a **shell rebuild** (the graph is imported
statically); ports update at runtime via `/api/ports`. New nodes are registered
in `docs/docker-map.json` (via `go-live`), which `rebuild-life.ps1` also reads.

## CLI stages (reference)
`forge` · `docs-scaffold` · `go-live [--dry-run]` · `dod-whichck [--json]` — all in
`suite_core.nodes`. These are the commands the future **GUI** will invoke; `forge.status.json`
+ the `dod-whichck` JSON output are the display surface.

References: `docs/superpowers/specs/2026-07-01-node-forge-design.md`,
`docs/onboarding/node-standardization-roadmap.md` (DoD), `.claude/agents/node-architect.md`.

## Instance specifics

Run `python -m suite_core.nodes skill-overlay node-forge` and apply what it prints (it may print nothing).
