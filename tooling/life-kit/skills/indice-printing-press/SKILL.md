---
name: indice-printing-press
description: "Indicates which Printing Press skill to use to talk to an external service through a ready-made or printable CLI, instead of writing a scraper. Use it when a project needs to integrate an API, site, or portal, before writing integration code, or when the user mentions Printing Press, a print CLI, or /printing-press."
---

# Index Printing Press

Working rule: For a recurring external service, use a printed CLI, never one
one-off scraper. The `printing-press*` and `pp-*` skills come from external packages, installed from their source: they do not change. If they appear in the listing, open with
tool Skills; otherwise **read their `SKILL.md`** (`~/.claude/skills/<name>/SKILL.md` or the
plugin folder). If Printing Press is not installed, say so before writing code
integration and ask whether to install it.

## Copy and tick

- [ ] 1. Search the catalog: `npx -y @mvanhorn/printing-press-library search <query>`
- [ ] 2. If there is, install it: `npx -y @mvanhorn/printing-press-library install <name>`
- [ ] 3. If it is not there, print it following `printing-press/SKILL.md`
- [ ] 4. Refine it until verification passes: `printing-press-polish/SKILL.md`
- [ ] 5. Integrate it into the node (brain, CLAUDE.md, via the old scrapers): `/node-clis` command if the `suite-tooling` plugin is installed

If in step 4 the check fails after two rounds, go back to step 3 with the output of the
check: usually an endpoint is missing in the specification.

## Which skill for which need

| Need | Skills |
|---|---|
| Print a new CLI | `printing-press` |
| Bring it to publishable | `printing-press-polish`, `printing-press-score` |
| Fix or extend a published CLI | `printing-press-amend`, `printing-press-reprint` |
| Get a CLI from the public library | `printing-press-import` |
| Publish it | `printing-press-publish` (exits outward: ask first) |
| Retrospective after a ride | `printing-press-retro` |
| Ready-made catalog CLIs | `pp-<servizio>` (search for them with step 1) |

`printing-press-output-review` is a sub-skill: they call it polish and printing-press, not
it opens by itself.

## Needed

Node.js (for `npx`). To print: Go 1.26.3+ and
`go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest`.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py indice-printing-press` and apply the tree-specific appendix it prints. The appendix may be empty.
