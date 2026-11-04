---
name: git-workflow
description: "Writes long-form commit messages, closes an issue with a commit (Closes #N), manages feature branches, and resolves merge conflicts. Use it when you need an explicit commit message, a `Closes #N`, a feature branch, or when the git output shows CONFLICT."
allowed-tools: Bash
---

# Git Workflow — commits, branches, conflicts

Index: Basic rule Explicit commit Closing an issue Feature branch Non-merging branch Conflicts Token saving

Multiple Claude sessions can work on the same repo: they share a single working tree and a single index. This is why we always commit with the named files and always merge from a worktree that already has the right branch.

Quick guide: if you only need a message or a `Closes #N`, use “Explicit commit.” If you need to isolate a large task, use “Feature branch.” If Git shows `CONFLICT`, use “Conflicts.”

## Basic rule

One commit per completed task, followed immediately by a push. Work on the main branch; use a feature branch only for tasks involving more than 10 files. Files created, deleted, or moved via Bash (`mv`, `cp`, script) must be explicitly named in the commit.

## Explicit commit

```bash
git commit -m "feat: short description" -- <files for this session>
git push origin HEAD
```

The pathspec after `--` is mandatory: without it, the commit takes everything in index, even the work of other sessions. Never `git add -A && git commit` when another session is alive on the same repo.

Types: `feat:` `fix:` `refactor:` `docs:` `test:` `chore:`
- Maximum 50 characters, in English.
- No commit body, except for `Closes #N`.

## Close an issue with commit

The message goes on multiple true lines (`\n` inside the quotes does not wrap, so `Closes #N` would not be read):

```bash
git commit -F - -- <files for this session> <<'MSG'
feat: short description

Closes #N
MSG
git push origin HEAD
```

After the push, check that the issue has closed: `gh issue view N --json state`.

## Feature branch (task of more than 10 files)

The branch is removed when the task is complete: closing the issue, merging the work, and deleting the branch happen together. If these steps are separated, in a month no one will know whether the branch contains anything.

1. Create the branch in your own worktree, without touching the shared tree (`EnterWorktree`, or manually):
   ```bash
   git -C <repo> worktree add ../<repo>-feature-short-name -b feature/short-name
   ```
Work and commit there. Then run `git push -u origin feature/short-name`.
2. When the work is complete, merge **from the worktree that already has the main branch** checked out (here `main`; use `master` if that is the repository's branch), as a chain: if the merge fails or conflicts, neither the push nor deletion will happen.
   ```bash
   git -C <main-worktree> merge --no-ff feature/short-name -m "merge: <description>" \
     && git -C <main-worktree> push origin main \
     && git push origin --delete feature/short-name \
     && git worktree remove <feature-worktree> \
     && git branch -d feature/short-name
   ```
Never run `git checkout main` in the shared tree: it would also move HEAD for the other sessions.
3. Close the issue (`gh issue close N`) as part of the same step.

Check: `git branch -a | grep feature/short-name` should not return anything.

## Branch not merging (superseded, abandoned)

Do not merge blindly or simply delete the branch: first assess it, then preserve it in a tag.

```bash
git rev-list --left-right --count origin/main...origin/feature/X   # ahead / behind
comm -23 <(git ls-tree -r --name-only origin/feature/X | sort) \
         <(git ls-tree -r --name-only origin/main | sort)          # files only on that branch

git tag -a archive/X origin/feature/X -m "<why it is obsolete>"
git push origin archivio/X && git push origin --delete feature/X
```

The tag costs nothing and remains recoverable (`git checkout archive/X`). If the branch is far behind, ask: “What does it contain that main does not already have?” In two cases out of three, the feature has since been rewritten better, and merging the old branch would regress the code. Already merged branches can be pruned with `git branch --merged`.

## Conflicts

A `git pull --rebase` at session start reduces conflicts. If a rebase or merge stops with `CONFLICT`:

Copy and check off:
- [ ] 1. `git status --short`: List the `UU` (conflicting) files. If there are also files that are not yours, leave them alone.
- [ ] 2. For each conflicting file, open it and search for `<<<<<<<`, `=======`, and `>>>>>>>`. Above `=======` is your part; below it is the other branch's part. If you do not understand what the other branch intended, run `git log -p -1 <other-branch> -- <file>`. If it returns nothing, go back to step 1.
- [ ] 3. Write a final version that preserves both sides' intent, without the markers. If the two parts are incompatible, keep the other branch's version and tell the user; do not silently delete someone else's work.
- [ ] 4. `grep -n '^<<<<<<<\|^>>>>>>>' <file>` should return nothing. If it returns any lines, go back to step 3.
- [ ] 5. Run the project tests. If they fail, go back to step 3: the merge may have combined two parts that do not fit together.
- [ ] 6. Run `git add <resolved-files>` and then `git rebase --continue` (or `git commit --no-edit` if it was a merge). If it stops again, repeat from step 1 for the new files.
- [ ] 7. If the situation is unmanageable, `git rebase --abort` (or `git merge --abort`) restores everything to its previous state. This is a way to start over, not a failure.

Finish only when `git status` no longer shows `rebase in progress` or any `UU` files, and the tests pass. Then run `git push origin HEAD` (after a rebase that was already published, use `--force-with-lease`, never `--force`, and only on your branch).

## Token saving

- Run `git diff` before committing only if you are unsure what you changed: when the files are named in the pathspec, you usually already know.
- `git log` after the commit is useless: the commit has printed its hash.
- `git status --short` only when necessary to check the status.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py git-workflow` and apply what it prints. It may print nothing.
