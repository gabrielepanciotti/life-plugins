#!/usr/bin/env bash
# stato.py on a throwaway repo: a stale running issue becomes failed, a fresh one stays.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
git init -q -b main "$tmp/r"; cd "$tmp/r"
echo a > a; git add a; git commit -q -m init
GIT_COMMITTER_DATE="2026-01-01T00:00:00" git commit -q --allow-empty -m old
git branch vecchio
git branch nuovo main~1
git checkout -q -b fresco; git commit -q --allow-empty -m now; git checkout -q main
git branch -f nuovo fresco
mkdir -p .claude/do-everything
cat > .claude/do-everything/state.json <<'EOF'
{"session_id": "S1", "created_at": "x",
 "issues": {
  "1": {"id": 1, "title": "a", "status": "running", "branch": "vecchio"},
  "2": {"id": 2, "title": "b", "status": "running", "branch": "nuovo"},
  "3": {"id": 3, "title": "c", "status": "completed"}},
 "question_queue": [], "macro_agents": {}}
EOF
out="$(python3 "$here/../scripts/stato.py" . --aggiorna)"
grep -q "Completati: 1/3" <<<"$out" || { echo "FAIL riepilogo: $out"; exit 1; }
grep -q "#1" <<<"$(grep 'interrotti' <<<"$out")" || { echo "FAIL interrotto: $out"; exit 1; }
python3 - <<'EOF'
import json
s = json.load(open(".claude/do-everything/state.json"))
assert s["issues"]["1"]["status"] == "failed" and s["issues"]["1"]["error"] == "interrotto", s
assert s["issues"]["2"]["status"] == "running", s
assert s["stats"]["failed"] == 1
EOF
cd "$tmp" && python3 "$here/../scripts/stato.py" "$tmp" | grep -q "no session" || { echo "FAIL without state"; exit 1; }
echo "test-stato: ok"
