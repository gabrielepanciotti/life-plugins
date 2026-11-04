# Test gates — “real tests, not just green” (anti reward hacking)

Operational details for the gates cited in `SKILL.md`. Goal: the agent must not be able to close the loop
by cheating on the tests. Ordered by importance.

## 1. Fail-to-pass + Pass-to-pass (gold standard, from SWE-bench)

The fix must:
- make tests that **previously failed** (fail-to-pass) pass → proves the problem is fixed;
- not break tests that **already passed** (pass-to-pass) → no regressions.

Implementation in the loop:
1. Before starting, run the suite and record the set `PASS_BEFORE`.
2. Define the `NEW_TESTS` (derived from the spec) that must pass.
3. STOP only if: `NEW_TESTS` all pass **AND** `PASS_BEFORE` all still pass.
4. **Freeze** the test/regression files: the loop agent may NOT modify them. If they need to change, that requires an
   explicit human decision outside the loop.

## 2. Test writer separate from the implementer

If the same agent writes tests and code in the same step, it tailors them to each other (it writes tests that its
code already passes).

- Subagent A (**test-writer**): reads ONLY `SPEC.md`/UAT, NOT the implementation code. Produces the tests.
- Subagent B (**implementer**): receives the tests as an immutable contract and writes code to satisfy them.
- In Claude Code: `gsd-add-tests` (tests from UAT criteria) for A; `subagent-driven-development` for B.

## 3. verification-before-completion (superpowers)

Do not claim "done / fixed / passing" without:
- running the actual command;
- pasting the actual output (exit code, test count).

"Evidence before assertions." Eliminates "it should work." This is the most important cultural gate.

## 4. Independent adversarial reviewer

A **fresh** subagent (without the implementer’s context) whose job is to **break** the work:
- `gsd-code-review` — bugs, security, quality;
- `code-reviewer` / `security-auditor`;
- `silent-failure-hunter` — try/catch blocks that swallow errors, fallbacks that mask problems;
- `pr-test-analyzer` — do the tests really cover edge cases?

The loop does NOT close if the reviewer finds real problems. (This is the same principle as the workflows’
three-vote adversarial review.)

## 5. Make tests resistant to gaming

- **Mutation testing**: mutate the code; if the tests do not fail, they are weak → strengthen them.
- **Property-based** (Hypothesis): generates random inputs against invariants, not just cherry-picked examples.
- **Golden / snapshot** for observed real behavior.
- **E2E** (Playwright) in addition to unit tests: `gsd-integration-checker` for complete user flows.
- Forbid empty/tautological assertions (`assert True`, mocks that verify themselves).

## 6. Eval grounded in intent, not green tests (GSD)

- `gsd-verify-work` — conversational UAT: does the feature do what the spec promised?
- `gsd-validate-phase` (Nyquist auditor) — fills the phase’s coverage gaps.
- `gsd-audit-uat` / `gsd-audit-milestone` — the delivered work matches the original intent before archiving.

## 7. Measurable stop criteria (no subjective judgments)

STOP_CMD must be a conjunction of commands with exit codes, plus the two human-simulated gates (reviewer, UAT):

```
STOP =  pytest(new+regression)==0
    AND lint==0 AND type==0
    AND frontend_lint==0 AND frontend_test==0
    AND reviewer_subagent == APPROVED
    AND gsd-verify-work == UAT_PASS
```

No "looks good", "it should work", or "clean tone." Only verifiable conditions.

## Anti-patterns to explicitly block

- Delete/comment out a failing test to “make it pass”.
- Weaken an assertion (`assertEqual` → `assertIsNotNone`).
- `try/except: pass` to hide an error and make the test pass.
- Write the test after seeing the code, modeling it on the implementation.
- Hardcode the expected output to match the current output (snapshot of the bug).
- Skip/xfail a test without a written reason and a removal date.
