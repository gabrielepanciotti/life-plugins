---
name: idee-revisione
description: Use when reviewing brain proposals produced by a Life digest — approve, reject, or edit them before they become notes. Triggers "/idee-revisione", "review the proposals", "what needs approval for the brain".
---

# Review brain proposals

The digest proposes; you decide. This skill guides the decision and writes only
what you approve.

The queue and digest are **per Life tree**, not per node (contract:
`docs/brain-coda-istanza.md` in Life): review from the tree, regardless of which
node the session is open in, and each block names the node before the path
(`## [ ] NEW — Home/brain/casa/lampadine.md`).

## Setup — find the tree and framework

Using Life's venv (`<Life>/packages/shared/.venv`, Python 3.13), from `packages/shared`:

```bash
python -m suite_core.nodes framework-root                    # FW: the Life folder
python -m suite_core.nodes brain-root --node <nodo-corrente> # <istanza>/brain
```

`ISTANZA` is the folder above that `brain` directory (if `LIFE_INSTANCE_DIR` is set, it
is that directory, and `brain-root` responds on its own without `--node`). This skill
does not start from a manually entered path: if either command does not respond, tell
the user and stop.

- If `--node` says “no instance for this node”, no Life tree is connected: review
  the node's local proposals (`brain/sources/_proposte-*.md`) and tell the user.
- Otherwise, everything else works in `$ISTANZA/brain/sources/_proposte-*.md`.
  `$FW` (the engine) lives in the **framework**, never copied into a tree. Run the
  tools below (`scripts.brain.*`) from `$FW` using Life's venv.
- If no `_proposte-*.md` file exists, the digest has not been run (or found nothing
  in the queue): run `python scripts/brain/digest.py --instance "$ISTANZA"` from `$FW`.

## Procedure

1. Find the open files: `ls "$ISTANZA/brain/sources"/_proposte-*.md`. Work from the oldest.
   **Filtering by project** (“only the ones about the Payments node”) means based on
   **what the proposal is about**, not which word it contains: a note about Invoices
   that mentions Payments is about Invoices. Ask if unsure.

   **Node has two meanings — keep them separate.** Where the information came from
   (a call, session, email) does not determine where the note belongs: write the note
   **in the node for the project it discusses**, with `fonte:` and `progetto:` in the
   frontmatter. If the digest proposes the source node for a fact about another project,
   correct it.

   **Do not show `DISCARD … already covered` items.** Verify them yourself: open the
   cited notes and, if it exists, the original record (session notes in the node) and
   check that **every** fact in the candidate is present. If everything is there, check
   it off. If something is missing, show the user **only what is missing**, one fact per line.

   **Verify facts before showing a block**, against the code, emails, and notes: a
   digest may write from an old record, and reality may have changed since then (a
   supplier response, a commit). Also check that wikilinks exist. Present the proposal
   **already corrected**, and say what you corrected.

2. For each block `## [ ] <OUTCOME> — <Node>/<path>`, show it to the user **one at a time**,
   compactly: outcome, node, path, key, and the two lines `indice` and `semantica`.
   Do not paste the entire note if it exceeds 20 lines: summarize it and offer to open it.
   The block's path is **relative to the named node**, resolved as the node folder
   (`brain-root --node` confirms it; usually a sibling of the tree, `<srv>/<Nodo>`) —
   never a subfolder of the tree. A block about the tree itself uses its name
   (`life-<id>/brain/…`) and resolves inside `$ISTANZA`.
3. Ask for a decision: **approve** · **edit** (the user dictates the correction,
   you rewrite the block) · **discard** (reason in one line).
4. For approved items, always work in the node named in the block (not the tree, unless
   the block names the tree itself):
   - `NUOVA` → write the note at the specified path, with the proposed frontmatter and
     the `chiave` and `status: active` fields. Add its entry to the folder's `_index.md`
     “Domain notes” list.
   - `AGGIORNA` → apply the patch to the existing note and update `updated`.
   - `REVOCA` → apply the revocation **with the tool, never by moving files manually**
     (from `$FW`, using Life's venv):

     ```bash
     python -c "
     import pathlib
     from datetime import date
     from scripts.brain.revoke import revoca
     print(revoca(pathlib.Path('<nodo-della-nota>'), pathlib.Path('<nota-da-revocare>'),
                  sostituita_da='<slug-nota-nuova>',
                  contraddizione='<cosa diceva, cosa dice ora, su quale evidenza>',
                  oggi=date.today()))
     "
     ```

     Then **remove the revoked note's line from the “Domain notes” list in its
     folder's `_index.md`**. This is not a matter of tidiness: `_index.md` is published
     and indexed, so a pointer left there continues to present as current a note that
     the corpus no longer considers valid — the opposite of what revocation is meant
     to achieve. If a new note replaces it, put the new entry in place of the old one.

     Then write the new note, as for `NUOVA`. The old note ends up in
     `brain/_revocate/` (inside the note's node) and **must not be deleted**: it is
     needed for audits and possible re-promotion. The `contraddizione` field is not
     bureaucracy — in six months, it will be the only thing explaining why the brain
     changed its mind.

5. Check off the block: change `## [ ]` to `## [x]`, and append
   ` (approved)` or ` (discarded: <reason>)`.

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

   For a **revocation**, call `spromuovi` with the same wikilink instead of `promuovi`:
   otherwise the tree becomes an archive of things that are no longer true, with a link
   that still appears authoritative.

   ```bash
   python -c "
   import pathlib
   from scripts.brain.promote import spromuovi
   spromuovi(pathlib.Path('$ISTANZA'), '<Nodo>', '[[<slug-nota>]]')
   "
   ```

7. **Pass lint** and report the result in two lines, in the note's node (not the tree,
   unless the note belongs to the tree itself), from `$FW`:

   ```bash
   python -m scripts.brain.lint_brain --nodo "<path-del-nodo-della-nota>"
   ```

   Immediately resolve blocking issues **introduced by this review** — a link to a note
   you did not write, or two active notes with the same key. Pre-existing issues are not
   this session's responsibility: just report them.

8. Final summary in three lines: how many approved, discarded, and revoked.

## Rules

- **One note per concept.** If a proposal contains two, split it before writing.
- **Do not mix types**: a `type/how-to` note must not contain architectural explanations.
  If the digest mixed them, separate them and write two notes.
- **When unsure about classification, choose the more restricted level.** A note must
  never become more visible by accident.
- **The discard rate is data, not failure.** If you discard almost everything, the
  digest is proposing too much; if you never discard anything, you are approving
  without looking — or it is missing ideas. Tell the user when you notice this.
- Do not automatically commit notes: leave that to the node's normal workflow.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py idee-revisione` and apply what it prints
(it may print nothing).
