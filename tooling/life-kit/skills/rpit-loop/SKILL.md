---
name: rpit-loop
description: Take a medium or complex development task through Research, Plan, Implement, and Test, with the plan approved before coding. Use when a task touches more than 3 files, requires research, or is a new feature; for trivial fixes in fewer than 3 files, use dev-workflow.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, MultiEdit
---

# RPIT Loop — Research, Plan, Implement, Test

Use this when a task touches more than 3 files, is a new feature or integration, is a major
refactoring, or requires understanding how something works before acting. For an isolated fix in fewer
than 3 files, use `dev-workflow`.

## Required tools

The repo decides which checking tools to use (`ruff`, `tsc --noEmit`, `npm run build`,
`pytest`). Do not install anything: if the repo has none, report that as a finding. Use Python
from the project's `.venv`: `.venv/bin/python` on Linux, `.venv/Scripts/python` on Windows.

## Copy and check off

- [ ] R: area understood, project patterns found, no files created.
- [ ] P: plan written and **approved by the user**. Do not proceed to I without approval.
- [ ] I: plan executed, one file at a time, tests written for new logic.
- [ ] T: tests and mechanical checks pass, review done with fresh context.
      If a test fails due to a code error, return to I. If it fails because the plan does
      not hold up, return to P and propose the plan again. If you misunderstood the area,
      return to R.
- [ ] Commit (with `Closes #N` if there was an issue) and push.

Finish only when every item is checked off.

## R — Research

1. Existing code in the area you will touch.
2. Project patterns: how similar things are built.
3. `.claude/docs/` for architecture, DB, and API.
4. Framework documentation: `mcp__context7__resolve-library-id` and
   `mcp__context7__get-library-docs` if the server is active; otherwise, web search.

For large research tasks, use the `Explore` subagent to keep the main context clear.

## P — Plan

Write the plan and wait for the user's approval. If they add a note, update it and propose it again. This
is a basic format; adapt it to the task.

```markdown
## Plan: [title]
**Issue**: #N (if any)
**Goal**: what changes and why
**Files involved**: list
**Steps**:
1. [action] → [file] (simple/medium/complex)
**Risks**: what might break
**Tests**: how we will verify
**Parallelizable**: yes/no, which steps are independent
```

For a costly-to-reverse decision (architecture that will last for years, changing
provider, data schema read by other projects), first use the `consiglio` skill and include its verdict under **Risks**.

## I — Implement

- Follow the approved plan; ask if a deviation is needed.
- New logic: write tests first (red, then green, then cleanup), skill
  `superpowers:test-driven-development`.
- Bug: first write a test that reproduces it and fails, then fix it, then get that same test
  passing (`superpowers:systematic-debugging`). Keep the test as a regression test.
- One file at a time; after each file, verify that it has no errors.
- If something unexpected happens, stop and inform the user.
- Independent steps: propose parallel subagents (for more than 5 subagents, estimate and get approval first).

## T — Test

1. Run existing tests and those written in I; critical logic without tests needs at least one.
2. Run the project's mechanical checks: build, lint, types.
3. If the API changed: verify with `curl`. For frontend: no console errors.
4. Review with fresh context: agent `revisione-codice` on the diff (the author knows the intent,
   not the diff). If auth, permissions, uploads, or personal data were touched,
   also use agent `sicurezza`.
5. Everything passes: commit and push.

## After the loop

- Commit with `Closes #N`, long-form message using the `git-workflow` skill; close
  the issue using the `github-issues` skill.
- If architecture, API, or DB changed: update `.claude/docs/` (agent `docs`).
- Any decision made during the loop: use the `idea` skill and record it in the brain without asking.
- Milestone: `gh issue list -m "name" --json state`.
- If the loop went badly (spinning without progress, plan rewritten twice): suggest `/retro`
  to the user in one line (user-only; the model cannot run it).

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py rpit-loop` and apply what it prints (it may print nothing).

