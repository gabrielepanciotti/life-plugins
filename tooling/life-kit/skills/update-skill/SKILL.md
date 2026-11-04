---
name: update-skill
description: "Creates, updates, tests, and improves shared skills while avoiding duplicates and checking clarity, portability, and activation. Use it for ‘create skill’, ‘new skill’, ‘update skill’, ‘improve skill’, ‘auto-improve skill’, or ‘add eval’."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# update-skill — write, test, and improve skills

Index: Decision path · Destination · Duplicates · Questions · Writing · Tests · Self-improvement · Review

A skill is good when a new session chooses it at the right time and follows its steps.
Claude Code and OpenCode natively read from the same destination:
`~/.claude/skills/<nome>/`.

## Decision path

| Request | Path |
|---|---|
| new skill | destination, duplicates, questions, writing, tests, review |
| existing skill to change | writing, then review; add tests if missing |
| tests or eval only | tests, then review |
| automatic improvement | self-improvement, then review |

## Single destination

Every shared skill lives in:

```text
~/.claude/skills/<nome>/
```

If it serves only one project, use `<repo>/.claude/skills/<nome>/` instead, versioned with the
code. Do not create marketplaces or separate copies for each tool: duplication makes
instructions diverge.

## Duplicates

1. List the folders in `~/.claude/skills/` and, when relevant, in
   `<repo>/.claude/skills/`.
2. Read the `name` and `description` of skills that may overlap.
3. If one already covers nearly the same goal, ask the user whether to update it.
4. Create a new skill only when its scope is distinct.

## Questions for a new skill

Gather in a single message:

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

Use this structure only as a starting point and keep the sections that are needed:

```text
<nome>/
├── SKILL.md
├── references/   details loaded only when needed
├── scripts/      reusable deterministic operations
├── evals/        tests and optional automated evals
└── assets/       materials used in the output
```

Rules:

- keep frontmatter with `name` and `description`;
- write the description in Italian, third person, in the form «What it does. Use it when…»;
- include conditions and trigger phrases, not a summary of the steps;
- keep `SKILL.md` under 500 lines and add an index above 100 lines;
- put instructions that must not be lost at the top;
- use the imperative and explain why costly rules matter;
- use one term per concept and one default solution;
- avoid personal paths, secrets, and organization-specific data;
- list dependencies and installation commands in the `Serve` section;
- link directly from `SKILL.md` to every additional file;
- state whether a script should be run or read;
- use concrete examples and measurable checks;
- with more than four steps, add a «Copy and check off» list and say where to return if a
  check fails.

For a commit, add only the skill folder:

```bash
git add -- ~/.claude/skills/<nome>
git commit -m "feat: add <nome> skill"
```

For an update, use a message consistent with the repository. Do not use `git add -A`.

## Tests and evals

Automatic evaluations use `llm-run` and `life.skillEval`; the router chooses the executor.
Results from different executors are not directly comparable: establish a new baseline
when it changes. The loop's cost threshold is an estimate, not a provider-enforced cap.

Always create `evals/prove.md` with at least three real requests, the expected result, and the sentence:
«Try them with and without the skill, in a new conversation.» Link the file from `SKILL.md`.

For skills with many branches or an automatic cycle, add:

- `evals/evals.json` for training;
- `evals/val.json` with different validation prompts;
- at least two negative cases;
- 5–8 assertions per case, mostly objective checks on files, commands, and content;
- no more than 20% regex and no purely subjective judgments.

Run tests in new sessions: the context of whoever wrote the skill can hide missing
instructions.

## Self-improvement

Start only if `SKILL.md` and automated evals exist. Use a project script, if
available, that changes only `SKILL.md`, records hypotheses and results, and keeps a
change only when the score improves.

Before a long cycle, communicate the cost, maximum number of iterations, and risk of changing
branches. Run it in an isolated worktree. Compare training and validation: if only training
improves, expand the validation cases and relax assertions that are too literal.

## Final review

- [ ] Name and description activate the skill in the right cases and not in unrelated ones.
- [ ] Body is under 500 lines; index is present if needed.
- [ ] Paths are portable and contain no private data.
- [ ] Every reference exists and is linked directly.
- [ ] Dependencies and script intent are explicit.
- [ ] `evals/prove.md` contains at least three real requests.
- [ ] Tests were run with and without the skill in a new session.
- [ ] The available repository check passes without findings.

If a check fails, fix the skill and repeat it. Finish only when all checks pass or when the
exception is documented with a verifiable reason.
