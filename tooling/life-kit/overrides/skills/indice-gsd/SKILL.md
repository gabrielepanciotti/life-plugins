---
name: indice-gsd
description: "Indicates which GSD skill (Get Shit Done, 57 skills from an external package) uses for phased work with roadmaps, plans and milestones, and how to open it. Use it when a project has the `.planning/` folder, when the user names GSD, a phase, a milestone, or a roadmap, or type /gsd-something."
---

# GSD index

The `gsd-*` skills come from an external package, installed from its source: not yes
modify (an update would erase the corrections). If they appear in the listing, open with
tool Skills; otherwise they are used **reading their `SKILL.md` and following it**
(`~/.claude/skills/<nome>/SKILL.md` or the plugin folder). The user can always type them
with `/<nome>`. If GSD is not installed, say so and use `dev-workflow` or `rpit-loop`.

## Crossroads

- The project **doesn't** have `.planning/` and the work is normal → GSD is not needed: use
`dev-workflow` (less than 3 rows) or `rpit-loop`. GSD is suitable for long, phased work.
- The project has `.planning/` → pick up where it is: `gsd-progress`.
- New project to be set up in phases → `gsd-new-project`.

## Which skill for which need

| Need | Skills |
|---|---|
| Where we are, what comes next | `gsd-progress` (or `gsd-stats`) |
| Resume or pause | `gsd-resume-work`, `gsd-pause-work` |
| Clarify what a phase delivers | `gsd-spec-phase`, then `gsd-discuss-phase` |
| Plan and execute a phase | `gsd-plan-phase`, `gsd-execute-phase` |
| Check the work of a phase | `gsd-verify-work`, `gsd-validate-phase`, `gsd-add-tests` |
| Review and security | `gsd-code-review`, `gsd-secure-phase`, `gsd-ui-review` |
| Manage phases and milestones | `gsd-phase`, `gsd-new-milestone`, `gsd-complete-milestone`, `gsd-audit-milestone` |
| Small task with GSD guarantees | `gsd-quick`, `gsd-fast` |
| Debugging with persistent state | `gsd-debug`, `gsd-forensics` |
| Import existing documents or plans | `gsd-ingest-docs`, `gsd-import`, `gsd-map-codebase` |
| Ideas and prototypes | `gsd-explore`, `gsd-spike`, `gsd-sketch`, `gsd-capture` |
| Configuration | `gsd-settings`, `gsd-config`, `gsd-health`, `gsd-help` |

You don't find what you need in the table: `ls ~/.claude/skills | grep '^gsd-'` and read the
description in the frontmatter of the nearest one.

## Rules that also apply within GSD

- GitHub issues remain the project's todolist: GSD does not replace them.
- More than 5 subagents or a Workflow: estimate and yes of the user first. It also applies to
`gsd-autonomous` and `gsd-execute-phase`.
- Commit with session files only: nothing `git add -A` if other sessions work on the same repo.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py indice-gsd` and apply the tree-specific appendix it prints. The appendix may be empty.
