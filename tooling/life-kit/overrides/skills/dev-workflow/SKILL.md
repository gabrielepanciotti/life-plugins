---
name: dev-workflow
description: "It drives any simple development task (up to 3 files): classify the task, read before modifying, implement with ecosystem rules, and verify before declaring done. Use it when implementing, modifying, fixing, refactoring, or adding code; for medium tasks switch to rpit-loop."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Dev Workflow — workflow for each development task

Index: Basic rules · Step 0 rank · Step 1 pre-flight · Step 2 implement · Step 3 verify · Step 4 close · Related skills

## Basic rules

- Formatting and lint: those of the project (`ruff`/`black` for Python, `prettier` for JS/TS). If your project doesn't have them configured, don't introduce them yourself.
- Commit and push at the end of the task, not at the end of the day: one commit per task, conventional commit (see Step 4).
- At the beginning of the session `git pull --rebase` on the repo, to avoid working on old code.
- With multiple sessions on the same repo: no `git add -A`, always commit with the named files, and heavy work in its own worktree (skill `git-workflow`).

---

## STEP 0 — CLASSIFY THE TASK

Classify the intent **before** touching any file:

| Intent | Signals | Routing |
|--------|---------|---------|
| **Vague prompt** | missing success criteria, "fix a bit" | ASK before acting |
| **Bug fix** | error, crash, wrong output | obvious cause? → direct : `superpowers:systematic-debugging` |
| **Simple Feature** | up to 3 files, clear logic | → Implement direct (if it involves DB: read existing models and migration files, then generate migration Alembic) |
| **Media Feature** | more than 3 files, new logic | → `rpit-loop` |
| **Complex Feature** | new architecture, > 10 files, design decisions | → **STOP — do not implement directly**: state "I propose a plan before proceeding", use `superpowers:brainstorming` + `superpowers:writing-plans`, wait for approval |
| **Refactoring** | same logic, different structure | → `rpit-loop` |
| **Parallel tasks** | 2+ independent subfeatures | → `superpowers:dispatching-parallel-agents` |

---

## STEP 1 — PRE-FLIGHT

1. Read the project's `CLAUDE.md` if it is the first change of this session
2. **Read each file before editing** — never edit blindly
3. Identify related files that might break: tests, types, dependencies, routes
4. Framework/lib you don't know well → Context7 before writing code
5. Parallelize independent reads: multiple `Read`/`Grep` in one message

---

## STEP 2 — IMPLEMENT

### Python
- Type hints on each public function
- `logging` instead of `print`
- Config in `config.py`, secrets in `.env`, never in code

### React / JS
- Loading state + error state on each component with fetch
- `try-catch` on every `async` call
- UI controls (checkbox, select, toggle) → always custom Tailwind components — never native browsers
- Custom hook (`useXxx`) if stateful logic exceeds ~30 lines in component
- Mobile-first: single-column layout first, then breakpoints

### API (FastAPI / Flask)
- Validate input at handler start: client is not trusted
- Response with the same pattern as the other project endpoints
- Security: never user input in a SQL query, never secrets in a JSON response, never constructed paths from user input

### Databases
- New field or model: say in the text that you read the existing models and Alembic migrations, read them, then declare that you generate the migration with `alembic revision --autogenerate`
- Review the generated migration before applying it (`alembic upgrade head`)
- No manual ALTER/DROP in prod and no bulk queries without WHERE: in prod there is no way to go back without backup

### Security — SQL query
- Only parameterized queries, never f-string or concatenation; user input is validated first.
- If they ask you for vulnerable code or you correct it, write only the correct version and explain in one line what was wrong, without copying the query or the vulnerable code (whoever copies from the answer would copy the hole).

### Plugin / MCP per-project (auto-enable)
- Does the feature require a **plugin** or **MCP** that is not yet active in this project? → **enable it yourself** in `<repo>/.claude/settings.json` (`enabledPlugins`: `"nome@marketplace": true`) and, for MCPs, in `<repo>/.mcp.json`. It's part of the task: don't ask for manual enablement, don't delay. Verify that the JSON remains valid. (The marketplace must already be added: `claude plugin marketplace list`.)

### Universal rules
- Functions under 40 lines: if more than that, extract a function with an explicit name
- No `TODO` without issue connected (`# TODO: vedi #123`)
- Do not add unwanted features; Don't refactor surrounding code
- Bug not related to the task: report, do not fix — open issue

---

## STEP 3 — VERIFICATION (Definition of Done)

Run before declaring "done":

**Functionality**
- [ ] Task fully implemented (not partial or with workaround)
- [ ] Existing tests pass
- [ ] Critical logic without tests → write at least one test (see skill `testing`)
- [ ] API changed → check with `curl` or HTTP client

**Quality**
- [ ] No debug `console.log` / `print` left
- [ ] No useless commented code left
- [ ] No `TODO` without issue connected

**Security** (if you touched API, auth, user input or DB)
- [ ] All inputs are validated and sanitized
- [ ] No queries constructed with string concatenation
- [ ] No hardcoded or plaintext logged secrets
- [ ] Permission checked before accessing other users' resources

**Doubts about completeness?** → use `superpowers:verification-before-completion` before committing.

Finish only when all Definition of Done ticks pass. If one fails, go back to Step 2 (implementation) and fix it, then repeat Step 3. A failing test doesn't weaken itself: you fix the code.

---

## STEP 4 — CLOSE

**Docs** — Update `.claude/docs/` **only** if you have changed:
- Architecture or structure of the project
- DB schema or templates (update `database.md`)
- API endpoint — add/remove/signature (update `api.md`)
- Deployment procedure (update `deployment.md`)

Do not update docs for minor fixes or internal refactoring.

**Commit with issue closure**, message on multiple true lines and named files, never `git add -A`:
```bash
git commit -F - -- <files for this session> <<'MSG'
feat: short description

Closes #N
MSG
git push origin HEAD
```
For conflicts, feature branches and long-form messages: skill `git-workflow`.

---

## QUICK REFERENCE — Related skills

| Situation | Skills to use |
|-----------|----------------|
| Bug with non-obvious cause | `superpowers:systematic-debugging` |
| Feature > 3 files / refactoring | `rpit-loop` |
| New architecture design | `superpowers:brainstorming` |
| Plan written, ready to implement | `superpowers:executing-plans` |
| Parallelizable independent subfeatures | `superpowers:dispatching-parallel-agents` |
| Doubt: is the task really complete? | `superpowers:verification-before-completion` |
| Do you want TDD on new feature | `superpowers:test-driven-development` |
| Ready to merge, want review | `superpowers:requesting-code-review` |
| Write tests for critical logic | `testing` |
| Commit with explicit message / branch | `git-workflow` |
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py dev-workflow` and apply the tree-specific appendix it prints. The appendix may be empty.
