#!/usr/bin/env python3
"""validate_evals.py — quality gate per output di evals-from-spec (stdlib only).

Usage (python3.13 on Linux, py -3.13 on Windows):
  python3.13 validate_evals.py <evals.json>                     # valida un file (exit 0 ok, 1 fail)
  python3.13 validate_evals.py <train.json> --pair <val.json>   # valida + check pairing
  python3.13 validate_evals.py --selftest                       # test interni
"""

import json
import sys
import argparse

TIER = {
    "file_exists": "S",
    "command_succeeds": "S",
    "command_output_contains": "S",
    "output_max_lines": "S",
    "output_min_lines": "S",
    "file_contains": "A",
    "file_not_contains": "A",
    "file_regex": "A",
    "output_not_contains": "B",
    "output_contains": "C",
    "output_regex": "D",
}


def check_schema(data):
    errors = []
    if not isinstance(data, dict):
        return ["root must be an object"]
    if "split" not in data:
        errors.append("missing top-level 'split'")
    tcs = data.get("test_cases")
    if not isinstance(tcs, list):
        return errors + ["'test_cases' must be a list"]
    seen_ids = {}
    for i, tc in enumerate(tcs):
        if not isinstance(tc, dict):
            errors.append(
                f"test_case[{i}] must be an object, got {type(tc).__name__}"
            )
            continue
        if "id" not in tc:
            errors.append(f"test_case[{i}] missing 'id' (keys found: {sorted(tc)})")
        else:
            if tc["id"] in seen_ids:
                errors.append(
                    f"test_case[{i}] duplicate id {tc['id']!r} "
                    f"(already used by test_case[{seen_ids[tc['id']]}])"
                )
            else:
                seen_ids[tc["id"]] = i
        if "prompt" not in tc:
            errors.append(f"test_case[{i}] missing 'prompt' (keys found: {sorted(tc)})")
        asserts = tc.get("assertions")
        if not isinstance(asserts, list):
            errors.append(
                f"test_case[{i}] 'assertions' must be a list, got {type(asserts).__name__}"
            )
            continue
        for j, a in enumerate(asserts):
            if not isinstance(a, dict):
                errors.append(
                    f"test_case[{i}].assertion[{j}] must be an object, "
                    f"got {type(a).__name__}"
                )
                continue
            if a.get("type") not in TIER:
                errors.append(
                    f"test_case[{i}].assertion[{j}] unknown type {a.get('type')!r}. "
                    f"Valid types: {', '.join(sorted(TIER))}"
                )
            if "value" not in a and a.get("type") != "command_succeeds":
                errors.append(
                    f"test_case[{i}].assertion[{j}] missing 'value' (keys found: {sorted(a)})"
                )
    return errors


def _all_assertions(data):
    out = []
    for tc in data.get("test_cases", []):
        if not isinstance(tc, dict) or not isinstance(tc.get("assertions"), list):
            continue
        out.extend(a for a in tc["assertions"] if isinstance(a, dict))
    return out


def _type_breakdown(asserts, tiers_wanted):
    """Count assertion types in the given tiers, most used first, e.g. 'output_regex x12'."""
    counts = {}
    for a in asserts:
        t = a.get("type")
        if TIER.get(t, "F") in tiers_wanted:
            counts[t] = counts.get(t, 0) + 1
    ordered = sorted(counts.items(), key=lambda kv: -kv[1])
    return ", ".join(f"{t} x{n}" for t, n in ordered) or "none"


def check_tiering(data):
    errors = []
    asserts = _all_assertions(data)
    if not asserts:
        return ["no assertions to tier"]
    tiers = [TIER.get(a.get("type"), "F") for a in asserts]
    n = len(tiers)
    sab = sum(1 for t in tiers if t in ("S", "A", "B"))
    df = sum(1 for t in tiers if t in ("D", "F"))
    if sab / n < 0.60:
        errors.append(
            f"only {sab}/{n} ({sab/n:.0%}) assertions Tier S/A/B (need >=60%). "
            f"Too many weak types: {_type_breakdown(asserts, ('C', 'D', 'F'))}. "
            "Convert some to output_not_contains or file/command checks."
        )
    if df / n > 0.20:
        errors.append(
            f"{df}/{n} ({df/n:.0%}) assertions Tier D/F (max 20%). "
            f"Types in excess: {_type_breakdown(asserts, ('D', 'F'))}"
        )
    return errors


def check_counts(data):
    errors = []
    tcs = data.get("test_cases", [])
    if len(tcs) < 8:
        errors.append(f"only {len(tcs)} test_cases (need >=8)")
    for tc in tcs:
        if not isinstance(tc, dict):
            continue
        a = tc.get("assertions", [])
        if not isinstance(a, list):
            continue
        if len(a) < 3:
            errors.append(
                f"test_case {tc.get('id','?')} has {len(a)} assertions (need >=3)"
            )
    total = len(_all_assertions(data))
    if total < 40:
        errors.append(f"only {total} total assertions (need >=40)")
    return errors


def check_pairing(train, val):
    errors = []
    if len(train.get("test_cases", [])) != len(val.get("test_cases", [])):
        errors.append("train and val must have same number of test_cases")
    if val.get("split") != "validation":
        errors.append("val file must have split == 'validation'")
    return errors


def validate(data):
    schema_errors = check_schema(data)
    if not isinstance(data, dict) or not isinstance(data.get("test_cases"), list):
        return schema_errors
    return schema_errors + check_tiering(data) + check_counts(data)


def load_evals(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _selftest():
    good = {
        "split": "train",
        "test_cases": [
            {
                "id": f"tc{i}",
                "prompt": "p",
                "assertions": [
                    {"type": "file_exists", "value": "x"},
                    {"type": "file_contains", "value": "y"},
                    {"type": "output_not_contains", "value": "z"},
                    {"type": "output_contains", "value": "w"},
                    {"type": "output_regex", "value": "r"},
                ],
            }
            for i in range(8)
        ],
    }
    assert validate(good) == [], validate(good)
    bad_tier = {
        "split": "train",
        "test_cases": [
            {
                "id": f"tc{i}",
                "prompt": "p",
                "assertions": [
                    {"type": "output_regex", "value": "r"},
                    {"type": "output_regex", "value": "r"},
                    {"type": "output_contains", "value": "w"},
                ],
            }
            for i in range(8)
        ],
    }
    assert any("Tier" in e for e in validate(bad_tier)), validate(bad_tier)
    bad_count = {
        "split": "train",
        "test_cases": [
            {
                "id": "tc1",
                "prompt": "p",
                "assertions": [{"type": "file_exists", "value": "x"}],
            }
        ],
    }
    assert any("test_cases" in e for e in validate(bad_count)), validate(bad_count)
    bad_schema = {"test_cases": "nope"}
    assert validate(bad_schema)
    dup = {
        "split": "train",
        "test_cases": [
            {"id": "a", "prompt": "p", "assertions": ["not a dict", {"type": "zzz", "value": "v"}]},
            {"id": "a", "prompt": "p", "assertions": []},
            "not a dict either",
        ],
    }
    errs = validate(dup)
    assert any("duplicate id" in e for e in errs), errs
    assert any("must be an object" in e for e in errs), errs
    assert any("Valid types" in e for e in errs), errs
    print("selftest OK")


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("file", nargs="?")
    p.add_argument("--pair")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    if not args.file:
        p.error("file required (or --selftest)")
    data = load_evals(args.file)
    errors = validate(data)
    if args.pair:
        errors += check_pairing(data, load_evals(args.pair))
    if errors:
        print(f"INVALID: {args.file}")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"VALID: {args.file} ({len(_all_assertions(data))} assertions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
