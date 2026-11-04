---
name: delega-llm
description: "Decide whether to do work in the OpenCode session or delegate it via Life's LLM queues. Use it for testing, refactoring, documentation, reviews, extensive reading, summaries, extractions, translations, and other batch or repetitive tasks."
allowed-tools: Bash, Read
---

# Delegate to another model — when and with which queue

The OpenCode session orchestrates: it understands the problem, chooses a category and
difficulty, checks the result, and handles delicate parts directly. Delegate batch work to
Life when the task is self-contained and its result can be verified.

## Crossroads

| The task… | Choice |
|---|---|
| requires the live context of the conversation, project judgment, or sensitive decisions | do it in the current session |
| is mechanical, repetitive, extensive, or has a verifiable outcome | delegate it with `scripts/llm-run` |
| is ambiguous or has no acceptance criteria | clarify it first, then choose |

Don't delegate just to reduce your workload: the task must be explainable to someone who
has not seen the conversation.

## Life's dedicated engine

Queues are defined per tree in `<instance>/config/llm-routing.json`. The caller chooses
the category and, when useful, the difficulty level; `llm-run` tries the available providers in queue order and passes
the task to the next provider if an attempt fails.

```bash
scripts/llm-run run --categoria <categoria> [--livello facile|difficile] "<compito>"
```

For a job that needs to read or modify a repository, also pass its folder:

```bash
scripts/llm-run run --categoria <categoria> --dir <repo> \
  [--livello facile|difficile] "<compito>"
```

Use the categories declared by the tree, for example `implementazione`, `bugfix`, `test`,
`refactoring`, `documentazione`, `revisione`, `riassunto`, `estrazione`, `traduzione`, or
`contesto-lungo`. Verify them with `scripts/llm-run code`; don't invent a category that isn't declared.

## Choose the level

| Level | When | Examples |
|---|---|---|
| `facile` | mechanical and limited work, without decisions | rename, docstring, trivial tests, short summary |
| `medio` | multiple files or ordinary logic, with a verifiable result | contained feature, tests to pass, documentation of a module |
| `difficile` | sensitive logic, many files, costly errors, or unknown cause | security, concurrency, migrations, architectural refactoring |

The default level is `medio`; omit `--livello` in that case. Keep a difficult task in the
current session if it will inform a project decision.

## Write a self-contained assignment

Include:

- essential objective and context;
- files or modules involved;
- project constraints;
- measurable acceptance criteria;
- tests or verification commands;
- whether the job can modify files and whether it should avoid committing.

Example:

```bash
scripts/llm-run run --categoria test --livello medio --dir <repo> \
  "In packages/x, add tests for y.py covering the specified cases. Follow repository conventions, run the relevant test suite, and fix failures until it passes. Do not commit."
```

## After delegation

1. Read the complete output and locate the worktree or result produced.
2. Check the diff: the executor does not know the project's unwritten rules.
3. Run relevant tests, lint, type checks, or builds.
4. Correct the work or delegate a second round, using the errors observed.
5. Merge the work only when the result and checks meet the acceptance criteria.

If the queue runs out, report the reason shown by `llm-run` and decide whether to carry out the
task directly; do not declare the delegation successful without a verified result.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py delega-llm` and apply what it prints. It may print nothing.
