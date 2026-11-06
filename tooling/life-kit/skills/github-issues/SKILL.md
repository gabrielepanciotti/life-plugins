---
name: github-issues
description: "Manages the project's GitHub issues, which are its todolist (all via gh CLI). Use it when an issue is touched — open it, close it, break it down, label it — or when the user writes only a number (\"31\", \"make 12\"), \"create issue\", \"open an issue\", \"close #N\", \"backlog\". To choose the next task among the open ones (\"what should I do\", \"next task\") use next."
allowed-tools: Bash, Read, Write, Grep
---

# GitHub Issues — Task management

GitHub Issues is the TODO of the project. Every significant task becomes an issue. No issues for trivial stuff (type, formatting).

## Where do you start from

- **the user writes only one number** ("10", "make it 12", "let's make it 31"): it is the issue with that number in the current repo. Don't ask for clarification: `gh issue view N`, execute the task, close with a commit `Closes #N` (see «Issue-driven work»). This applies to all projects.
- **the user asks «what should I do» or «backlog»**: list the open issues (command below) and propose the next one.
- **A new task emerges as you work**: create the issue («Create issue» section).

## Needed

`gh` authenticated (`gh auth status`). If missing: `sudo apt install gh` on Linux, `winget install GitHub.cli` on Windows, then `gh auth login`.

## Create issue
All `gh` commands on one line, without `\` to wrap. Title of maximum 60 characters.
```bash
gh issue create -t "feat: short description" -b "Details if needed" -l "type:feature"

# With acceptance criteria (the body may span lines inside the quotes)
gh issue create -t "fix: margin calculation bug" -b "## Problema
Margin calculated without VAT.
## Acceptance Criteria
- [ ] Margin includes VAT
- [ ] Unit test
- [ ] Correct endpoint" -l "type:bug" -l "priority:P1"
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

1. **Check open issues** (compact output with `--json` + `--jq`):
```bash
gh issue list --state open --json number,title,labels --jq '.[] | "#\(.number) [\(.labels | map(.name) | join(","))] \(.title)"'
```
2. **Start work.** Large task (more than 10 files): `gh issue develop N --checkout`. Normal task: Work on main.
3. **End of work.** The commit closes the issue: the message has two `-m`, the second with `Closes #N`. A `\n` inside `-m` remains literal text and the issue does not close. No `git add -A && git commit` when other sessions work on the same repo: the commit is done with only the files of this session (skill `git-workflow`).
```bash
git commit -m "feat: short description" -m "Closes #N"
git push origin HEAD
```
4. **Final check.** The issue must be closed:
```bash
gh issue view N --json state
```
If it says `OPEN`, the push did not arrive or the message does not contain `Closes #N`: go back to step 3. Close (`gh issue close N`) by hand only after understanding why it did not close on its own.

Finish only when `gh issue view N --json state` says `CLOSED`.

## Sub-tasks and milestones
A subtask is a checklist in the body of the issue.
```bash
gh api repos/{owner}/{repo}/milestones -f title="v1.0" -f description="First release"
gh issue edit N -m "v1.0"
gh issue list -m "v1.0" --json state --jq 'group_by(.state) | map({state: .[0].state, count: length})'
```
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py github-issues` and apply the tree-specific appendix it prints. The appendix may be empty.
