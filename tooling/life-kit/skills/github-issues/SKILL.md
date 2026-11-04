---
name: github-issues
description: "Manage project GitHub issues as its task list (all through the gh CLI). Use when handling an issue—creating, closing, splitting, or labeling it—or when the user writes only a number («31», «do 12»), «create issue», «open an issue», «close #N», or «backlog». To choose the next task from open issues («what should I do», «next task»), use next."
allowed-tools: Bash, Read, Write, Grep
---

# GitHub Issues — Task management

GitHub Issues is the project's TODO list. Turn every significant task into an issue. Do not create issues for trivial things (typos, formatting).

## Where to start

- **The user writes only a number** («10», «do 12», «let's do 31»): this is the issue with that number in the current repository. Do not ask for clarification: run `gh issue view N`, do the task, and close it with a commit containing `Closes #N` (see “Issue-driven work”). This applies to every project.
- **The user asks “what should I do” or “backlog”**: list the open issues (command below) and suggest the next one.
- **A new task comes up while you are working**: create an issue (see “Create issues”).

## Requirements

`gh` must be authenticated (`gh auth status`). If it is missing: run `sudo apt install gh` on Linux or `winget install GitHub.cli` on Windows, then run `gh auth login`.

## Create issues
Put each `gh` command on one line; do not use `\` to continue a line. Keep titles to 60 characters or fewer.
```bash
gh issue create -t "feat: descrizione breve" -b "Dettagli se servono" -l "type:feature"

# With acceptance criteria (the body can span multiple lines inside the quotes)
gh issue create -t "fix: bug calcolo margine" -b "## Problema
Margine calcolato senza IVA.
## Acceptance Criteria
- [ ] Margine include IVA
- [ ] Test unitario
- [ ] Endpoint corretto" -l "type:bug" -l "priority:P1"
```

## Standard labels (create on first use)
```bash
gh label create "type:feature" --color 0E8A16
gh label create "type:bug" --color D73A4A
gh label create "type:refactor" --color FBCA04
gh label create "priority:P1" --color D73A4A
gh label create "priority:P2" --color FBCA04
gh label create "priority:P3" --color 0E8A16
```

## Issue-driven work

1. **Check the open issues** (compact output with `--json` and `--jq`):
```bash
gh issue list --state open --json number,title,labels --jq '.[] | "#\(.number) [\(.labels | map(.name) | join(","))] \(.title)"'
```
2. **Start work.** For a large task (more than 10 files): `gh issue develop N --checkout`. For a normal task: work on main.
3. **Finish work.** The commit closes the issue: use two `-m` options, with `Closes #N` in the second. A `\n` inside `-m` remains literal text, so the issue will not close. Do not run `git add -A && git commit` when other sessions are working in the same repository: commit only the files from this session (skill `git-workflow`).
```bash
git commit -m "feat: breve" -m "Closes #N"
git push origin HEAD
```
4. **Final check.** The issue must be closed:
```bash
gh issue view N --json state
```
If it says `OPEN`, the push did not arrive or the message did not include `Closes #N`: return to step 3. Close it manually (`gh issue close N`) only after understanding why it did not close automatically.

Finish only when `gh issue view N --json state` reports `CLOSED`.

## Subtasks and milestones
A subtask is a checklist in the issue body.
```bash
gh api repos/{owner}/{repo}/milestones -f title="v1.0" -f description="Prima release"
gh issue edit N -m "v1.0"
gh issue list -m "v1.0" --json state --jq 'group_by(.state) | map({state: .[0].state, count: length})'
```

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py github-issues` and apply what it prints (it may print nothing).
