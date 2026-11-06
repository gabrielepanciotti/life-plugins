# Advanced gates — extended autoloop

Index: 1 Multi-tier · 2 Playwright E2E · 3 Role-based · 4 Doc-always · 5 UX-simplicity

These 5 gates extend and refine the basic `autoloop` cycle. Each gate is actionable and measurable.

---

## 1. Multi-tier mode

Tiers are derived from the backlog/SPEC in priority order: `P1 → tier1`, `P2 → tier2`, etc.
Dependencies between tasks determine the internal order within each tier.

**Strict rule**: tier N+1 starts ONLY if:
- `STOP_CMD(tier N)` is fully green (exit code 0 for all commands), **AND**
- the human checkpoint has passed (the user has approved the previous tier).

**Persistent state**: between iterations, each tier's state (green / red / in progress) is written
to `PLAN.md` or to a `loop-state.json` file in the project root. Never reread it from context.

**Red dependencies**: if a task in tier N depends on a task that is still red, tier N remains blocked.
Never start a tier ahead of unresolved dependencies.

**Example structure**:
```
tier1: [auth, db-schema]          ← STOP_CMD green + checkpoint → unlocks tier2
tier2: [api-endpoints, hooks]     ← STOP_CMD green + checkpoint → unlocks tier3
tier3: [ui, docs, ux-review]
```

---

## 2. Playwright E2E gate

In addition to unit tests, every primary user workflow is covered by an E2E test in a real browser.

**What it does**:
- Runs with `npx playwright test` (or `npm --prefix frontend run test:e2e`).
- At least one E2E flow for each user process defined in the SPEC.
- Included in `STOP_CMD`: the loop does not stop if Playwright tests fail.

**Who writes the tests**:
- The **test-writer subagent** (separate from the implementer, as in Phase 1).
- E2E tests are derived from the SPEC's UAT criteria, **not** from the implemented code.
- The implementer may not modify E2E files once they are frozen.

**Exit criterion**: `npx playwright test` exits with code 0 for all primary user flows.

---

## 3. Role-based gate

Every role defined in the SPEC is tested separately: authentication, visibility, permissions.

**For each role**:
1. At least one Playwright E2E test of the role's typical path (happy path).
2. At least one **negative** RBAC test: the role CANNOT see / CANNOT do what is outside its scope
   (e.g. a standard user cannot access admin routes or read another tenant's data).

**Measurable**: the negative RBAC test must assert an HTTP 403/401 or that the UI element is absent
—not merely that "it doesn't crash".

**Suggested file structure**:
```
tests/e2e/role_admin.spec.ts
tests/e2e/role_user.spec.ts
tests/e2e/rbac_negative.spec.ts   # contains all the "must not see/do" cases
```

**Exit criterion**: all role tests (positive + negative) pass with `npx playwright test`.

---

## 4. Doc-always gate

At the end of **every tier**, project documentation is updated before declaring the tier "done".

**What to update** (in order):
1. Docstrings and type hints in the modified code.
2. `.claude/docs/` files relevant to the tier: `architecture.md`, `api.md`, `database.md`, `deployment.md`.
3. The tier's **commit message**, in long form: what changes, why, and what it costs if it is wrong. No `changelog.md`: history travels with the diff and issues,
   not in a fourth file that will drift.

**How**: invoke the `docs` agent (or the equivalent skill configured in the project) or run
the project's documentation command. If there is no dedicated skill, documentation must be an explicit
action in `PLAN.md` at the last step of every tier.

**Strict rule**: a tier is NOT "done" until the relevant docs reflect the state
produced by that tier. The human checkpoint happens AFTER the docs, not before.

---

## 5. UX-simplicity gate

Every primary user process must be reachable in ≤ 3 clicks from the main dashboard.

**Measurable heuristic** (verified in code review / E2E):
- **Click depth**: count the clicks from the entry point (dashboard / home) to process completion.
  If > 3, simplify the flow or restructure the navigation.
- **Onboarding**: a new user finds a tutorial or initial wizard on first access.
  Verified with an E2E `role_new_user.spec.ts` that completes onboarding from scratch.
- **No native browser controls**: checkboxes, radio buttons, selects, and toggles must always be
  custom Tailwind components — polished, animated, with hover/focus/active states. Design system UI rule (`@suite/design-system`).
  Verified in review with grep for `<input type="checkbox"`, `<select`, `<input type="radio"`.

**Exit criterion**:
```bash
# No native controls in the frontend
grep -rn '<input type="checkbox"\|<input type="radio"\|<select\|<input type="range"' frontend/src/ && echo "FAIL: native controls found" || echo "OK: no native controls"
# Click depth: verified manually or by a reviewer during gsd-ui-review
```

The gate is **red** if even one of the three criteria fails. Verified in the adversarial review
at the end of the tier (PHASE 3 + `gsd-ui-review`).
