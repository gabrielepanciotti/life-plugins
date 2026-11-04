---
name: brain-journal
description: >
  Use to manage living memory and daily journal integrated with the `.remember/`
  mechanism: "good morning" (open session: summarize now.md + today + recent,
  propose focus), "close session" (write handoff into remember.md),
  "end of day" (consolidate the day into today-*.md). Distinguishes volatile
  work diary from consolidated brain notes; journal entries can graduate to
  [[brain-note]] when facts consolidate. Trigger: "good morning", "close session",
  "end of day", "/brain-journal".
argument-hint: "[good morning | close session | end of day]"
allowed-tools: Read, Write, Edit, Bash, Glob
---

# brain-journal

Living memory and daily work journal, integrated with the session's
`.remember/` mechanism. It does not duplicate the external history — it connects
to it.

## Three natural commands

### 1. `good morning` — Open the session

At the start of the day (or session):
1. Read `.remember/now.md` (current session buffer)
2. Read `.remember/today-*.md` (today's entries)
3. Read `.remember/recent.md` (notable facts from the last 7–14 days)
4. **Summarize**: what is on my mind? Which topics recur? What do I expect today?
5. **Propose a focus**: what is the priority for this session (e.g. "continue feature X", "fix bug Y")?

Output: open conversation, context summary + proposed focus, ready for work.

### 2. `close session` — Write the handoff

At the end of a session (when I say "close session" or similar):
1. Briefly summarize what you did in this session
2. Mark whether the task is completed, blocked, or in progress
3. If blocked: what is the stopping point?
4. **Write a handoff** in `.remember/remember.md`: a brief note for the next
   session (who picks up the task, what was done, what remains).
5. Update `.remember/now.md` → `[done]`

The handoff is ephemeral: the next session reads it, then removes it.

### 3. `end of day` — Consolidate the day

In the evening or at the end of the day:
1. Gather all `.remember/now.md` files (today's buffers)
2. Read `.remember/today-*.md` (today's entries)
3. **Consolidate**: which facts from today should be **archived** (because they
   are complete or irrelevant)? Which should be **carried over to tomorrow** (in progress)?
4. Write a summary in the `.remember/` folder (e.g. `today-YYYY-MM-DD.md`):
   hours worked, main topic, win + blocker, links to GitHub/ClickUp tasks if any.
5. Update `.remember/archive.md` with completed facts.
6. **Suggest**: if an observation from today could become a **consolidated brain
   note** (rather than volatile journal content), suggest moving it to
   [[brain-note]].

Output: stable daily summary, history ready for retrospective review.

---

## The distinction: Journal vs. Brain Notes

- **Journal** (`.remember/`): volatile work diary — blockers, wins, context
  for the session. It does not need to be perfect. Ephemeral: completed items
  go into the archive.
- **Brain notes** (`brain/`): consolidated facts and knowledge, with complete
  frontmatter, wikilinks, atomic (>=3 links, <=300 lines). Permanent.

**Transition rule**: when a journal fact becomes **stable and reusable**
(e.g. "discovered that the solver does not converge with X constraint" →
document the rule), suggest `[[brain-note]]` to turn the observation into a
canonical domain note.

---

## Integration with `.remember/`

The journal uses the existing history:
- `.remember/now.md` — session buffer (read by `good morning`, closed by
  `close session`)
- `.remember/today-*.md` — today's entries (consolidated into the
  archive by `end of day`)
- `.remember/recent.md` — facts from recent days (summarized in
  `good morning`)
- `.remember/archive.md` — completed history (updated by `end of day`)
- `.remember/core-memories.md` — patterns/lessons from the retrospective
  (consulted for proposals + focus)

This skill **reads and updates** these files according to the command. It does
not invent a new layer; it integrates with the existing system.

---

## Usage hints

- **Early morning or switching tasks**: `/brain-journal good morning` (remind me
  where I left off)
- **When you tell me**: `close session` (I write the handoff)
- **Before bed or end of shift**: `/brain-journal end of day` (consolidate +
  suggest migrations to the brain)

See [[brain-note]], [[brain-gate]].
