---
name: gcloud-console-automation
description: "Route and automate operations in cloud consoles (Google Cloud, Firebase, Cloudflare) without asking the user to open a site and click. Includes a ‘which tool for which process’ table (official MCP, then CLI, then REST, then CDP browser) and scripts for tasks vendors block from the CLI: OAuth Client ID, consent screen, test user, sensitive scopes. Use when a project needs to connect to a Google service (Drive, Gmail, Calendar, Firebase/FCM), manage Cloudflare (tunnels, DNS, Workers, Access), or complete an OAuth login from the CLI without opening the wrong browser."
allowed-tools: Bash, Read, Write, Edit
---

# Cloud console — total automation (Google Cloud, Firebase, Cloudflare)

Never tell the user, “Go to this site and click.” At most, the user says, “I need to do this,” approves it, and the operator does it. If a console gets in the way, add the missing tool here instead of handing the task back to the user.

Index:
- When to use it
- Where do we start?
- Which tool for which process
- Rules about secrets and tokens
- MCP server: which one to use
- Copy and tick (connect a project to Google)
- Final check
- Detail files

## Needed

- `gcloud` CLI. Windows: `winget install --id Google.CloudSDK -e`. Linux: `sudo snap install google-cloud-cli --classic` (or Google's apt repo).
- The `gclientid` tool in `~/.claude/tools/gclientid/` (see Python 3.13, `.venv/bin/python` on Linux, `.venv/Scripts/python.exe` on Windows): recreate it using the commands in `references/oauth-client.md` if it is missing. After recreating it, reapply the patches in `references/note-operative.md`; they fix real bugs.
- `uv` for `workspace-mcp` (`uv tool install workspace-mcp`), Chrome for CDP profile, `firebase-tools`, `wrangler`, `cloudflared` only if the table row requires them.

## Where do we start?

- **Connect a project to a Google service with OAuth** (Client ID, consent screen, test user) → “Copy and check” below and `references/oauth-client.md`.
- **Drive, Docs, Sheets, Gmail, Calendar from one session** → `workspace-mcp`, `references/workspace-mcp.md`.
- **Firebase or Cloudflare** → the table below, without going through the Client ID.
- **An OAuth login from the CLI** (`gcloud auth login`, `firebase login`) that needs completing → section “1-bis” of `references/oauth-client.md`.
- **Something breaks in half** → `references/note-operative.md`.

## Which tool for which process

The hierarchy: **Official MCP, then Official CLI, then REST API, then CDP Browser Automation**. You only go down a level when the one above does not cover the operation.

| Process | Tool | Level |
|---|---|---|
| GCP project, API enable, IAM | `gcloud` CLI | 2 |
| **OAuth Client ID** (Web/Desktop) | `gclientid` + Chrome CDP | 4 |
| **Consent screen** Branding/Audience/Data Access | script in `~/.claude/tools/gclientid/scripts/` | 4 |
| OAuth login of a CLI (`gcloud`, `firebase`, ADC) | `complete_consent.py` | 4 |
| Drive/Docs/Sheets/Gmail/Calendar | MCP `workspace-mcp` | 1 |
| Drive: final delete, trash, revisions, shared drives, shortcuts, quota | `drive_cli.py` | 2 |
| Firebase: app, **SHA Android**, SDK config, FCM, Crashlytics, Remote Config, Auth users, deploy | MCP `firebase-tools mcp --only <gruppi>` | 1 |
| Firebase: **App Distribution**, declarative auth, Crashlytics web onboarding | `firebase` CLI (not in MCP) | 2 |
| Firebase: extra OAuth providers, App Check, Spark→Blaze billing | REST (`identitytoolkit`, `firebaseappcheck`, `cloudbilling`) | 3 |
| Firebase: **upload APNs key `.p8`** for FCM iOS | console-only, no API exists | 4 |
| Cloudflare: DNS, zones, Workers, R2, KV, Access, WAF, ingress tunnel | Remote MCP `https://mcp.cloudflare.com/mcp` (Full API v4) | 1 |
| Cloudflare: create/manage tunnels, tunnel DNS routes, daemons | `cloudflared` CLI | 2 |
| Cloudflare: deploy Workers/Pages, R2, KV, secret | `wrangler` CLI | 2 |
| Cloudflare: Local copy of API (`sync`+`search` offline), JSONL export/import, `tail`, minimum scope token | `cloudflare-pp-cli` (skill `pp-cloudflare`, token from `CLOUDFLARE_API_TOKEN`) | 2 |
| Cloudflare: **first** API token | dashboard, once only (you need a token to create others) | — |

Create projects, enable APIs, and configure IAM directly with `gcloud`: it is faster and supported. Use this skill’s scripts only for OAuth and consent-screen tasks, which Google deliberately blocks from the CLI.

## Rules about secrets and tokens

- **Never pass a secret through chat or a file opened in a live session.** File-change notifications send the modified line, including the token, into the context. A “placeholder you replace” provides no protection while the session is open. Use an environment variable, or replace the line while the session is closed.
- **After creating a token, check permissions via API, not trusting the form.** The Cloudflare dashboard can crash mid-compilation and save less than it shows. A `403` on an endpoint in that group proves that the permission is not there.

## MCP server: which one to use

- **Drive, Docs, Sheets, Gmail, Calendar: `workspace-mcp` is the default.** Installation, web client and credentials are in `references/workspace-mcp.md`.
- The old method with `@modelcontextprotocol/server-gdrive` is **read only** and should not be used for new jobs. It remains described in `references/metodo-server-gdrive.md` for those who have yet to maintain it.
- **Do not install `@google-cloud/gcloud-mcp`**: it provides only one tool (`run_gcloud_command`), a CLI wrapper. It adds latency without adding capability. The same applies to the community Firebase MCPs (`@gannonh/firebase-mcp` and its fork): they offer subsets that the official MCP has superseded for over a year.
- **Firebase MCP omits capabilities without saying so.** It infers tools from `firebase.json`, enabled APIs, and discovered SDKs. In a repository without `firebase.json`, it exposes about 19 of 67 tools, making the other capabilities seem unavailable. Always pass `--only <gruppi>` (or `--tools <nomi>`) to disable auto-detection. Groups: `core` (always), `auth`, `firestore`, `storage`, `crashlytics`, `apphosting`, `realtimedatabase`, `dataconnect`, `remoteconfig`, `messaging`.

## Copy and check (link a project to Google)

For command-by-command details, see `references/oauth-client.md`. Copy the list and check off each item.

```
- [ ] 1 gcloud CLI installed and signed in
- [ ] 2 Dedicated Chrome CDP session started, user signed in to the target account (the user does this)
- [ ] 3 gclientid: project + API + OAuth app + client (pass scopes here)
- [ ] 4 Branding complete (home page, privacy policy, authorized domain)
- [ ] 5 Test user added, along with any extra scopes
- [ ] 6 workspace-mcp MCP authenticated with that client
- [ ] 7 Verify: OAuth login succeeded and the client exists
```

If step 7 returns `403 access_denied`, revisit step 4 (incomplete Branding), then step 5 (the test user may not have been saved). If `gclientid` stops with a `TimeoutError`, rerun the same command from step 3; it is idempotent.

## Final check

Before stating a fact, verify it: the client responds with `redirect_uri_mismatch` (it exists), not `deleted_client` or `invalid_client` (see the command in the “Read before changing” section of `references/oauth-client.md`); rereading the consent screen with `dump_page.py` in a new tab shows the expected Branding, test user, and scopes. If anything does not add up, repeat the step that produced it. Finish only when OAuth login actually works with the target account.

## Detail file

- `references/oauth-client.md` — why you need `gclientid`, installation, end-to-end procedure, OAuth login from CLI, reading the consent screen, script inventory
- `references/workspace-mcp.md` — `workspace-mcp` (default) and `drive_cli.py`
- `references/metodo-server-gdrive.md` — the old, read-only method
- `references/note-operative.md` — real bugs encountered and local patches
- `references/storia.md` — dates and checks
- `evals/prove.md` — three test requests. Try them without and with the skill, in a new conversation.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py gcloud-console-automation` and apply what it prints (it may print nothing).
