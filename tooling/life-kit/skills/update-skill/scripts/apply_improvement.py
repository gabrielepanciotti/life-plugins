#!/usr/bin/env python3
"""Apply the answer of the `improve` step (procedures/improve.md) to a skill.

usage: apply_improvement.py <SKILL.md> <journal.md> < answer
Writes the new SKILL.md, appends the journal entry, prints the one-line change.
Exit 1 with nothing written when the answer does not have the three blocks.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

BLOCKS = re.compile(
    r"^=== SKILL\.md ===\n(?P<skill>.*?)\n=== JOURNAL ===\n(?P<journal>.*?)\n=== CHANGE ===\n(?P<change>[^\n]*)",
    re.DOTALL | re.MULTILINE,
)


def parse(answer: str) -> tuple[str, str, str] | None:
    m = BLOCKS.search(answer.replace("\r\n", "\n"))
    if not m or not m["skill"].strip() or not m["change"].strip():
        return None
    return m["skill"].rstrip() + "\n", m["journal"].strip(), m["change"].strip()[:80]


def main(argv: list[str]) -> int:
    parsed = parse(sys.stdin.read())
    if parsed is None:
        print("unparseable answer", file=sys.stderr)
        return 1
    skill, journal, change = parsed
    Path(argv[1]).write_text(skill, encoding="utf-8")
    with Path(argv[2]).open("a", encoding="utf-8") as fh:
        fh.write("\n" + journal + "\n")
    print(change)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
