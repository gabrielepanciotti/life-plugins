#!/usr/bin/env bash
# SessionStart hook: reports when the nearest node's brain is stale, so a quiet
# index is not mistaken for "nothing changed" (issue #61: an index once stayed
# stale for a month without anyone noticing). Normal cost: one stat per brain
# file, no network access, and no output when the index is current.
set +e
SUITE_SHARED="${CLAUDE_PLUGIN_ROOT}/../../packages/shared"
SUITE_MCP="${CLAUDE_PLUGIN_ROOT}/../suite-mcp"
SUITE_ROOT="${CLAUDE_PLUGIN_ROOT}/../.."
MCP_PY="${SUITE_MCP}/.venv/Scripts/python"; [ -x "$MCP_PY" ] || MCP_PY="${SUITE_MCP}/.venv/bin/python"
START="${CLAUDE_PROJECT_DIR:-$PWD}"

# Use the same discovery as suite-wiki-sync.sh: select the first interpreter
# that can import suite_core, not merely the first one at an assumed path.
export PYTHONPATH="${SUITE_SHARED}${PYTHONPATH:+:${PYTHONPATH}}"
PY=""
for cand in "${SUITE_SHARED}/.venv/Scripts/python" "${SUITE_SHARED}/.venv/bin/python" \
            "${SUITE_ROOT}/backend/.venv/Scripts/python" "${SUITE_ROOT}/backend/.venv/bin/python" \
            "$(command -v python3 2>/dev/null)"; do
  { [ -n "$cand" ] && [ -x "$cand" ]; } || continue
  "$cand" -c "import suite_core" >/dev/null 2>&1 || continue
  PY="$cand"; break
done
[ -n "$PY" ] || exit 0

OUT="$("$PY" -m suite_core.nodes brain-staleness --nearest "$START" 2>&1)"
RC=$?
[ $RC -eq 1 ] || exit 0   # 0 = ok or no brain here; 2 = invalid usage. Never block the session.

MSG="[brain-staleness] ${OUT}. Recovery: \`python -m suite_core.nodes wiki-sync --nearest .\` from the node."

# If semantic reindexing cannot start, report it on the same line instead of
# letting the session discover a turn later that wiki-sync silently skipped it
# (cause #2/#3 of issue #61).
if [ -z "${BRAIN_DB_URL:-}" ] && [ -r "${SUITE_ROOT}/.env" ]; then
  BRAIN_DB_URL="$(sed -n 's/^[[:space:]]*BRAIN_DB_URL=//p' "${SUITE_ROOT}/.env" | tail -1)"
fi
if [ ! -x "$MCP_PY" ] || [ -z "${BRAIN_DB_URL:-}" ]; then
  MSG="${MSG} Semantic reindexing is also stopped: missing $( [ ! -x "$MCP_PY" ] && echo -n "the suite-mcp venv"; [ ! -x "$MCP_PY" ] && [ -z "${BRAIN_DB_URL:-}" ] && echo -n " and "; [ -z "${BRAIN_DB_URL:-}" ] && echo -n "BRAIN_DB_URL (in ${SUITE_ROOT}/.env)" )."
fi

echo "$MSG" >&2
exit 0
