# Operational Notes and Local Patches

Contents:
- Bugs encountered
- Local venv patches

## Bugs encountered

- **The server opens the browser on its own, and chooses the wrong one.** In stdio, `workspace-mcp` calls `webbrowser.open(auth_url)`: it opens the system default browser, signed in to different accounts. There is no flag to disable this, but `webbrowser` respects the `BROWSER` variable: set it to the CDP Chrome (`"<chrome>" --user-data-dir=<profilo> %s`) in both the auth script and the server `env` in `.mcp.json`.
- **Do not trust the “saved” state in the same tab you just edited.** An Angular save may appear successful (field populated, «Save» button active again) even though the HTTP request never started. Verify by opening a **new** tab and reading the AX tree again: this is the only proof of server-side persistence. The scripts in `scripts/` already do this.
- **Cause found once**: a cookie banner («OK, got it») at the bottom of the page covered the button «Save» and intercepted its click without an error. Fixed by patch 4 below.
- A generic **403 access_denied** on the consent screen, with the test user present, is almost always caused by one of these two things (in order of likelihood): (1) Incomplete branding for sensitive scopes (step 4 of `oauth-client.md`); (2) the test user was never actually saved (the cookie banner). Check with a hard refresh (Ctrl+Shift+R) in the Console.
- If `gclientid` stops with a `TimeoutError` during `Enabling N Google APIs`, `Configuring the OAuth app`, or `Creating the Desktop OAuth client`: rerun the same command; it is idempotent.
- The Italian Console breaks the English text selectors in `gclientid` (searches for `"Account:"` and finds `"Account: "`). Every URL `console.cloud.google.com` in the local fork has `&hl=en` forced.
- `page.click(node)` and `page.fill_text(node, ...)` from `fastcdp` require `node.backend_id` (an int), not the `AXNode`: passing the whole object gives `TypeError: Object of type AXNode is not JSON serializable`.
- `page.screenshot()` returns an IPython object `Image` (requires `pip install ipython` in the venv) with the `.data` (bytes) attribute, not a base64 string.

## Local venv patches (`~/.claude/tools/gclientid/.venv`)

These are in the files `gclientid/oauth.py` and `gclientid/projects.py` (fork of `gclientid`) and `fastcdp/core.py` (fork of `fastcdp`), under `lib/python3.13/site-packages/` on Linux or `Lib/site-packages/` on Windows. Reapply them if you recreate the venv from scratch:

1. **Force `&hl=en`** on every URL `console.cloud.google.com/...` in `oauth.py` and `projects.py`: the Italian Console breaks the English AX tree selectors.
2. **Operation timeout increased from 10 s to 30 s** in `configure_app()` (`oauth.py`): the Google Auth Platform SPA is often slower than the default.
3. **`_publish()` disabled** in `configure_app()` (commented out): publishing to production requires an Authorized domain verified through Search Console; personal or team clients can remain in Testing, which supports up to 100 test users.
4. **`fastcdp.core.Page.click()` dismisses the cookie banner before each click**: looks for a button `"OK, got it"` in the AX tree and clicks it first if present and not the target. This is the critical patch.
