# Revoke and promote — commands

Index: Revoke · Promote · Withdraw a promotion

Run these after the `SKILL.md` setup (which assigns `LW` and `ISTANZA` and exports
both). Replace the placeholders inside `<...>`. Use the commands as written;
change only the placeholder contents.

If `$LW` is not set, the script exits with “LW is not set: repeat the setup.”

## Revoke

```bash
python3 - <<'PY'
import os, sys, pathlib
from datetime import date
lw = os.environ.get("LW") or sys.exit("LW is not set: repeat the setup in SKILL.md")
sys.path.insert(0, lw)
from scripts.brain.revoke import revoca
print(revoca(pathlib.Path("<note-node>"), pathlib.Path("<note-to-revoke>"),
             sostituita_da="<new-note-slug>",
             contraddizione="<what it said, what it says now, and the supporting evidence>",
             oggi=date.today()))
PY
```

## Promote

The first argument is the instance directory (`$ISTANZA`), not a fixed path.

```bash
python3 - <<'PY'
import os, sys, pathlib
lw = os.environ.get("LW") or sys.exit("LW is not set: repeat the setup in SKILL.md")
sys.path.insert(0, lw)
from scripts.brain.promote import promuovi
promuovi(pathlib.Path(os.environ["ISTANZA"]), "<Node>",
         [("[[<note-slug>]]", "<two-line distillation>")])
PY
```

## Withdraw a promotion

When revoking a note, call `spromuovi` with the same wikilink. Without this step,
the instance becomes an archive of claims that are no longer true, with a link
that still appears authoritative.

```bash
python3 - <<'PY'
import os, sys, pathlib
lw = os.environ.get("LW") or sys.exit("LW is not set: repeat the setup in SKILL.md")
sys.path.insert(0, lw)
from scripts.brain.promote import spromuovi
spromuovi(pathlib.Path(os.environ["ISTANZA"]), "<Node>", "[[<note-slug>]]")
PY
```
