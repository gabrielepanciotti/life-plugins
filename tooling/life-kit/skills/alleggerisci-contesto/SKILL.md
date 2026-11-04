---
name: alleggerisci-contesto
description: Check that only necessary content is injected by default at the start of a session (`@`-includes in CLAUDE.md files, heavy skills, bloated MEMORY.md, unused plugins). Use when a session starts unnecessarily heavy, after adding a skill or a section to a CLAUDE.md file, or for a periodic context audit.
---

# Lighten context

One principle: **anything not needed in every session is loaded only on request** (a skill called with the `Skill` tool, a document read by an agent, memory retrieved on a match). Never load it by default, because every default line costs something in every session.

## Requirements

Only `bash` and `grep`: nothing to install.

## Checklist

- [ ] 0. Measure the starting point: run `wc -c` on the loaded CLAUDE.md files (the global one in `~/.claude/`, those in the repo and its parents) and count the lines in `MEMORY.md`. An `@include` weighs as much as the included file: add it to the total. Measure again at the end: the comparison is the outcome.
- [ ] 1. Search for `@`-includes in CLAUDE.md files (section 1).
- [ ] 2. Check the skills (section 2).
- [ ] 3. Check MEMORY.md (section 3).
- [ ] 4. Rerun the grep from step 1: it must return nothing, or only intentional and justified `@`-includes. If anything remains, return to step 1.

## 1. Technical documentation (CLAUDE.md)

- An `@path` in a CLAUDE.md file injects the **entire file at every session**, whatever the task. Keep it only for content that is literally always needed (rare).
- To refer to a skill, write only its **name** (`skill git-workflow`). Claude opens it with the `Skill` tool when needed.
- Keep the project CLAUDE.md as an index under 120 lines. Put details in `.claude/docs/*.md`, to be read by the `docs` agent or with Read only when the task concerns that area.
- The check works in bash without `globstar` (`--include` searches recursively; no `**`):
  ```bash
  grep -rnE --include=CLAUDE.md '(^|[[:space:]])@(~/|\./|/|\.claude/|[A-Za-z0-9_.-]+/)[^[:space:]]*' <radice> 2>/dev/null
  ```
  Every matching line is an `@`-include: this also applies to `@.claude/docs/*.md` without a preceding `./`. A reference such as `@suite/design-system` (a package) appears in the results: inspect it and discard it. The reason for this pattern is in `references/storia.md`.

## 2. Skills and plugins

- `SKILL.md` contains the trigger and essential workflow. Long details (API catalogs, extended examples) belong in `references/*.md`, read by the step that needs them.
- An `@include` inside a skill is fine only if the skill starts only on explicit request: the cost is incurred when needed.
- Each project enables only the plugins it uses in `.claude/settings.json`. Reading the file is not enough: if the merge is “per key, the more specific scope wins,” a `true` in the user settings can enable a plugin that the project does not declare. Verify with `/plugin` (or `claude plugin list`) in the project session.

## 3. Memory

- `MEMORY.md` is an index: one line per memory, under 150 characters, no content. It is the only piece of memory always injected.
- The content belongs in individual `memory/*.md` files, retrieved only when needed.
- Remove entries that point to files or facts that are no longer true (renamed paths, removed features): an index of dead links is just overhead.
- Cite long-term knowledge (SOPs, notes in the tree brain, `python -m suite_core.nodes brain-root`) from a skill with a specific trigger, never from a global CLAUDE.md.

## Do not touch

- Global `enabledPlugins` (`~/.claude/settings.json`): change these with `claude plugin enable|disable` or from the `/plugin` menu, not by hand.

Finish only when the grep from step 4 returns nothing (or every result is justified), MEMORY.md has no dead links, and you have stated what you removed or moved.

## Evidence

`references/storia.md` explains why this pattern is used. Try it with and without the skill in a new conversation.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py alleggerisci-contesto` and apply what it prints (it may print nothing).
