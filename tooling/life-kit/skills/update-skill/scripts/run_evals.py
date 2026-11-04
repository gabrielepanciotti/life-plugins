#!/usr/bin/env python3
"""run_evals.py -- Run binary eval assertions against a Claude Code skill.

Usage: python run_evals.py <path-to-evals.json>

Output: JSON with score, passed/failed counts, and per-test-case details.
Exit code: 0 if perfect score, 1 otherwise.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

MAX_BUDGET_PER_SKILL = 10.0  # $10 hard cap (matches SKILL.md)
COST_PER_CALL_ESTIMATE = 0.05  # planning estimate only; actual costs belong to the router


def check_assertion(assertion: dict, output: str, workspace: str) -> bool:
    """Evaluate a single binary assertion. Returns True if passed."""
    atype = assertion["type"]
    value = assertion.get("value", "")

    if atype == "output_contains":
        return value.lower() in output.lower()

    elif atype == "output_not_contains":
        return value.lower() not in output.lower()

    elif atype == "output_regex":
        return bool(re.search(value, output, re.IGNORECASE | re.MULTILINE))

    elif atype == "output_max_lines":
        return len(output.strip().split("\n")) <= int(value)

    elif atype == "output_min_lines":
        return len(output.strip().split("\n")) >= int(value)

    elif atype == "file_exists":
        return (Path(workspace) / value).exists()

    elif atype == "file_contains":
        fpath = Path(workspace) / assertion["path"]
        if not fpath.exists():
            return False
        return value.lower() in fpath.read_text(errors="ignore").lower()

    elif atype == "file_not_contains":
        fpath = Path(workspace) / assertion["path"]
        if not fpath.exists():
            return True
        return value.lower() not in fpath.read_text(errors="ignore").lower()

    elif atype == "file_regex":
        fpath = Path(workspace) / assertion["path"]
        if not fpath.exists():
            return False
        return bool(re.search(value, fpath.read_text(errors="ignore"), re.MULTILINE))

    elif atype == "command_succeeds":
        try:
            r = subprocess.run(
                value, shell=True, cwd=workspace,
                capture_output=True, timeout=30
            )
            return r.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    elif atype == "command_output_contains":
        try:
            r = subprocess.run(
                assertion["command"], shell=True, cwd=workspace,
                capture_output=True, text=True, timeout=30
            )
            return value.lower() in r.stdout.lower()
        except subprocess.TimeoutExpired:
            return False

    return False


def run_single_eval(
    test_case: dict, model: str, max_budget: float, cost_tracker: dict
) -> tuple:
    """Run one test case. Model and per-call budget are legacy fields, not routing overrides."""
    tc_id = test_case["id"]
    workspace = tempfile.mkdtemp(prefix=f"skill-eval-{tc_id}-")

    try:
        # Run setup commands if any
        for cmd in test_case.get("context", {}).get("setup_commands", []):
            subprocess.run(cmd, shell=True, cwd=workspace, timeout=30)

        # Stop at the planning estimate, not a provider-enforced cost ceiling.
        if cost_tracker["total"] >= MAX_BUDGET_PER_SKILL:
            return tc_id, [{
                "assertion": "BUDGET EXCEEDED",
                "type": "budget_check",
                "passed": False
            }]

        prompt = test_case["prompt"]

        # Run a session in the test workspace; the router chooses the executor.
        cmd = [
            os.environ.get("LLM_RUN", "llm-run"), "run",
            "--servizio", "life.skillEval", "--dir", workspace, "--", prompt,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, cwd=workspace, stdin=subprocess.DEVNULL,
                timeout=300
            )
            if result.returncode:
                raise RuntimeError(f"skill evaluation routing failed (exit {result.returncode})")
            output = result.stdout
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("skill evaluation routing timed out") from exc

        # Track estimated cost
        cost_tracker["total"] += COST_PER_CALL_ESTIMATE
        cost_tracker["calls"] += 1

        # Check each assertion
        results = []
        for assertion in test_case["assertions"]:
            passed = check_assertion(assertion, output, workspace)
            results.append({
                "assertion": assertion["description"],
                "type": assertion["type"],
                "passed": passed
            })

        return tc_id, results

    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_evals.py <path-to-evals.json>", file=sys.stderr)
        sys.exit(2)

    evals_path = Path(sys.argv[1])
    if not evals_path.exists():
        present = sorted(x.name for x in evals_path.parent.glob("*")) if evals_path.parent.exists() else "cartella inesistente"
        print(f"ERROR: {evals_path} not found. Present in {evals_path.parent}: {present}", file=sys.stderr)
        sys.exit(2)

    evals = json.loads(evals_path.read_text(encoding="utf-8"))

    model = evals.get("model", "sonnet")
    budget_per_case = evals.get("max_budget_usd", 0.50)
    cost_tracker = {"total": 0.0, "calls": 0}

    all_results = {}
    total_pass = 0
    total_fail = 0

    for tc in evals["test_cases"]:
        if cost_tracker["total"] >= MAX_BUDGET_PER_SKILL:
            print(
                f"WARNING: Budget cap ${MAX_BUDGET_PER_SKILL} reached after "
                f"{cost_tracker['calls']} calls. Stopping.",
                file=sys.stderr,
            )
            break

        tc_id, results = run_single_eval(tc, model, budget_per_case, cost_tracker)

        passed = sum(1 for r in results if r["passed"])
        failed = sum(1 for r in results if not r["passed"])
        tc_total = passed + failed
        tc_score = round(passed / tc_total * 100, 1) if tc_total > 0 else 0
        total_pass += passed
        total_fail += failed

        all_results[tc_id] = {
            "results": results,
            "passed": passed,
            "failed": failed,
            "score": tc_score,
        }

    total = total_pass + total_fail
    score = (total_pass / total * 100) if total > 0 else 0

    tc_summary = {
        tc_id: {
            "score": tc_data["score"],
            "passed": tc_data["passed"],
            "failed": tc_data["failed"],
            "failing_assertions": [
                r["assertion"] for r in tc_data["results"] if not r["passed"]
            ],
        }
        for tc_id, tc_data in all_results.items()
    }

    output = {
        "score": round(score, 1),
        "total_assertions": total,
        "passed": total_pass,
        "failed": total_fail,
        "estimated_cost": round(cost_tracker["total"], 2),
        "api_calls": cost_tracker["calls"],
        "tc_summary": tc_summary,
        "test_cases": all_results,
    }

    print(json.dumps(output, indent=2))
    sys.exit(0 if total_fail == 0 else 1)


if __name__ == "__main__":
    main()
