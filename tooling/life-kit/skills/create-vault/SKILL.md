---
name: create-vault
description: "Create or update a digital brain made up of an editorial vault, agent integration, and optional engine, using an idempotent scaffold. Use it for ‘create a vault’, ‘new digital brain’, ‘scaffold the project’, or updating an already generated vault."
---

# create-vault

Scaffold a digital brain. Conduct the interview, prepare `cfg.json`, invoke the
generator, check the output, and initialize the repository when requested. Do not populate
content during scaffolding.

## Decision path

- **New project**: follow the workflow and choose `tier: 0` or `tier: 1`.
- **Already generated project**: use `--mode upgrade`; the update is additive.
- **An engine is needed**: use tier 1 and also check the backend, container, and database.

## Requirements

- Python 3.13;
- a virtual environment for the skill;
- the packages listed in `requirements.txt`;
- Docker running only for tier 1.

Example setup from the skill directory:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

In the examples, `PY` refers to the Python interpreter in the skill's virtual environment.

## Workflow

Copy and check off:

- [ ] Interview complete; if a field is missing, stay on step 1.
- [ ] `cfg.json` written to a temporary directory.
- [ ] Generation finished with `OK: scaffold ...`; if there is an error, fix the config.
- [ ] `vault/SYSTEM_PROMPT.md` exists; for tier 1, `backend/` exists too.
- [ ] Links in the project instructions have been updated with approval.
- [ ] The user has received a summary and next steps.

### 1. Mini-interview

Ask one question at a time and offer options where helpful. Collect:

- `project_name`: kebab-case slug;
- `persona` and `persona_full`: identity of the domain assistant;
- `aliases`: at least one invocation phrase;
- `mission`: one line;
- `scope`: project configuration profile;
- `wiki_domains`: at least one domain, with an initial proposal to confirm;
- `entity_types`: canonical page types and frontmatter fields;
- `decision_queries`: decisions the vault must support;
- `tier`: `0` for vault only, `1` for application engine and database.

### 2. Temporary configuration

Write `cfg.json` to a temporary directory. Do not include credentials, personal paths, or
data that does not belong in the scaffold.

### 3. Generation

Always pass an explicit destination:

```bash
PY -m create_vault.cli --config <cfg.json> --dest <destinazione> --git
```

`--today YYYY-MM-DD` is optional; without it, the current date is used. If the destination
contains files, first check that the requested operation is an upgrade rather than a new
creation.

### 4. Project links

With the user's approval, update the instruction file that lists the project's vaults or
agents. Use relative paths or portable placeholders.

### 5. Summary

Show:

- generated destination;
- commands and agents created;
- chosen tier;
- how to populate the wiki;
- for tier 1, how to start the container and run migrations;
- any link that still needs to be completed with the project's orchestrator.

## Tier 1 — engine and database

Tier 1 adds an asynchronous backend, migrations, environment-based configuration, and
Compose. Keep credentials and host paths in `.env`, never in versioned files.

If the project uses shared infrastructure that is already set up, generate or update its
configuration in a directory chosen by the user and link it to the scaffold:

```bash
PY -m create_vault.cli --emit-infra <dir-infra>
PY -m create_vault.cli --config cfg.json --dest <destinazione> --git \
  --ensure-infra <dir-infra>/docker-compose.yml --ensure-db
```

Then, in the generated project:

```bash
docker compose up -d
alembic upgrade head
```

Check the generated files before starting services or running migrations. The scaffold
includes an example model: replace it with the domain entities in a separate task.

## Idempotency

- `--mode upgrade` writes only what is missing and adds new domains, entities, and components.
- `--force <path...>` overwrites only the named files.
- Files declared write-once, such as the vault registry, are not regenerated.
- Before using `--force`, show the user the expected diff and get confirmation.

## Out of scope

- Populating the wiki with real content.
- Defining domain migrations beyond the initial scaffold.
- Starting unrequested external services.
- Automatically registering the vault with unconfigured orchestrators.

## Verification

Run from the skill root:

```bash
PY -m pytest
```

Finish only when the scaffold command returns `OK`, the expected files exist, the tests
pass, and the user has a reproducible summary.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py create-vault` and apply what it prints (it may print nothing).
