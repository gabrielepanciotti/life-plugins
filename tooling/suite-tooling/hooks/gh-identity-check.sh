#!/usr/bin/env bash
# SessionStart hook: verify that the active GitHub identity matches the one
# declared by this project and remains selected (Life#50). Silent when the
# project declares no context (GH_CONFIG_DIR is absent) and when all is well.
# All checks are offline: read hosts.yml without calling GitHub. Never block
# the session.
set +e
[ -n "${GH_CONFIG_DIR:-}" ] || exit 0

SUITE_ROOT="${CLAUDE_PLUGIN_ROOT}/../.."
SCRIPT="${SUITE_ROOT}/scripts/gh_identity.py"
[ -r "$SCRIPT" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

ARGS=(check --dir "$GH_CONFIG_DIR" --one-line --require-env)
[ -n "${GH_IDENTITY_USER:-}" ] && ARGS+=(--user "$GH_IDENTITY_USER")
OUT="$(python3 "$SCRIPT" "${ARGS[@]}" 2>/dev/null)"
[ -n "$OUT" ] && printf '%s\n' "$OUT" >&2
exit 0
