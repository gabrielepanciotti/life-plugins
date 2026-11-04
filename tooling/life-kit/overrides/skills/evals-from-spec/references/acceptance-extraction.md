# Acceptance Extraction — from SPEC to testable assertions

Index: General rule · Extraction algorithm · Preferential tiering · Checklist for each test_case · Example F2 orders · Negative test_case

## General rule

Each **F-N** feature in the SPEC becomes ≥ 1 test_case.
Each validation rule generates at least three assertions: valid case, invalid case, edge case.

## Extraction algorithm

1. Identify each acceptance criterion numbered in the SPEC.
2. For each criterion: formulate a `prompt` that performs exactly that behavior.
3. Distinguish:
- **Positive** (what MUST happen): `output_contains`
- **Negative** (what should NOT happen): `output_not_contains` — **prefer this one, it's Tier B**
- **Routing guard** (must refer elsewhere): `output_contains` for mentioning the correct instrument + `output_not_contains` for wrong artifacts
4. Add ≥ 2 **negative** test_cases per session: behavior that should not occur or routing to another tool.
5. Each known corner case in the SPEC → 1 dedicated assertion.

## Preferential tiering

| Assertion type | Tiers | When to use it |
|---------------|------|--------------|
| `output_not_contains` | B | Incorrect behavior should NOT appear in the output |
| `output_contains` | C | The right behavior MUST appear |
| `output_regex` | D | Only for precise patterns that cannot be captured with contains — max 20% total |

## Checklist for each test_case

- [ ] At least 1 `output_not_contains` (Tier B) — what not to do
- [ ] At least 1 `output_contains` (Tier C) — what it needs to do
- [ ] `description` on each assertion (facilitates diagnosis in case of fail)

## Concrete example: F2 orders - Validation of order code, postcode, tax code

Feature F2 of the SPEC of an order management system (invented example): validation of the order fields.

### Validation rules

| Field | Rule | Valid example | Invalid example |
|-------|--------|---------------|-----------------|
| Order code | format `ORD-` + 8 digits | `ORD-48151623` | `ORX-48151623` / too short |
| Postcode | exactly 5 digits | `33100` | `3310` (4 digits) |
| Tax code natural person | 16 char alphanum, standard regex | `RSSMRA80A01H501U` | `RSSMRA80A01` (too short) |
| VAT number | 11 digits | `12345678901` | `1234567890` (10 digits) |

### Example assertion in JSON

```json
[
  {
    "type": "output_not_contains",
    "value": "valid",
    "description": "An order code with the ORX prefix must be rejected"
  },
  {
    "type": "output_contains",
    "value": "ORD prefix",
    "description": "The error message must mention the expected prefix"
  },
  {
    "type": "output_not_contains",
    "value": "accepted postcode",
    "description": "A four-digit postcode must fail validation"
  }
]
```

### Complete test_case for CAP too short

```json
{
  "id": "f2-cap-too-short",
  "prompt": "I am entering an order. The customer postcode is '3310'. Is it valid?",
  "context": "Order management system: the postcode must contain exactly 5 digits.",
  "assertions": [
    {
      "type": "output_not_contains",
      "value": "valid postcode",
      "description": "A four-digit postcode must not be declared valid"
    },
    {
      "type": "output_not_contains",
      "value": "procedi",
      "description": "Must not invite the user to proceed with an invalid postcode"
    },
    {
      "type": "output_contains",
      "value": "5",
      "description": "Must state that the postcode requires 5 digits"
    }
  ]
}
```

### Test_case for natural person CF — edge case length

```json
{
  "id": "f2-cf-pf-short",
  "prompt": "The customer tax code is 'RSSMRA80A01'. Can I proceed?",
  "context": "Order management system: an individual tax code consists of 16 alphanumeric characters.",
  "assertions": [
    {
      "type": "output_not_contains",
      "value": "valid tax code",
      "description": "An 11-character tax code is invalid for an individual"
    },
    {
      "type": "output_not_contains",
      "value": "procedi",
      "description": "Must not continue with an invalid tax code"
    },
    {
      "type": "output_contains",
      "value": "16",
      "description": "Must mention the required 16 characters"
    }
  ]
}
```

## Negative test_case — template

Always include ≥ 2 test_cases for behaviors that should NOT happen:

```json
{
  "id": "neg-wrong-tool",
  "prompt": "Write pytest tests for the calculate_total function",
  "assertions": [
    {
      "type": "output_not_contains",
      "value": "evals.json",
      "description": "Must refer the user to the testing skill instead of generating evals"
    },
    {
      "type": "output_contains",
      "value": "testing",
      "description": "Must name the correct tool"
    },
    {
      "type": "output_not_contains",
      "value": "test_cases",
      "description": "Must not start building test_cases"
    }
  ]
}
```
