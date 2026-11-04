#!/usr/bin/env bash
# SessionStart hook: ONE line when this device is not aligned to the standard Life tree
# (spec 2026-10-15-layout-knowledge-brain, F5). Silent when `layout doctor` says ok.
#
# Rate-limited: at most one check every 12h (stamp in ~/.claude/state), because the
# doctor reads every instance graph and that is not free on every session start.
# Never fails the session: no venv, no Python, a crash in the doctor -> silence.
set +e
SUITE_SHARED="${CLAUDE_PLUGIN_ROOT}/../../packages/shared"
PY="${SUITE_SHARED}/.venv/Scripts/python"
[ -x "$PY" ] || PY="${SUITE_SHARED}/.venv/bin/python"
[ -x "$PY" ] || exit 0

STATE_DIR="${HOME}/.claude/state"
STAMP="${STATE_DIR}/layout-doctor-hint.stamp"
INTERVAL=$((12 * 3600))
NOW="$(date +%s 2>/dev/null)" || exit 0
if [ -f "$STAMP" ]; then
  LAST="$(cat "$STAMP" 2>/dev/null)"
  case "$LAST" in ''|*[!0-9]*) LAST=0 ;; esac
  [ $((NOW - LAST)) -lt $INTERVAL ] && exit 0
fi
mkdir -p "$STATE_DIR" 2>/dev/null && printf '%s\n' "$NOW" > "$STAMP" 2>/dev/null

OUT="$("$PY" -m suite_core.nodes layout doctor --json 2>/dev/null)" || [ -n "$OUT" ] || exit 0
printf '%s' "$OUT" | "$PY" -c '
import json, sys
try:
    rep = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if rep.get("verdict") == "ok":
    sys.exit(0)
rows = [r for r in rep.get("nodes", []) if r.get("status") in ("link-missing", "link-wrong")]
issues = len(rows) + len(rep.get("blocking", [])) + len(rep.get("warnings", []))
verdict = rep.get("verdict")
print(
    f"[layout] device is not aligned with the standard tree ({verdict}, {issues} issues): "
    "bash scripts/devices/align-layout.sh  (simula; poi --execute)"
)
' 2>/dev/null
exit 0
