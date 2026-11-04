---
name: prior-art-redteam
description: >
  Two quality gates for specs and plans: GATE A "prior art" (search online on GitHub,
  docs, blogs, forums, and papers to find who has already solved the problem, BEFORE
  deciding) and GATE B "red team" (adversarially dismantle a written plan or phase,
  with an independent refutation of every finding). Activate when the user asks to
  review completed phases or future plans adversarially/critically, look for similar
  projects or who has already done it, find flaws in a plan, avoid reinventing the
  wheel, or "stand on the shoulders of giants." Requires the Workflow tool
  (multi-agent) — use only with the user's explicit opt-in (ultracode or a direct
  request).
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Workflow, WebSearch, WebFetch, ToolSearch, Agent
---

# Prior Art & Red Team — two gates, not one

## The principle

A plan written in isolation inherits two systematic flaws: **anchoring** (the first
ideas become constraints without ever being questioned) and **provincialism**
(solving from scratch a problem the world has already solved better).

They are addressed by two distinct gates, at different points. **They are not the
same gate moved to another point.**

| | **GATE A — Prior Art** | **GATE B — Red Team** |
|---|---|---|
| When | *Before* the spec freezes decisions | *After* the plan is concrete, *before* writing code |
| Question | "Who has already done it, and how?" | "Where does this plan break?" |
| Direction | Broadens the space of options | Narrows it: removes what does not hold up |
| Cost | Low/medium, broad | High, deep |
| Output | Menu of options + known anti-patterns | Confirmed flaws + open decisions |

> **Why A comes first.** If you search for prior art after writing the spec, the
> search becomes confirmation: you read the giants looking for someone who agrees
> with you. The giants help define *the menu*, not validate the dish you already
> ordered.
>
> **Why B comes later.** A red team on a plan that does not exist yet produces
> generalities. An attack needs a concrete target: files, lines, sequences.

## How it fits into the normal workflow

```
brainstorming ──► [GATE A: prior-art] ──► spec ──► plan ──► [GATE B: red-team] ──► build
                   effort medio, largo                        effort massimo, profondo
                   ~5 agenti web                              ~5 audit + 5 refutatori
```

If the plan already exists (the common case: "review the completed phases"), run
**B on what is done** and **A on what remains to be decided**, in parallel — this is
the combined case covered by the template.

## Engagement rule

Use the Workflow tool **only** with the user's explicit opt-in (the word `ultracode`,
a direct request for multi-agent orchestration, or invoking this skill). Without
opt-in: propose the gate, estimate the cost, and ask.

---

## Procedure

### 0. Manual grounding — do not delegate it

Before launching any agent, verify the basic facts **yourself**. Agents inherit your
mistaken assumptions and amplify them ×N.

- [ ] The paths really exist (watch for junctions/symlinks: two different paths can
      point to the same volume — ask git, which reports the real path)
- [ ] `git log --oneline -10` + `git status --porcelain | wc -l` — does the stated
      status match reality?
- [ ] The cited documents exist and are **committed** (an untracked plan does not exist)
- [ ] Artifacts that earlier phases claim to have produced are on disk

Include every anomaly found here in the agents' prompt as **"anomaly to verify, do
not take it for granted"**: it becomes a concrete anchor instead of noise.

### 1. Break the target into attack areas

Do not just say "review the plan." Each agent needs an attack axis and a different
*lens*. Recurring axes (see `references/attack-catalog.md` for the full catalog):

- **Claims vs reality** — forensic: has what is claimed as done actually been done?
- **Neutrality / coupling** — does the promised abstraction hold, or does it lose the domain?
- **Contract** — idempotency, deletion, versioning, partial errors, auth, timing
- **Plan** — what the plan *does not say*: data, identity, rollback, dual-run, tests
- **Cross-cutting / ops** — deployment, secrets, backups, observability, cost/benefit

### 2. Independent refutation — mandatory

Send every finding to a **second agent whose task is to prove the first one wrong**.
Without this step, a red team produces plausibility, not truth: LLMs generate
credible criticisms as easily as they generate credible code.

Verdicts: `REFUTED` (the evidence does not hold or the issue is already handled
elsewhere — cite where) / `PARTIAL` (the issue exists but its severity is overstated)
/ `CONFIRMED` (I tried to dismantle it and could not). The refuter must also state
what the auditor **missed** (`missed`).

Calibrate severity against the real system: use `critical` only if it blocks the
project or corrupts data. A concurrency issue in a two-user system is not `critical`.

### 3. Prior-art research — constrain it, or it becomes a bibliography

Always require the following in web prompts:

- **Load the tools**: `ToolSearch(query: "select:WebSearch,WebFetch")`. Alternatively,
  use the indexing tools of the `context-mode` plugin, if installed, to keep raw
  bytes out of the context.
- **At least 8 real sources with verifiable URLs.** If a page does not open, say so —
  never make one up.
- **Extract the mechanism, not the name**: pattern name, data structure, API shape,
  model variables. "They use RRULE" ≫ "they handle recurrence."
- **Verdict for each source**: `adopt` / `adapt` / `study` / `ignore`, with a reason.
- **Look for failures**: those who tried and regretted it, closed `wontfix` issues,
  post-mortems, abandonment threads. This is the most valuable part and the one no
  one searches for spontaneously.

Always cover these sources: GitHub repos (README + issues, not just the landing
page), official documentation, technical blogs, forums (industry Reddit, Hacker
News, StackOverflow, project mailing lists), and papers if the problem is
algorithmic. Search in both **English** and **Italian**.

### 4. Actionable synthesis

The final report is not a list of links. Minimum structure:

1. **Verdict in 10 lines** — can we proceed, yes or no?
2. **Immediate blockers** — with the concrete command to resolve each
3. **Confirmed flaws** by severity — evidence `file:line`, breakage scenario, fix, phase
4. **Missed gaps** — from the `missed` field
5. **What we borrow from the giants** — source + mechanism + adopt/adapt/study/ignore
6. **Anti-patterns to avoid** — with the source that documents them
7. **The uncomfortable question** — is the chosen approach justified? (Always require
   one agent to argue *against* the project's thesis using data: lines of code, users,
   criteria found in sources)
8. **Revised plan** — correct sequence, exit criteria, verification milestones
9. **Open decisions** — numbered, with options and a recommendation

Write it to `docs/superpowers/reviews/<date>-<topic>.md`. Never in the root.

---

## Template

Ready-to-use Workflow script: `references/workflow-template.js`.
Catalog of attack axes and questions by area: `references/attack-catalog.md`.

Typical sizing: 5 auditors + 5 refuters + 5 researchers + 1 synthesizer = 16 agents.
For a gate-A-only run: 5 researchers + 1 synthesis. For a gate-B-only run: 5 + 5 + 1.

## Mistakes to avoid

| Mistake | Why it hurts |
|---|---|
| Launching agents without manual grounding | You amplify a wrong assumption ×N |
| Skipping refutation | You get plausible criticisms, not real flaws |
| Searching for prior art after the spec | It becomes confirmation, not discovery |
| Asking "find problems" without an attack axis | 5 agents give the same generic answer |
| Accepting sources without URLs | Hallucinations disguised as research |
| Not asking anyone to argue *against* the project | The most costly bias remains intact |
| Severity without calibration against the real system | Everything is `critical`, so nothing is critical |

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py prior-art-redteam` and apply what it prints (it may print nothing).
