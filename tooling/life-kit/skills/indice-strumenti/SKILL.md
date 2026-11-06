---
name: indice-strumenti
description: "Identifies which skill to use to turn material into knowledge (such as a codebase graph, a book converted into a skill, or a video transcription), find new skills, or hand off a session. Use it when the user asks for a project graph, wants to turn a book or handout into a skill, transcribe or understand a video, find a skill, or conduct a retrospective or handoff."
---

# Tool index

`graphify`, `book-to-skill`, `handoff`, and `retro` are part of the kit. The other skills in the
table come from external packages and are available only when installed; they are not modified. If
a skill appears in the listing, open it with the Skill tool; otherwise, read its `SKILL.md` in the
package's `skills/` folder. If a skill is not installed, say so and suggest the closest alternative.
The user must start `handoff` and `retro` (`/handoff`, `/retro`); suggest them in one line.

## Which skill to use for each need

| Need | Skills |
|---|---|
| Knowledge graph of a codebase or documents | `graphify` (`/graphify` command) |
| Turn a book, handout, or collection of PDFs into a skill, organized by chapter | `book-to-skill` |
| Transcribe or understand video or audio | `video-understand` (if installed) |
| Find and install a skill we don't have | `find-skills` (if installed) |
| Hand off to another session | `handoff` (user only) |
| Retrospective of a session | `retro` (user only) |

If the user asks whether a skill exists for something: 1) run `ls ~/.claude/skills` and
`claude plugin list` to check whether it is already available; 2) if it is missing and `find-skills` is installed, open that skill;
3) if you find a suitable skill, ask where to install it: globally only if it serves multiple projects,
otherwise in `<repo>/.claude/skills/`.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py indice-strumenti` and apply what it prints. It may print nothing.
