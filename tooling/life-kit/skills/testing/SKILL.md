---
name: testing
description: Write and run tests: unit, integration, and end-to-end with Playwright, and guide TDD for bugs. Use when the user asks to write tests, says “test it” or “do TDD,” or when dev-workflow requires verification of critical logic.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Testing

## Required tools

Everything must run inside the project's `.venv`, never global Python (`.venv/bin/python` on Linux,
`.venv/Scripts/python` on Windows). If a package is missing:

- pytest: `.venv/bin/pip install pytest` (Windows: `.venv/Scripts/pip install pytest`)
- Local Playwright: `.venv/bin/pip install playwright` and then `.venv/bin/playwright install chromium`
- Frontend: `cd frontend && npm install` (use Vitest or Jest already in `package.json`)

## Choose which test to write

| Situation | Test |
|---|---|
| Calculation logic (margins, prices, conversions) | unit test, always |
| New API endpoint | at least one success case and one error case |
| Bug to fix | first write a test that reproduces it and fails (TDD), then fix it |
| Critical frontend | end-to-end with Playwright |
| Trivial getter or setter | no test |

One test per behavior, not per implementation. Mock only external dependencies,
not internal logic. The name should describe the behavior: `test_margine_include_iva`, not
`test_1`.

## Run tests

From the project root:

```bash
cd backend && .venv/bin/python -m pytest tests/ -v --tb=short   # (Windows: .venv/Scripts/python)
cd frontend && npm test
```

If `backend/.venv` does not exist, the venv is in the project root: use
`../.venv/bin/python`. File structure: `tests/test_<module>.py`.

Example of an integration test for an endpoint (adapt fixtures and paths to the project):

```python
def test_create_offerta(client, auth_headers):
    response = client.post("/api/offerte", json={...}, headers=auth_headers)
    assert response.status_code == 201
    assert "id" in response.json()
```

## End-to-end with Playwright

**With the MCP server** (if connected): `mcp__plugin_playwright_playwright__browser_navigate`,
`..._browser_snapshot`, `..._browser_fill_form`, `..._browser_click`,
`..._browser_take_screenshot`. If the page requires a login, the user handles it: do not enter
credentials on their behalf.

**Local, without MCP**: the toolkit is in this skill's `playwright/` folder (a copy of an
Anthropic skill; do not modify it); `<skill>` below is its path. Run scripts with `--help` before reading them.

- `with_server.py` — starts and stops servers (backend and frontend) around your script.
- `examples/element_discovery.py` — lists buttons, links, and page fields.
- `examples/console_logging.py` — captures browser logs.
- `examples/static_html_automation.py` — automation on static HTML via `file://`.

```bash
.venv/bin/python <skill>/playwright/with_server.py \
  --server "cd backend && ../.venv/bin/python main.py" --port 8000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- .venv/bin/python my_automation.py
```

After `page.goto(...)`, wait for `page.wait_for_load_state('networkidle')` before inspecting the
DOM: without it, tests on dynamic apps are unstable.

## TDD for a bug

1. Write a test that reproduces the bug and verify that it fails for the right reason.
2. Fix it.
3. Run the same test again: it must pass, along with all the others.
4. Commit only the files touched: `git add -- <file>`, then `git commit -m "fix: description" -m "Closes #N"`.

## Copy and check off

- [ ] The new test fails without the change (or reproduces the bug).
- [ ] The new test passes with the change.
- [ ] The entire suite passes. If another test breaks, return to the change, not the test.
- [ ] No test depends on production data or secrets.

Finish only when the full suite passes.

## Related files

- `playwright/` — local toolkit copied from Anthropic (do not modify).
