#!/usr/bin/env bash
# Adds a line to the tail of the brain (skill idea, «Queue» section).
#
# append.sh "<text>"
#
# The queue is that of the Life instance of the node (<istanza>/.brain-inbox/ideas.jsonl);
# if no instance can be determined with certainty, the local one of the node
# (<nodo>/.brain-inbox/ideas.jsonl). Contract: docs/brain-queue-instance.md in Life.
# Print "queuing for <path>".
set -euo pipefail
[ $# -eq 1 ] && [ -n "$1" ] || { echo "use: $0 \"<testo>\"" >&2; exit 2; }
NODE="${CLAUDE_PROJECT_DIR:-$PWD}"

# 1. Instance: LIFE_INSTANCE_DIR, then the Life engine (suite_core.knowledge).
INSTANCE=""
if [ -n "${LIFE_INSTANCE_DIR:-}" ] && [ -d "$LIFE_INSTANCE_DIR" ]; then
INSTANCE="$(cd "$LIFE_INSTANCE_DIR" && pwd)"
else
is_life() { [ -d "$1/packages/shared/suite_core" ] && [ -f "$1/docs/instances.catalog.json" ]; }
FW="${LIFE_FRAMEWORK_DIR:-${LIFE_FRAMEWORK_ROOT:-}}"
if [ -z "$FW" ]; then
d="$(cd "$NODE" && pwd)"
while [ -n "$d" ] && [ "$d" != "/" ]; do
if is_life "$d"; then FW="$d"; break; fi
d="$(dirname "$d")"
done
fi
# last chance: Life as node's sister folder (layout <srv>/Life, <srv>/<Nodo>)
if [ -z "$FW" ]; then
s="$(cd "$NODE/.." && pwd)/Life"
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
BRAIN="$(cd "$FW/packages/shared" && LIFE_FRAMEWORK_DIR="$FW" "$PY" -m suite_core.nodes brain-root --node "$NODE" 2>/dev/null || true)"
if [ -n "$BRAIN" ]; then INSTANCE="$(dirname -- "$BRAIN")"; fi
fi
fi
fi

if [ -n "$INSTANCE" ]; then
QUEUE="$INSTANCE/.brain-inbox/ideas.jsonl"
else
echo "no Life instances attached to this node: using local queue" >&2
QUEUE="$NODE/.brain-inbox/ideas.jsonl"
fi
mkdir -p "$(dirname -- "$QUEUE")"

PY2="$(command -v python3 || command -v python)"
NODE="$NODE" QUEUE="$QUEUE" "$PY2" -c '
import json, os, sys, datetime, pathlib
row = {
"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
"session": os.environ.get("CLAUDE_CODE_SESSION_ID", ""),
"node": pathlib.Path(os.environ["NODE"]).name,
"marker": "manual",
"text": sys.argv[1],
}
with open(os.environ["QUEUE"], "a", encoding="utf-8") as fh:
fh.write(json.dumps(row, ensure_ascii=False) + "\n")
print("queued for", os.environ["QUEUE"])
' "$1"
