#!/usr/bin/env bash
# Stop hook: warn-mode brain quality gate on the nearest node. Best-effort,
# never blocks the session (like lifegate: warn now, block after cleanup).
set +e
SUITE_SHARED="${CLAUDE_PLUGIN_ROOT}/../../packages/shared"
PY="${SUITE_SHARED}/.venv/Scripts/python"; [ -x "$PY" ] || PY="${SUITE_SHARED}/.venv/bin/python"
START="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -x "$PY" ] || { echo "[brain-gate] suite_core venv missing — skip" >&2; exit 0; }
"$PY" -m suite_core.nodes brain-gate --nearest "$START" --mode warn >&2 2>&1
exit 0
