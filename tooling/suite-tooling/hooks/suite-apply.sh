#!/usr/bin/env bash
# SessionStart hook: non-invasively (re)materialize the nearest Life node's
# resolved config + agents. Best-effort: never blocks or fails the session.
set +e
SUITE_SHARED="${CLAUDE_PLUGIN_ROOT}/../../packages/shared"
PY="${SUITE_SHARED}/.venv/Scripts/python"
[ -x "$PY" ] || PY="${SUITE_SHARED}/.venv/bin/python"   # linux fallback
START="${CLAUDE_PROJECT_DIR:-$PWD}"

# Per-device config (gitignored, the one place absolute paths are legal). Not
# sourced by any shell profile, so a hook that wants `$LIFE_CHECKOUTS` has to
# read it here — otherwise that setting is unreachable and the feature reading
# it is dead code. Guarded and best-effort like everything else in this hook.
if [ -r "$HOME/.claude/paths.sh" ]; then
  # shellcheck disable=SC1091
  . "$HOME/.claude/paths.sh" >/dev/null 2>&1 || true
fi

if [ ! -x "$PY" ]; then
  echo "[suite-apply] suite_core venv not found at ${SUITE_SHARED}/.venv — skipping" >&2
  exit 0
fi
# Keep EVERY framework checkout fresh, not just the one this plugin loaded from.
# One machine legitimately hosts several (framework on master in each, device
# profile in a sibling instance dir), and a node's `inherits` pointer resolves
# into its own checkout — so a stale one silently feeds stale parent config to
# every node under it. Discovery is derived (running checkout + the current
# node's inherits-chain root) plus `$LIFE_CHECKOUTS` for one no session opens.
# Runs BEFORE apply, so this session already uses what it just pulled.
# Says nothing when everything is current; a dirty tree is reported and left
# alone. The previous version pulled one checkout as `--quiet >/dev/null 2>&1`,
# and that swallowed failure is how a checkout went 31 commits stale unnoticed.
# `echo "[tag] $OUT"` tags only the FIRST line of a multi-line output, and the
# rest surfaces as stray text with no idea which step produced it — which is how
# a real "updated" line went unnoticed while being printed. Tag every line.
tag() { sed "s/^/[$1] /" >&2; }

CO_OUT="$("$PY" -m suite_core.nodes checkouts --refresh "$START" 2>&1)"
if [ -n "$CO_OUT" ]; then
  printf '%s\n' "$CO_OUT" | tag checkouts
fi

OUT="$("$PY" -m suite_core.nodes apply --nearest "$START" 2>&1)"
RC=$?
if [ $RC -ne 0 ]; then
  printf 'apply failed (rc=%s): %s\n' "$RC" "$OUT" | tag suite-apply
else
  printf '%s\n' "$OUT" | tag suite-apply
fi

# Drift report, never a write. `conform` regenerates TRACKED files (the managed
# .gitignore block, AGENTS.md, deploy/*, the index.html head), so running it
# unattended would have the auto-commit hook version blueprint churn in whatever
# branch this session is on — production repos included. Measured 2026-08-16: an
# unattended sweep over nine nodes would have replaced a production favicon on
# two of them. So the session TELLS you what is stale and you conform by hand.
# Exit 1 means "stale" (CI gates on it); here it is expected and ignored, because
# a stale AGENTS.md must never keep a session from starting.
CHK_OUT="$("$PY" -m suite_core.nodes conform --check --nearest "$START" 2>&1)"
if [ -n "$CHK_OUT" ]; then
  printf '%s\n' "$CHK_OUT" | tag conform-check
fi

BUS_OUT="$("$PY" -m suite_core.nodes bus-conform --nearest "$START" 2>&1)"
BUS_RC=$?
if [ $BUS_RC -ne 0 ]; then
  printf 'failed (rc=%s): %s\n' "$BUS_RC" "$BUS_OUT" | tag bus-conform
elif [ -n "$BUS_OUT" ]; then
  printf '%s\n' "$BUS_OUT" | tag bus-conform
fi
exit 0
