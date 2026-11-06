#!/usr/bin/env python3
"""Summary and liveness check of a do-everything session (skill do-everything, «Resume»).

    stato.py [REPO] [--aggiorna]

Reads REPO/.claude/do-everything/state.json. For every issue `running`, an agent is
considered alive when its branch got a commit, or a file in its worktree changed, in the
last 45 minutes (the same threshold as live sessions). A branch on the remote proves
nothing. Without --aggiorna it only prints; with it, dead agents become `failed` with
error «interrotto» and `stats` is recomputed and written back.

Exit 0 with "nessuna sessione" when there is no state file.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

SOGLIA = 45 * 60


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def _worktrees(repo: Path) -> dict[str, Path]:
    out, path = {}, None
    for line in _git(repo, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            path = Path(line[9:])
        elif line.startswith("branch ") and path:
            out[line[7:].removeprefix("refs/heads/")] = path
    return out


def _vivo(repo: Path, branch: str | None, worktrees: dict[str, Path], now: float) -> bool:
    if not branch:
        return False
    ts = _git(repo, "log", "-1", "--format=%ct", branch)
    if ts and now - int(ts) < SOGLIA:
        return True
    wt = worktrees.get(branch)
    if wt and wt.is_dir():
        for f in wt.rglob("*"):
            if ".git" in f.parts:
                continue
            try:
                if f.is_file() and now - f.stat().st_mtime < SOGLIA:
                    return True
            except OSError:
                continue
    return False


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", default=".", type=Path)
    ap.add_argument("--aggiorna", action="store_true")
    args = ap.parse_args()
    repo = args.repo.resolve()
    state_file = repo / ".claude" / "do-everything" / "state.json"
    if not state_file.is_file():
        print("nessuna sessione do-everything in questo progetto: /do-everything per avviarne una")
        return
    state = json.loads(state_file.read_text(encoding="utf-8"))
    issues = state.get("issues", {})
    macro = state.get("macro_agents", {})
    worktrees = _worktrees(repo)
    now = time.time()

    interrotti = []
    for iid, it in issues.items():
        if it.get("status") != "running":
            continue
        branch = it.get("branch") or macro.get(it.get("category", ""), {}).get("worktree_branch")
        if not _vivo(repo, branch, worktrees, now):
            interrotti.append(iid)
            if args.aggiorna:
                it["status"], it["error"] = "failed", "interrotto"

    by = lambda s: [i for i in issues.values() if i.get("status") == s]  # noqa: E731
    stats = {
        "total": len(issues),
        "completed": len(by("completed")),
        "running": len(by("running")),
        "blocked_on_questions": len(by("questions")),
        "failed": len(by("failed")),
    }
    if args.aggiorna:
        state["stats"] = stats
        state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fmt = lambda xs: ", ".join(f"#{i['id']}" + (f" ({i['branch']})" if i.get("branch") else "") for i in xs) or "—"  # noqa: E731
    domande = [q for q in state.get("question_queue", []) if not q.get("answered")]
    print(f"Progresso do-everything — sessione {state.get('session_id', '?')} (avviata {state.get('created_at', '?')})")
    print(f"Completati: {stats['completed']}/{stats['total']}")
    print(f"In esecuzione: {fmt(by('running'))}")
    print(f"In coda (domande): {fmt(by('questions'))}")
    print(f"Bloccati (dipendenze): {fmt(by('blocked'))}")
    print(f"Falliti: " + (", ".join(f"#{i['id']} ({i.get('error') or '?'})" for i in by('failed')) or "—"))
    print(f"In attesa di avvio: {fmt(by('pending') + by('ready'))}")
    print(f"Prossima domanda: " + (f"#{domande[0]['issue_id']} — {domande[0]['question']}" if domande else "—"))
    if interrotti:
        verbo = "segnati failed" if args.aggiorna else "da segnare failed (rilancia con --aggiorna)"
        print(f"Agenti interrotti (niente commit né file da 45 min): {', '.join('#' + i for i in interrotti)} — {verbo}")


if __name__ == "__main__":
    main()
