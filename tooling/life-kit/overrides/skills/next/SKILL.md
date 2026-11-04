---
name: next
description: "Proposes the next task taken from the project's open GitHub issues, prepares the briefing and guides the reset of the context. Use it when the user writes /next, «next task», «what needs to be done», «what do I have to do», «resume work». To open, close or split a specific issue use github-issues."
---

# /next — next task from issues, with context reset

Issues are the project todolist (`backlog.md` is just a pointer, not a source).
The task: choose the issue with the user, give a briefing, then start again with a clean context.

## Copy and tick

- [ ] Step 1: Open task table shown, no code file read.
- [ ] Step 2: issue chosen by the user and written briefing. If the issue does not exist or already exists
closed, return to step 1.
- [ ] Step 3: the user made `/clear` and wrote «proceed with #N».
- [ ] Step 4: workflow chosen for complexity and started; when the job is finished, commit with
`Closes #N`.

## 1. List of tasks

```bash
gh issue list --state open --json number,title,labels --limit 100
```

Build the table ordered by priority (P1, then P2, then P3; if the number is equal, the plus number
Bass). Priority and domain are obtained from the repo labels (for example `priority:P1`,
`backend`); without priority label, sort by number. The table is the basic form:
adapt it to the labels that the repo actually has.

```
## Open tasks
| # | Titolo | P | Dominio |
|---|--------|---|---------|
| 14 | Drafts missing after seeding | P1 | backend |

Recommended next: #14 (P1). Confirm or choose another?
```

Do not read code files before confirming. If there are no open issues, say so and suggest `gh issue create` only if the owner has a task to record.

## 2. After confirmation — briefing

```bash
gh issue view NUMERO --json number,title,body,labels,comments
```

Write a compact briefing: objective in 1-2 lines, files involved (estimated), complexity
(simple, medium, complex) and suitable workflow.

## 3. Reset the context

Only the user can do the `/clear`. After the briefing tell him:

```
Briefing ready. Type /clear, then write: "proceed with #NUMBER"
```

When the owner writes «proceed with #N»: reread the issue (`gh issue view N --json title,body`),
read the files indicated in the briefing and start the workflow without further questions.

## 4. Workflow for complexity

| Complexity | How |
|---|---|
| Simple (less than 3 rows) | Read files, deploy, commit with `Closes #N` and push. |
| Medium (3-10 files) | Skill `rpit-loop`: research, plan, wait for yes, implement, test. |
| Complex (over 10 files) | Branch `feature/short-name`, brainstorm and spec, subagents in parallel if useful (over 5 subagents: estimate and yes before). |

If other sessions are alive on the same repo, work in your worktree
(`EnterWorktree`, or `git worktree add`), not in shared checkout.

## Final check

- [ ] The issue was closed by commit (`gh issue view N --json state`).
- [ ] Test and build of the project pass.

Finish only when the checks pass. If one fails, go back to step 4.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py next` and apply the tree-specific appendix it prints. The appendix may be empty.
