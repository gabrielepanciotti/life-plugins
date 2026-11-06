---
name: do-everything
description: "Process all open GitHub issues of a project with a subagent tree, persistent state and resume after an interrupt. Use it for «do all issues», «process all backlog», `/do-everything`, `/do-everything resume` or job status requests."
---

# do-everything — all open issues, with subagents in parallel

Index: Estimation · Agent tree · Status · Init or resume · Discovery · Categories and dependencies · Questions · Startup · Monitoring · Resume · Rules

The work starts only after a confirmed estimate. Read stacks, commands, ports and conventions from
project instruction files and its documentation; pass them to subagents without
invent values.

## Before starting — estimate and confirm

Before launching more than five subagents, tell the user:

- number of issues, categories and agents expected;
- token and duration estimate;
- a reduced version, for example a priority or a single category.

Wait for explicit confirmation. The authorization is valid for that run; if the remaining work
changes significantly, update the estimate.

## Agent tree

```text
Orchestrator
├── category coordinator
│   └── issue agent: research and plan
│       └── executor: implementation and verification
│           └── sub-executor, only for independent parts
```

- Do not specify a template if the environment does not require it.
- Launch independent agents together; keep those with dependencies in sequence.
- Assign each coordinator an isolated worktree.
- If an executor fails twice on the same step, increase the reasoning effort or replace the executor for that step only.

## State

Keep `.claude/do-everything/state.json` in the project root and update it after every
change of state. Minimum form:

```json
{
  "session_id": "YYYYMMDD_HHMMSS",
  "created_at": "ISO datetime",
  "project": "project-name",
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

## Copy and tick

- [ ] Existing status read, or folder created.
- [ ] Estimate communicated and confirmation received.
- [ ] Issues downloaded with `gh issue list`.
- [ ] Registered categories and dependencies.
- [ ] Structural questions queued.
- [ ] Coordinators started for ready categories.
- [ ] Before each shutdown: green tests, successful build and revised diff.
- [ ] At the end: branches and outcomes listed for user review.

## Phase 0 — Init or resume

```bash
test -f .claude/do-everything/state.json
```

If it exists, read it, show the summary and follow **Resume**. If it does not exist, create the folder and
continue with discovery.

## Phase 1 — Discovery

```bash
gh issue list --state open --json number,title,labels,body --limit 200
```

Record number, title, label, body and references to other issues.

## Phase 2 — Categories and dependencies

Group issues into no more than 6-8 domains obtained from labels and documentation.
For each one write down:

- explicit dependencies in the body;
- implicit dependencies necessary for operation;
- `needs_decision: true` if there are multiple valid approaches with different impacts, trade-offs
architectural or ambiguous product logic.

Don't ask for decisions already defined in the project instructions.

## Phase 3 — Questions

For each issue with `needs_decision`, prepare 2-4 questions that really change the product,
with concrete options and consequences. Enter them in `question_queue` and present them one at a time:

```text
Issue #N — title
Describe the dilemma in 2–3 lines.
Question: choose option A, B, or C, with the consequences.
```

A question does not block independent issues.

## Phase 4 — Parallel startup

For each category with ready issues, start a coordinator in the background and in an isolated worktree. Adapt this prompt:

```text
Coordinate the <category> of project <project>.
Handle issues according to their dependencies. For each issue, start an agent to read the files,
produce a plan, and delegate implementation to an executor.

Issues: <id, title, dependencies, answers>
Sequence: <parallel work and constraints>
Context: read the repository instructions and documentation.

For each issue: research, plan, implement, test and build, review the diff, and commit with
Closes #N. Add only changed files. Do not merge into the main branch.
```

When the user answers a question, save the answer in the status and send it to
active coordinator or include it in its startup prompt.

## Phase 5 — Monitoring

Read `state.json`, check branch and worktree and show:

- completed out of the total;
- issue running with branch;
- next question;
- blocked and related dependencies;
- failed with the error;
- issue still to be started.

Don't consider an agent alive just because the branch exists: look for modified commits or files
recently in the worktree.

## Resume

1. If the state is missing, say so and stop without creating files.
2. Recalculate the statistics and mark the interrupted agents as `failed`, maintaining branches and
worktree.
3. Manage in order: open questions, failures to retry, issues ready without agent,
final review of the completed ones.
4. Before relaunching more than five agents, update the estimate and wait for confirmation.

Conversational commands: `skip` blocks only the issue with the current question; `status` shows the summary; `retry` proposes rerunning failed issues.

## Rules

- One worktree per coordinator; independent agents in parallel.
- Failure does not stop the other categories.
- No merge on main branch: branches remain for user review.
- No locking before testing, building and review.
- A maximum of four structural questions per issue.
- Update the status immediately: it is the contract that makes the work resumeable.

Finish only when each issue has a consistent status, the completed checks are
documented and the user has the list of branches and decisions still needed.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py do-everything` and apply the tree-specific appendix it prints. The appendix may be empty.
