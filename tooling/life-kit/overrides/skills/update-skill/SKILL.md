---
name: update-skill
description: "Create, update, test, and improve shared skills while avoiding duplicates and checking clarity, portability, and activation. Use it for ‘create skill,’ ‘new skill,’ ‘update skill,’ ‘improve skill,’ ‘auto-improve skill,’ or ‘add eval.’"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# update-skill — writes, tests, and improves skills

Index: Decision · Destination · Duplicates · Questions · Writing · Tests · Self-improvement · Review

A skill is good when a new session selects it at the right time and follows its steps.
Claude Code and OpenCode natively read the same destination:
`~/.claude/skills/<nome>/`.

## Decision

| Request | Route |
|---|---|
| new skill | destination, duplicates, questions, writing, tests, review |
| existing skill to change | writing, then review; add tests if missing |
| tests or evals only | tests, then review |
| automatic improvement | self-improvement, then review |

## Single destination

Every shared skill lives in:

```text
~/.claude/skills/<nome>/
```

If it serves only one project, use `<repo>/.claude/skills/<nome>/` instead, versioned with the
code. Do not create marketplaces or separate copies for each tool: duplication makes the
instructions diverge.

## Duplicates

1. List the folders in `~/.claude/skills/` and, when relevant, in
   `<repo>/.claude/skills/`.
2. Read the `name` and `description` of skills that plausibly overlap.
3. If one already covers nearly the same goal, ask the user whether to update it.
4. Create a new skill only when its scope is distinct.

## Questions for a new skill

Gather these in a single message:

1. what it should do, in one sentence;
2. phrases or situations that should trigger it;
3. minimum tools required;
4. expected output;
5. rules that must not be broken and the cost of breaking them;
6. a real task or similar skill to use as a model;
7. whether `references/`, `scripts/`, `assets/`, or `evals/` are needed.

Wait for the answers before writing. If the name and goal are already complete, do not repeat
questions that have already been answered.

## Writing

Use this structure only as a starting point, and keep the sections that are needed:

```text
<nome>/
├── SKILL.md
├── references/   details loaded only when needed
├── scripts/      reusable deterministic operations
├── evals/        tests and optional automated evals
└── assets/       materials used in the output
```

Rules:

- keep front matter with `name` and `description`;
- write the description in Italian, third person, in the form “What it does. Use it when…”;
- include triggering conditions and phrases, not a summary of the steps;
- keep `SKILL.md` under 500 lines and add an index when it exceeds 100 lines;
- put instructions that must not be lost at the top;
- use the imperative and explain the reason for costly rules;
- use one term per concept and one default solution;
- avoid personal paths, secrets, and organization-specific data;
- list dependencies and installation commands in the `Serve` section;
- link directly from `SKILL.md` to every additional file;
- state whether a script should be run or read;
- use concrete examples and measurable checks;
- when there are more than four steps, add a “Copy and check off” list and say where to return if a
  check fails.

For a commit, add only the skill folder:

```bash
git add -- ~/.claude/skills/<nome>
git commit -m "feat: add <nome> skill"
```

For an update, use a message that fits the repository. Do not use `git add -A`.

## Tests and evals

Automatic evaluations use `llm-run` and `life.skillEval`; the router chooses the executor.
Results from different executors are not directly comparable: establish a new baseline
when it changes. The loop's cost threshold is an estimate, not a provider-enforced cap.

Always create `evals/prove.md` with at least three realistic requests, the expected result, and the
sentence: “Try them without and with the skill, in a new conversation.” Link to the file from
`SKILL.md`.

For skills with many branches or an automatic cycle, add:

- `evals/evals.json` for training;
- `evals/val.json` with different prompts for validation;
- at least two negative cases;
- 5–8 assertions per case, mostly objective checks of files, commands, and content;
- no more than 20% regex assertions and no purely subjective judgments.

Run the tests in new sessions: the context of the skill's author can hide missing instructions.

## Self-improvement

Start it only if `SKILL.md` and automated evals exist. Use a project script, if available, that
modifies only `SKILL.md`, records hypotheses and results, and keeps a change only when the score
improves.

Before a long cycle, communicate the cost, maximum number of iterations, and risk of changing
branches. Run it in an isolated worktree. Compare training and validation: if only training
improves, expand the validation cases and loosen assertions that are too literal.

## Final review

- [ ] Name and description activate the skill in the right cases and not in unrelated cases.
- [ ] Body is under 500 lines; an index is present when needed.
- [ ] Paths are portable and there is no private data.
- [ ] Every reference exists and is linked directly.
- [ ] Dependencies and script intent are explicit.
- [ ] `evals/prove.md` contains at least three realistic requests.
- [ ] Tests were run without and with the skill in a new session.
- [ ] The available repository check passes without findings.

If a check fails, fix the skill and run the check again. Finish only when every check passes or
when the exception is documented with a verifiable reason.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py update-skill` and apply what it prints (it may print
nothing).
