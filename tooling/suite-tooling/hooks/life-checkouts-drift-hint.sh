#!/usr/bin/env bash
# SessionStart hook: warn when a Life engine checkout remains skipped/failed
# for too many consecutive days. The file is written by
# `suite_core.nodes checkouts --refresh` (called by suite-apply.sh) whenever a
# pull is skipped because the working tree is dirty.
#
# Added after the 2026-09-17 bug: tracked .claude/settings.json kept every
# checkout permanently dirty, refresh_checkout() silently skipped it each
# session, and one checkout fell 32 commits behind without any hook reporting
# it. Silent when all is well or the file is absent; reads a small JSON file
# with python -c and starts no heavy process.
set +e
python3 - <<'PYEOF'
import json, os, sys
from datetime import datetime, timezone

path = os.path.expanduser("~/.claude/state/life-checkouts-status.json")
if not os.path.isfile(path):
    sys.exit(0)
try:
    state = json.load(open(path, encoding="utf-8"))
except Exception:
    sys.exit(0)

SOGLIA_GIORNI = 3
now = datetime.now(timezone.utc)
avvisi = []
for root, info in state.items():
    status = info.get("status")
    if status not in ("skipped", "failed"):
        continue
    try:
        since = datetime.fromisoformat(info.get("since", ""))
    except Exception:
        continue
    giorni = (now - since).total_seconds() / 86400
    if giorni >= SOGLIA_GIORNI:
        avvisi.append((root, status, info.get("detail", ""), giorni))

if avvisi:
    print(f"[life-checkouts] {len(avvisi)} checkout(s) stuck for days and never automatically synced:")
    for root, status, detail, giorni in avvisi:
        print(f"  - {root}: {status} for {giorni:.0f}d ({detail})")
        print(f"    -> git -C {root} status --short   # inspect what is blocking it")
PYEOF
