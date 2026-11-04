# Loop engineering for autonomous agents

Reference for the **Build loop** phase of `lavoro-notturno` (and for any execution
autonomous recursive). It formalizes what the skill already does, so the loop is disciplined and
does not diverge.

## 1. Fundamental Pattern — Reason / Act / Observe

Each iteration of the loop is an explicit RAO round:

1. **Reason** — before taking action, break down the objective into subtasks and state the
strategy of the current iteration. For each unit: what changes, where, why.
2. **Act** — execute: manipulate files, call APIs, write code, integrate data. One unit
at a time, isolated (subagent/worktree if multiple units mutate files in parallel).
3. **Observe** — analyze the **real** output (log, stack trace, metrics, render),
not the agent's summary. If the Stop Condition is not satisfied → new round
RAO, incorporating what you observed (see Version Memory).

## 2. The three elements of the loop

- **Trigger** — what triggers the loop: explicit user command, event of
system (hook/webhook), or cadence (cron/`ScheduleWakeup`).
- **Action** — the competence delegated to the loop (refactor, ETL, build feature, remediation node…).
- **Stop Condition (Definition of Done)** — **quantitative and objective**, never "seems
done": green test suite, endpoint responding 200, score ≥ threshold, gate passing.
Without a measurable DoD the loop doesn't know when to stop.

## 3. Architecture taxonomy — choose by complexity

| Architecture | Logic | When | Typical duration |
|---|---|---|---|
| **Loop Only** | An agent cycles through self-correction by reading its own error logs in the sandbox. | Linear task, isolated script, quick fix. | 15-30 min |
| **Maker-Checker** | One agent generates (Maker), a second **independent** valid with rigid address book (Checker); fix-loop until it passes. | Software component, UI layout, anything where "written" ≠ "correct". | 30-60 min |
| **Manager-Helpers (Swarm)** | Orchestrator (`Workflow`) distributes subtasks to a fleet of specialists; final summary. | Refactor of entire codebases, massive migrations, fan-out on many nodes. | 4-8 hours |

Rule of thumb in Life: research uses **Swarm** (`Workflow`), build uses
**Maker-Checker** (`subagent-driven-development` + opponent verification). The
**Solo Loop** is the targeted fix within a single unit.

> **True Edge of Environment:** The Swarm is **wide and flat**, not deep.
> `Workflow` nests **only one level** (an agent inside the workflow does not launch a
> other workflow) and subagents do not spawn subagents at will. No recursion
> infinite: orchestrate from the main session, in multiple sequential steps if needed.

## 4. Tooling binding

- **CLI / sandbox** — terminal to run code, launch tests, capture stacks
trace to replay in Reason. (`Bash`; large outputs to files and read in chunks.)
- **Visual verification** — for UI: MCP `playwright` or `chrome-devtools`, if installed →
screenshots and snapshots, comparison with the expected layout. Don't close a UI without rendering it.
- **Multi-source aggregator** — normalizes heterogeneous sources (prod logs, API docs,
markdown) in a summary, written to file by a subagent.

## 5. Guardrail (anti-loop-infinity, anti-budget-drift)

- **Explicit Hard Cap.** Sets a maximum of iterations (sensible default: **8 steps**
per unit/node). Upon reaching without DoD → **stop and report status**, not
continue. ⚠️ Automatic loops are **infinite by default** (for example `ralph-loop`
without `--max-iterations`): the cap must always be placed manually.
- **Version Memory (V1..Vn).** Stores the history of the intermediate outputs of the iteration
in the same session (what you tried, what the checker failed), so you don't repeat
the same error. Loop N feedback enters the loop N+1 prompt.
- **Failure threshold (pattern, not just count).** If ≥3 consecutive fixes fail,
**don't insist**: the problem is probably architectural → change your approach
(`systematic-debugging` Step 4 rule).
- **Asynchrony for long tasks.** Beyond ~2 h, run in background (workflow/`run_in_background`),
without blocking, with **intermediate reports** available for consultation. Don't keep the synchronous session busy.

## 6. Working example in Life

`.claude/workflows/node-remediation-cycle.js` (in the Life repo) — reusable workflow that
embodies all of the above: **Swarm** (one branch per node) by **Maker-Checker** (fix →
adversarial verification on disk + `brain-gate`), with **RAO** per iteration, **Hard Cap 8**,
Version Memory (`history[]` of checker feedback) and guardrails (never destructive DB ops).
Retrievable by name with `args` = slug list. Use it as a template when the task is
"autonomously bring a set of N similar units up to standard / system".
