#!/usr/bin/env python3
"""Store task reports in the Life tree brain and publish the generated note.

The skill writes the report to
`.claude/closures/YYYY-MM-DD-<slug>.md`; this module copies it into the versioned
brain, refreshes the brain index, commits the note, and pushes it. Standard
library only.

Exit codes:
  0 - success, or the note was not stored (the `brain: ...` line explains why;
      the task work remains in the project repository)
  1 - the report file cannot be read

The brain and framework are located through `brain-root` and `framework-root`.
"""

import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)


def _git(repo, *args, timeout=120):
    """Runs git in `repo` and returns (rc, output). Never raises."""
    try:
        esito = subprocess.run(
            ["git", "-C", repo, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return esito.returncode, (esito.stdout + esito.stderr).strip()
    except Exception as e:  # git missing, timeout, disk full
        return 1, repr(e)


def _radice_repo(cwd):
    rc, out = _git(cwd, "rev-parse", "--show-toplevel")
    return out if rc == 0 and out else cwd


def _radice_nodo(cwd):
    """Return the node root, which differs from the current root in a worktree.

    `--show-toplevel` in a linked worktree returns the worktree directory, whose
    basename is the task name. Deriving the slug from it would store the note
    under a fabricated node. `--git-common-dir` always points to the main
    checkout's `.git` directory.
    """
    rc, out = _git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")
    comune = out.strip() if rc == 0 else ""
    # `--path-format` was added in Git 2.31; older versions return an error.
    if comune and os.path.isabs(comune) and os.path.basename(comune) == ".git":
        principale = os.path.dirname(comune)
        if os.path.isdir(principale):
            return principale
    return _radice_repo(cwd)


def _slug_nodo(cwd):
    """Return `slug` from node.config, or the lowercase directory name.

    Both are resolved from the **node** root (see `_radice_nodo`). Strip a
    leading dot because a hidden directory is not a brain node.
    """
    radice = _radice_nodo(cwd)
    try:
        with open(os.path.join(radice, "node.config"), encoding="utf-8") as fh:
            slug = json.load(fh).get("slug")
        if slug:
            return str(slug)
    except Exception:
        logger.debug("ignored exception in %s", "_slug_nodo", exc_info=True)
        pass
    return os.path.basename(radice.rstrip("/\\")).lower().lstrip(".")


def _id_nodo(cwd):
    """Return `taxonomy.id` from node.config (the graph key), or None."""
    try:
        with open(os.path.join(_radice_nodo(cwd), "node.config"), encoding="utf-8") as fh:
            valore = (json.load(fh).get("taxonomy") or {}).get("id")
        return str(valore) if valore else None
    except Exception:
        logger.debug("ignored exception in %s", "_id_nodo", exc_info=True)
        return None


# --- Find framework and brain without device configuration ----------


def _framework_shared(radice_nodo):
    """Return the framework's `<Life>/packages/shared` directory, or None.

    Use `LIFE_FRAMEWORK_DIR` when set; otherwise search parent directories for
    a sibling `Life` directory.
    """
    candidati = []
    if os.environ.get("LIFE_FRAMEWORK_DIR"):
        candidati.append(os.environ["LIFE_FRAMEWORK_DIR"])
    corrente = os.path.abspath(radice_nodo)
    while True:
        genitore = os.path.dirname(corrente)
        if genitore == corrente:
            break
        candidati.append(os.path.join(genitore, "Life"))
        corrente = genitore
    for radice in candidati:
        if os.path.isdir(os.path.join(radice, "packages", "shared", "suite_core")):
            return os.path.join(radice, "packages", "shared")
    return None


def _framework_root(radice_nodo):
    condivisi = _framework_shared(radice_nodo)
    return os.path.dirname(os.path.dirname(condivisi)) if condivisi else None


def _python_framework(condivisi):
    """Return the first interpreter that can import suite_core (framework venv, then current)."""
    ambiente = dict(os.environ, PYTHONPATH=condivisi)
    candidati = [
        os.path.join(condivisi, ".venv", *parti)
        for parti in (("Scripts", "python.exe"), ("bin", "python"))
    ] + [sys.executable]
    for py in candidati:
        if not py or not os.path.isfile(py):
            continue
        try:
            prova = subprocess.run(
                [py, "-c", "import suite_core"],
                env=ambiente,
                capture_output=True,
                timeout=60,
            )
        except Exception:
            logger.debug("ignored exception in %s", "_python_framework", exc_info=True)
            continue
        if prova.returncode == 0:
            return py, ambiente
    return None, ambiente


def _brain_root_cli(radice_nodo):
    """Run the framework's `brain-root --node <root>` command, or return None."""
    condivisi = _framework_shared(radice_nodo)
    if not condivisi:
        return None
    py, ambiente = _python_framework(condivisi)
    if not py:
        return None
    try:
        esito = subprocess.run(
            [py, "-m", "suite_core.nodes", "brain-root", "--node", radice_nodo],
            env=ambiente,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception:
        logger.debug("ignored exception in %s", "_brain_root_cli", exc_info=True)
        return None
    percorso = esito.stdout.strip()
    return percorso if esito.returncode == 0 and percorso else None


def _brain_istanza(radice_nodo):
    """Return the brain for the instance that contains the node.

    Check these sources from most explicit to most derived:

    1. `LIFE_INSTANCE_DIR`, the canonical instance selector;
    2. a sibling `life-*/brain` found while walking up from the node root. If
       multiple instances share a bucket, the result is ambiguous and lookup
       continues to step 3;
    3. the framework's `python -m suite_core.nodes brain-root --node <root>`.

    If no source resolves the brain, return None and report that the note was
    not stored.
    """
    esplicito = os.environ.get("LIFE_INSTANCE_DIR")
    if esplicito:
        candidato = os.path.join(esplicito, "brain")
        if os.path.isdir(candidato):
            return candidato

    corrente = os.path.abspath(radice_nodo)
    while True:
        genitore = os.path.dirname(corrente)
        if genitore == corrente:  # filesystem root
            break
        istanze = [
            p
            for p in sorted(glob.glob(os.path.join(genitore, "life-*", "brain")))
            if os.path.isdir(p)
        ]
        if len(istanze) == 1:
            return istanze[0]
        if istanze:  # more than one: ambiguous, do not guess
            break
        corrente = genitore

    return _brain_root_cli(radice_nodo)


def _nodi_noti(brain, radice_nodo=None):
    """Return known slugs where a closure can be stored without inventing a node.

    The sources are existing directories in the brain's `nodi/`, the instance
    graph beside the brain, and the Life framework graph. Falling back to a
    directory basename would invent nodes and make their notes hard to find.
    """
    noti = set()
    try:
        noti.update(
            d
            for d in os.listdir(os.path.join(brain, "nodi"))
            if os.path.isdir(os.path.join(brain, "nodi", d))
        )
    except OSError:
        logger.debug("ignored exception in %s", "_nodi_noti", exc_info=True)
        pass
    grafi = [os.path.join(os.path.dirname(brain.rstrip("/\\")), "life.graph.json")]
    radice = _framework_root(radice_nodo) if radice_nodo else None
    radice = radice or os.environ.get("LIFE_FRAMEWORK_DIR")
    if radice:
        dati = os.path.join(radice, "shell", "src", "data")
        grafi += [
            os.path.join(dati, "life.graph.default.json"),
            os.path.join(dati, "life.graph.json"),
        ]
    for grafo in grafi:
        try:
            with open(grafo, encoding="utf-8") as fh:
                nodi = json.load(fh).get("nodes", {})
        except Exception:
            logger.debug("ignored exception in %s", "_nodi_noti", exc_info=True)
            continue
        if isinstance(nodi, dict):
            noti.update(nodi)
        else:
            noti.update(n.get("id") for n in nodi if isinstance(n, dict))
    noti.discard(None)
    return noti


def _etichetta_issue(radice, resoconto, esplicita=None, percorso_resoconto=None):
    """Return the closed issue number, or a short label when there is none.

    Accept only an **explicit closing reference** (`Closes #N`) in the report:
    reports may mention issues they do not close, and recent commits in a shared
    repository may belong to anyone. Otherwise use the report filename
    (`YYYY-MM-DD-<slug>.md` -> `<slug>`). The label becomes the brain filename,
    so choosing the wrong issue would make the note hard to find.
    """
    if esplicita:
        return str(esplicita).lstrip("#")
    chiude = r"(?:[Cc]loses|[Ff]ixes|[Rr]esolves|[Cc]hiude) #(\d+)"
    trovato = re.search(chiude, resoconto)
    if trovato:
        return trovato.group(1)
    if percorso_resoconto:
        nome = os.path.splitext(os.path.basename(percorso_resoconto))[0]
        nome = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", nome)
        if nome and nome not in ("chiusura", "chiusure"):
            return nome
    return "chiusura"


def _frontmatter(testo, slug, etichetta, oggi):
    """Build frontmatter that makes the closure a brain note.

    The brain is a corpus: lint requires title/summary/tags/status/created/
    updated on every `.md` in `nodi/`. Do not set `classification` here; it is
    inherited from `brain/nodi/_index.md`.
    """
    righe = [r.rstrip() for r in testo.splitlines()]

    titolo = next((r[2:].strip() for r in righe if r.startswith("# ")), "")
    if not titolo:
        titolo = f"Closure {slug} #{etichetta}"

    # Search the summary by BLOCKS, not lines: a wrapped paragraph has the
    # marker only on its first line.
    blocchi, corrente = [], []
    for riga in righe:
        if riga.strip():
            corrente.append(riga.strip())
        elif corrente:
            blocchi.append(corrente)
            corrente = []
    if corrente:
        blocchi.append(corrente)

    sommario = ""
    for blocco in blocchi:
        if blocco[0].startswith(("#", "-", "*", "|", ">", "`", "---")):
            continue
        if re.match(r"^\d+[.)]\s", blocco[0]):  # elenco numerato
            continue
        sommario = " ".join(blocco)
        break

    # A complete sentence says more than two sentences cut in half.
    if len(sommario) > 200:
        punto = sommario.find(". ")
        sommario = (
            sommario[: punto + 1]
            if 0 < punto <= 200
            else sommario[:197].rsplit(" ", 1)[0] + "..."
        )
    if not sommario:
        sommario = f"Closure report for task #{etichetta} on node {slug}."

    # Double quotes are the only character that would break the YAML scalar.
    def _yaml(v):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'

    return "\n".join(
        [
            "---",
            f"title: {_yaml(titolo)}",
            f"summary: {_yaml(sommario)}",
            f"tags: [chiusure, type/chiusura, {slug}]",
            "status: active",
            f"created: {oggi}",
            f"updated: {oggi}",
            "---",
            "",
            "",
        ]
    )


def _rigenera_indice(brain, radice_nodo):
    """Regenerate the brain's index.md/llms.txt/showcase.md; return (success, message).

    The caller storing the note is responsible for refreshing its brain index.
    If the framework is unavailable or cannot import suite_core, keep the note;
    the next `wiki-sync` can regenerate the index, and report the condition.
    """
    condivisi = _framework_shared(radice_nodo)
    if not condivisi:
        return False, "index not regenerated (Life framework not found beside node; set LIFE_FRAMEWORK_DIR)"
    py, ambiente = _python_framework(condivisi)
    if not py:
        return False, "index not regenerated (no Python interpreter can import suite_core)"
    nodo = os.path.dirname(brain.rstrip("/\\"))
    try:
        esito = subprocess.run(
            [py, "-m", "suite_core.nodes", "wiki-sync", "--nearest", nodo],
            env=ambiente,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except Exception as e:
        return False, f"index not regenerated ({e!r})"
    if esito.returncode == 0:
        return True, "index regenerated"
    coda = (esito.stdout + esito.stderr).strip().splitlines()
    return False, f"wiki-sync failed ({coda[-1] if coda else esito.returncode})"


def porta_nel_brain(percorso_resoconto, cwd, issue=None):
    """Copy the report into the instance brain, commit it, and push it.

    Return a status line for printing. Never raise: the brain is memory and the
    closure is the task work, so the latter must not depend on the former. Any
    failure is reported.
    """
    nodo = _radice_nodo(cwd)
    brain = _brain_istanza(nodo)
    if not brain or not os.path.isdir(brain):
        return (
            f"brain: no instance brain for this node ({brain or 'missing'}); "
            "note not stored - set LIFE_INSTANCE_DIR or check "
            "`python -m suite_core.nodes brain-root`"
        )

    radice = _radice_repo(cwd)
    try:
        with open(percorso_resoconto, encoding="utf-8") as fh:
            testo = fh.read()
    except OSError as e:
        return f"brain: report cannot be read ({e}); note not stored"

    slug = _slug_nodo(radice)
    noti = _nodi_noti(brain, nodo)
    if slug not in noti:
        # The graph indexes nodes by `taxonomy.id` (camelCase); the `slug` is
        # kebab-case: a node registered only in the graph must still be found.
        id_nodo = _id_nodo(radice)
        if id_nodo in noti:
            slug = id_nodo
    if slug not in noti:
        return (
            f"brain: node \"{slug}\" is missing from both the brain and graph; "
            "note not stored - add a node.config with the correct slug to the repository"
        )
    etichetta = _etichetta_issue(radice, testo, issue, percorso_resoconto)
    oggi = datetime.date.today().isoformat()
    cartella = os.path.join(brain, "nodi", slug, "chiusure")
    destinazione = os.path.join(cartella, f"{oggi}-{etichetta}.md")
    try:
        os.makedirs(cartella, exist_ok=True)
        # The brain is append-only: a note is never overwritten.
        if os.path.exists(destinazione):
            n = 2
            while os.path.exists(os.path.join(cartella, f"{oggi}-{etichetta}-{n}.md")):
                n += 1
            destinazione = os.path.join(cartella, f"{oggi}-{etichetta}-{n}.md")
        with open(destinazione, "w", encoding="utf-8") as fh:
            if not testo.startswith("---"):
                fh.write(_frontmatter(testo, slug, etichetta, oggi))
            fh.write(testo)
    except OSError as e:
        return f"brain: copy failed ({e})"

    relativo = os.path.relpath(destinazione, brain)
    rc, _ = _git(brain, "rev-parse", "--git-dir")
    if rc != 0:
        return f"brain: copied {relativo} (not a Git repository; no commit created)"

    # Commit the index with the note so it does not become stale.
    rigenerato, nota_indice = _rigenera_indice(brain, nodo)

    # Stage only these files, never `-A`; other sessions may have brain changes.
    gestiti = ["index.md", "llms.txt", "showcase.md"] if rigenerato else []
    percorsi = [relativo] + [
        g for g in gestiti if os.path.isfile(os.path.join(brain, g))
    ]
    _git(brain, "add", "--", *percorsi)
    rc, out = _git(
        brain,
        "commit",
        "-m",
        f"chore(brain): closure {slug} #{etichetta}",
        "--",
        *percorsi,
    )
    if rc != 0 and "nothing to commit" not in out:
        return f"brain: commit failed ({out.splitlines()[-1] if out else rc})"

    rc, remoti = _git(brain, "remote")
    if rc != 0 or not remoti.strip():
        return (
            f"brain: committed {relativo}, {nota_indice} (no remote configured)"
        )

    rc, out = _git(brain, "push")
    if rc != 0:
        # The remote may have advanced; rebase and retry.
        _git(brain, "pull", "--rebase")
        rc, out = _git(brain, "push")
    if rc != 0:
        return f"brain: committed {relativo} but not pushed - run `git -C {brain} push` manually ({out.splitlines()[-1] if out else rc})"
    return f"brain: stored and pushed {relativo}, {nota_indice}"


def main():
    parser = argparse.ArgumentParser(
        description="Deposit a task report in the Life tree brain."
    )
    parser.add_argument(
        "--resoconto", required=True, help="Text file containing the report"
    )
    parser.add_argument(
        "--issue",
        help="Closed issue number (default: from `Closes #N` in the report, "
        "otherwise from the filename)",
    )
    parser.add_argument(
        "--no-brain", action="store_true", help="Do not deposit the note in the brain"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.resoconto):
        print(f"Cannot read report '{args.resoconto}'")
        return 1
    if args.no_brain:
        print("brain: skipped (--no-brain)")
        return 0
    print(porta_nel_brain(os.path.abspath(args.resoconto), os.getcwd(), args.issue))
    return 0


if __name__ == "__main__":
    sys.exit(main())
