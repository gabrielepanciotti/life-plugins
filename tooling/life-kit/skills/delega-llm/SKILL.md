---
name: delega-llm
description: "Decide whether to do work in the OpenCode session or delegate it through Life’s LLM queues. Use for tests, refactoring, documentation, reviews, extended reading, summaries, extraction, translation, and other batch or repetitive tasks."
allowed-tools: Bash, Read
---

# Delegate to another model — when and which queue

Index: Estimate · Agent tree · State · Init or resume · Discovery · Categories and dependencies · Questions · Launch · Monitoring · Resume · Rules

The OpenCode session orchestrates: it understands the problem, chooses a category and difficulty,
checks the result, and handles sensitive parts directly. Delegate batch work to
Life when the task is self-contained and its result can be verified.

## Decision point

| The task… | Choice |
|---|---|
| requires the live conversation context, project judgment, or sensitive decisions | do it in the current session |
| is mechanical, repetitive, extensive, or has a verifiable outcome | delegate with `scripts/llm-run` |
| is ambiguous or has no acceptance criteria | clarify it first, then choose |

Do not delegate just to reduce your workload: the task must be explainable to an executor who
has not seen the conversation.

## Life’s single engine

Queues are defined per tree in `<instance>/config/llm-routing.json`. The caller chooses
the category and, when useful, the level; `llm-run` tries the queue’s backends in order and moves
to the next if an attempt fails.

```bash
scripts/llm-run run --categoria <categoria> [--livello facile|difficile] "<compito>"
```

For work that must read or modify a repository, also pass its directory:

```bash
scripts/llm-run run --categoria <categoria> --dir <repo> \
  [--livello facile|difficile] "<compito>"
```

Use the categories declared by the tree, for example `implementazione`, `bugfix`, `test`,
`refactoring`, `documentazione`, `revisione`, `riassunto`, `estrazione`, `traduzione`, or
`contesto-lungo`. Check them with `scripts/llm-run code`; do not invent a missing category.

## Choose a level

| Level | When | Examples |
|---|---|---|
| `facile` | mechanical, scoped work with no decisions | rename, docstring, trivial tests, short summary |
| `medio` | multiple files or ordinary logic, with a verifiable result | small feature, tests to make pass, module documentation |
| `difficile` | sensitive logic, many files, costly errors, or unknown cause | security, concurrency, migrations, architectural refactoring |

The default level is `medio`; omit `--livello` in that case. A difficult task meant
to inform a project decision stays in the current session.

## Write a self-contained task

Include:

- objective and essential context;
- files or modules involved;
- project constraints;
- measurable acceptance criteria;
- tests or verification commands;
- whether the work may modify files and whether it must avoid committing.

Example:

```bash
scripts/llm-run run --categoria test --livello medio --dir <repo> \
  "In the packages/x module, add tests for y.py covering the specified cases. Follow the repository conventions, run the relevant suite, and fix issues until it passes. Do not commit."
```

## After delegation

1. Read the full output and locate the worktree or result produced.
2. Check the diff: the executor does not know the project’s unwritten rules.
3. Run relevant tests, lint, type checks, or builds.
4. Fix issues or delegate another pass with the observed errors.
5. Merge the work only when the result and checks match the acceptance criteria.

If the queue runs out, report the reason shown by `llm-run` and decide whether to do
the task directly; do not claim a delegation succeeded without a verified result.
