---
name: suite-mcp-info
description: >
  Background knowledge on the suite-mcp server: the brain_*/db_*/graph_* tool families,
  per-node scoping via SUITE_TOOLSETS/TOOLS/EXCLUDE_TOOLS/READ_ONLY, and context-frugal
  output (CSV + counts, never blobs). Use when wiring a node's MCP tools or debugging scope.
user-invocable: true
---

# suite-mcp

One FastMCP server, mounted per node via `.mcp.json` with different env. Tool families are
tag-scoped: `SUITE_TOOLSETS` selects families (e.g. `db,brain`), `SUITE_TOOLS` is an allowlist,
`SUITE_EXCLUDE_TOOLS` always wins, `SUITE_READ_ONLY=1` suppresses write tools. Every tool
returns a derived answer (CSV preview + counts, snippets), never raw blobs; `db_query` injects
a LIMIT and rejects non-SELECT SQL.

## Tool families

### `db_*` (tag: `db`)
`db_schema`, `db_aggregate`, `db_query` — read-only by default.
`db_execute` — write path, only registered when `SUITE_READ_ONLY=0`.

### `brain_*` (tag: `brain`) — available as of T-E
Snippet-first hybrid search across the vault brain index.

- `brain_search(query, scope, node_id, subtree, top_k)` — vector+FTS fused via RRF;
  returns `[{path, heading, snippet, score}]` — **never** includes `content`/body.
  `scope`: `"node"` (single node), `"tree"` (subtree id list), `"all"` (whole vault).
- `brain_read(path, heading?)` — read a vault document or heading section (snippet-only).
- `brain_backlinks(path)` — list all vault nodes that wikilink to the given path.

**Note:** live pgvector index is pending (T-G follow-up). Until configured, all `brain_*`
tools return `{"error": "brain index not configured (pgvector pending)"}`. The in-memory
fake (`InMemoryStore` + `HashEmbedder`) is used for offline tests.

### `graph_*` (tag: `graph`) — available as of T-E
Wikilink graph traversal — fully offline, built from `VAULT_PATH` at call time.

- `graph_neighbors(name, direction)` — wikilink neighbors (`out`/`in`/`both`).
- `graph_path(source, target)` — shortest directed BFS path between two vault nodes;
  returns `[]` when no path exists.

Requires `VAULT_PATH` env var to point at the Obsidian vault root.
