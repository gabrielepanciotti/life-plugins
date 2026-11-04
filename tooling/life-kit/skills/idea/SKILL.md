---
name: idea
description: "Capture a fact, decision, idea, or constraint in the Life tree's brain: write it immediately without asking when it has happened (a decision was made, a task was completed or defined, or a supplier said something in an email or call); queue it for the digest if it is still a fresh idea. Use when the user writes '/idea', 'note this down', 'this belongs in the brain', 'remember that', 'record this decision', or whenever a project fact obviously belongs in the brain."
---

# Capture a fact in the brain

Index: Setup · Direct or queue? · Write directly · Queue · What not to do

## Setup — where the brain lives

The brain belongs to the **Life tree** (`life-<id>`), not to the node where the
session is open. From Life's `packages/shared` directory, using its venv (`.venv`, Python 3.13):

```bash
python -m suite_core.nodes brain-root --node <node-folder>   # <instance>/brain
python -m suite_core.nodes framework-root                    # the Life folder
```

When `LIFE_INSTANCE_DIR=<instance>` is set, `brain-root` works without `--node`.
If `--node` says “no instance for this node”, no tree can be determined with
certainty: write the fact in the node's `brain/` anyway, and say so. In the rest of
this skill, `$BRAIN` means that path and `$FW` means the Life folder.

## Direct or queue?

- **Direct** when the fact *has happened*: decided, done, or said by someone (a decision
  made, a task completed or defined, a supplier email or call, a deadline, who does what).
  Write it immediately, **without asking**: the question “Should I write this?” goes
  unanswered and the fact never makes it in. The brain is internal and easy to correct;
  confirmation is needed only for things sent to other people.
- **Queue** when it is a fresh idea that may change during the session: the safety net,
  processed by the digest and reviewed with `idee-revisione`.

## Write directly

1. Choose the fact (or facts) from the same moment: one fact, one note.
2. Write to the tree's brain (`$BRAIN`):
   - a dated project fact → a new note
     `nodes/<node>/facts/<YYYY-MM-DD>-<slug>.md` (`<node>` = ID in the Life graph, that is the
     `slug` in `node.config`), with front matter:
     `title`, `summary`, `tags: [facts, type/fact, <node>]`, `status: active`,
     `created`, `updated`, plus two fields that must not be confused:
     `source:` = where the information came from (`supplier email 2026-09-17`,
     `call with the client`, `session on node X`), and `project:` = which
     project it concerns, using its key (separate multiple keys with commas). The
     `<node>` folder follows `project:`, never the source.
     Body: what, why, what changes, who.
   - a fact that corrects the project page (`projects/<x>.md`) → update it and
     advance `updated`; if it contradicts the page, it is a **revocation**: follow
     `idee-revisione`.
3. Commit and push the tree repo (`git -C <instance>`), then report in one line:
   `🧠 Written: <path>`. Do not also add it to the queue.

The dated name distinguishes a new fact from a reference note. For the rest of the
format (hub, wikilinks, length), follow the `brain-note` skill from the `suite-tooling` plugin.

## Queue

Append an entry to the queue of the Life tree linked to this node
(`<instance>/.brain-inbox/ideas.jsonl`), or to the node's local queue if no tree is
linked (contract: `docs/brain-coda-istanza.md` in Life). Life's digest
(`scripts/brain/digest.py --instance <instance>`) processes it by proposing notes
in `<instance>/brain/sources/_proposte-<date>.md`, which the user approves with `idee-revisione`.

1. Take the text. With `/idea <text>`, use that. With `/idea` alone, use the last thing
   said that is worth keeping and say so in one line: “I'll note this: ‘…’”. Then apply
   “Direct or queue?”: if it is a decision already made or a fact that happened (“we don't
   use Redis”), it belongs under Write directly, not here.
2. If context needed to understand it six months from now is missing (which project it
   concerns, which alternative was chosen over), add that context to the end of the text,
   in square brackets: the digest works from this text, not the conversation.
3. Append the entry using this skill's script, `scripts/accoda.sh` (in this skill's
   directory; that is the directory from which you read this file):
   `bash <skill-folder>/scripts/accoda.sh "<text>"`. It prints `in coda per <path>`: the
   path shows which queue received it (Life tree or node). It finds the tree and Life
   automatically; if it cannot, set `LIFE_INSTANCE_DIR` and/or `LIFE_FRAMEWORK_DIR`.
4. Confirm in one line: `📌 Queued for the brain of <instance>: “<first 60 characters>…”`
   (if the command says no tree is linked: `📌 Queued in the node: “…”`).

The queue does not clear itself: the digest must be run (manually or as a scheduled
activity for the user) with `python scripts/brain/digest.py --instance <instance>` from
`$FW`, using Life's venv. Without it, ideas remain queued and never reach review.

## What not to do

- Do not ask for confirmation before writing to the brain or adding to the queue: that
  takes longer than capturing the fact, and a wrong note can be corrected (revoked with
  `idee-revisione`).
- Do not write the same thing twice in one turn, either directly or in the queue.
- Do not write directly for an idea that is still tentative: queue it.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py idea` and apply what it prints (it may print nothing).
