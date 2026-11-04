"""Print the appendices of a kit skill (device, person, tree), from any directory.

Usage: python skill-overlay.py <skill> [--instance ID]

The kit skills are generic; what belongs to one person, company or machine is an
appendix the skill reads in its last step. With the Life framework importable (the kit
inside a Life checkout, or LIFE_FRAMEWORK_DIR set) this defers to suite_core.skill_overlay,
which also resolves the tree layer; otherwise it reads the device and person layers with
the standard library only, so an installed plugin works on a machine without Life.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

SKILL_NAME = re.compile(r"[a-z0-9][a-z0-9._-]*")


def _framework_candidates() -> list[Path]:
    found = []
    if os.environ.get("LIFE_FRAMEWORK_DIR"):
        found.append(Path(os.environ["LIFE_FRAMEWORK_DIR"]))
    found.append(Path(__file__).resolve().parents[3])  # <framework>/tooling/life-kit/scripts
    return found


def _with_suite_core(skill: str, instance: str | None) -> str | None:
    for root in _framework_candidates():
        shared = root / "packages" / "shared"
        if (shared / "suite_core" / "skill_overlay.py").is_file():
            sys.path.insert(0, str(shared))
            try:
                from suite_core import skill_overlay
            except ImportError:
                sys.path.pop(0)
                continue
            return skill_overlay.overlay_text(skill, instance)
    return None


def _standalone(skill: str) -> str:
    life_home = Path(os.environ.get("LIFE_HOME") or Path.home() / ".life")
    agent_home = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    parts = []
    for path in (life_home / "skills" / f"{skill}.md", agent_home / "skill-overlays" / f"{skill}.md"):
        if path.is_file():
            body = path.read_text(encoding="utf-8").strip()
            if body:
                parts.append(f"<!-- {path.as_posix()} -->\n{body}")
    return "\n\n".join(parts)


def main(argv: list[str]) -> int:
    instance = argv[argv.index("--instance") + 1] if "--instance" in argv[:-1] else None
    names = [a for a in argv if not a.startswith("--") and a != instance]
    if not names or not SKILL_NAME.fullmatch(names[0]):
        sys.stderr.write("usage: skill-overlay.py <skill> [--instance ID]\n")
        return 2
    text = _with_suite_core(names[0], instance)
    if text is None:
        text = _standalone(names[0])
    if text:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
