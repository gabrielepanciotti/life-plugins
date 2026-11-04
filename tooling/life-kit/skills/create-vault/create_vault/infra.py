from __future__ import annotations

import subprocess
from collections.abc import Sequence
from typing import Callable

PERSONAL_NET = "personal-net"
PERSONAL_DB = "personal-db"

Runner = Callable[[Sequence[str]], "subprocess.CompletedProcess[str]"]


def _default_runner(cmd: Sequence[str]) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(list(cmd), capture_output=True, text=True)


# --- command builders (pure, testable without docker) ---


def network_inspect_cmd(name: str = PERSONAL_NET) -> list[str]:
    return ["docker", "network", "inspect", name]


def compose_up_cmd(compose_file: str) -> list[str]:
    return ["docker", "compose", "-f", compose_file, "up", "-d"]


def db_exists_cmd(db_name: str, *, container: str = PERSONAL_DB, user: str = "postgres") -> list[str]:
    return [
        "docker", "exec", container,
        "psql", "-U", user, "-tAc",
        f"SELECT 1 FROM pg_database WHERE datname='{db_name}'",
    ]


def db_create_cmd(db_name: str, *, container: str = PERSONAL_DB, user: str = "postgres") -> list[str]:
    return ["docker", "exec", container, "createdb", "-U", user, db_name]


# --- ensure (idempotent) ---


def ensure_personal_infra(compose_file: str, *, runner: Runner = _default_runner) -> bool:
    """Start the shared infrastructure with Compose if `personal-net` does not exist.

    Return True if Compose was started, or False if the network already existed.
    """
    res = runner(network_inspect_cmd())
    if res.returncode == 0:
        return False
    runner(compose_up_cmd(compose_file))
    return True


def ensure_database(
    db_name: str,
    *,
    container: str = PERSONAL_DB,
    user: str = "postgres",
    runner: Runner = _default_runner,
) -> bool:
    """Create database `db_name` in the Postgres container if it does not exist.

    Return True if it was created, or False if it already existed. This is idempotent.
    """
    res = runner(db_exists_cmd(db_name, container=container, user=user))
    if res.returncode == 0 and "1" in (res.stdout or ""):
        return False
    runner(db_create_cmd(db_name, container=container, user=user))
    return True
