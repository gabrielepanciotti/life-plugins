from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable

from .config import EntityType, ScaffoldConfig
from .render import render_static_tree, render_string

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

# Files that must NEVER be overwritten after their initial creation (write-once).
WRITE_ONCE = frozenset({"vault/wiki/log.md"})

ENTITY_TEMPLATE = """\
---
type: {{ entity.name }}
title: ""
tags: []
created: {{ today }}
updated: {{ today }}
sources: ""
coverage: med
{% for f in entity.fields %}{{ f }}: ""
{% endfor %}---

#

> [coverage: med]
"""

COMMAND_QUERY = """\
---
description: "{{ persona }} — domain decision query for {{ project_name }}"
---

[CMD:/{{ alias }}] $ARGUMENTS

Follow the QUERY procedure in vault/SYSTEM_PROMPT.md: read the relevant context,
narrow the options, and propose 2–3 reasoned alternatives. Domain decision queries:
{% for q in decision_queries %}- {{ q }}
{% endfor %}
"""

COMMAND_BUONGIORNO = """\
---
description: "{{ persona }} — session start: load context and make a proposal"
---

[CMD:/buongiorno-{{ persona | lower }}]

Load `vault/wiki/index.md` and `vault/wiki/log.md`, summarize the vault's state
in <=12 lines, and suggest the next useful action in the {{ project_name }} domain.
"""

AGENT_PERSONA = """\
---
name: {{ persona | lower }}
description: "{{ persona }}, a digital knowledge vault for {{ project_name }}. Invoked with {% for a in aliases %}{{ a }}{% if not loop.last %}/{% endif %}{% endfor %}."
tools: Read, Glob, Grep, Bash
---

You are {{ persona }}. Follow `vault/SYSTEM_PROMPT.md`. Work in EDIT/INGEST/QUERY/LINT modes.
When you receive a `[CMD:/...]` marker, follow the corresponding skill or command procedure.
"""


def _ctx(config: ScaffoldConfig, today: str) -> dict:
    return {
        "persona": config.persona,
        "persona_full": config.persona_full or config.persona,
        "project_name": config.project_name,
        "mission": config.mission,
        "aliases": config.aliases,
        "wiki_domains": config.wiki_domains,
        "entity_types": config.entity_types,
        "decision_queries": config.decision_queries,
        "scope": config.scope,
        "tier": config.tier,
        "db_name": config.db_name,
        "project_dir": config.project_dir,
        "today": today,
    }


def _writer(dest: Path, mode: str, force: frozenset[str]) -> Callable[[str], bool]:
    """Predicate for should_write: 'create' writes everything except existing WRITE_ONCE files;
    'upgrade' writes only missing files, except paths in `force` (which are overwritten).
    WRITE_ONCE paths are never overwritten, even if present in force."""

    def should_write(rel: str) -> bool:
        exists = (dest / rel).exists()
        if rel in WRITE_ONCE:
            return not exists
        if mode == "upgrade":
            return (not exists) or (rel in force)
        return True  # create

    return should_write


def scaffold(
    config: ScaffoldConfig,
    dest: Path | str,
    today: str,
    *,
    mode: str = "create",
    force: frozenset[str] = frozenset(),
) -> Path:
    """Generate or update the project in `dest`. Return dest."""
    dest = Path(dest)
    ctx = _ctx(config, today)
    should_write = _writer(dest, mode, force)

    # 1. Static project tree (Tier 0).
    render_static_tree(TEMPLATES / "project", dest, ctx, should_write=should_write)

    # 2. Wiki domain directories (additive, never overwritten).
    for d in config.wiki_domains:
        gk = Path("vault/wiki") / d / ".gitkeep"
        if should_write(gk.as_posix()):
            (dest / gk).parent.mkdir(parents=True, exist_ok=True)
            (dest / gk).write_text("", encoding="utf-8")

    # 3. Entity template (one per entity type).
    for e in config.entity_types:
        rel = Path("vault/_templates") / f"{e.name}.md"
        if should_write(rel.as_posix()):
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            (dest / rel).write_text(
                render_string(ENTITY_TEMPLATE, {"entity": e, "today": today}),
                encoding="utf-8",
            )

    # 4. .claude/ plugin (QUERY command for the first alias, greeting, and persona agent).
    cmd_dir = Path(".claude/commands")
    q_rel = cmd_dir / f"{config.aliases[0]}.md"
    if should_write(q_rel.as_posix()):
        (dest / q_rel).parent.mkdir(parents=True, exist_ok=True)
        (dest / q_rel).write_text(
            render_string(COMMAND_QUERY, {**ctx, "alias": config.aliases[0]}),
            encoding="utf-8",
        )
    b_rel = cmd_dir / f"buongiorno-{config.persona.lower()}.md"
    if should_write(b_rel.as_posix()):
        (dest / b_rel).parent.mkdir(parents=True, exist_ok=True)
        (dest / b_rel).write_text(render_string(COMMAND_BUONGIORNO, ctx), encoding="utf-8")

    a_rel = Path(".claude/agents") / f"{config.persona.lower()}.md"
    if should_write(a_rel.as_posix()):
        (dest / a_rel).parent.mkdir(parents=True, exist_ok=True)
        (dest / a_rel).write_text(render_string(AGENT_PERSONA, ctx), encoding="utf-8")

    # 5. Optional Tier 1 engine: FastAPI, SQLAlchemy, Alembic, and Docker backend.
    if config.tier >= 1:
        render_static_tree(TEMPLATES / "engine", dest, ctx, should_write=should_write)

    return dest


def emit_infra(dest: Path | str, *, scope: str = "personal") -> Path:
    """Write shared Docker infrastructure (Compose `personal-db` and `personal-net`) to `dest`.

    Idempotent and additive: existing files are not overwritten. This is a one-time
    operation independent of individual projects (Tier 1 projects *use* it, not recreate it).
    """
    dest = Path(dest)
    src = TEMPLATES / "infra" / scope
    render_static_tree(src, dest, {}, should_write=lambda rel: not (dest / rel).exists())
    return dest


def git_init_and_commit(dest: Path | str, message: str) -> None:
    """Initialize a Git repository in dest and create the initial commit."""
    dest = str(dest)
    subprocess.run(["git", "-C", dest, "init", "-q"], check=True)
    subprocess.run(["git", "-C", dest, "add", "-A"], check=True)
    subprocess.run(["git", "-C", dest, "commit", "-q", "-m", message], check=True)
