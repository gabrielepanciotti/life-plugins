---
name: idea
description: "Record a fact, decision, idea, or constraint in the Life tree brain. Record confirmed events immediately; queue ideas that are still tentative. Use when the user invokes `/idea`, asks to remember something, or a project fact clearly belongs in the brain."
---

# Record a fact in the brain

Index: Setup · Direct or queued? · Direct writing · Queue · What not to do

## Setup — where the brain is

The brain belongs to the **Life tree** (`life-<id>`), not the node where the session is running. From Life's `packages/shared` folder, with its venv (`.venv`, Python 3.13):

```bash
python -m suite_core.nodes brain-root --node <node-directory> # <instance>/brain
python -m suite_core.nodes framework-root                       # Life framework directory
```

With `LIFE_INSTANCE_DIR=<instance>` set, `brain-root` (without `--node`) responds on its own.
If `--node` says «no instance for this node», no tree can be determined with
certainty, record the fact in the node `brain/` and tell the user. In this skill, `$BRAIN` means that path and `$FW` means the Life framework directory.

## Direct or queued?

- **Direct** when an event *has happened*: a decision, completed or defined task, someone
said something, a supplier email or call, a deadline, or an assignment. Record it immediately,
**without asking**. The brain is internal and can be corrected; confirmation is needed only for
content sent to other people.
- **Queue** when an idea is tentative and may change during the session. The digest processes
queued ideas, which are reviewed with `idee-revisione`.

## Direct writing

1. Choose the fact (or facts) of the same moment: a fact, a note.
2. Write in the brain of the tree (`$BRAIN`):
- a dated fact about a project → new note
`nodes/<node>/facts/<YYYY-MM-DD>-<slug>.md` (`<node>` is the node ID in the Life graph,
that is, the `slug` in `node.config`), with frontmatter:
`title`, `summary`, `tags: [facts, type/fact, <node>]`, `status: active`,
`created`, `updated`, and two distinct fields:
`fonte:` = where the information came from (`supplier email 2026-09-17`,
`customer call`, `session on node X`); `progetto:` = the project being discussed,
identified by its key (separate multiple keys with commas). The `<node>` folder follows
`progetto:`, never the source.
Body: what happened, why, what changes, and who is responsible.
- A fact that corrects a project file (`projects/<x>.md`) → update it and refresh
`updated`. If it contradicts existing information, treat it as a **revocation** and follow `idee-revisione`.
3. Commit and push the tree repository (`git -C <instance>`), then report:
`🧠 Recorded: <path>`. Do not also add the same fact to the queue.

The date distinguishes a new fact from a reference note. For the rest of the format
(hub, wikilinks, and length), follow the `brain-note` skill in the `suite-tooling` plugin.

## Queue

Appends an entry to the tail of the Life tree connected to this node
(`<instance>/.brain-inbox/ideas.jsonl`), or to the node's local queue if no tree is
connected (contract: `docs/brain-coda-istanza.md` in Life). Life's digest
(`scripts/brain/digest.py --instance <instance>`) disposes of it by proposing the notes
in `<instance>/brain/sources/_proposte-<data>.md`, and the user approves them with `idee-revisione`.

1. Get the text. With `/idea <text>` it is that. With only `/idea` use the last thing
dictated as worth keeping and repeat it in one line: “I captured this: …”. Then apply
«Direct or queue?»: if it is a decision made or an event that happened ("we don't use Redis")
it goes to Direct Writing, not here.
2. If the context that makes it understandable is missing in six months (which project is it talking about,
against which alternative was chosen), add it at the end of the text, in brackets
squares: the digest works on this text, not on the conversation.
3. Append the entry with the skill script, `scripts/accoda.sh` (in this folder
skills; its folder is the one from which you read this file):
`bash <skill-directory>/scripts/accoda.sh "<text>"`. Print `queued for <path>`: the
path tells which queue (tree Life or node) received it. Find tree and Life yourself;
if it fails, set `LIFE_INSTANCE_DIR` and/or `LIFE_FRAMEWORK_DIR`.
4. Confirm in one line: `📌 Queued for the <instance> brain: “<first 60 characters>…”`
(if no tree is connected, use: `📌 Queued in the node: “…”`).

The queue does not empty itself: the digest must be launched (by hand or from a scheduled task
of the user) with `python scripts/brain/digest.py --instance <instance>` from `$FW`, with the
venv of Life. Without it, ideas sit in the queue and never make it to review.

## What not to do

- Do not ask for confirmation before writing in the brain or before queuing: it costs more than
capture itself, and a wrong note is corrected (revoked with `idee-revisione`).
- Do not write the same thing twice in the same shift, neither live nor in the queue.
- Don't write direct writing for a still tentative idea: it goes to the back of the queue.
## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py idea` and apply the tree-specific appendix it prints. The appendix may be empty.
