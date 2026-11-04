#!/usr/bin/env bash
# Stop hook: regenerate the nearest node's wiki index, and re-index the brain
# vector store only if brain/*.md changed. Best-effort: never blocks the session.
set +e
SUITE_ROOT="${CLAUDE_PLUGIN_ROOT}/../.."
SUITE_SHARED="${SUITE_ROOT}/packages/shared"
SUITE_MCP="${CLAUDE_PLUGIN_ROOT}/../suite-mcp"
MCP_PY="${SUITE_MCP}/.venv/Scripts/python"; [ -x "$MCP_PY" ] || MCP_PY="${SUITE_MCP}/.venv/bin/python"
START="${CLAUDE_PROJECT_DIR:-$PWD}"

# Pick the first interpreter that can actually IMPORT suite_core, rather than the
# first that exists at a guessed path: not every box has a venv under
# packages/shared (the Linux dev boxes keep a single venv in backend/), and there
# the hook used to skip silently at every turn — the brain simply stopped
# regenerating and nothing said so. PYTHONPATH is exported so the fallbacks can
# reach suite_core at all.
export PYTHONPATH="${SUITE_SHARED}${PYTHONPATH:+:${PYTHONPATH}}"
PY=""
for cand in "${SUITE_SHARED}/.venv/Scripts/python" "${SUITE_SHARED}/.venv/bin/python" \
            "${SUITE_ROOT}/backend/.venv/Scripts/python" "${SUITE_ROOT}/backend/.venv/bin/python" \
            "$(command -v python3 2>/dev/null)"; do
  { [ -n "$cand" ] && [ -x "$cand" ]; } || continue
  "$cand" -c "import suite_core" >/dev/null 2>&1 || continue
  PY="$cand"; break
done
[ -n "$PY" ] || { echo "[wiki-sync] no Python interpreter can import suite_core — skipping" >&2; exit 0; }

# 1) regenerate the public index
"$PY" -m suite_core.nodes wiki-sync --nearest "$START" >&2 2>&1

# 2) re-index only if brain markdown changed in the working tree
if git -C "$START" status --porcelain -- 'brain/**/*.md' '**/brain/**/*.md' 2>/dev/null | grep -q .; then
  # A hook inherits the session's environment, not the repo's .env — so
  # BRAIN_DB_URL was never set and the reindex skipped at every single turn.
  # Load it here (per-device, gitignored) unless the environment already
  # provides one, which stays authoritative.
  if [ -z "${BRAIN_DB_URL:-}" ] && [ -r "${SUITE_ROOT}/.env" ]; then
    BRAIN_DB_URL="$(sed -n 's/^[[:space:]]*BRAIN_DB_URL=//p' "${SUITE_ROOT}/.env" | tail -1)"
  fi
  if [ -x "$MCP_PY" ] && [ -n "${BRAIN_DB_URL:-}" ]; then
  # `--incremental`: rewrite only notes whose hash changed, usually one or two,
  # rather than reprocessing the whole tree (which takes minutes because every
  # chunk must be embedded again). Run in the background under a lock: an empty
  # index still requires a full reindex, and the lock prevents nearby sessions
  # from writing to the same database at once.
    # One indexer per brain database, not per path: every worktree of a repo has
    # its own path and used to start its own ~2 GB indexer (Life#313). The DSN is
    # hashed, never written in clear into the lock name.
    LOCK="${TMPDIR:-/tmp}/suite-wiki-sync-db-$(printf '%s' "$BRAIN_DB_URL" | cksum | cut -d' ' -f1).lock"
    LOG_DIR="${HOME}/.life/logs"; mkdir -p "$LOG_DIR" 2>/dev/null
    if mkdir "$LOCK" 2>/dev/null; then
      # Pass it as an environment variable, not `--dsn`: process arguments are
      # visible to local users via `ps`, and the DSN contains the database
      # password. The indexer reads BRAIN_DB_URL itself. Its output (peak memory,
      # or why it stopped over budget) goes to brain_indexing.log.
      (
        { echo "$(date -u +%FT%TZ) brain_indexing.index_incremental start $START"
          BRAIN_DB_URL="$BRAIN_DB_URL" "$MCP_PY" -m suite_mcp.indexer --incremental "$START" 2>&1
          echo "$(date -u +%FT%TZ) brain_indexing.index_incremental exit $?"
        } >>"$LOG_DIR/brain_indexing.log" 2>/dev/null
        rmdir "$LOCK" 2>/dev/null
      ) &
      echo "[wiki-sync] brain reindex started in the background" >&2
    else
      echo "[wiki-sync] reindex already running — skipping this session" >&2
    fi
  else
    echo "[wiki-sync] brain changed but BRAIN_DB_URL (or the suite-mcp venv) is missing — skipping reindex" >&2
  fi
fi
exit 0
