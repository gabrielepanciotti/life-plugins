from __future__ import annotations

from pathlib import Path
from typing import Callable

from jinja2 import Environment, StrictUndefined

_env = Environment(
    undefined=StrictUndefined,
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_string(text: str, ctx: dict) -> str:
    """Render a Jinja2 string with the given context."""
    return _env.from_string(text).render(**ctx)


def render_static_tree(
    template_dir: Path,
    dest: Path,
    ctx: dict,
    *,
    should_write: Callable[[str], bool] = lambda rel: True,
) -> list[Path]:
    """Walk template_dir and render path names and file contents.

    - Files named `*.j2` are rendered and lose the `.j2` suffix.
    - Other files are copied verbatim (their path names are still rendered).
    - `should_write(rel_posix)` decides whether to write (rel is the output's POSIX relative path).
    Return the list of files actually written.
    """
    template_dir = Path(template_dir)
    dest = Path(dest)
    written: list[Path] = []

    for src in sorted(template_dir.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(template_dir)
        out_parts = [render_string(p, ctx) for p in rel.parts]
        out_rel = Path(*out_parts)
        if out_rel.suffix == ".j2":
            out_rel = out_rel.with_suffix("")
            content = render_string(src.read_text(encoding="utf-8"), ctx)
        else:
            content = src.read_text(encoding="utf-8")

        if not should_write(out_rel.as_posix()):
            continue

        out_path = dest / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        written.append(out_path)

    return written
