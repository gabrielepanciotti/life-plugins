---
name: evals-from-spec
description: "Generate truth-kit and train/val evals from a SPEC with acceptance criteria. Use with '/evals-from-spec', 'generate evals from spec', 'create genuine tests from this spec', 'extract acceptance criteria and do evals'. Not to self-improve a skill or write test code."
---

# evals-from-spec — from SPEC to genuine evals

Index: When to use it · Needed · Process (6 steps) · Human gate · Output · Notes

## When to use it / when NOT

| Situation | Do you use this skill? |
|---|---|
| You have a SPEC with acceptance criteria and you want the truth-kit + eval file | **Yes** |
| Do you want to self-improve an existing skill | No → use `update-skill` if it is installed, otherwise `autoloop` with the truth-kit produced here |
| Do you want to write tests in pytest/unittest for Python logic | No → that's TDD, use the skill `testing` |
| You don't have a SPEC, just a vague idea | No → write the SPEC first, then come back here |

## Needed

Python 3.13 only (validator uses standard library, no packages): `python3.13` on Linux, `py -3.13` on Windows. The validator is in `scripts/validate_evals.py` next to this skill (to be executed, not to be read): `<skill>` below is the skill folder.

## Process

Copy and tick (if a check fails, go back to the indicated step):
- [ ] 1. Testable criteria extracted from the SPEC (if a criterion is vague, normalize it before moving forward)
- [ ] 2. `evals/evals.json` written (train)
- [ ] 3. `evals/val.json` written, same test_case number
- [ ] 4. Validator `VALID` on both files (if `INVALID`, go back to step 2 or 3 depending on the file indicated in the error)
- [ ] 5. Human gate passed (if user asks for changes, go back to step 2)
- [ ] 6. Final files written only after OK

1. **Read the SPEC and acceptance criteria.**
For each F-N feature and each validation rule, list the expected behaviors (positive and negative).
If the criteria are not formulated in a testable way (e.g. "the system must be robust"), normalize them first: explicit input, expected output, invalid cases.
Refer to `references/acceptance-extraction.md` for technique and examples (F2 Orders).

2. **Generate `evals/evals.json` (split train).**
Structure: `{"skill":"...", "split":"train", "model":"sonnet", "max_budget_usd":0.6, "test_cases":[...]}`.
Each test_case: unique `id`, `prompt`, `context` (optional), `assertions` (≥ 3).
Respect tiering: use `output_not_contains` (Tier B) as the dominant type for "must not do X".
Include ≥ 2 negative test_cases (bad routing, prohibited behavior).
See `references/tiering-and-schema.md` for full scheme and thresholds.

3. **Generate `evals/val.json` (split validation).**
Same behaviors as train. Paraphrase the prompts (different language, alternative wording).
Add `"split": "validation"` at top-level.
The test_case number must be identical to train (required by the `--pair` validator).

4. **Autogate.**
   ```bash
   V=<skill>/scripts/validate_evals.py   # on Windows, use py -3.13 instead of python3.13
   python3.13 "$V" evals/evals.json --pair evals/val.json
   python3.13 "$V" evals/val.json
   ```
If the output is INVALID, read the errors and correct:
- Tier S/A/B < 60%: Convert `output_contains`/`output_regex` to `output_not_contains` where it makes semantic sense.
- Total assertions < 40: add assertion to test_cases with less than 5.
- Test_case < 8: Add cases for missing corner cases or routing guards.
Repeat until both files print VALID.

5. **Human gate (5 minutes) — see dedicated section.**
Show the summary to the user. Wait for confirmation before freezing files.

6. **Write the final files only after approval.**
Commit only the eval and references files, naming them (`git commit -m "…" -- evals/evals.json evals/val.json`): other sessions may have dirty files in the same repo.

## Human Gate (5 minutes)

Before declaring the files ready, show the user:

- Number of test_cases in train and val
- Tier distribution (how many S/A/B, how many C, how many D/F, percentages)
- 2-3 examples of test_cases with their assertions (one positive, one negative, one edge case)
- Validator output (`VALID: ... (N assertions)`)

Ask explicitly: _"Do these evals cover the SPEC correctly? Do you want to add or change anything before freezing?"_

Without explicit OK from the user, do not freeze: the files change the judge with which everything is then measured. If the user doesn't respond within the turn, re-present the summary in the next turn.

## Outputs

At the end of the process, deliver:

1. **`evals/evals.json`** — train file validated (validator exit 0)
2. **`evals/val.json`** — validation file validated, same test_case number
3. **Truth-Kit** — textual list of covered behaviors, in this format (use identical):
   ```
   PASS → [id]: [description of the expected behavior]
   FAIL → [id]: [behavior that must not occur]
   ```
This kit is delivered to the autoloop as ground truth to verify iterative improvements of the skill.

## Notes

- This skill is generic (not tied to a single project).
- The `scripts/validate_evals.py` script uses only the standard library: no venv needed. Its errors name the problem and what's in its place (valid types, excess types, duplicate ids, items that aren't objects).
- The validator also checks the train/val pairing: the number of test_cases must be the same. If you add a case to the train, add one corresponding to the val.
- The minimum thresholds (≥ 8 test_cases, ≥ 40 total assertions, ≥ 60% S/A/B, ≤ 20% D/F) are fixed in the script: if the files do not reach them, adjust the eval files, not the validator (otherwise the gate no longer guarantees anything).
- References: `references/tiering-and-schema.md` (scheme + thresholds), `references/acceptance-extraction.md` (extraction technique + example of F2 Orders).

Finish only when both files print `VALID`, the human gate has been OKed, and the truth-kit has been delivered.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py evals-from-spec` and apply the tree-specific appendix it prints. The appendix may be empty.
