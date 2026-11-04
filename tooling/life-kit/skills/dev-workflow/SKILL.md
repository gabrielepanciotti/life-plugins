---
name: dev-workflow
description: "Guides every small development task (up to 3 files): classifies the task, reads before editing, implements with the ecosystem's rules, and verifies before declaring it done. Use when implementing, modifying, fixing, refactoring, or adding code; for medium-sized tasks, use rpit-loop."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Dev Workflow — workflow for every development task

Index: Basic rules · Step 0 classify · Step 1 pre-flight · Step 2 implement · Step 3 verify · Step 4 close · Related skills

## Basic rules

- Formatting and linting: use the project's tools (`ruff`/`black` for Python, `prettier` for JS/TS). If the project has none configured, do not introduce any yourself.
- Commit and push at the end of each task, not at the end of the day: one commit per task, using a conventional commit (see Step 4).
- At the start of a session, run `git pull --rebase` in the repository so you do not work on outdated code.
- With multiple sessions in the same repository: do not use `git add -A`; always commit named files, and do substantial work in your own worktree (skill `git-workflow`).

---

## STEP 0 — CLASSIFY THE TASK

Classify the intent **before** touching any files:

| Intent | Signals | Routing |
|--------|---------|---------|
| **Vague prompt** | Missing success criteria, "tidy this up a bit" | ASK before acting |
| **Bug fix** | Error, crash, wrong output | Obvious cause? → handle directly : `superpowers:systematic-debugging` |
| **Simple feature** | Up to 3 files, clear logic | → Implement directly (if it involves a DB: read existing models and migration files, then generate an Alembic migration) |
| **Medium feature** | More than 3 files, new logic | → `rpit-loop` |
| **Complex feature** | New architecture, > 10 files, design decisions | → **STOP — do not implement directly**: say "I propose a plan before proceeding," use `superpowers:brainstorming` + `superpowers:writing-plans`, and wait for approval |
| **Refactoring** | Same logic, different structure | → `rpit-loop` |
| **Parallel tasks** | 2+ independent subfeatures | → `superpowers:dispatching-parallel-agents` |

---

## STEP 1 — PRE-FLIGHT

1. Read the project's `CLAUDE.md` if this is the first change in the session
2. **Read every file before modifying it** — never edit blindly
3. Identify related files that could break: tests, types, dependencies, routes
4. For frameworks or libraries you do not know well, consult Context7 before writing code
5. Parallelize independent reads: multiple `Read`/`Grep` calls in one message

---

## STEP 2 — IMPLEMENT

### Python
- Add type hints to every public function
- Use `logging` instead of `print`
- Put configuration in `config.py`, secrets in `.env`, and never in code

### React / JS
- Add loading and error states to every component that fetches data
- Use `try-catch` for every `async` call
- UI controls (checkbox, select, toggle) → always use custom Tailwind components — never native browser controls
- Use a custom hook (`useXxx`) if stateful logic exceeds ~30 lines in the component
- Mobile-first: start with a single-column layout, then add breakpoints

### API (FastAPI / Flask)
- Validate input at the start of the handler: clients are untrusted
- Return a response using the same schema as the project's other endpoints
- Security: never put user input directly in an SQL query, never include secrets in a JSON response, and never build paths from user input

### Database
- For a new field or model: say that you will read the existing models and Alembic migrations, read them, then state that you will generate the migration with `alembic revision --autogenerate`
- Review the generated migration before applying it (`alembic upgrade head`)
- Do not run manual ALTER/DROP in production or bulk queries without WHERE: in production, there is no way to roll back without a backup

### Security — SQL queries
- Use parameterized queries only, never f-strings or concatenation; validate user input first.
- If asked for vulnerable code or if you fix it, provide only the corrected version and explain in one line what was wrong, without reproducing the query or vulnerable code (someone copying from the response would copy the vulnerability).

### Per-project plugins / MCPs (auto-enable)
- Does the feature require a **plugin** or **MCP** that is not yet active in this project? → **enable it yourself** in `<repo>/.claude/settings.json` (`enabledPlugins`: `"name@marketplace": true`) and, for MCPs, in `<repo>/.mcp.json`. This is part of the task: do not ask for manual enablement or defer it. Verify that the JSON remains valid. (The marketplace must already be added: `claude plugin marketplace list`.)

### Universal rules
- Keep functions under 40 lines: if one grows longer, extract a function with an explicit name
- Do not add a `TODO` without a linked issue (`# TODO: see #123`)
- Do not add unrequested features or refactor surrounding code
- Report bugs unrelated to the task without fixing them — open an issue

---

## STEP 3 — VERIFY (Definition of Done)

Complete these checks before declaring the work "done":

**Functionality**
- [ ] Task fully implemented (not partial or using a workaround)
- [ ] Existing tests pass
- [ ] If critical logic has no tests, write at least one test (see skill `testing`)
- [ ] If an API changed, verify it with `curl` or an HTTP client

**Quality**
- [ ] No leftover debug `console.log` / `print`
- [ ] No unnecessary commented-out code left behind
- [ ] No `TODO` without a linked issue

**Security** (if you touched an API, auth, user input, or DB)
- [ ] All input is validated and sanitized
- [ ] No query is built by string concatenation
- [ ] No secrets are hardcoded or logged in plaintext
- [ ] Authorization is checked before accessing other users' resources

**Unsure whether the work is complete?** → use `superpowers:verification-before-completion` before committing.

Finish only when every Definition of Done check passes. If one fails, return to Step 2 (implementation), fix it, then repeat Step 3. Do not weaken a failing test: fix the code.

---

## STEP 4 — CLOSE

**Docs** — Update `.claude/docs/` **only** if you changed:
- Project architecture or structure
- DB schema or models (update `database.md`)
- API endpoints — add/remove/signature (update `api.md`)
- Deployment procedure (update `deployment.md`)

Do not update docs for minor fixes or internal refactoring.

**Commit with issue closure**, using real line breaks and named files, never `git add -A`:
```bash
git commit -F - -- <file di questa sessione> <<'MSG'
feat: breve descrizione

Closes #N
MSG
git push origin HEAD
```
For conflicts, feature branches, and long-form messages: skill `git-workflow`.

---

## QUICK REFERENCE — Related skills

| Situation | Skill to use |
|-----------|--------------|
| Bug with a non-obvious cause | `superpowers:systematic-debugging` |
| Feature > 3 files / refactoring | `rpit-loop` |
| Designing a new architecture | `superpowers:brainstorming` |
| Written plan, ready to implement | `superpowers:executing-plans` |
| Independent subfeatures that can be parallelized | `superpowers:dispatching-parallel-agents` |
| Unsure whether the task is truly complete | `superpowers:verification-before-completion` |
| Want to use TDD for a new feature | `superpowers:test-driven-development` |
| Ready to merge and want a review | `superpowers:requesting-code-review` |
| Write tests for critical logic | `testing` |
| Commit with an explicit message / branch | `git-workflow` |

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py dev-workflow` and apply what it prints (it may print nothing).
