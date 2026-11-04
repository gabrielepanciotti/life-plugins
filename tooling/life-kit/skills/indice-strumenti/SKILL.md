---
name: indice-strumenti
description: "Choose the right skill for turning material into knowledge (such as building a codebase graph, turning a book into a skill, or transcribing a video), finding skills, or handing off a session. Use it when the user asks for a project graph, to turn a book or handout into a skill, to transcribe or understand a video, to find a skill, or to write a retrospective or handoff."
---

# Instrument index

`graphify`, `book-to-skill`, `handoff` and `retro` are part of the kit. The other skills in the
table come from external packages and are available only when installed; do not modify them. If
a skill appears in the list, open it with the Skill tool; otherwise, read its `SKILL.md` from the
package's `skills/` folder. If a skill isn't installed, say so and suggest the closest alternative.
The user must start `handoff` and `retro` with `/handoff` or `/retro`; suggest them in one line.

## Which skill for which need

| Need | Skills |
|---|---|
| Knowledge graph of a codebase or documents | `graphify` (`/graphify` command) |
| Turn a book, handout, or collection of PDFs into a chapter-based skill | `book-to-skill` |
| Transcribe or understand video or audio | `video-understand` (if installed) |
| Find and install a skill we don't have | `find-skills` (if installed) |
| Hand off to another session | `handoff` (user only) |
| Write a session retrospective | `retro` (user only) |

If the user asks whether a skill exists for something: 1) run `ls ~/.claude/skills` and
`claude plugin list` to check whether it is already available; 2) if it is missing and `find-skills` is installed, open it;
3) if you find a suitable skill, ask where to install it before installing: globally only if it serves multiple
projects, otherwise in `<repo>/.claude/skills/`.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py indice-strumenti` and apply what it prints (it may print nothing).
