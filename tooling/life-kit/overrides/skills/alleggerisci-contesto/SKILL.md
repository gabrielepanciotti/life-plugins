---
name: alleggerisci-contesto
description: Check that nothing unnecessary is injected by default at the start of a session (`@`-includes in CLAUDE.md files, heavy skills, bloated MEMORY.md, unused plugins). Use when a session starts out heavy for no reason, after adding a skill or section to a CLAUDE.md, or for a periodic context audit.
---

# Lighten context

One principle: **load only what is not needed in every session on demand** (a skill called with the `Skill` tool, docs read by an agent, memory retrieved on a match). Never load it by default: every default line costs something in every session.

## Requirements

Only `bash` and `grep`; nothing to install.

## Checklist

- [ ] 0. Measure the starting point: run `wc -c` on the loaded CLAUDE.md files (the global one in `~/.claude/`, those in the repo and its parents) and count the lines in `MEMORY.md`. An `@include` weighs as much as the included file: add it to the total. Measure again at the end: the comparison is the result.
- [ ] 1. Search for `@`-includes in CLAUDE.md files (section 1).
- [ ] 2. Check skills (section 2).
- [ ] 3. Check MEMORY.md (section 3).
- [ ] 4. Rerun the grep from step 1: it should return nothing, or only intentional and justified `@` entries. If anything remains, return to step 1.

## 1. Technical documentation (CLAUDE.md)

- An `@path` in a CLAUDE.md injects the **entire file into every session**, regardless of the task. Keep it only for content that is literally always needed (rare).
- To refer to a skill, write only its **name** (`skill git-workflow`). Claude opens it with the `Skill` tool when needed.
- Keep the project CLAUDE.md as an index under 120 lines. Put details in `.claude/docs/*.md`; the `docs` agent or `Read` should read them only when a task touches that area.
- This check works in bash without `globstar` (`--include` searches recursively; no `**`):
  ```bash
  grep -rnE --include=CLAUDE.md '(^|[[:space:]])@(~/|\./|/|\.claude/|[A-Za-z0-9_.-]+/)[^[:space:]]*' <radice> 2>/dev/null
  ```
  Every matching line is an `@`-include; this also includes `@.claude/docs/*.md` without a preceding `./`. A reference such as `@suite/design-system` (a package) also appears in the results: inspect and discard it. The reason for this pattern is in `references/storia.md`.

## 2. Skills and plugins

- `SKILL.md` contains the trigger and essential workflow. Put lengthy details (API catalogs, extended examples) in `references/*.md`, which the relevant step reads when needed.
- An `@include` inside a skill is fine only if the skill starts only on explicit request: the cost is paid when needed.
- Each project should enable only the plugins it uses in `.claude/settings.json`. Reading the file is not enough: if settings merge “by key, with the most specific scope winning,” a `true` in user settings can turn on a plugin the project does not declare. Verify with `/plugin` (or `claude plugin list`) in the project session.

## 3. Memory

- `MEMORY.md` is an index: one line per memory, under 150 characters, with no content. It is the only memory injected every time.
- Content belongs in individual `memory/*.md` files, retrieved only when needed.
- Remove entries pointing to files or facts that are no longer true (renamed paths, removed features): an index of dead links is just overhead.
- Cite long-form knowledge (SOPs, notes in the tree's brain, `python -m suite_core.nodes brain-root`) from a skill with a specific trigger, never from a global CLAUDE.md.

## Leave untouched

- Global `enabledPlugins` (`~/.claude/settings.json`): change these with `claude plugin enable|disable` or from the `/plugin` menu, not by editing the file.

Finish only when the grep in step 4 is empty (or every result is justified), MEMORY.md has no dead links, and you have said what you removed or moved.

## Evidence

`references/storia.md` explains why this pattern is used. Try it with and without the skill in a new conversation.
