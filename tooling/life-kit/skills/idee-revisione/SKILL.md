---
name: idee-revisione
description: "Use when reviewing the brain proposals produced by the Life digest — approving, rejecting or editing them before they become notes. Triggers \"/ideas-review\", \"review proposals\", \"what needs to be approved for brain\"."
---

# Review of brain proposals

The digest proposes items; you decide. This skill guides that decision and writes only
what you approve.

The queue and digest are **per Life tree**, not per node (contract:
`docs/brain-coda-istanza.md` in Life): review from the tree, even if the session is open on a node. Each block names the node in its path (`## [ ] NUOVA — Home/brain/casa/lampadine.md`).

## Setup — find trees and frameworks

With the venv of Life (`<Life>/packages/shared/.venv`, Python 3.13), from `packages/shared`:

```bash
python -m suite_core.nodes framework-root                    # FW: Life framework directory
python -m suite_core.nodes brain-root --node <current-node> # <instance>/brain
```

`ISTANZA` is the folder above `brain` (when `LIFE_INSTANCE_DIR` is set, it is the instance directory;
`brain-root` without `--node` returns only the root). Do not rely on a manually entered path. If either command
does not respond, tell the user and stop.

- If `--node` reports «no instance for this node», no Life tree is connected: review
the node-local proposals (`brain/sources/_proposte-*.md`) and tell the user.
- Otherwise, work with `$ISTANZA/brain/sources/_proposte-*.md`.
`$FW` (the engine) lives in the **framework** and is never copied into a tree. Run the tools below
(`scripts.brain.*`) from `$FW` using Life’s virtual environment.
- If no `_proposte-*.md` file exists, the digest has not been run (or found no items in the queue): `python scripts/brain/digest.py --instance "$ISTANZA"` from `$FW`.

## Procedure

1. Find open files: `ls "$ISTANZA/brain/sources"/_proposte-*.md`. Start with the oldest.
**Filter by project** ("only those on the Payments node") according to **what the
proposal is about**, not which words it contains: a note about Invoices that mentions
Payments is about Invoices. When in doubt, ask.

**Knot, two meanings — keep them separate.** Where information *arrived*
(a call, session, or email) does not determine where the note belongs: write it
**in the project node the proposal concerns**, with `fonte:` and `progetto:` in the frontmatter. If
the digest proposes the source node for a fact about another project, correct it.

**`SCARTA … già coperto` items are not shown.** Check them yourself: consult the cited notes
and, if available, the original source (the node’s session notes), and verify that
**every** fact about the candidate is present. If everything is covered, simply check the box. If anything is missing,
show the user **only what is missing**, one line per item.

**Before showing a block, verify the facts** against the code, emails, and notes:
a digest is based on old material, and circumstances may have changed since (for example, a
vendor response or a commit). Also verify that wikilinks exist. Present the
**corrected** proposal to the user and explain what you changed.

2. For each block `## [ ] <ESITO> — <Nodo>/<path>`, show it to the user **one at a time**,
in compact form: outcome, node, path, key, and the two lines `indice` and `semantica`.
If the note exceeds 20 lines, summarize it and offer to open it instead of pasting it in full.
The block path is **relative to the node it names**, resolved from the node folder
(`brain-root --node` confirms this; it is usually a sibling of the tree, `$SRV_ROOT/<Project>`) — never
a subfolder of the tree. A block about the tree itself uses its name
(`life-<id>/brain/…`) and resolves to `$ISTANZA`.
3. Ask the user to choose: **approve** · **edit** (the user specifies the correction;
you rewrite the block) · **discard** (one-line reason).
4. For approved items, always work in the node named by the block (not in the tree, unless
the block itself names the tree):
- `NUOVA` → write the note to the indicated path, with the proposed frontmatter and the fields
`chiave` and `status: active`. Add an entry to the folder’s «Domain Notes» list
in `_index.md`.
- `AGGIORNA` → apply the patch to the existing note and update `updated`.
- `REVOCA` → apply the revocation **with the tool; never move files manually**
(from `$FW`, using Life’s virtual environment):

     ```bash
     python -c "
     import pathlib
     from datetime import date
     from scripts.brain.revoke import revoca
     print(revoca(pathlib.Path('<note-node>'), pathlib.Path('<note-to-revoke>'),
                  sostituita_da='<replacement-note-slug>',
                  contraddizione='<what it said, what it says now, and the supporting evidence>',
                  oggi=date.today()))
     "
     ```

Then **remove the revoked note’s line from the «Domain Notes» list
in the folder’s `_index.md`**. This is not a minor detail: `_index.md`
is published and indexed, so a pointer left there continues to present
as current a note that no longer exists in the corpus — the opposite of
what revocation is meant to achieve. If a new note replaces it, the new note
takes the old one’s place.

Then write the new note as for `NUOVA`. The old one goes into
`brain/_revocate/` (inside the note node) and **must not be deleted**: it is needed
for auditing and possible re-promotion. The `contraddizione` field is not
bureaucracy; it is the only record that will explain six months from now why the owner changed their mind.

5. Check the checkbox of the machined block: from `## [ ]` to `## [x]`, with queued
` (approvata)` or ` (scartata: <motivo>)`.

6. **Promote** anything other nodes also need: 2–4 lines plus the wikilink, **never the
note body**. Skip this step when the node **is the tree itself**.

   ```bash
   python -c "
   import pathlib
   from scripts.brain.promote import promuovi
   promuovi(pathlib.Path('$ISTANZA'), '<Nodo>',
            [('[[<slug-nota>]]', '<distillato in due righe>')])
   "
   ```

The first argument is the **tree directory** (`$ISTANZA`).

For a **revocation**, call `spromuovi` with the same wikilink instead of `promuovi`;
otherwise the tree becomes an archive of things that are no longer true, linked as if
they were still authoritative.

   ```bash
   python -c "
   import pathlib
   from scripts.brain.promote import spromuovi
   spromuovi(pathlib.Path('$ISTANZA'), '<Nodo>', '[[<slug-nota>]]')
   "
   ```

7. **Run the linter** and report the result in two lines, in the note node (not in the tree,
unless the note belongs to the tree itself), from `$FW`:

   ```bash
   python -m scripts.brain.lint_brain --nodo "<note-node-path>"
   ```

Fix any **blocking problems introduced by this review** now — for example, a link to
a note you did not write or two active notes with the same key. Existing
problems are outside this session’s scope; just report them.

8. End with a three-line summary: number approved, rejected, and revoked.

## Rules

- **One note per concept.** If a proposal contains two concepts, split it before writing.
- **Do not mix types**: a `type/how-to` note contains no architectural explanations.
If the digest combines them, separate them into two notes.
- **When classification is uncertain, choose the most restrictive level.** A note should never become
more visible by accident.
- **The rejection rate is a fact, not a failure.** If you reject almost everything, the digest
is proposing too much. If you never discard anything, you may be approving without review — or it may be
losing ideas. Tell the user if you notice this.
- Do not auto-commit notes; follow the node’s normal workflow.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py idee-revisione` and apply the tree-specific appendix it prints. The appendix may be empty.
