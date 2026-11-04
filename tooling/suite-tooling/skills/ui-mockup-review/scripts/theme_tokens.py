"""Print a design-system theme's color/shape tokens as flat `path = value` lines.

Usage: python theme_tokens.py [theme]   (default: base = Eclisse 2)
Use it to refresh the :root blocks of assets/mockup-kit.html when the theme changes.
"""

import json
import sys
from pathlib import Path

THEMES = Path(__file__).resolve().parents[5] / "packages" / "design-system" / "themes"


def walk(node: dict, prefix: str = ""):
    for key, val in node.items():
        if key.startswith("$") or not isinstance(val, dict):
            continue
        if "$value" in val:
            yield prefix + key, val["$value"]
        else:
            yield from walk(val, prefix + key + ".")


def main() -> None:
    theme = sys.argv[1] if len(sys.argv) > 1 else "base"
    data = json.loads((THEMES / theme / "theme.tokens.json").read_text(encoding="utf-8"))
    for part in ("shared", "light", "dark"):
        print(f"## {part}")
        for path, value in walk(data.get(part, {})):
            print(f"{path} = {value}")


if __name__ == "__main__":
    main()
