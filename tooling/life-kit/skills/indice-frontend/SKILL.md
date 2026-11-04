---
name: indice-frontend
description: "Indicates which design and frontend skill to use (Tailwind design system, React composition, UI review, DESIGN.md, curated diagrams) and how to apply it within the project's standard UI. Use it when designing or reviewing an interface, React component, design system, or diagram to present."
---

# Index frontend and design

`design-md` is part of the kit. The other skills in the table come from external packages
(third-party plugins or `npx skills add`): they are not modified and are only useful if installed.
If they appear in the skill list, open them with the `Skill` tool; otherwise read theirs
`SKILL.md` in the `skills/` directory of the package that contains them (`~/.claude/skills/<name>/`
or the plugin folder). If one is not installed, skip the line: do not invent its contents.

## Before external skills, the project standard

On a Life node with interface the project standard wins: `@suite/design-system` (two themes, design tokens, and custom components for checkboxes, selects, and toggles; do not use native browser controls). The skills below give techniques, they do not replace the standard one: if one of their guidance conflicts it, follow the standard.

## Which skill for which need

| Need | Skills |
|---|---|
| Tailwind v4 tokens, components and variants | `tailwind-design-system` |
| React components too full of boolean props, component API | `vercel-composition-patterns` |
| Review of a UI (accessibility, UX, guidelines) | `web-design-guidelines` |
| Obtaining a DESIGN.md from a Stitch | project `design-md` |
| Curated diagram to publish (slide, analysis, supplier page) | `diagram-design` |
| Style, palette, typography, UX pattern | `ui-ux-pro-max` (plugin) |

For a diagram that lives in the repo docs, Mermaid remains: `diagram-design` is needed when the
diagram must be presented.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py indice-frontend` and apply the tree-specific appendix it prints. The appendix may be empty.
