---
name: git-workflow
description: "Writes long-form commit messages, closes an issue with a commit (Closes #N), manages feature branches, and resolves merge conflicts. Use it when you need an explicit commit message, a `Closes #N`, a feature branch, or when git output shows CONFLICT."
allowed-tools: Bash
---

# Git Workflow — Commits, Branches, Conflicts

Contents: Basic rule · Explicit commit · Close an issue · Feature branch · Branch that will not merge · Conflicts · Saving tokens

Multiple agent sessions can work in the same repo: they share one working tree and one index. Therefore, always commit named files and merge from a worktree that already has the correct branch checked out.

Decision: need only a message or `Closes #N` → “Explicit commit.” Need to isolate a large task → “Feature branch.” Git shows `CONFLICT` → “Conflicts.”

## Basic rule

One commit per completed task, followed immediately by a push. Work on the main branch; use a feature branch only for tasks involving more than 10 files. Files created, deleted, or moved via Bash (`mv`, `cp`, script) must be named explicitly in the commit.

## Explicit commit

```bash
git commit -m "feat: short description" -- <files from this session>
git push origin HEAD
```

The pathspec after `--` is required: otherwise, the commit includes everything in the index, including work from other sessions. Never run `git add -A && git commit` while another session is active in the same repo.

Types: `feat:` `fix:` `refactor:` `docs:` `test:` `chore:`
- 50 characters maximum, in English.
- No body except `Closes #N`.

## Close an issue with the commit

The message must use actual newlines (`\n` inside quotes does not create a newline, so `Closes #N` would not be recognized):

```bash
git commit -F - -- <files from this session> <<'MSG'
feat: short description

Closes #N
MSG
git push origin HEAD
```

After pushing, verify that the issue closed: `gh issue view N --json state`.

## Feature branch (tasks with more than 10 files)

The branch ends with the task: close the issue, merge the work, and delete the branch as one operation. If these are separate, in a month no one will know whether the branch contains anything.

1. Create the branch in your own worktree, without touching the shared tree (`EnterWorktree`, or manually):
   ```bash
   git -C <repo> worktree add ../<repo>-feature-nome-breve -b feature/nome-breve
   ```
   Work and commit there. Then `git push -u origin feature/nome-breve`.
2. When the work is done, merge **from the worktree that already has the main branch** in checkout (here `main`; use `master` if that is the repo’s branch), as a chain: if the merge fails or conflicts, neither the push nor deletion runs.
   ```bash
   git -C <worktree-con-main> merge --no-ff feature/nome-breve -m "merge: <cosa>" \
     && git -C <worktree-con-main> push origin main \
     && git push origin --delete feature/nome-breve \
     && git worktree remove <worktree-del-branch> \
     && git branch -d feature/nome-breve
   ```
   Never run `git checkout main` in the shared tree: that would move HEAD for the other sessions too.
3. Close the issue (`gh issue close N`) in the same step.

Check: `git branch -a | grep feature/nome-breve` should return nothing.

## Branch that will not merge (superseded, abandoned)

Do not merge blindly or simply delete it: first measure the difference, then archive it with a tag.

```bash
git rev-list --left-right --count origin/main...origin/feature/X   # ahead / behind
comm -23 <(git ls-tree -r --name-only origin/feature/X | sort) \
         <(git ls-tree -r --name-only origin/main | sort)          # files only on that branch

git tag -a archivio/X origin/feature/X -m "<perché è superato>"
git push origin archivio/X && git push origin --delete feature/X
```

The tag costs nothing and remains recoverable (`git checkout archivio/X`). If the branch is far behind, the right question is “what does it contain that main does not already have?” In two cases out of three, the feature has been rewritten better, and merging it would regress the code. Prune already merged branches with `git branch --merged`.

## Conflicts

A `git pull --rebase` at the start of a session reduces conflicts. If a rebase or merge stops with `CONFLICT`:

Copy and check off:
- [ ] 1. `git status --short`: lists the `UU` (conflicted) files. Leave any files that are not yours alone.
- [ ] 2. For each conflicted file, open it and look for `<<<<<<<`, `=======`, `>>>>>>>`. Above `=======` is your section; below is the other branch’s. If you cannot tell what the other side intended: `git log -p -1 <ramo-altro> -- <file>`. If that does not help, return to step 1.
- [ ] 3. Write the final version to preserve both sides’ intent, without the markers. If the two sides are incompatible, keep the other branch’s version and tell the user; do not silently discard someone else’s work.
- [ ] 4. `grep -n '^<<<<<<<\|^>>>>>>>' <file>` should return nothing. If it returns lines, go back to step 3.
- [ ] 5. Run the project tests. If they fail, return to step 3: the merge may have kept two halves that do not work together.
- [ ] 6. `git add <file risolti>` then `git rebase --continue` (or `git commit --no-edit` if it was a merge). If it stops again, repeat from step 1 for the new files.
- [ ] 7. If the situation is unmanageable: `git rebase --abort` (or `git merge --abort`) restores the previous state. This is a way to restart, not a failure.

Finish only when `git status` no longer shows `rebase in progress` or `UU` and the tests pass. Then `git push origin HEAD` (after a previously pushed rebase, use `--force-with-lease`, never `--force`, and only on your branch).

## Saving tokens

- `git diff` before committing only if you do not know what changed; named files in the pathspec usually make that clear.
- `git log` after committing is unnecessary: the commit printed its hash.
- `git status --short` only when you need to check the state.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py git-workflow` and apply what it prints (it may print nothing).
