#!/usr/bin/env bash
# auto_improve.sh -- Autoresearch-style improvement loop for Claude Code skills.
#
# Inspired by github.com/karpathy/autoresearch:
#   SKILL.md    = train.py       (only mutable file)
#   evals.json  = prepare.py     (immutable judge — train split)
#   val.json    = validation set (optional — checks overfitting)
#   results.tsv = experiment log (append-only)
#   journal.md  = scientific log (what was tried, what worked, what didn't)
#
# Usage: auto_improve.sh <skill-dir> [max-iterations]
# Budget: max $10 per skill (tracked cumulatively)

set -euo pipefail

SKILL_DIR="$(realpath "$1")"
MAX_ITER="${2:-50}"
SKILL_NAME="$(basename "$SKILL_DIR")"
SKILL_FILE="$SKILL_DIR/SKILL.md"
EVALS_FILE="$SKILL_DIR/evals/evals.json"
VAL_FILE="$SKILL_DIR/evals/val.json"
RESULTS_TSV="$SKILL_DIR/results.tsv"
JOURNAL_FILE="$SKILL_DIR/journal.md"
HISTORY_DIR="$SKILL_DIR/history"
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_EVALS="$SCRIPTS_DIR/run_evals.py"
BUDGET_MAX=10.00
BUDGET_USED=0.00

# --- Validation ---
[[ -f "$SKILL_FILE" ]] || { echo "ERROR: $SKILL_FILE not found. Contents of $SKILL_DIR: $(ls "$SKILL_DIR" | tr "\n" " ")"; exit 1; }
[[ -f "$EVALS_FILE" ]] || { echo "ERROR: $EVALS_FILE not found. Contents of $SKILL_DIR: $(ls "$SKILL_DIR" | tr "\n" " "). Create the evals using step 4 of update-skill."; exit 1; }
[[ -f "$RUN_EVALS" ]] || { echo "ERROR: $RUN_EVALS not found"; exit 1; }

HAS_VAL="no"
[[ -f "$VAL_FILE" ]] && HAS_VAL="yes"

# --- Find Python ---
PYTHON="python"
# Linux: .venv/bin/python; Windows: .venv/Scripts/python.exe; then system python3
for candidate in \
    "$SKILL_DIR/../../.venv/bin/python" \
    "$HOME/.claude/.venv/bin/python" \
    "$SKILL_DIR/../../.venv/Scripts/python.exe" \
    "$HOME/.claude/.venv/Scripts/python.exe" \
    "python3"; do
    if command -v "$candidate" &>/dev/null || [[ -f "$candidate" ]]; then
        PYTHON="$candidate"
        break
    fi
done

# --- Setup ---
mkdir -p "$HISTORY_DIR"
[[ -f "$JOURNAL_FILE" ]] || printf "# Auto-Improve Journal — %s\n\n" "$SKILL_NAME" > "$JOURNAL_FILE"

echo "============================================"
echo "  Autoresearch-Style Auto-Improve Loop"
echo "  Skill: $SKILL_NAME"
echo "  Max iterations: $MAX_ITER"
echo "  Budget cap: \$$BUDGET_MAX"
echo "  Validation split: $HAS_VAL"
echo "============================================"
echo ""

# --- Initialize results.tsv ---
if [[ ! -f "$RESULTS_TSV" ]]; then
    printf "iteration\tsplit\tscore\tdelta\tstatus\ttc_scores\tdescription\n" > "$RESULTS_TSV"
fi

# --- Create branch ---
cd "$SKILL_DIR"
BRANCH="auto-improve/$SKILL_NAME"
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    echo "Branch $BRANCH already exists, switching to it..."
    git checkout "$BRANCH"
else
    echo "Creating branch: $BRANCH"
    git checkout -b "$BRANCH"
fi

# --- Helpers ---
extract_score() {
    echo "$1" | "$PYTHON" -c "import sys,json; print(json.load(sys.stdin)['score'])" 2>/dev/null || echo "0"
}

extract_cost() {
    echo "$1" | "$PYTHON" -c "import sys,json; print(json.load(sys.stdin).get('estimated_cost', 0))" 2>/dev/null || echo "0"
}

extract_tc_scores() {
    echo "$1" | "$PYTHON" -c "
import sys, json
data = json.load(sys.stdin)
parts = []
for tc_id, tc in sorted(data['test_cases'].items()):
    total = tc['passed'] + tc['failed']
    pct = round(tc['passed'] / total * 100) if total > 0 else 0
    parts.append(f'{tc_id}:{pct}')
print('|'.join(parts))
" 2>/dev/null || echo "parse_error"
}

extract_failure_report() {
    echo "$1" | "$PYTHON" -c "
import sys, json
data = json.load(sys.stdin)
total_pass = data['passed']
total_fail = data['failed']
total = total_pass + total_fail
print(f'Overall: {total_pass}/{total} assertions passed ({data[\"score\"]}%)')
print()
for tc_id, tc in sorted(data['test_cases'].items()):
    tc_total = tc['passed'] + tc['failed']
    tc_pct = round(tc['passed'] / tc_total * 100) if tc_total > 0 else 0
    status = 'PASS' if tc['failed'] == 0 else 'FAIL'
    print(f'  [{status}] {tc_id}: {tc[\"passed\"]}/{tc_total} ({tc_pct}%)')
    for r in tc['results']:
        icon = 'OK' if r['passed'] else 'XX'
        print(f'    [{icon}] {r[\"assertion\"]} (type: {r[\"type\"]})')
" 2>/dev/null || echo "Could not parse results"
}

extract_failures_only() {
    echo "$1" | "$PYTHON" -c "
import sys, json
data = json.load(sys.stdin)
for tc_id, tc in sorted(data['test_cases'].items()):
    tc_total = tc['passed'] + tc['failed']
    if tc['failed'] > 0:
        tc_pct = round(tc['passed'] / tc_total * 100) if tc_total > 0 else 0
        print(f'[{tc_id}] Score: {tc_pct}% - Failing assertions:')
        for r in tc['results']:
            if not r['passed']:
                print(f'  FAIL: {r[\"assertion\"]} (type: {r[\"type\"]})')
        print()
" 2>/dev/null || echo "Could not parse failures"
}

run_and_log() {
    # $1 = evals file, $2 = split label, $3 = iteration number
    local evals="$1"
    local split="$2"
    local iter="$3"
    local result
    local errfile="$SKILL_DIR/.eval_stderr_${split}.log"
    result=$("$PYTHON" "$RUN_EVALS" "$evals" 2>"$errfile" || true)
    if [[ -z "$result" ]]; then
        # Show stderr on eval failure for debugging
        echo "    (eval stderr):" >&2
        sed 's/^/      /' "$errfile" >&2 2>/dev/null | head -20
        echo ""  # signal empty
        return
    fi
    local s; s=$(extract_score "$result")
    local c; c=$(extract_cost "$result")
    local tcs; tcs=$(extract_tc_scores "$result")
    BUDGET_USED=$("$PYTHON" -c "print(round(float('$BUDGET_USED') + float('$c'), 2))" 2>/dev/null || echo "$BUDGET_USED")
    printf "%s\t%s\t%s\t-\tmeasure\t%s\tauto\n" "$iter" "$split" "$s" "$tcs" >> "$RESULTS_TSV"
    echo "$result"
}

# --- Baseline ---
echo ""
echo "--- Baseline (train) ---"
BASELINE=$(run_and_log "$EVALS_FILE" "train" "0")
if [[ -z "$BASELINE" ]]; then
    echo "ERROR: Baseline train eval returned empty. Check run_evals.py."
    git checkout "$ORIGINAL_BRANCH"
    exit 1
fi
BASELINE_SCORE=$(extract_score "$BASELINE")
TC_SCORES=$(extract_tc_scores "$BASELINE")
echo "Train baseline: ${BASELINE_SCORE}% | per-tc: $TC_SCORES"

VAL_BASELINE_SCORE="n/a"
if [[ "$HAS_VAL" == "yes" ]]; then
    echo ""
    echo "--- Baseline (val) ---"
    VAL_BASELINE=$(run_and_log "$VAL_FILE" "val" "0")
    if [[ -n "$VAL_BASELINE" ]]; then
        VAL_BASELINE_SCORE=$(extract_score "$VAL_BASELINE")
        VAL_TC_SCORES=$(extract_tc_scores "$VAL_BASELINE")
        echo "Val baseline:   ${VAL_BASELINE_SCORE}% | per-tc: $VAL_TC_SCORES"
    else
        echo "WARN: val eval returned empty. Continuing without val."
        HAS_VAL="no"
    fi
fi

echo ""
echo "Budget used so far: \$$BUDGET_USED"

# --- Journal: baseline entry ---
{
    echo ""
    echo "## Iteration 0 — baseline"
    echo "- Train score: ${BASELINE_SCORE}%"
    echo "- Val score:   ${VAL_BASELINE_SCORE}"
    echo "- Train per-tc: $TC_SCORES"
    echo ""
} >> "$JOURNAL_FILE"

if [[ "$BASELINE_SCORE" == "100.0" ]]; then
    echo ""
    echo "Already perfect on train! Nothing to improve."
    git checkout "$ORIGINAL_BRANCH"
    exit 0
fi

cp "$SKILL_FILE" "$HISTORY_DIR/v_baseline.md"
git add "$HISTORY_DIR" 2>/dev/null || true
git commit -m "chore: baseline before auto-improve ($SKILL_NAME) — train ${BASELINE_SCORE}%" --allow-empty 2>/dev/null || true

BEST_SCORE="$BASELINE_SCORE"
LAST_RESULT="$BASELINE"
CONSECUTIVE_DISCARDS=0

# --- Improvement loop ---
for i in $(seq 1 "$MAX_ITER"); do
    echo ""
    echo "=== Iteration $i / $MAX_ITER (best train: ${BEST_SCORE}%) ==="

    # Budget check
    OVER_BUDGET=$("$PYTHON" -c "print('yes' if float('$BUDGET_USED') >= float('$BUDGET_MAX') else 'no')" 2>/dev/null || echo "no")
    if [[ "$OVER_BUDGET" == "yes" ]]; then
        echo "BUDGET CAP REACHED (\$$BUDGET_USED >= \$$BUDGET_MAX). Stopping."
        printf "%d\ttrain\t%s\t0\tbudget_stop\t%s\tbudget cap reached\n" "$i" "$BEST_SCORE" "$TC_SCORES" >> "$RESULTS_TSV"
        break
    fi

    # Stagnation strategy
    STRATEGY=""
    if [[ $CONSECUTIVE_DISCARDS -ge 5 ]]; then
        STRATEGY="STRATEGY NOTE: $CONSECUTIVE_DISCARDS consecutive failed attempts. Incremental tweaks are NOT working. Try a RADICALLY different approach: restructure a whole section, rewrite a rule from scratch, or address multiple failing test cases with one cohesive refactor. Read the journal — do NOT repeat ideas already tried."
        CONSECUTIVE_DISCARDS=0
    fi

    SKILL_SNAPSHOT=$(cat "$SKILL_FILE")
    FAILURE_REPORT=$(extract_failure_report "$LAST_RESULT")
    FAILURES_ONLY=$(extract_failures_only "$LAST_RESULT")
    RECENT_HISTORY=$(tail -10 "$RESULTS_TSV" 2>/dev/null || echo "no history")
    RECENT_JOURNAL=$(tail -40 "$JOURNAL_FILE" 2>/dev/null || echo "empty journal")

    # The improver goes through the routing (service life.miglioraSkill): the procedure is the stable `task`,
    # the skill and the eval reports are the material (stdin); the answer carries the whole new SKILL.md.
    IMPROVE_INPUT="Iteration: $i / $MAX_ITER
Train score: ${BEST_SCORE}% (target: 100%)

## Full Eval Report (per test case)
$FAILURE_REPORT

## Failing Assertions Only
$FAILURES_ONLY

## Recent Experiment History (results.tsv)
$RECENT_HISTORY

## Recent Journal Entries
$RECENT_JOURNAL

## Strategy
$STRATEGY

## Current SKILL.md
$SKILL_SNAPSHOT"

    echo "Asking the router to improve SKILL.md..."
    IMPROVE_OUT=$(printf '%s' "$IMPROVE_INPUT" | "${LLM_RUN:-llm-run}" run --servizio life.miglioraSkill \
        "$(cat "$SCRIPTS_DIR/../procedures/improve.md")" 2>/dev/null || true)
    CHANGE_DESC=$(printf '%s' "$IMPROVE_OUT" | "$PYTHON" "$SCRIPTS_DIR/apply_improvement.py" "$SKILL_FILE" "$JOURNAL_FILE" || echo "unknown change")

    BUDGET_USED=$("$PYTHON" -c "print(round(float('$BUDGET_USED') + 0.15, 2))" 2>/dev/null || echo "$BUDGET_USED")

    # Commit the change
    git add SKILL.md journal.md 2>/dev/null || true

    if ! git diff --cached --quiet 2>/dev/null; then
        git commit -m "auto-improve: iteration $i for $SKILL_NAME" 2>/dev/null || true
    else
        echo "No changes made by Claude. Skipping."
        printf "%d\ttrain\t%s\t0\tno_change\t%s\tno changes made\n" "$i" "$BEST_SCORE" "$TC_SCORES" >> "$RESULTS_TSV"
        CONSECUTIVE_DISCARDS=$((CONSECUTIVE_DISCARDS + 1))
        continue
    fi

    # Re-run train evals
    echo "Running train evals..."
    NEW_RESULT=$("$PYTHON" "$RUN_EVALS" "$EVALS_FILE" 2>/dev/null || true)

    if [[ -z "$NEW_RESULT" ]]; then
        echo "Eval returned empty. Restoring SKILL.md snapshot."
        echo "$SKILL_SNAPSHOT" > "$SKILL_FILE"
        git add "$SKILL_FILE" 2>/dev/null || true
        git commit -m "revert: iteration $i — empty eval result" 2>/dev/null || true
        printf "%d\ttrain\t%s\t0\tcrash\t%s\teval returned empty\n" "$i" "$BEST_SCORE" "$TC_SCORES" >> "$RESULTS_TSV"
        CONSECUTIVE_DISCARDS=$((CONSECUTIVE_DISCARDS + 1))
        continue
    fi

    NEW_SCORE=$(extract_score "$NEW_RESULT")
    NEW_COST=$(extract_cost "$NEW_RESULT")
    BUDGET_USED=$("$PYTHON" -c "print(round(float('$BUDGET_USED') + float('$NEW_COST'), 2))" 2>/dev/null || echo "$BUDGET_USED")
    NEW_TC_SCORES=$(extract_tc_scores "$NEW_RESULT")
    DELTA=$("$PYTHON" -c "print(round(float('$NEW_SCORE') - float('$BEST_SCORE'), 1))" 2>/dev/null || echo "?")

    echo "Score: ${NEW_SCORE}% (was: ${BEST_SCORE}%, delta: ${DELTA}) | Budget: \$$BUDGET_USED / \$$BUDGET_MAX"
    echo "Per-tc: $NEW_TC_SCORES"

    # STRICT improvement only (Karpathy-style): > not >=
    IS_BETTER=$("$PYTHON" -c "print('yes' if float('$NEW_SCORE') > float('$BEST_SCORE') else 'no')" 2>/dev/null || echo "no")

    if [[ "$IS_BETTER" == "yes" ]]; then
        echo ">>> KEEP — score strictly improved"
        BEST_SCORE="$NEW_SCORE"
        LAST_RESULT="$NEW_RESULT"
        TC_SCORES="$NEW_TC_SCORES"
        CONSECUTIVE_DISCARDS=0

        SHORT_DESC=$(echo "$CHANGE_DESC" | head -c 80 | tr '\t\n' '  ')
        printf "%d\ttrain\t%s\t%s\tkeep\t%s\t%s\n" "$i" "$NEW_SCORE" "$DELTA" "$NEW_TC_SCORES" "$SHORT_DESC" >> "$RESULTS_TSV"

        # Snapshot on every strict improvement
        SNAPSHOT_NAME="v${i}_train_${NEW_SCORE}"
        cp "$SKILL_FILE" "$HISTORY_DIR/${SNAPSHOT_NAME}.md"
        git add "$HISTORY_DIR/${SNAPSHOT_NAME}.md" 2>/dev/null || true
        git commit -m "snapshot: $SKILL_NAME train ${NEW_SCORE}% (iter $i)" 2>/dev/null || true
        echo "  Snapshot: history/${SNAPSHOT_NAME}.md"

        # Append outcome to journal
        {
            echo "- Outcome: KEEP (train ${BEST_SCORE}% -> ${NEW_SCORE}%, delta +${DELTA})"
            echo ""
        } >> "$JOURNAL_FILE"
        git add "$JOURNAL_FILE" 2>/dev/null || true
        git commit --amend --no-edit 2>/dev/null || true

        if [[ "$NEW_SCORE" == "100.0" ]]; then
            echo ""
            echo "============================================"
            echo "  PERFECT TRAIN SCORE at iteration $i!"
            echo "  Budget used: \$$BUDGET_USED"
            echo "============================================"
            cp "$SKILL_FILE" "$HISTORY_DIR/v_final_100.md"
            git add "$HISTORY_DIR/v_final_100.md" 2>/dev/null || true
            git commit -m "snapshot: $SKILL_NAME perfect train (100%)" 2>/dev/null || true
            break
        fi
    else
        echo "<<< REVERT — score not strictly better (${NEW_SCORE}% <= ${BEST_SCORE}%)"
        echo "$SKILL_SNAPSHOT" > "$SKILL_FILE"
        git add "$SKILL_FILE" 2>/dev/null || true
        if ! git diff --cached --quiet 2>/dev/null; then
            git commit -m "revert: iteration $i — no strict improvement (${NEW_SCORE}% <= ${BEST_SCORE}%)" 2>/dev/null || true
        fi
        CONSECUTIVE_DISCARDS=$((CONSECUTIVE_DISCARDS + 1))

        SHORT_DESC=$(echo "$CHANGE_DESC" | head -c 80 | tr '\t\n' '  ')
        printf "%d\ttrain\t%s\t%s\tdiscard\t%s\t%s\n" "$i" "$NEW_SCORE" "$DELTA" "$NEW_TC_SCORES" "$SHORT_DESC" >> "$RESULTS_TSV"

        {
            echo "- Outcome: REVERT (train ${NEW_SCORE}% <= ${BEST_SCORE}%)"
            echo ""
        } >> "$JOURNAL_FILE"
        git add "$JOURNAL_FILE" 2>/dev/null || true
        git commit --amend --no-edit 2>/dev/null || true
    fi
done

# --- Final val evaluation (overfitting check) ---
VAL_FINAL_SCORE="n/a"
VAL_DELTA="n/a"
if [[ "$HAS_VAL" == "yes" ]]; then
    echo ""
    echo "--- Final validation (overfitting check) ---"
    VAL_FINAL=$(run_and_log "$VAL_FILE" "val" "$i")
    if [[ -n "$VAL_FINAL" ]]; then
        VAL_FINAL_SCORE=$(extract_score "$VAL_FINAL")
        VAL_FINAL_TC=$(extract_tc_scores "$VAL_FINAL")
        VAL_DELTA=$("$PYTHON" -c "print(round(float('$VAL_FINAL_SCORE') - float('$VAL_BASELINE_SCORE'), 1))" 2>/dev/null || echo "?")
        echo "Val final: ${VAL_FINAL_SCORE}% (was ${VAL_BASELINE_SCORE}%, delta: ${VAL_DELTA})"
        echo "Val per-tc: $VAL_FINAL_TC"
    fi
fi

# --- Summary ---
TRAIN_DELTA=$("$PYTHON" -c "print(round(float('$BEST_SCORE') - float('$BASELINE_SCORE'), 1))" 2>/dev/null || echo "?")

echo ""
echo "============================================"
echo "  Auto-Improve Complete — $SKILL_NAME"
echo "  Train: ${BASELINE_SCORE}% -> ${BEST_SCORE}% (delta ${TRAIN_DELTA})"
if [[ "$HAS_VAL" == "yes" ]]; then
echo "  Val:   ${VAL_BASELINE_SCORE}% -> ${VAL_FINAL_SCORE}% (delta ${VAL_DELTA})"
    # Overfitting warning
    OVERFIT=$("$PYTHON" -c "
try:
    td = float('$TRAIN_DELTA'); vd = float('$VAL_DELTA')
    print('yes' if td >= 10 and vd < td / 2 else 'no')
except:
    print('unknown')
" 2>/dev/null)
    if [[ "$OVERFIT" == "yes" ]]; then
        echo "  WARNING: Train improved much more than Val — possible OVERFITTING to evals."
        echo "           Consider strengthening evals or adding more val cases."
    fi
fi
echo "  Iterations: $i"
echo "  Budget used: \$$BUDGET_USED / \$$BUDGET_MAX"
echo "  Log:       $RESULTS_TSV"
echo "  Journal:   $JOURNAL_FILE"
echo "  Snapshots: $HISTORY_DIR/"
echo "============================================"

# Append final summary to journal
{
    echo ""
    echo "## Final"
    echo "- Train: ${BASELINE_SCORE}% -> ${BEST_SCORE}% (delta ${TRAIN_DELTA})"
    if [[ "$HAS_VAL" == "yes" ]]; then
        echo "- Val:   ${VAL_BASELINE_SCORE}% -> ${VAL_FINAL_SCORE}% (delta ${VAL_DELTA})"
    fi
    echo "- Iterations: $i"
    echo "- Budget: \$$BUDGET_USED"
    echo ""
} >> "$JOURNAL_FILE"
git add "$JOURNAL_FILE" 2>/dev/null || true
git commit -m "journal: $SKILL_NAME auto-improve complete" 2>/dev/null || true

echo ""
echo "Branch: $BRANCH"
echo ""
echo "To squash-merge into main:"
echo "  git checkout $ORIGINAL_BRANCH"
echo "  git merge --squash $BRANCH"
echo "  git commit -m \"feat: auto-improve $SKILL_NAME (train ${BASELINE_SCORE}% -> ${BEST_SCORE}%)\""
echo "  git branch -d $BRANCH"
echo "  git push origin HEAD"
