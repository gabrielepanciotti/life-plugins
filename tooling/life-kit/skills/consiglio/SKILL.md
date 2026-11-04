---
name: consiglio
description: "Have an important decision examined by five independent advisers, with anonymous peer review and a verdict from a Chair. Use it when reversing a decision would be costly (pricing, leaving a customer or supplier, changing positioning, investing in something new, an architecture that will last for years), or when the user asks '/consiglio', 'convene the council', 'I want an unsycophantic opinion', or 'tell me if I am wrong'. Never use it for yes/no questions or questions that take two seconds to answer."
allowed-tools: Agent, Read, Glob, Grep
---

# Council — five viewpoints and a verdict

Index: Honest limitation · When not to use it · Step 0 cost · Step 1 neutral question · Step 2 advisers · Step 3 Chair · Step 4 what to return · History in `references/storia.md`

The problem: a model tends to agree with the person asking. Present an idea as good and it
builds arguments in favor; present it as bad and it builds arguments against (Anthropic,
*Towards Understanding Sycophancy in Language Models*, 2023, arXiv:2310.13548). A blunt
opinion on an important decision is therefore of little value. The council separates the
perspectives into different contexts so none inherits the framing of the question.

## Honest limitation (state in the verdict)

The five advisers are **the same model** in different roles: they share the same biases.
The council helps surface perspectives that might otherwise be missed; it does not replace
the advice of people. If the decision involves real money or people, the verdict is input
for the user, not the decision itself.

## When NOT to use it

- a yes/no question, personal taste, or a choice that can be reversed in a few minutes;
- there is already a written plan to dismantle → use the `prior-art-redteam` red team
  (GATE B): it attacks an existing plan axis by axis. The council is for **beforehand**,
  when the decision has not yet been made;
- the missing information is a verifiable fact (a number, price, or date): look up the
  fact; do not convene anyone.

If the request falls into one of these cases, say so in one line and answer directly.

## Step 0 — cost, and getting approval before starting

The full council costs **6 subagents** (5 advisers + 1 Chair), about 300–450 thousand
tokens and 3–6 minutes. That exceeds the limit of 5 subagents for one task, so **state the
estimate and wait for the user's approval**, offering the smaller version:

- **Full council** — as described below.
- **Small version** — one subagent answers in the five roles in sequence, then serves as
  Chair: about 90 thousand tokens, under a minute (see measurements in `references/storia.md`). Less independence (one context),
  but it remains outside the conversation context, which is what causes sycophancy.

Approval applies to that round only.

## Step 1 — rephrase the question neutrally

Before distributing it, rewrite the decision **without the asker's preference**:
- remove value-laden adjectives (“great idea”, “I’m not convinced”);
- present the options in parallel, with the same amount of detail;
- retain the real constraints (budget, deadlines, people involved, what is already decided).

Produce two versions:
- **Dossier**: neutral question + context + constraints. Goes to four advisers.
- **Bare question**: the decision alone in two or three lines, without context or history.
  Goes to the Outsider.

Show the neutral question to the user in one line before launching: if you have distorted
it, the whole council will answer the wrong question.

Example of a neutral rephrasing:

- User request: “I’m thinking of raising the price of the Dashboard service by 15% for
  long-standing customers. It seems fair given how much work goes into it, but I don’t know
  whether I might lose some of them. What do you think?”
- Neutral question (dossier): “Decision: keep the price of the Dashboard service for
  long-standing customers as it is, or raise it by 15%. Context: there are N long-standing
  customers, the current price is X, and the last adjustment was in year Y. Constraints: no
  contracts expire before Z; no known competing alternative.”
- Bare question (Outsider): “A supplier must decide whether to raise prices by 15% for
  customers who have been with them for years, or leave them unchanged. What would you
  consider?”

“It seems fair,” “how much work goes into it,” and “might lose” have been removed: they are
the asker's framing, and an adviser who inherits it responds to the preference, not the
decision. Both options receive equal weight and the facts (N, X, Y, Z) remain.

Check before launch: the dossier contains no sentence revealing which way the asker leans,
and both options get equal space. If it does, rewrite and check again.

## Step 2 — the five advisers, in parallel

Make five calls to the `Agent` tool **in the same message** (so they run in parallel), with
`subagent_type: "general-purpose"`, `model: "sonnet"` (the advisers execute against a given
brief; the judgment remains with the Chair, using the session's model).
Never use `fork`: it inherits the conversation,
which is exactly the sycophancy we want to avoid.

Each prompt contains the role, the material (dossier or bare question), and the response
format. No adviser knows about the others.

| Role | Receives | Task |
|---|---|---|
| **Contrarian** | dossier | Find flaws, weak points, and ways it could go wrong. Do not balance the case: that is your job. |
| **First principles** | dossier | What problem are we really trying to solve? Is this the right question? Is there an option the dossier does not list? |
| **Expansionist** | dossier | Overlooked advantages and opportunities: what is gained if it goes well, and what becomes possible afterward? |
| **Outsider** | bare question only | Without context, notice the obvious that insiders may no longer see. Also say what you would need to know. |
| **Executor** | dossier | Focus only on what happens next: the first three concrete steps, who takes them, how long each takes in minutes/hours/days, and where execution may get stuck. |

Adviser response format: use exactly this and include it in each prompt (maximum 250 words),
because the Chair compares the answers point by point:

```
Position: <one sentence>
Arguments (no more than three):
1. <argument> — supporting fact: <fact>
2. ...
What would change my mind: <one sentence>
```

## Step 3 — anonymous review and verdict (Chair)

A sixth `Agent`, with `subagent_type: "general-purpose"`, **without `model`** (inherits the
session model: synthesis and judgment use the best available level).

Give it the dossier and the five responses **labeled A–E in random order**, without the role
names: it should judge the arguments, not who made them. The Chair:

1. **Peer review**: for each response, identify its strongest and weakest point; then rank
   A–E by the quality of the arguments (not by agreement with the Chair).
2. **Verdict, under 250 words**:
   - recommended decision (or “do not decide yet; first, X is needed”);
   - the strongest reason in favor;
   - the biggest risk and how to spot it coming;
   - the first concrete step, with an estimate in minutes/hours;
   - one line stating the honest limitation (same model, five roles).

## Step 4 — what to return to the user

Only these items, in this order (use this exact structure):
1. the neutral question considered (one line);
2. the Chair's complete verdict;
3. one line per adviser giving their position, now with the role name;
4. the strongest remaining disagreement, if the Chair dismissed it.

No play-by-play, and no full adviser responses unless requested.

If the decision is made, it is a decision: record it in the brain using the “Direct writing”
procedure in the `idea` skill.

Finish only when the response contains all four items from Step 4 and the verdict states the
honest limitation.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py consiglio` and apply what it prints (it may print nothing).
