---
name: lavoro-notturno
description: "Autonomously carries out delegated work while the user sleeps: researches with agents, prepares a report with options and mockups, and runs build loops until the deliverable is verified. Use when the user asks for overnight work, autonomous execution, or a loop until completion."
---

# Night work — autonomous execution while the owner sleeps

Index: Step 0 token approval · The 4 rules · The protocol (0–4) · When not to unblock yourself · Operational notes

The owner lets you work independently (typically overnight) and cannot answer.
After token approval (Step 0): **ask no questions; decide and document.**
Work in a loop until the deliverable is verified and working. Leave a clear report for
the owner to read upon waking, covering what you did, the choices made, and open options.

Copy and tick (if a check fails, go back to the indicated step):
- [ ] Step 0: Estimate and ceiling approved by the owner before they go to sleep (if missing, ask now, while the owner is still awake)
- [ ] Step 1: report with at least 3 options written to file (if missing, go back to step 1)
- [ ] Step 2: each unit verified with your own diffs and tests (if a test is red, stay in step 2)
- [ ] Step 3: the system actually ran (if something doesn't add up, go back to step 2)
- [ ] Step 4: written summary, with real token consumption compared to the cap

## Step 0 — token approval before sleep

The token-use rule (estimate and approval before a `Workflow` or more than 5 subagents) also applies at night: one verification workflow consumed an entire weekly budget without anyone approving its scale. “Work independently” authorizes the work, not its scale.

1. **Before the owner goes to sleep**, write an estimate: number of agents, estimated tokens, duration. Always include a **small version** (fewer agents, one verifier instead of three).
2. Wait for the owner to approve the estimate and a token **ceiling**. That approval is valid for that night only.
3. The ceiling also applies overnight. If you reach it, stop: deliver what is verified and note in the report what remains and why you stopped.
4. If the prompt has no approved ceiling, do not start a `Workflow` or use more than 5 subagents: use the small version (few agents, no workflow) and say so in the report.

## The 4 rules

1. **No questions after the go-ahead.** No `AskUserQuestion`, no “do you want me to proceed?”. At a crossroads, choose the most sensible option, record it in the report under “Decisions made independently (to be confirmed)”, and move on. A doubt is not a reason to stop; put it in the report. Ask token questions first (Step 0), not overnight.
2. **Loop until working.** The deliverable is not merely **written**; it is **verified**:
the code runs, the tests pass, the page renders, the endpoint responds.
Iterate until you see it work with your own eyes (execute, don't assume).
3. **Verify subagents, not their reports.** After each agent: `git status`,
`git diff`, `git log`, and **your** tests. Agents can go off track, make unsolicited commits, and sometimes report falsehoods. Trust the actual output, never a summary.
4. **Leave a record for the morning.** Keep everything in files (reports, mockups, specs, code), and put only the final summary in chat. An updated task list lets the owner see at a glance how far you have progressed.

## The protocol (in order)

### 0. Set the goal and record progress
- Understand the end goal (the "perfect deliverable" the user wants to find).
- Create a **task list** (`TaskCreate`) with the steps below, dependencies included.
Update it gradually (`in_progress` → `completed`): it is the morning dashboard.

### 1. Research storm (Workflow)
If the Step 0 estimate includes a `Workflow`, run it within that estimate and ceiling: it launches
agents in parallel across the problem. Without approval, use the small version
(few `Explore` agents, no workflow):
- **Existing code** (`agentType: 'Explore'`): what is already there, path:line, not to be reinvented.
- **Solution options**: 2-3 architectures compared with pros and cons.
- **External search** (web): state of the art, data sources, similar products.
- **Specific nodes** of the domain (e.g. data source, calculation logic).
- **UX patterns** if there is a UI involved.

Then a **synthesis phase** that **writes to file** (the agents use `Write`,
don't let megabytes of text come back to you):
- a **report** `<project>/.claude/docs/specs/YYYY-MM-DD-<topic>-research.md`
(or `docs/superpowers/specs/` if the project uses that) with: current state,
requirements, **at least 3 options** with comparative table, recommendation,
step-by-step roadmap, open questions;
- **2-3 HTML mockups** self-contained if the task has a UI (`.../mockups/`).

The workflow returns only a **compact manifest** (path + recommendation).
It runs in the background: while it runs, prepare anything that does not depend on the research.

### 2. Build standalone loop
With the report as your compass, **build** the deliverable. Use dedicated subagents
(`subagent-driven-development`) for the independent pieces, but **you remain
the orchestrator who checks**. For each unit:
- spec → implementer subagent → **you verify** (diff + real tests) → fix loop.
- Follow project patterns (stacks, ports, conventions in CLAUDE.md).
- TDD where it makes sense; Schema migrations with the project tool (Alembic), never DDL by hand.

Structure each iteration as a **Reason → Act → Observe** loop with a **Quantitative
Stop Condition** (passing test, endpoint returns 200, gate passed — never "looks done"),
an **explicit Hard Cap** (default 8 iterations/unit: over, stop and report — loops
here they are infinite by default), and **Version Memory** (the feedback of lap N enters the
round N+1, so you don't repeat the mistakes). Choose architecture by complexity:
**Loop only** (targeted fix) **Maker-Checker** (generate+validate independently)
**Manager-Helpers/Swarm** (`Workflow`, wide and flat fan-out — single nesting level).
Full detail + working example (`node-remediation-cycle.js`) in
`references/loop-engineering.md`.

### 3. End-to-end verification loop
Don't close until you have **run** the system:
- backend: migrate, launch, `curl` on endpoints;
- frontend: build/serve, verify that the page renders real data;
- if something doesn't add up → go back to the build loop (systematic debugging, root cause before fixing).
Repeat until the deliverable is what the user expects to find.

### 4. Morning recap
Close with a chat message **short and scannable, without emojis**:
- Done and verified (with how you verified it);
- Where are reports and mockups (path/URL);
- Decisions taken independently, to be confirmed;
- What remains and how to resume (command to start or see the result);
- Open questions (non-blocking: you have bypassed them, you list them here);
- Tokens used against the approved cap.

Follow this outline in order, adapting the depth of each section to the work.

Finish only when all the checks on the top list are ticked and the summary is written.

## When not to get unstuck with an arbitrary choice
Only when an action is irreversible and risky (dropping data without a backup, force-pushing
to `main`, sending something externally, spending real money, handling credentials) and there is no
safe default: do not proceed. Prepare everything up to that point and list it among
the open questions. For everything else, decide and move on.

## Operational notes
- Commit/push: make one commit per verified unit and name the files (skill `git-workflow`).
Pushing to the working branch is fine. On shared `main`/`master`, **do not** push
autonomous work the owner has not seen unless the owner authorized it before going to sleep.
- Tokens: the cap approved in Step 0 also applies overnight. Within the ceiling, completeness and
verified correctness matters more than speed: an extra loop is better than a deliverable
  “written but untested”.
- See also: `references/loop-engineering.md` (architectures, RAO, hard cap, version
memory, async), `superpowers:subagent-driven-development`,
`superpowers:systematic-debugging`, and the "check subagents, not reports" reflex.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py lavoro-notturno` and apply what it prints. It may print nothing.
