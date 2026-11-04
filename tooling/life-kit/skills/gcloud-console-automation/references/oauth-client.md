# OAuth Client ID and Consent Screen — End-to-End Procedure

Contents:
- Why a dedicated tool is needed
- The gclientid tool
- 1. gcloud CLI
- 1-bis. OAuth CLI login with the right browser
- 2. Dedicated Chrome (CDP)
- 3. Provisioning
- 4. Branding
- 5. Test user and scopes
- Read before changing
- Script inventory

## Why a dedicated tool is needed

`gcloud` covers project creation, IAM, and service enablement. **Does not cover** (a deliberate Google choice to prevent phishing):
- creating an OAuth Client ID (Web or Desktop);
- configuring the consent screen (Branding/Audience/Data Access).

That page (`console.cloud.google.com/apis/credentials/oauthclient`) is available only in the UI. `gcloud alpha iam oauth-clients` is something else (Workforce Identity Federation) and is unrelated.

## The tool: `gclientid`

Path: `~/.claude/tools/gclientid/.venv` (Python 3.13, `gclientid` + `fastcdp` installed with pip and locally patched; see `note-operative.md`). Repo originale: [AnswerDotAI/gclientid](https://github.com/AnswerDotAI/gclientid). It controls a dedicated Chrome through the Chrome DevTools Protocol, signed in to the target Google account, and navigates the Console with an accessibility-tree walker (no fragile CSS selectors).

If the venv does not exist on this device, recreate it.

Linux:
```bash
mkdir -p ~/.claude/tools/gclientid && cd ~/.claude/tools/gclientid
python3.13 -m venv .venv
.venv/bin/python -m pip install gclientid requests ipython
```
Windows:
```bash
mkdir -p ~/.claude/tools/gclientid && cd ~/.claude/tools/gclientid
py -3.13 -m venv .venv
.venv/Scripts/python.exe -m pip install gclientid requests ipython
```
Then reapply the patches from `note-operative.md`. In the examples below `.venv/bin/python` is for Linux; on Windows use `.venv/Scripts/python.exe` and `.venv/Scripts/gclientid.exe`.

## 1. Per-device prerequisite: `gcloud` CLI

Windows:
```bash
winget install --id Google.CloudSDK -e --accept-package-agreements --accept-source-agreements
```
Linux: `sudo snap install google-cloud-cli --classic`.

## 1-bis. Any OAuth CLI login, without clicking or using the wrong browser

This applies to `gcloud auth login`, `gcloud auth application-default login`, `firebase login` and any tool that prints an authorization URL. The tool’s loopback listener captures the redirect from whichever browser opens it, so you only need to open the consent flow in CDP Chrome.

Linux:
```bash
export BROWSER='google-chrome --user-data-dir=$HOME/.cache/fastcdp/cdp-chrome %s'
gcloud auth login --quiet > /tmp/auth.log 2>&1 &
until grep -qo "https://accounts.google.com/o/oauth2/auth[^ ]*" /tmp/auth.log; do sleep 2; done
.venv/bin/python scripts/complete_consent.py \
  "$(grep -o 'https://accounts.google.com/o/oauth2/auth[^ ]*' /tmp/auth.log | head -1)" \
  --account <<account>@gmail.com>
```
Windows: use the same sequence, with
`BROWSER='"%ProgramFiles%/Google/Chrome/Application/chrome.exe" --user-data-dir=<home>/.cache/fastcdp/cdp-chrome %s'` and `.venv/Scripts/python.exe`.

`--account` is needed when the flow does not include a `login_hint` (`gcloud` does not) and Google displays the account picker. **Do not use `--no-launch-browser`**: it switches to the copy-and-paste code flow and waits indefinitely for stdin.

## 2. Dedicated Chrome (CDP, separate profile, English forced)

```bash
python ~/.claude/tools/gclientid/scripts/launch_cdp_chrome.py
```
**Stop and have the user sign in** to the target Google account in that window (do not delegate 2FA or passwords). Ask for confirmation before continuing.

## 3. Provisioning: project + APIs + OAuth app + client

```bash
cd ~/.claude/tools/gclientid
.venv/bin/gclientid --project <project-id> --desktop --accept-terms --cdp-chrome \
  --scope https://www.googleapis.com/auth/drive.readonly \
  --scope <altro-scope-sensibile-se-serve>
```
- `--project <project-id>`: creates it if it does not exist (the ID is unique across Google: use a slug such as `<nodo>-drive-mcp`).
- `--desktop`: creates a “Desktop app.” Omit it for a Web client (required by `workspace-mcp`; see `workspace-mcp.md`).
- `--accept-terms`: automatically accepts the API terms.
- `--scope`: repeat it for each sensitive or restricted scope the connector will use (Drive, Gneverl, Calendar). This avoids the manual step in section 5.
- Output: `~/.config/gclientid/oauth-client-desktop.json` (client_id/secret) and `~/.config/gclientid/config.ini`.
- **Idempotent**: if interrupted (it happens), rerun the same command to resume where it left off.

The app remains in **Testing** (no publishing or Google verification): up to 100 test users, suitable for personal or team use.

## 4. Required Branding fields (in addition to those marked `*`)

Google shows “Publishing status: Testing” as ready, but if **any** sensitive scope is declared, the consent screen remains “incomplete” until these are also filled in: Home page, Privacy policy, and an Authorized domain, even if the form does not mark them with an asterisk. Without this step, login fails with a **generic 403 access_denied** that does not name the cause.
```bash
.venv/bin/python scripts/fill_branding.py \
  --project <project-id> \
  --home "https://github.com/<org>/<repo>" \
  --privacy "https://github.com/<org>/<repo>" \
  --domain "github.com"
```
If the project has no public domain, its GitHub repository URL works as a placeholder (in Testing mode, Google does not check whether it responds).

## 5. Test user and additional scopes

```bash
.venv/bin/python scripts/add_test_user.py --project <project-id> --email <<account>@gmail.com>
.venv/bin/python scripts/add_scope.py --project <project-id> --scope <scope-url>
```
The first is needed if you did not pass it in step 3 or need to add it again; the second adds a scope to an already provisioned project.

## Read before changing

For a **personal project (without an organization)** there is no consent screen read API: `iap.googleapis.com/v1/projects/N/brands` returns *Project must belong to an organization*. Read it from the console in read-only mode:
```bash
.venv/bin/python scripts/dump_page.py "https://console.cloud.google.com/auth/clients?project=<id>&hl=en"   # client list
  # .../auth/audience  -> publishing status + test users
  # .../auth/scopes    -> declared sensitive scopes
```

**A client ID in the config does not mean it exists.** A deleted OAuth client remains in every config and produces no readable error: Android Credential Manager fails with a `unknownError` with no details. Verify it in one step, without the console:
```bash
curl -sL "https://accounts.google.com/o/oauth2/v2/auth?client_id=<ID>&redirect_uri=http%3A%2F%2Flocalhost%3A1&response_type=code&scope=openid" -o /dev/null -w "%{url_effective}\n"
# deleted_client -> deleted · invalid_client -> never existed · redirect_uri_mismatch -> exists
```

**Do not put internal tool clients in the product project.** Sensitive scopes for a Drive/Docs client remain attached to the shared consent screen, and publishing the app (to remove the 100-test-user limit) triggers Google verification. Use one GCP project for the product and another for tooling.

## Inventario script (`~/.claude/tools/gclientid/scripts/`)

Run the scripts rather than reading them: `--help` lists the arguments.

| Script | What it does |
|---|---|
| `launch_cdp_chrome.py` | Starts/restarts dedicated CDP Chrome (port 9223, isolated profile, `--lang=en-US`) |
| `dump_page.py` | Reads a Console page via AX tree (read-only): publishing status, test user, scope, client list |
| `complete_consent.py` | Completes OAuth consent in that Chrome using its URL (`--account` for the account picker) |
| `fill_branding.py` | Fills in Home page / Privacy policy / Authorized domain and verifies persistence |
| `add_test_user.py` | Adds a test user in Audience (idempotent, with verification) |
| `add_scope.py` | Declares sensitive/restricted scopes in Data Access (with verification) |
| `workspace_mcp_auth.py` | Generates `workspace-mcp` credentials by driving an MCP stdio session |
| `drive_cli.py` | Remaining Drive operations outside MCP (permanent delete, trash, revisions, shared drives, shortcuts, quota), with a coverage check at startup |
