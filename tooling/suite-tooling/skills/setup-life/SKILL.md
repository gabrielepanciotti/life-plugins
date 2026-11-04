---
name: setup-life
description: Guides the complete Life setup together with the user (system nodes, catalog nodes, tools and subscriptions, channels, operators), or migration from the old clone to the `life` repo on the prod channel. The agent performs and verifies every step; the user only handles login, 2FA, and pastes keys into the masked window. Triggers "/setup-life", "configure Life", "Life setup", "switch to the new Life", "migrate to life", "what is missing from setup".
argument-hint: "[setup|migration|status] [tree]"
---

# /setup-life — Life setup and migration with the agent

You (the agent) perform the steps; the user only does what a program cannot: browser login,
2FA, node selection, and pasting keys into the **masked window**. Work from the Life folder.
Works the same in Claude Code and OpenCode (the `sync-agents` port).

## Fixed rules

- **Never put a key, token, or password in chat**, a file, or a visible command. If the
  user pastes one, tell them to revoke and replace it, and do not use it.
- **Never write to or push to the Life repo.** Write only to the tree repo (`life-<id>`) and
  the user's node repos.
- Before each step, say what you are doing; afterwards, verify it against the actual output. A step
  without verification is not done.
- Stop and wait for the user only for: login, 2FA, keys, node and operator selection,
  and pending changes in the old clone.
- Everything is idempotent: rerunning is safe. If a command fails, show the error and the
  “how to fix” row in the final table; do not invent remedies.

## 0. Identify the situation

1. Ask (or read from the argument) for the tree `<id>` and user `<user>` if you do not already know them.
2. Check the status:
   ```bash
   bash scripts/onboarding/onboarding.sh --instance <id> --dry-run
   ```
   It prints an `ok / missing / skipped` table and saves it to `~/.life/onboarding.json`
   (`lastRun`), which is also what the launcher's **Setup** page displays.
3. Choose the path:
   - argument `status` → show the table, explain the `missing` rows, and stop;
   - an old Life clone is nearby (for example `../Life-old`) or the user says “switch to the
     new Life” → **migration**;
   - otherwise → **setup**.

## Migration (from the old clone to `life`, prod channel)

Follow `docs/onboarding/migrazione-a-life.md` from step 0 through step 8, one at a time, with the
checks written there. Stop points: changes in the old clone (step 0: stop and ask),
node selection (step 5), keys (step 7: `--popup` only). At the end, run the guide's final check
and then setup with `--dry-run` to show the table.

## Setup (new user or setup to complete)

One script, the same extended idempotent onboarding:

```bash
bash scripts/onboarding/onboarding.sh --instance <id> --channel prod \
  [--node <slug> ...] [--operator <name> ...]
# Windows PowerShell: .\scripts\onboarding\onboarding.ps1 --instance <id> --channel prod ...
```

The step order is in `scripts/onboarding/steps.json`:

1. **System**: Life prerequisites and venv, GitHub (browser login: the user), device and
   tree, channel (`--channel prod` for Life users, `dev` only for developers), catalog system nodes.
2. **Nodes**: show `python -m suite_core.nodes catalog list`, ask the user which ones they use,
   and pass them with `--node`. It is fine to choose none: add them later with `catalog enable`.
3. **Tools**: Claude Code plugins and skills, `sync-agents` (Claude Code and OpenCode equally),
   global OpenCode configuration.
4. **Subscriptions and keys**: log in to the subscriptions the user has; for API keys run
   `python3 scripts/kit/register-llm.py --instance <id> --user <user> --account <account>
   --popup --execute` (account table in `docs/onboarding/claude-code-e-opencode.md` §5).
5. **Channels**: `python -m suite_core.nodes instances connect <id>`; for every `missing` channel, run
   the printed command (`… connect <id> <channel> --esegui`). Personal channels: `--membro <user>`.
6. **Operators** (optional): Scheduler, call manager, launcher, only if the user wants them,
   using `--operator <name>`; those without a catalog card follow the manual procedure in
   `docs/onboarding/nuova-persona.md` §7.
7. **Verification**: `instances doctor`.

Rerun the script after each login or key: completed steps return `ok` without repeating anything.

## Wrap-up

- Show the final table and, for each `missing` row, what is needed and who will do it.
- If you enabled nodes, remember to commit and push `life-<id>` (the graph has changed).
- Point to the pages to review: `docs/onboarding/pagine/checklist.html`,
  `docs/onboarding/pagine/mappa-nodi.html`, and the launcher's **Setup** page.
- From then on, updates are done with one command: `bash scripts/devices/sync-device.sh --execute`.

## Instance specifics

Run `python -m suite_core.nodes skill-overlay setup-life` and apply what it prints (it may print nothing).
