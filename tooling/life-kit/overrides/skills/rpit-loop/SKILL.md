---
name: rpit-loop
description: Take a medium or complex development task through Research, Plan, Implement, and Test, with an approved plan before coding. Use when the task touches more than 3 files, requires research, or is a new feature; for trivial fixes under 3 files, use dev-workflow.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, MultiEdit
---

# RPIT Loop — Research, Plan, Implement, Test

Use when the task touches more than 3 files, is a new feature or integration, involves major
refactoring, or requires understanding how something works before acting. For an isolated fix under
3 files, use `dev-workflow`.

## Required tools

The repository determines which checks to use (`ruff`, `tsc --noEmit`, `npm run build`,
`pytest`). Do not install anything: if the repo has no checks, report that as a finding. Run Python
from the project `.venv`: `.venv/bin/python` on Linux, `.venv/Scripts/python` on Windows.

## Copy and check off

- [ ] R: area understood, project patterns found, no files created.
- [ ] P: plan written and **approved by the user**. Do not move to I without approval.
- [ ] I: plan implemented one file at a time; tests written for new logic.
- [ ] T: tests and mechanical checks pass; review performed with fresh context.
      If a test fails because of a code error, return to I. If it fails because the plan
      does not hold up, return to P and propose the plan again. If you misunderstood the area, return to R.
- [ ] Commit (with `Closes #N` if there was an issue) and push.

Finish only when every item is checked off.

## R — Research

1. Existing code in the area you are changing.
2. Project patterns: how similar things are built.
3. `.claude/docs/` for architecture, DB, and API.
4. Framework documentation: use `mcp__context7__resolve-library-id` and
   `mcp__context7__get-library-docs` if the server is active; otherwise, search the web.

For large research tasks, use the `Explore` subagent to keep the main context clear.

## P — Plan

Write the plan and wait for the user’s approval. If they add notes, update it and propose it again.
This is a basic format; adapt it to the task.

```markdown
## Piano: [titolo]
**Issue**: #N (se esiste)
**Goal**: what changes and why
**Files involved**: list
**Steps**:
1. [azione] → [file] (semplice/medio/complesso)
**Risks**: what could break
**Tests**: how we will verify
**Can be parallelized**: yes/no, which steps are independent
```

For a decision that is costly to reverse (architecture lasting years, vendor change, data schema
read by other projects), use the `consiglio` skill before planning and include its verdict under **Risks**.

## I — Implement

- Follow the approved plan; ask if a deviation is needed.
- New logic: tests first (red, then green, then cleanup), using the skill
  `superpowers:test-driven-development`.
- Bug: first write a test that reproduces the failure, then fix it and make that same test
  pass (use `superpowers:systematic-debugging` to find the cause). Keep the test as a regression test.
- One file at a time; after each file, check for errors.
- If something unexpected happens, stop and inform the user.
- For independent steps, propose parallel subagents (for more than 5 subagents, estimate effort and get approval first).

## T — Test

1. Run existing tests and those written in I; add at least one test for critical logic that lacks coverage.
2. Project checks: build, lint, and types.
3. For changed APIs, verify with `curl`. For the frontend, check that the console has no errors.
4. Fresh-context review: have the `revisione-codice` agent review the diff (the author remembers
   the intent, not just the diff). If auth, permissions, uploads, or personal data are involved,
   also use the `sicurezza` agent.
5. Once everything passes, commit and push.

## After the loop

- Commit with `Closes #N`, using the long-form message from the `git-workflow` skill; close the issue
  with the `github-issues` skill.
- If architecture, API, or DB changes, update `.claude/docs/` (use the `docs` agent).
- Record any decision made during the loop in the brain using the `idea` skill without asking.
- Milestone: `gh issue list -m "name" --json state`.
- If the loop went badly (spinning or rewriting the plan twice), suggest `/retro` to the user in one line (it is user-only; the model cannot invoke it).

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py rpit-loop` and apply what it prints (it may print nothing).

