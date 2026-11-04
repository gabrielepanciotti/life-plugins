---
name: orchestra-issue
description: "Orchestrate delegated and verified resolution of a series of issues. Use when the user asks for “resolve issues,” “issue roundup,” or “orchestrate,” or when the session has been opened as an orchestrator."
---

# Orchestra issue

This session selects, delegates, supervises, merges, and documents. The owner does not write production code here. Each issue is handled independently, and a result is merged only after the diff has been reviewed and the tests pass.

## How `llm-run` works

Life reads queues from `<instance>/config/llm-routing.json`. The caller chooses a category and difficulty level; the router tries the available providers in order and moves to the next if one fails.

```bash
scripts/llm-run run --categoria <categoria> --livello <facile|medio|difficile> \
  --dir <repo> "<compito>"
```

If `llm-run` is unavailable or the queue is full, use OpenCode subagents with the same self-contained task and checks. This fallback changes who performs the work; it does not reduce oversight or authorize the orchestrator to implement directly.

## Procedure for each issue

1. **Check the real state.** Look for commits that mention the issue, code, or configuration
indicated and, read only, any outcome data. If it is already solved, comment with evidence and close it. If it only needs an audit, perform and document it. If an owner decision is needed, apply `needs-human` and state the question and consequences of each option.

2. **Read and classify.** Run `gh issue view N`. Choose a category listed in the configuration, for example `implementazione`, `bugfix`, `test`, `refactoring`,
`migrazioni`, `frontend` or `documentazione`. Assign level:
- `facile`: mechanical, 1–3 files, no decision;
- `medio`: multiple files and verifiable ordinary logic;
- `difficile`: architecture, security, concurrency, migrations, many files or unknown cause.

3. **Delegation.** Write a self-contained task with context, acceptance criteria, files or modules, precise completion criteria, tests, and the phrase “do not commit”. If you start multiple processes, use a separate log for each issue and record its PID and path.

   ```bash
   scripts/llm-run run --categoria <categoria> --livello <livello> --dir <repo> \
     "<compito>" > <log-issue> 2>&1 &
   ```

4. **Check the executor.** Read the full output. In the indicated worktree check
`git status`, read the entire diff and run the required tests, plus lint, type-check or build
relevant. Do not integrate extraneous changes or incomplete proofs.

5. **Get difficult work reviewed.** Save the diff and ask for an independent review; with
`llm-run`, exclude if possible the family who wrote:

   ```bash
   scripts/llm-run run --categoria revisione --livello difficile \
     --escludi-famiglia <famiglia> --file <diff>
   ```

Verify every finding against the actual code. For corrections start a new delegate round with
errors, accepted findings and failed tests; then reread diff and test.

6. **Merge atomically.** Merge rounds of the same issue into a single commit with
`Closes #N`. Sequentially execute merge, commit, and tests on the integrated checkout; do not throw
Concurrent Git commands. Remove worktree and branch only after success. If the work is preserved but auto-commit failed, retrieve it from the worktree instead of launching it again.

7. **Close and report.** Only after integration and checks, comment on the issue with outcome,
tests and SHA. Update the documentation or the brain foreseen by the project. For usage that was not reported, write `unavailable`, never zero.

## What not to do

- Write production code in the orchestrator session.
- Merge without reading the whole diff and check the tests.
- Discard red tests as environmental without retrying them in the correct context.
- Delete a worktree that contains non-integrated work.
- Leave worktrees concluded after a successful integration.

Finish only when each issue has a documented outcome: integrated and verified, already resolved,
closed after verification or blocked by an explicit user decision.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py orchestra-issue` and apply the tree-specific appendix it prints. The appendix may be empty.
