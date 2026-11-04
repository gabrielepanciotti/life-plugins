from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from . import infra
from .config import ScaffoldConfig
from .scaffold import emit_infra, git_init_and_commit, scaffold


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="create-vault", description="Scaffolder cervello digitale")
    parser.add_argument("--config", help="path to cfg.json (not required with --emit-infra alone)")
    parser.add_argument("--dest", help="destination (default: config.project_dir)")
    parser.add_argument("--today", help="data YYYY-MM-DD (opzionale, default: oggi)")
    parser.add_argument("--mode", default="create", choices=["create", "upgrade"])
    parser.add_argument("--force", nargs="*", default=[], help="relative paths to overwrite during upgrade")
    parser.add_argument("--git", action="store_true", help="git init + first commit after scaffolding")
    parser.add_argument("--emit-infra", metavar="DIR", help="writes shared infra (personal-db + personal-net) to DIR")
    parser.add_argument("--ensure-infra", metavar="COMPOSE", help="starts shared infra if the personal-net network is missing (requires Docker)")
    parser.add_argument("--ensure-db", action="store_true", help="creates the project database on personal-db if missing (requires Docker, Tier-1 only)")
    args = parser.parse_args(argv)

    config = None
    if args.config:
        config = ScaffoldConfig.model_validate_json(Path(args.config).read_text(encoding="utf-8"))

    # Shared infra: one-time setup (does not require --config).
    if args.emit_infra:
        scope = config.scope if config else "personal"
        emit_infra(args.emit_infra, scope=scope)
        print(f"OK: infra '{scope}' -> {args.emit_infra}")
        if not config:
            return 0

    if args.ensure_infra:
        acted = infra.ensure_personal_infra(args.ensure_infra)
        print("OK: infra condivisa avviata" if acted else "OK: shared infra already present")

    if not config:
        parser.error("requires --config (or use --emit-infra alone)")
    if not args.today:
        args.today = date.today().isoformat()

    dest = Path(args.dest) if args.dest else Path(config.project_dir)
    scaffold(config, dest, today=args.today, mode=args.mode, force=frozenset(args.force))

    if args.ensure_db:
        created = infra.ensure_database(config.db_name)
        print(f"OK: database '{config.db_name}' creato" if created else f"OK: database '{config.db_name}' already exists")

    if args.git:
        git_init_and_commit(dest, f"feat: scaffold {config.project_name} cervello digitale ({config.persona})")

    print(f"OK: scaffold {config.project_name} -> {dest}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
