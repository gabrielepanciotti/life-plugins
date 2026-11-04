#!/usr/bin/env bash
# Append a line to the brain queue (idea skill, "Queue" section).
#
#   accoda.sh "<testo>"
#
# The queue belongs to the node's Life instance (<instance>/.brain-inbox/ideas.jsonl);
# if no instance can be determined with certainty, use the node-local queue
# (<nodo>/.brain-inbox/ideas.jsonl). Contratto: docs/brain-coda-istanza.md in Life.
# Stampa "in coda per <path>".
set -euo pipefail
[ $# -eq 1 ] && [ -n "$1" ] || { echo "uso: $0 \"<testo>\"" >&2; exit 2; }
NODO="${CLAUDE_PROJECT_DIR:-$PWD}"

# 1. Instance: LIFE_INSTANCE_DIR, then the Life engine (suite_core.knowledge).
ISTANZA=""
if [ -n "${LIFE_INSTANCE_DIR:-}" ] && [ -d "$LIFE_INSTANCE_DIR" ]; then
  ISTANZA="$(cd "$LIFE_INSTANCE_DIR" && pwd)"
else
  is_life() { [ -d "$1/packages/shared/suite_core" ] && [ -f "$1/docs/instances.catalog.json" ]; }
  FW="${LIFE_FRAMEWORK_DIR:-${LIFE_FRAMEWORK_ROOT:-}}"
  if [ -z "$FW" ]; then
    d="$(cd "$NODO" && pwd)"
    while [ -n "$d" ] && [ "$d" != "/" ]; do
      if is_life "$d"; then FW="$d"; break; fi
      d="$(dirname "$d")"
    done
  fi
  # last resort: Life as a sibling folder of the node (layout <srv>/Life, <srv>/<Node>)
  if [ -z "$FW" ]; then
    s="$(cd "$NODO/.." && pwd)/Life"
    if is_life "$s"; then FW="$s"; fi
  fi
  if [ -n "$FW" ]; then
    PY=""
    for c in "$FW/packages/shared/.venv/Scripts/python.exe" "$FW/packages/shared/.venv/bin/python" \
             "$FW/.venv/Scripts/python.exe" "$FW/.venv/bin/python"; do
      if [ -x "$c" ]; then PY="$c"; break; fi
    done
    [ -n "$PY" ] || PY="$(command -v python3 || command -v python || true)"
    if [ -n "$PY" ]; then
      BRAIN="$(cd "$FW/packages/shared" && LIFE_FRAMEWORK_DIR="$FW" "$PY" -m suite_core.nodes brain-root --node "$NODO" 2>/dev/null || true)"
      if [ -n "$BRAIN" ]; then ISTANZA="$(dirname -- "$BRAIN")"; fi
    fi
  fi
fi

if [ -n "$ISTANZA" ]; then
  QUEUE="$ISTANZA/.brain-inbox/ideas.jsonl"
else
  echo "no Life instance linked to this node: using the local queue" >&2
  QUEUE="$NODO/.brain-inbox/ideas.jsonl"
fi
mkdir -p "$(dirname -- "$QUEUE")"

PY2="$(command -v python3 || command -v python)"
NODO="$NODO" QUEUE="$QUEUE" "$PY2" -c '
import json, os, sys, datetime, pathlib
row = {
    "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "session": os.environ.get("CLAUDE_CODE_SESSION_ID", ""),
    "nodo": pathlib.Path(os.environ["NODO"]).name,
    "marcatore": "manuale",
    "testo": sys.argv[1],
}
with open(os.environ["QUEUE"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
print("in coda per", os.environ["QUEUE"])
' "$1"
