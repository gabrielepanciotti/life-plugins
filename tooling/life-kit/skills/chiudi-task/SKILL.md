---
name: chiudi-task
description: "When a task is finished and needs to be closed: the user says ‘I’m done’, ‘close task’, /chiudi-task. Runs tests, updates docs, writes a report to .claude/chiusure/, commits and pushes, and adds a note to the tree’s Life brain."
---

# Close task

When the work is finished, perform these steps in order to document and save
the closure — **do not skip any step**, and if one fails, stop and report it.

## Procedure

### 1. Tests
Run the repository’s test suite (`pytest`, `npm test`, or whatever the project
uses). If tests fail → **stop** and say so: a task is not closed with failing tests.

### 2. Update project documentation
Update `.claude/docs/*` and/or `CLAUDE.md` to reflect what changed
(architecture, API, database — any documentation file affected by the change).

### 3. Write the report — **one file per task**
In the project repository, write `.claude/chiusure/YYYY-MM-DD-<slug>.md`, where
`<slug>` describes the task (`reminder-config-escalation`, `issue-81`). **Do not**
use a fixed filename: two sessions closing tasks on the same day would write to
the same path, and one report would be lost during the merge.

Contents:
- **What was done** (briefly, focused on the outcome)
- **How it works** (the mechanism, not just a list of files)
- **Structure**: files/modules changed or created
- **How to verify**: command(s) to check it
- **Decisions**: choices made and why, alternatives rejected

If the task closes an issue, write `Closes #N` in the report: it becomes the
brain note’s label.

### 4. Commit and push
Add ALL files touched in this session (`git add <file...>` — list each file
explicitly; never use `-A` or `.`) and commit. If the issue is known, end the
last commit message with `Closes #N`. Then run `git push`. Use the `git-workflow`
and `github-issues` skills for the long-form commit message and issue closure.

### 5. Brain note — `chiudi.py` handles this
```bash
python3 <cartella-della-skill>/chiudi.py --resoconto .claude/chiusure/YYYY-MM-DD-<slug>.md
```
The report goes into the tree’s brain, because “what we did about X, and why”
is a question for the brain, rather than something to reconstruct from the `git log`.
The script:

1. finds the tree’s brain: `LIFE_INSTANCE_DIR/brain`, otherwise the only
   `life-*/brain` next to the node, otherwise the cloned Life’s
   `python -m suite_core.nodes brain-root --node <nodo>`;
2. gets the node slug (the `slug` field in `node.config`, otherwise the name of
   the main checkout directory, even when running in a worktree). If the slug
   does not exist among the `nodi/` folders or in the graph (tree + Life), it
   **does not deposit the note** and reports this: the fix is a `node.config`
   with the correct slug, not an invented node;
3. copies the report to `nodi/<slug>/chiusure/YYYY-MM-DD-<etichetta>.md` with
   the brain’s front matter (the label is the report’s `Closes #N`, or the
   filename; `--issue N` overrides it);
4. regenerates the brain index (`wiki-sync`), commits, and pushes the note and index.

It prints a `brain: …` line. If it reports a problem — brain not found, unknown
node, index not regenerated, commit or push failed — **report it to the user**:
the work is committed in the project repository, but the note is not safe. If
Life cannot be reached (`LIFE_FRAMEWORK_DIR`), the note is copied and committed,
but the index still needs to be regenerated with
`python -m suite_core.nodes wiki-sync --nearest <istanza>`. `--no-brain` skips
the deposit (only if you have already placed the note yourself).

### 6. Outcome
Summarize in a few lines: tests, commit/push, and the result of the `brain:`
line. If you are working in a worktree, integrating the branch (merge or PR)
and removing the worktree are up to you and the user; the skill does not do that.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py chiudi-task` and apply what it
prints (it may print nothing).
