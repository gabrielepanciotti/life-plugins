---
name: orchestra-issue
description: "Orchestrate delegated and verified resolution of a series of issues. Use when the user asks for “resolve issues,” “issue roundup,” or “orchestrate,” or when the session has been opened as an orchestrator."
---

# Orchestra issue

This session selects, delegates, supervises, merges, and documents. It does not write
production code. It treats each issue as an independent unit and merges a result only after
reviewing the diff and passing the tests.

## How `llm-run` works

Life reads queues from `<instance>/config/llm-routing.json`. The caller chooses a category
and difficulty level; the router tries the available providers in order and moves to the next
if one fails.

```bash
scripts/llm-run run --categoria <categoria> --livello <facile|medio|difficile> \
  --dir <repo> "<compito>"
```

If `llm-run` is unavailable or the queue is full, use OpenCode subagents with the same
self-contained task and checks. The fallback changes who performs the work; it does not reduce
oversight or authorize the orchestrator to implement directly.

## Procedure for each issue

1. **Check the actual state.** Look for commits that mention the issue, inspect the indicated
code or configuration, and review any outcome data without changing it. If the issue is already
resolved, comment with the evidence and close it. If it only requires an audit, perform and
document it. If a user decision is needed, apply `needs-human` and state the consequences of
each option in the question.

2. **Read and classify.** Run `gh issue view N`. Choose a category defined in the
configuration, for example `implementazione`, `bugfix`, `test`, `refactoring`,
`migrazioni`, `frontend`, or `documentazione`. Assign a difficulty level:
- `facile`: mechanical, 1–3 files, no decision;
- `medio`: multiple files and verifiable ordinary logic;
- `difficile`: architecture, security, concurrency, migrations, many files or unknown cause.

3. **Delegate.** Write a self-contained task with context, acceptance criteria, files or
modules, precise completion criteria, tests, and the phrase "do not commit". If you start
multiple processes, use a separate log for each issue and record its PID and path.

   ```bash
   scripts/llm-run run --categoria <categoria> --livello <livello> --dir <repo> \
     "<compito>" > <log-issue> 2>&1 &
   ```

4. **Check the executor's work.** Read the full output. In the indicated worktree, check
`git status`, read the entire diff, and run the required tests, plus lint, type checks, or builds
as relevant. Do not integrate unrelated changes or incomplete evidence.

5. **Request an independent review for difficult issues.** Save the diff and request an
independent review. With `llm-run`, exclude the authoring model family if possible:

   ```bash
   scripts/llm-run run --categoria revisione --livello difficile \
     --escludi-famiglia <famiglia> --file <diff>
   ```

Check every finding against the actual code. For corrections, start a new delegation round with
the errors, accepted findings, and failed tests; then reread the diff and rerun the tests.

6. **Merge atomically.** Combine rounds for the same issue into a single commit with
`Closes #N`. Run the merge, commit, and tests sequentially in the integrated checkout; do not
run concurrent Git commands. Remove the worktree and branch only after success. If the work is
preserved but autocommit failed, retrieve it from the worktree instead of relaunching the task.

7. **Close and report.** Only after integration and checks, comment on the issue with the
outcome, tests, and SHA. Update the documentation or brain specified by the project. For usage
that was not reported, write `unavailable`, never zero.

## What not to do

- Write production code in the orchestrator session.
- Merge without reading the whole diff and check the tests.
- Discard red tests as environmental without retrying them in the correct context.
- Delete a worktree that contains non-integrated work.
- Leave worktrees concluded after a successful integration.

Finish only when every issue has a documented outcome: integrated and verified, already
resolved, closed after verification, or blocked pending an explicit user decision.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py orchestra-issue` and apply what it prints. It may print nothing.
