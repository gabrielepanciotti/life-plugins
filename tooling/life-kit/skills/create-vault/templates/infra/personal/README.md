# Shared personal infrastructure — `personal-db` + `personal-net`

Shared Postgres 16 and a common Docker network used by all personal **Tier-1** digital brains.
Define it **once** (here), then each project creates its own database on it.

## Start (one-time)
```bash
cp .env.example .env   # adjust username/password if desired
docker compose up -d   # creates container 'personal-db' + network 'personal-net'
```

## For each new personal Tier-1 project
The `create-vault` scaffolder creates the project database on shared Postgres:
```bash
# Windows: use .venv/Scripts/python instead of .venv/bin/python
.venv/bin/python -m create_vault.cli --config cfg.json --dest <folder> --git \
    --ensure-infra <path>/docker-compose.yml --ensure-db
```
- `--ensure-infra` starts this infrastructure if the `personal-net` network does not exist.
- `--ensure-db` creates database `<db_name>` on `personal-db` if missing (idempotent).

Then, from the project folder: `docker compose up -d` and `alembic upgrade head`.

## Portability (another server)
Copy this folder to another server and run `docker compose up -d` again. Projects remain unchanged:
only the host paths in their `.env` files change.
