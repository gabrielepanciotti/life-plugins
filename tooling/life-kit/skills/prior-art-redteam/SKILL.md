---
name: prior-art-redteam
description: >
  Two quality gates for specs and plans: GATE A "prior art" (search GitHub, docs, blogs, forums, and papers for who has already solved the problem BEFORE deciding) and GATE B "red team" (adversarially dismantle a written plan or phase, independently refuting each finding). Trigger when the user asks for an adversarial/critical review of completed phases or future plans, similar projects or prior solutions, flaws in a plan, avoiding reinvention, or "standing on the shoulders of giants." Requires the Workflow tool (multi-agent); use only with the user’s explicit opt-in (ultracode or a direct request).
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Workflow, WebSearch, WebFetch, ToolSearch, Agent
---

# Prior Art & Red Team — two gates, not one

## Principle

A plan written on its own inherits two systematic flaws: **anchoring** (initial ideas
become constraints without ever being challenged) and **provincialism**
(solving from scratch a problem the world has already solved better).

Address these with two distinct gates at different points. **They are not the same gate moved.**

| | **GATE A — Prior Art** | **GATE B — Red Team** |
|---|---|---|
| When | *Before* the spec freezes decisions | *After* the plan is concrete, *before* writing code |
| Question | "Who has already done it, and how?" | "Where does this plan break?" |
| Direction | Expands the set of options | Narrows it: removes what does not hold up |
| Cost | Low/medium, broad | High, deep |
| Output | Menu of options + known antipatterns | Confirmed flaws + open decisions |

> **Why A comes first.** If you search for prior art after writing the spec, the research
> becomes confirmation: you read the giants looking for someone who agrees with you. The giants help
> define *the menu*, not validate the dish you have already ordered.
>
> **Why B comes later.** A red team on a plan that does not yet exist produces
> generalities. An attack needs a concrete target: files, lines, sequences.

## How it fits the normal workflow

```
brainstorming ──► [GATE A: prior-art] ──► spec ──► piano ──► [GATE B: red-team] ──► build
                   effort medio, largo                        effort massimo, profondo
                   ~5 agenti web                              ~5 audit + 5 refutatori
```

If the plan already exists (a common case: "review the completed phases"), run **B on what
is done** and **A on what remains to be decided**, in parallel — this is the combined case,
covered by the template.

## Engagement rule

Use the Workflow tool **only** with the user's explicit opt-in (the word `ultracode`,
a direct request for multi-agent orchestration, or invocation of this skill).
Without opt-in: propose the gate, estimate the cost, and ask.

---

## Procedure

### 0. Verify the basics yourself — do not delegate this

Before launching any agent, verify the basic facts **yourself**. Agents inherit your mistaken assumptions and amplify them ×N.

- [ ] The paths really exist (watch for junctions/symlinks: two different paths may
      point to the same volume — ask git, which reports the real path)
- [ ] `git log --oneline -10` + `git status --porcelain | wc -l` — does the stated status
      match reality?
- [ ] The cited documents exist and are **committed** (an untracked plan does not exist)
- [ ] The artifacts that previous phases claim to have produced are on disk

Put every anomaly found here in the agents’ prompts as **"anomaly to verify; do not assume it is correct"**: this makes it a concrete lead rather than noise.

### 1. Break the target into attack areas

Do not just say "review the plan." Give each agent a distinct attack angle and lens.
Recurring angles (see `references/attack-catalog.md` for the full catalog):

- **Claims vs reality** — forensic: is what is claimed to be done actually done?
- **Neutrality / coupling** — does the promised abstraction hold up or lose the domain?
- **Contract** — idempotency, deletion, versioning, partial errors, auth, time
- **Plan** — what the plan *does not say*: data, identity, rollback, dual-run, tests
- **Cross-cutting / ops** — deploy, secrets, backups, observability, cost/benefit

### 2. Independent refutation — required

Pass every finding to a **second agent whose task is to prove the first agent wrong**.
Without this step, a red team produces plausibility, not truth: LLMs generate
credible critiques as easily as they generate credible code.

Verdicts: `REFUTED` (the evidence does not hold up or is already handled elsewhere — cite where) /
`PARTIAL` (it exists, but its severity is overstated) / `CONFIRMED` (I tried to dismantle it and
could not). The refuter must also state what the auditor **did not see** (`missed`).

Calibrate severity against the real system: `critical` only if it blocks the project or corrupts data.
A concurrency problem in a two-user system is not `critical`.

### 3. Prior art research — with constraints, or it is just a bibliography

Always include these requirements in web research prompts:

- **Load the tools**: `ToolSearch(query: "select:WebSearch,WebFetch")`. Alternatively,
  use the indexing tools from the `context-mode` plugin, if installed, to keep raw
  bytes out of the context.
- **At least 8 real sources with verifiable URLs.** If a page does not open, say so — never invent it.
- **Extract the mechanism, not the name**: pattern name, data structure, API shape,
  model variables. "They use RRULE" ≫ "they handle recurrence."
- **Verdict for each source**: `adopt` / `adapt` / `study` / `ignore`, with a reason.
- **Look for failures**: who tried it and regretted it, closed `wontfix` issues, postmortems,
  abandonment threads. This is the most valuable part and the one no one searches for spontaneously.

Always cover these sources: GitHub repositories (README + issues, not just the landing page), official
documentation, technical blogs, forums (relevant Reddit communities, Hacker News, StackOverflow, project
mailing lists), and papers if the problem is algorithmic. Search in both English **and** Italian.

### 4. Actionable synthesis

The final report is not a list of links. Minimum structure:

1. **Verdict in 10 lines** — can we proceed, yes or no?
2. **Immediate blockers** — with the concrete command to resolve them
3. **Confirmed flaws** by severity — `file:line` evidence, failure scenario, fix, phase
4. **Missed gaps** — from the `missed` field
5. **What we borrow from the giants** — source + mechanism + adopt/adapt/study/ignore
6. **Antipatterns to avoid** — with the source that documents them
7. **The uncomfortable question** — is the chosen approach justified? (always require an agent
   to argue *against* the project's thesis, using data: lines of code, users, criteria
   found in the sources)
8. **Revised plan** — correct sequence, exit criteria, verification milestones
9. **Open decisions** — numbered, with options and a recommendation

Write it to `docs/superpowers/reviews/<date>-<topic>.md`, never the repository root.

---

## Template

Ready-to-use Workflow script: `references/workflow-template.js`.
Catalog of attack angles and questions by area: `references/attack-catalog.md`.

Typical sizing: 5 auditors + 5 refuters + 5 researchers + 1 synthesizer = 16 agents.
For an A-only gate: 5 researchers + 1 synthesizer. For a B-only gate: 5 + 5 + 1.

## Mistakes to avoid

| Mistake | Why it hurts |
|---|---|
| Launching agents without manual grounding | You amplify a false premise ×N |
| Skipping refutation | You get plausible critiques, not real flaws |
| Searching for prior art after the spec | It becomes confirmation, not discovery |
| Asking "find problems" without an angle | 5 agents saying the same generic thing |
| Accepting sources without URLs | Hallucinations disguised as research |
| Not asking anyone to argue *against* the project | The most costly bias remains intact |
| Severity without calibration against the real system | Everything is `critical`, so nothing is critical |

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py prior-art-redteam` and apply what it prints (it may print nothing).
