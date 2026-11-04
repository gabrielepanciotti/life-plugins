# Advanced gates — extended autoloop

Index: 1 Multi-tier · 2 Playwright E2E · 3 Role-based · 4 Doc-always · 5 UX-simplicity

These five gates integrate with and refine the basic `autoloop` loop. Each gate is operational and measurable.

---

## 1. Multi-tier mode

Tiers are derived from the backlog/SPEC in priority order: `P1 → tier1`, `P2 → tier2`, and so on.
Dependencies between tasks determine the order within each tier.

**Hard rule**: tier N+1 starts ONLY if:
- `STOP_CMD(tier N)` is entirely green (exit code 0 for every command), **AND**
- the human checkpoint has passed (the user approved the previous tier).

**Persistent state**: between iterations, each tier's state (green / red / in progress) is written
to `PLAN.md` or a `loop-state.json` file in the project root. Never reread it from context.

**Red dependencies**: If a tier N task depends on a task that is still red, tier N remains blocked.
Never advance a tier while its dependencies are unresolved.

**Structure example**:
```
tier1: [auth, db-schema]          ← green STOP_CMD + checkpoint → unlocks tier2
tier2: [api-endpoints, hooks]     ← green STOP_CMD + checkpoint → unlocks tier3
tier3: [ui, docs, ux-review]
```

---

## 2. Playwright E2E gate

In addition to unit tests, each primary user workflow is covered by a real browser E2E test.

**What it does**:
- Runs with `npx playwright test` (or `npm --prefix frontend run test:e2e`).
- Includes at least one E2E flow for each user process defined in SPEC.
- Is part of `STOP_CMD`: the loop does not stop if Playwright tests fail.

**Who writes the tests**:
- The **test-writer subagent** (separate from the implementer, as specified in Phase 1).
- E2E tests are derived from the SPEC's UAT criteria, **not** from the implemented code.
- The implementer cannot modify E2E files after they are frozen.

**Exit criterion**: `npx playwright test` exits with code 0 for all primary user flows.

---

## 3. Role-based gate

Test each role defined in SPEC separately for authentication, visibility, and permissions.

**For each role**:
1. At least one E2E Playwright test for the role's typical path (happy path).
2. At least one **negative** RBAC test: the role CANNOT see or do anything it is not authorized to
(e.g. a standard user cannot access admin routes or read data from other tenants).

**Measurable**: A negative RBAC test must assert an HTTP 403/401 or that the UI element is absent
— not merely that the app does not crash.

**Recommended file structure**:
```
tests/e2e/role_admin.spec.ts
tests/e2e/role_user.spec.ts
tests/e2e/rbac_negative.spec.ts   # contains all "must not see/do" cases
```

**Exit criterion**: All role tests (positive and negative) pass with `npx playwright test`.

---

## 4. Doc-always gate

At the end of **each tier**, update the project documentation before declaring the tier "done".

**What to update** (in order):
1. Docstrings and type hints in the modified code.
2. `.claude/docs/` files relevant to the tier: `architecture.md`, `api.md`, `database.md`, `deployment.md`.
3. The tier's **commit message**, in long form: what changed, why, and what it costs if it is wrong. Do not add `changelog.md`: the history belongs with the diff and the issues, not in a fourth file that will drift.

**How**: invoke the `docs` agent (or an equivalent skill configured in the project) or run
the project's documentation command. If there is no dedicated skill, add the documentation task
explicitly to the final step of each tier in `PLAN.md`.

**Hard rule**: A tier is NOT "done" until the relevant docs reflect the status
produced by that tier. The human checkpoint happens AFTER the documentation update, not before.

---

## 5. UX-simplicity gate

Each primary user process must be reachable in ≤ 3 clicks from the main dashboard.

**Measurable heuristics** (verified in code review / E2E):
- **Click depth**: Count clicks from the entry point (dashboard / home) to process completion.
If > 3, simplify the flow or restructure the navigation.
- **Onboarding**: A new user finds an initial tutorial or wizard on first login.
Verify with an E2E `role_new_user.spec.ts` test that completes onboarding from scratch.
- **No native browser controls**: Checkboxes, radio buttons, selects, and toggles must
always use custom Tailwind components — elegant, animated, with hover/focus/active states. This is a
design-system UI rule (`@suite/design-system`). Verify in review by searching for `<input type="checkbox"`, `<select`, and `<input type="radio"`.

**Exit criterion**:
```bash
# No native controls in the frontend
grep -rn '<input type="checkbox"\|<input type="radio"\|<select\|<input type="range"' frontend/src/ && echo "FAIL: native controls found" || echo "OK: no native controls"
# Click depth: verified manually or by a reviewer during gsd-ui-review
```

The gate is **red** if even one of the three criteria fails. Verify it in the tier's opposing review
at the end of the tier (PHASE 3 + `gsd-ui-review`).

## Instance specifics

Run `python -m suite_core.nodes skill-overlay autoloop` and apply what it prints (it may print nothing).
