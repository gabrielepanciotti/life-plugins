# Tiering & Schema — evals-from-spec

## Tier Table

| Tier | Assertion type | Notes |
|------|---------------|-------|
| S | `file_exists` | Checks file exists on disk |
| S | `command_succeeds` | Shell command exits 0 (no `value` required) |
| S | `command_output_contains` | Shell command stdout contains value |
| S | `output_max_lines` | Agent output ≤ N lines |
| S | `output_min_lines` | Agent output ≥ N lines |
| A | `file_contains` | File content includes string |
| A | `file_not_contains` | File content does NOT include string |
| A | `file_regex` | File content matches regex |
| B | `output_not_contains` | Agent output does NOT contain string — **primary tool for "must NOT do X"** |
| C | `output_contains` | Agent output contains string |
| D | `output_regex` | Agent output matches regex — use sparingly |
| F | (unknown type) | Any unrecognised type counts as F |

## Gate Thresholds

| Check | Requirement |
|-------|------------|
| Minimum test_cases | ≥ 8 |
| Assertions per test_case | ≥ 3 each |
| Total assertions | ≥ 40 |
| Tier S/A/B share | ≥ 60% of all assertions |
| Tier D/F share | ≤ 20% of all assertions |

## Eval JSON Schema

### Top-level object

```json
{
  "skill": "skill-name",
  "split": "train",
  "model": "sonnet",
  "max_budget_usd": 0.6,
  "test_cases": [ ... ]
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `skill` | string | recommended | identifies the skill under test |
| `split` | string | **yes** | `"train"` for train file; `"validation"` for val file |
| `model` | string | optional | model to run against (e.g. `"sonnet"`) |
| `max_budget_usd` | number | optional | cost ceiling per run |
| `test_cases` | array | **yes** | list of test case objects |

### test_case object

```json
{
  "id": "tc-unique-id",
  "prompt": "User-facing prompt sent to the skill",
  "context": "Optional extra context or file contents",
  "assertions": [ ... ]
}
```

| Field | Type | Required |
|-------|------|----------|
| `id` | string | **yes** |
| `prompt` | string | **yes** |
| `context` | string/object | optional |
| `assertions` | array | **yes** — ≥ 3 per test_case |

### assertion object

```json
{
  "type": "output_not_contains",
  "value": "import pytest",
  "description": "Must not dump pytest code"
}
```

| Field | Type | Required |
|-------|------|----------|
| `type` | string (see Tier Table) | **yes** |
| `value` | string | **yes** (except `command_succeeds`) |
| `description` | string | optional but recommended |

## Strategy Notes

- For skill evals testing agent _output_ (not files), lean on **`output_not_contains` (Tier B)** as dominant type.
- Use `output_contains` (Tier C) for phrases that must appear.
- Keep `output_regex` (Tier D) at ≤ 20% of total assertions.
- Negative test_cases (routing refusals, wrong-tool guard) rely almost entirely on `output_not_contains`.
