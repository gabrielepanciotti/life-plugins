# Attack Axis Catalog

Choose **one axis per agent**. Different axes = different lenses = different findings.
Five agents on the same axis produce the same generic finding five times.

---

## A. Claims vs reality (forensics)

The most underrated agent. It checks that what is *claimed as done* is actually *done*.

- `git log` / `git show --stat` / `gh issue view N`: do the commits match the stated phases?
- Do the promised artifacts exist on disk? (directories, migrations, containers, config files)
- Is the working tree clean? Are deleted files still imported? Does the project actually compile?
- For claimed tests: run the suite and report **actual numbers**, never estimates
- Do cited documents exist? Are they committed? Is their last modification consistent with the stated date?
- Runtime state: `docker ps`, health endpoint, migrations at head?

Rule: every finding must cite **the command run and its output**.

## B. Neutrality / coupling

When a plan promises an abstraction ("generic engine", "neutral layer", "plugin"),
check that the abstraction holds up instead of merely moving the problem elsewhere.

- Does the "neutral" model carry fields that exist only for the original use case?
- Does the core still reference entities from the specific domain?
- Are there **two paths** (old and new)? Are they equivalent in capability? List every feature
  reachable only through the old path — that is hidden debt
- Who dereferences relationships that the new path leaves `NULL`?
- How much of the UI assumes the local entity that is about to disappear?

Required final question: *after the refactoring, does the original use case still work
using **only** the new abstraction?* If not, list exactly what is missing.

## C. Contract (API between services / modules)

- **Idempotency**: partial retry, duplicates within a batch, races between two writes, atomicity
- **Deletion / tombstone**: how does the consumer know a resource no longer exists?
  Is there a full-sync reconciliation or only incremental sync? Phantom records?
- **Versioning**: does the contract have a version? How does it evolve without breaking the consumer?
- **Partial failures**: can we tell *which* records failed and *why*? Per-record errors or
  all-or-nothing?
- **Auth**: constant-time comparison, secret rotation, can one origin impersonate another?
- **Validation**: mutually exclusive fields, ranges, references to nonexistent entities,
  **cyclic dependencies**, values that cross midnight
- **Identity**: two databases, two user tables — which is the source of truth? What if they diverge?
- **Time**: time zone, DST, ISO week, who decides the window
- **Read-back**: pagination, consistency during a write, how does the consumer know something
  is new (polling? push? webhook?)
- **Observability**: can we diagnose "my X never arrived" while distinguishing
  *not sent* / *sent but rejected* / *accepted but discarded by the logic*?

## D. The plan — what it does NOT say

The plan describes the happy path. Attack everything else.

- **Data migration**: is there real data? ID mapping? FKs crossing the new
  boundary? Backfill? **Rollback?**
- **Identity / auth**: does the user have to authenticate twice? Cookies, domains, CORS between ports?
- **Ownership**: who owns the bot / channel / scheduled job / cron?
- **Frontend**: two SPAs? Does the user navigate between two ports? One shell? Does the plan sidestep this?
- **Realtime**: data lives here, names live there — denormalization or cross-service N+1?
- **Sequence and reversibility**: when is the old code deleted? Is there a **dual-run**?
  How is equivalence checked *before* deletion (shadow run, output comparison)?
- **Tests**: how do you test a flow that crosses two services? Contract tests? Where do
  existing tests that touch the moved domain go?
- **Real scope**: count it (`wc -l`, `git ls-files | wc -l`). Is the plan undersized?
- **Deferrals**: "we'll detail this just in time" is often an excuse to postpone the
  hard decisions. List them.

Required finding: *if followed to the letter, how long does this plan leave the system nonfunctional?*

## E. Cross-cutting / operations

- **Deploy**: ordering of components with a shared contract, migrations, downtime
- **Backup / restore**: two DBs cannot have a transactionally consistent backup — how is this handled?
- **Secrets**: how is a secret generated, shared, and **rotated** between two repos?
- **Shared dependencies**: packages linked in multiple places — versioning, drift, who updates them
- **Observability**: correlated logs? Propagated request ID? If a nightly job fails,
  does anyone notice?
- **Ports / resources**: are they actually free and registered?

## F. Runtime reachability — the axis everyone forgets

Axes A–E look at the **change**. This one looks at **what is already there** and asks one
question: *can a real client actually follow the path claimed to work, today?*

- Is every "ready" component **mounted** and **reachable**? Middleware, gate, auth, proxy,
  CORS, firewall: does something return 403/404 before the right code even runs?
- Do "new" functions have **production callers**? (`grep` for the name: if it appears only in its
  definition and docstrings, nothing calls it)
- Do green tests prove the real path, or do they run with an active **bypass** (`APP_ENV=test`,
  mocked middleware, fixture that skips auth)? A gate disabled in tests is a blind spot
  by definition: 400 green tests say nothing about that path.
- Does the deployed code match the repo? Was the container rebuilt?

It is worth assigning **an entire agent** to this. In a red team review of this project's split,
five auditors focused on the change produced 89 findings without noticing that the central
contract in the epic returned 403 to everyone, because the middleware did not exempt it
and the tests ran with the gate disabled. The synthesizer found it by chance while checking something else.

## G. The uncomfortable question (always present)

An agent must argue **against** the project's thesis, using data:

> "Is this approach necessary? What is the cheapest alternative that achieves the same
> goal?"

It must provide actual numbers (lines of code, endpoints, users, usage frequency) and decision
criteria found in sources, not opinions. This is the finding no other agent will produce
spontaneously, because all the others work *within* the premise.

---

# Prior-art research axes

One agent per topic. Every prompt ends with an **adversarial question** that looks for failures.

| Topic | What to look for |
|---|---|
| **Competing products** | OSS that solves the same problem: data model, mechanisms, UX. Who has a real engine and who relies on simple rules, and with what result |
| **Algorithm / library** | Official docs + real examples from the upstream repo + community primer + authors' blog. Concrete patterns, not theory |
| **Reference architecture** | Who made the same separation at a larger scale, and how they model the boundary |
| **Integration patterns** | Idempotency key, outbox, CDC, reconciliation, bulk operations with per-record errors, contract testing |
| **Strategic decision** | Literature *for and against* the architectural choice, with documented criteria and cases where the decision was reconsidered |

## Queries that work

- `<problem> site:github.com` then **open the issues**, not just the README
- `<technology> post mortem` / `why we moved away from <X>` / `<X> regret`
- `<project> wontfix` — closed issues say more than the roadmap
- `site:reddit.com/r/<subreddit> <problem>` — real-world usage experience
- `<pattern> antipattern` — critical literature almost always exists
- Search in the user's language too: the local community may have different cases
