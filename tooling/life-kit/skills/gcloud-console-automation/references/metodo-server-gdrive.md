# Old method: `@modelcontextprotocol/server-gdrive` (read only)

Index:
- When needed
- Authenticate the server
- Register it in the project

## When needed

Not the default method: for new jobs use `workspace-mcp` (`workspace-mcp.md`). This server exposes search and reading only. Only keep it if a project already uses it and cannot be migrated.

## Authenticate the server

You need a **Desktop** client (`gclientid --desktop`, see `oauth-client.md`).
```bash
GDRIVE_OAUTH_PATH="<path>/oauth-client-desktop.json" \
GDRIVE_CREDENTIALS_PATH="<path>/<progetto>-gdrive-credentials.json" \
npx -y @modelcontextprotocol/server-gdrive auth
```
Opens the **system default browser** (not necessarily the right one) and listens on a random local port. If it opens in the wrong browser or account:
1. Find the process and port. Linux: `pgrep -af 'server-gdrive.*auth'` then `ss -ltnp | grep <PID>`. Windows:
```bash
   powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*server-gdrive*auth*' }"
   netstat -ano | grep <PID>
   ```
2. Build the authorization URL by hand (client_id from JSON, port found above, redirect_uri always `http://localhost:<porta>/`, root path and not `/oauth2callback`, for «installed» clients of `@google-cloud/local-auth`):
```
   https://accounts.google.com/o/oauth2/v2/auth?client_id=<CLIENT_ID>&redirect_uri=http%3A%2F%2Flocalhost%3A<PORTA>%2F&response_type=code&scope=<SCOPE_URLENCODED>&access_type=offline
   ```
3. Paste it into the right browser and account. The listening server catches the redirect whatever browser opens it.

## Register it in the project

`.mcp.json` of the project (does not touch the global connector):
```json
{
  "mcpServers": {
    "google-drive-<nodo>": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gdrive"],
      "env": {
        "GDRIVE_OAUTH_PATH": "<path>/oauth-client-desktop.json",
        "GDRIVE_CREDENTIALS_PATH": "<path>/<progetto>-gdrive-credentials.json"
      }
    }
  }
}
```
Absolute paths are only allowed in a `.mcp.json` ignored by git: check that it is, otherwise isolate the two variables in an unversioned local file.
