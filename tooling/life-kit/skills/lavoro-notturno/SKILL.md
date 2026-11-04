---
name: lavoro-notturno
description: "Autonomously carries out delegated work while the user sleeps: researches with agents, prepares a report with options and mockups, and runs build loops until the deliverable is verified. Use when the user asks for overnight work, autonomous execution, or a loop until completion."
---

# Night work — autonomous execution while the user sleeps

Index: Step 0 the yes on tokens · The 4 rules · The protocol (0-4) · When not to unblock yourself · Operational notes

The user lets you work independently (typically overnight) and cannot answer.
After approval of the token budget (Step 0): **no questions asked, just decide and document.**
You work in a loop until a verified working deliverable, leaving
upon waking up a clear report with what was done, the choices and open options.

Copy and tick (if a check fails, go back to the indicated step):
- [ ] Step 0: Estimate and ceiling approved by user before he went to sleep (if missing, ask for them now, while he is still awake)
- [ ] Step 1: report with at least 3 options written to file (if missing, go back to step 1)
- [ ] Step 2: each unit verified with your own diffs and tests (if a test is red, stay in step 2)
- [ ] Step 3: the system actually ran (if something doesn't add up, go back to step 2)
- [ ] Step 4: written summary, with real token consumption compared to the cap

## Step 0 — the yes on the tokens, before sleeping

The rule on token consumption (estimate and yes before a `Workflow` or more than 5 subagents) also applies at night: a verification workflow alone consumed an entire weekly budget without anyone having approved the scale. «Go independently» authorizes the work, not the scale.

1. **Before the user goes to sleep**, write an estimate: number of agents, estimated tokens, duration. Always include a **small version** (fewer agents, one verifier instead of three).
2. Wait for his yes to an estimate and a **ceiling** of tokens. The yes is valid for that night only.
3. The cap also applies overnight. If you reach it, you stop: you deliver what is verified, write in the report what remains and why you stopped.
4. If there is no approved ceiling in the prompt, do not start with the `Workflow` or with more than 5 subagents: work with the small version (few agents, no workflow) and say so in the report.

## The 4 rules

1. **Zero questions after the green light.** No `AskUserQuestion`, no "do you want me to proceed?". In front of
a crossroads: choose the option that makes the most sense, state it in the report below
«Decisions made independently (to be confirmed)», and move on. A doubt is not a
reason to stop: it's a line in the report. Token questions are asked first (Step 0), not at night.
2. **Loop until working.** The deliverable is not «written», it is **verified**:
the code runs, the tests pass, the page renders, the endpoint responds.
Iterate until you see it work with your own eyes (execute, don't assume).
3. **Verify subagents, not their reports.** After each agent: `git status`,
`git diff`, `git log`, and **your** tests. The agents deviate with brooms,
they commit unsolicited things and sometimes report falsehoods. Trust the actual output, never a summary.
4. **Leave traces for the morning.** Everything on file (reports, mockups, specs, code),
only the final summary in chat. An updated task list = the user can see at a glance where you have arrived.

## The protocol (in order)

### 0. Define and track
- Understand the desired end result (the "perfect deliverable" the user wants to find).
- Create a **task list** (`TaskCreate`) with the steps below, dependencies included.
Update it gradually (`in_progress` → `completed`): it is the morning dashboard.

### 1. Research storm (Workflow)
If the Step 0 estimate includes a `Workflow`, throw it within that estimate and that ceiling: it's the
surge of agents, in parallel on all sides of the problem. Without the yes, use the small version
(few `Explore` agents, no workflow):
- **Existing code** (`agentType: 'Explore'`): what is already there, path:line, not to be reinvented.
- **Solution options**: 2-3 architectures compared with pros/cons.
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

The workflow only gives you a **compact manifest** (path + recommendation).
Works in the background: while it runs, it prepares what does not depend on the search.

### 2. Standalone build loop
With the report as your compass, **build** the deliverable. Use dedicated subagents
(`subagent-driven-development`) for the independent pieces, but **you remain
the orchestrator who checks**. For each unit:
- spec → implementer subagent → **you verify** (diff + real tests) → fix loop.
- Follow project patterns (stacks, ports, conventions in CLAUDE.md).
- TDD where it makes sense; Schema migrations with the project tool (Alembic), never DDL by hand.

Structure each iteration as a **Reason → Act → Observe** loop with a **Stop
Quantitative Condition** (green test, endpoint 200, gate passed — never "looks done"),
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

This is the outline to follow as it is: the entries remain in this order, but the breadth of each adapts to the work.

Finish only when all the checks on the top list are ticked and the summary is written.

## When not to force an arbitrary choice
Only if an action is irreversible and risky (data drop without backup, push
forced on `main`, sending out, real spend, credentials) and there is no
safe default: don't do it, leave everything ready up to that point and put it in between
open questions. Everything else: decide and move on.

## Operational notes
- Commit/push: one commit per verified unit, with the files named (skill `git-workflow`).
Push is fine on the working branch; on shared `main`/`master` **do not** push in
autonomy stuff that the user hasn't seen, unless he authorized it before going to sleep.
- Token: the cap approved in Step 0 also applies at night. Inside the roof, the completeness and the
verified correctness matters more than speed: an extra loop is better than a deliverable
  “written but untested”.
- See also: `references/loop-engineering.md` (architectures, RAO, hard cap, version
memory, async), `superpowers:subagent-driven-development`,
`superpowers:systematic-debugging`, and the "check subagents, not reports" reflex.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py lavoro-notturno` and apply the tree-specific appendix it prints. The appendix may be empty.
