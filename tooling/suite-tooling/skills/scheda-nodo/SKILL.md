---
name: scheda-nodo
description: >
  Use when the user asks for a full node overview, wants to generate or regenerate
  the node card, or scaffold the /overview endpoint and NodeOverview page.
  Triggers: "/scheda-nodo", "node overview", "node card", "generate card",
  "regenerate card".
  Wraps `suite_core.nodes node-overview` (deterministic generator) and,
  for fastapi-react-app nodes, scaffolds/updates the live endpoint and frontend page.
argument-hint: "[node-dir | --nearest start-dir]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# node-overview

Generate (or regenerate) the two node overview artifacts:

1. `brain/NODE-OVERVIEW.md` — brain document that passes the gate (≥3 outgoing wikilinks)
2. `backend/app/overview.manifest.json` — static manifest consumed by the live endpoint

## Procedure

### Step 1 — Run the deterministic generator

From the root of `packages/shared`:

```bash
.venv/Scripts/python -m suite_core.nodes node-overview --nearest <start-dir>
# or for a specific node:
.venv/Scripts/python -m suite_core.nodes node-overview <node-dir>
```

The output reports `manifest=<path> doc=<path> changed=true/false`.
Idempotent: rewrites only if the content (excluding `generated_at`) has changed.

### Step 2 — Node `*-react-app`: `/overview` endpoint and `NodeOverview` page

If the node has `type: fastapi-react-app` (or a similar type with a React frontend):

- **Backend already present** (`backend/app/api/overview.py` and `backend/app/services/overview.py`
  exist) → skip scaffolding; the newly written manifest is sufficient.
- **Backend is absent** → scaffold using the reference template
  (`${SRV_ROOT}/product-a/backend/app/api/overview.py` and `${SRV_ROOT}/product-a/backend/app/services/overview.py`),
  adapting the slug/name/ports to the target node.

Frontend (`frontend/src/components/NodeOverview.tsx` and `frontend/src/hooks/useNodeOverview.ts`):
- Use `${SRV_ROOT}/product-a/frontend/src/components/NodeOverview.tsx` as the reference template.
- If the page already exists, do not overwrite it — the updated manifest is sufficient.
- If absent, scaffold the component and add `"overview"` to the view state in `App.tsx`
  with the **ⓘ Node overview** button in the header.

### Step 3 — Validate the brain document

```bash
.venv/Scripts/python -m suite_core.nodes wiki-sync --nearest <node-dir>
.venv/Scripts/python -m suite_core.nodes brain-gate --mode warn --nearest <node-dir>
```

If `brain-gate` reports errors for `NODE-OVERVIEW.md`, check that the wikilinks point
to existing notes in the node brain. The document automatically generates links to
`[[README]]`, `[[overview]]`, `[[architecture-engine]]` — if any are missing, add
the missing notes or update the document to point to real notes.

### Step 4 — Summary

Report:
- Manifest path (`backend/app/overview.manifest.json` or root)
- Document path (`brain/NODE-OVERVIEW.md`)
- Status `changed: true/false`
- Result `brain-gate` (OK / warnings)

## Operational notes

- The manifest **does not include** `database` or `live` — these sections are added live
  by the `GET /overview` endpoint on each request.
- After a significant node change (new functions, new integrations), run
  `/scheda-nodo` again to update both artifacts.
- If the node does not yet have a backend/frontend (CLI-only), the generator produces only
  `brain/NODE-OVERVIEW.md` (the manifest is written to the node root).

## See also

Related skills: [[brain-dashboard]] (HTML brain dashboard), [[brain-gate]] (validation), [[wiki-sync]].

## Instance specifics

Run `python -m suite_core.nodes skill-overlay scheda-nodo` and apply what it prints (it may print nothing).
