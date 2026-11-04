---
name: do-everything
description: "Process all open GitHub issues in a project using a tree of subagents, persistent state, and recovery after interruption. Use it for ‘do all issues’, ‘process the entire backlog’, `/do-everything`, `/do-everything resume`, or work status requests."
---

# do-everything — all open issues, with parallel subagents

Index: Estimate · Agent tree · State · Init or resume · Discovery · Categories and dependencies · Questions · Launch · Monitoring · Resume · Rules

Work starts only after an estimate is confirmed. Read the stack, commands, ports, and conventions
from the project instruction file and its documentation; pass them to subagents without
inventing values.

## Before starting — estimate and confirmation

Before launching more than five subagents, tell the user:

- number of issues, categories, and planned agents;
- estimated tokens and duration;
- a reduced option, such as one priority or a single category.

Wait for explicit confirmation. Authorization applies to that run; if the remaining work
changes significantly, update the estimate.

## Agent tree

```text
Orchestrator
├── category coordinator
│   └── issue agent: research and plan
│       └── executor: implementation and verification
│           └── sub-executor, only for independent parts
```

- Do not specify a model unless the environment requires it.
- Launch independent agents together; keep dependent work sequential.
- Assign each coordinator an isolated worktree.
- If an executor fails twice on the same step, increase its reasoning capacity
  or change the executor for that step only.

## State

Maintain `.claude/do-everything/state.json` at the project root and update it after every
state change. Minimum structure:

```json
{
  "session_id": "YYYYMMDD_HHMMSS",
  "created_at": "ISO datetime",
  "project": "nome",
  "categories": [],
  "issues": {
    "123": {
      "id": 123,
      "title": "...",
      "labels": [],
      "category": "...",
      "status": "pending|questions|ready|running|completed|blocked|failed",
      "blocking": [],
      "blocked_by": [],
      "needs_decision": false,
      "questions": [],
      "answers": [],
      "branch": null,
      "agent_id": null,
      "completed_at": null,
      "error": null
    }
  },
  "question_queue": [],
  "macro_agents": {},
  "stats": {"total": 0, "completed": 0, "running": 0, "blocked_on_questions": 0, "failed": 0}
}
```

## Checklist

- [ ] Read existing state, or create the folder.
- [ ] Shared the estimate and received confirmation.
- [ ] Fetched issues with `gh issue list`.
- [ ] Recorded categories and dependencies.
- [ ] Queued structural questions.
- [ ] Started coordinators for ready categories.
- [ ] Before each closure: tests pass, build succeeds, and diff is reviewed.
- [ ] At the end: list branches and outcomes for user review.

## Phase 0 — Init or resume

```bash
test -f .claude/do-everything/state.json
```

If it exists, read it, show the summary, and follow **Resume**. If it does not exist, create the folder and
continue with discovery.

## Phase 1 — Discovery

```bash
gh issue list --state open --json number,title,labels,body --limit 200
```

Record the number, title, labels, body, and references to other issues.

## Phase 2 — Categories and dependencies

Group issues into no more than 6–8 domains derived from labels and documentation.
For each, note:

- explicit dependencies in the body;
- implicit dependencies required for it to work;
- `needs_decision: true` if there are multiple valid approaches with different impacts, architectural trade-offs,
  or ambiguous product logic.

Do not ask about decisions already defined in the project instructions.

## Phase 3 — Questions

For each issue with `needs_decision`, prepare 2–4 questions that materially affect the product,
with options and concrete consequences. Add them to `question_queue` and present them one at a time:

```text
Issue #N — title
Context for the dilemma in 2–3 lines.
Question: option A, B, or C, with consequences.
```

A question does not block independent issues.

## Phase 4 — Parallel launch

For each category with ready issues, start a coordinator in the background and in an
isolated worktree. Adapt this prompt:

```text
Coordinate category <category> of project <project>.
Manage issues while respecting dependencies. For each one, start an agent to read the files,
produce a plan, and delegate implementation to an executor.

Issues: <id, title, dependencies, answers>
Sequence: <parallel work and constraints>
Context: read the repository instructions and documentation.

For each issue: research, plan, implementation, tests and build, diff review, commit with
Closes #N. Add only the files changed. Do not merge into the main branch.
```

When the user answers a question, save the answer in the state and send it to the active
coordinator, or include it in its startup prompt.

## Phase 5 — Monitoring

Read `state.json`, verify branches and worktrees, and show:

- completed out of total;
- issues in progress with their branches;
- next question;
- blocked issues and their dependencies;
- failed issues and the error;
- issues not yet started.

Do not consider an agent active just because its branch exists: look for recent commits or
modified files in the worktree.

## Resume

1. If the state is missing, say so and stop without creating files.
2. Recalculate statistics and mark interrupted agents `failed`, preserving branches and
   worktrees.
3. Handle, in order: open questions, failed issues to retry, ready issues without an agent,
   final review of completed issues.
4. Before relaunching more than five agents, update the estimate and wait for confirmation.

Conversational commands: `skip` blocks only the issue for the current question; `status` shows
the summary; `retry` proposes relaunching failed issues.

## Rules

- One worktree per coordinator; independent agents run in parallel.
- A failure does not stop other categories.
- Do not merge into the main branch: leave branches for user review.
- Do not close issues before tests, build, and review.
- Ask no more than four structural questions per issue.
- Update state immediately: it is the contract that makes the work resumable.

Finish only when every issue has a consistent status, checks for completed issues are
documented, and the user has the list of branches and decisions still needed.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py do-everything` and apply what it prints (it may print nothing).
