# workspace-mcp (default for Drive, Docs, Sheets, Gneverl, Calendar) and drive_cli.py

Contents:
- Installation and Web client
- Credentials
- Remaining Drive operations: drive_cli.py

## Installation and Web client

`@modelcontextprotocol/server-gdrive` is read-only by design: a single tool (`gdrive_search`) plus reading through *resources*, with no way to extend it (no uploads, folders, or permissions). That is why the default is [`workspace-mcp`](https://github.com/taylorwilsdon/google_workspace_mcp) (PyPI `workspace-mcp`, stdio, over 120 tools, OAuth with your own client):
```bash
uv tool install workspace-mcp     # → ~/.local/bin/workspace-mcp (.exe on Windows)
```
It requires a **Web** client (not Desktop): its callback is `http://localhost:<porta>/oauth2callback`, a path that Desktop clients do not register. Create it with the same `gclientid`, without `--desktop`:
```bash
.venv/bin/gclientid --project <project-id> --cdp-chrome --accept-terms \
  --redirect http://localhost:<porta>/oauth2callback \
  --scope https://www.googleapis.com/auth/drive
```
(Windows: `.venv/Scripts/gclientid.exe`.)

## Credentials

The callback listener exists only within a live MCP session, so a CLI command alone is not enough: the script manually drives a stdio session and clicks consent in CDP Chrome.
```bash
.venv/bin/python scripts/workspace_mcp_auth.py \
  --client-secret ~/.config/gclientid/oauth-client.json \
  --email <<account>@gmail.com> \
  --creds-dir ~/.config/gclientid/workspace-mcp-creds \
  --port <porta> --service drive --cdp-port 9223
```
**Before running it, stop any `workspace-mcp` process that is still running**: the server silently falls back to the next port if its own is occupied, but `redirect_uri` remains set to the configured value, so the callback goes nowhere and the only symptom is a timeout.

Linux: `pkill -f workspace-mcp`. Windows:
```bash
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -like '*workspace-mcp*' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }"
```

## Remaining Drive operations: `drive_cli.py`

`workspace-mcp` covers more than the tool names suggest: **check the parameters before concluding that something is missing**. `update_drive_file` already supports trashing (`trashed`), renaming, moving (`add_parents`/`remove_parents`), starring files, and appending text; `manage_drive_access` handles permissions, bulk sharing, expiration, and ownership transfer.

Only these operations remain outside it; they are covered by `scripts/drive_cli.py` (using the same MCP credentials and the already approved `drive` scope; no new consent is needed):
```bash
python scripts/drive_cli.py quota
python scripts/drive_cli.py trash-list [--limit N]
python scripts/drive_cli.py delete <fileId> --yes        # PERMANENT, bypasses trash
python scripts/drive_cli.py empty-trash --yes
python scripts/drive_cli.py revisions list|keep|delete|download|restore <fileId> [<revId>]
python scripts/drive_cli.py drives list|create --name X|delete --drive-id Y --yes
python scripts/drive_cli.py shortcut <nome> <targetId> [--parent <folderId>]
```
`delete`, `empty-trash`, and `drives delete` are irreversible: ask the user to confirm before running them.

Drive **labels** (`modifyLabels`) are unavailable: they require the `drive.labels` scope, which is not approved. Add it with `add_scope.py` if needed.

Each command starts with a **coverage check**: the CLI queries the live MCP (`tools/list`), compares its available tools against the baseline at `~/.config/gclientid/drive-cli-mcp-baseline.json` (TTL 24h, `--recheck` to force a check), and warns if a new tool appears to cover the operation. This prevents the CLI from outliving the reason it exists. `--skip-check` skips it in non-interactive scripts.
