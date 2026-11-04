---
name: consiglio
description: "Have five independent advisers examine an important decision, with anonymous peer review and a verdict from a Chair. Use it when reversing a decision would be costly (prices, leaving a customer or supplier, changing positioning, investing in something new, an architecture that will last for years), or when the user asks '/consiglio', 'convene the council', 'I want an unflattering opinion', or 'tell me if I am wrong'. Never use it for yes/no questions or questions that take two seconds."
allowed-tools: Agent, Read, Glob, Grep
---

# Council — five perspectives and a verdict

Index: Honest limitation · When not to use it · Step 0 cost · Step 1 neutral question · Step 2 advisers · Step 3 Chair · Step 4 what to return · History in `references/storia.md`

The problem: a model tends to agree with the person asking. Present an idea as good and it builds arguments in favor; present it as bad and it builds arguments against it (Anthropic, *Towards Understanding Sycophancy in Language Models*, 2023, arXiv:2310.13548). A snap opinion on an important decision is therefore of little value. The council separates perspectives into different contexts, so none inherits the framing of the question.

## Honest limitation (state this in the verdict)

The five advisers are **the same model** with different roles: they share the same biases. The council helps surface perspectives that might otherwise be missed; it does not replace advice from people. If the decision involves real money or people, the verdict is an input for the user, not the decision itself.

## When NOT to use it

- A yes/no question, personal taste, or a choice that can be reversed in a few minutes;
- There is already a written plan to tear apart → use the `prior-art-redteam` red team
  (GATE B): it attacks an existing plan axis by axis. The council is for **before** the decision
  has been made;
- The missing information is a verifiable fact (a number, price, or date): find the
  fact; do not convene anyone.

If the request falls into one of these cases, say so in one line and answer directly.

## Step 0 — cost, and approval before starting

The full council costs **6 subagents** (5 advisers + 1 Chair), about 300–450 thousand
tokens and 3–6 minutes. This exceeds 5 subagents for a single task, so **state the estimate
and wait for the user's approval**, offering the smaller version:

- **Full council** — as described below.
- **Small version** — one subagent responds in the five roles in sequence and then acts as
  Chair: about 90 thousand tokens, under a minute (measured in `references/storia.md`). Less
  independence (a single context), but it remains outside the conversation context, which is
  what causes the sycophancy.

Approval applies to that run only.

## Step 1 — reframe the question neutrally

Before distributing it, rewrite the decision **without the asker's preference**:
- remove value judgments ("great idea", "I'm not convinced");
- present the options in parallel, with the same amount of detail;
- keep the real constraints (budget, deadlines, people involved, what has already been decided).

Produce two versions:
- **Dossier**: neutral question + context + constraints. Goes to four advisers.
- **Bare question**: the decision alone in two or three lines, without context or history. Goes
  to the Outsider.

Show the user the neutral question in one line before launching: if you got it wrong, the whole
council will answer the wrong question.

Example of a neutral reframe:

- User request: "I'm thinking of raising the price of the product-a service by 15% for
  long-standing customers. It seems fair given how much work goes into it, but I don't know if
  I risk losing any of them. What do you think?"
- Neutral question (dossier): "Decision: keep the price of the product-a service for
  long-standing customers as it is, or raise it by 15%. Context: there are N long-standing
  customers, the current price is X, and the last adjustment was in Y. Constraints: no
  contracts expire before Z; no known competing alternative."
- Bare question (Outsider): "A supplier must decide whether to raise the price by 15% for
  people who have been customers for years, or leave it unchanged. What would you consider?"

"It seems fair", "how much work goes into it", and "risk" have been removed: they are the
asker's framing, and an adviser who inherits it answers the preference, not the decision. The
two options have equal weight, and the facts (N, X, Y, Z) remain.

Check before launch: the dossier contains no sentence revealing which way the asker leans, and
the options take up the same space. If it does, rewrite and check again.

## Step 2 — the five advisers, in parallel

Make five calls to the `Agent` tool **in the same message** (so they run in parallel), with
`subagent_type: "general-purpose"` and `model: "sonnet"` (the advisers execute against a given
prompt; judgment remains with the Chair, using the session's model). Never use `fork`: it
inherits the conversation, which is exactly the sycophancy to avoid.

Each prompt contains the role, the material (dossier or bare question), and the response format.
No adviser knows about the others.

| Role | Receives | Task |
|---|---|---|
| **Contrarian** | dossier | Look for flaws, weak points, and ways this could go wrong. Do not balance the view: that is the job. |
| **First principles** | dossier | What problem are we really trying to solve? Is this the right question? Is there an option the dossier does not list? |
| **Expansionist** | dossier | Overlooked benefits and opportunities: what is gained if it goes well, and what becomes possible next? |
| **Outsider** | bare question only | Without context, notice the obvious that insiders no longer see. Also say what information you would need. |
| **Executor** | dossier | Focus only on what happens next: the first three concrete steps, who takes them, how long they take in minutes/hours/days, and where things might get stuck. |

Adviser response format: use exactly this and include it in each prompt (at most 250 words),
because the Chair compares the answers item by item:

```
Position: <one sentence>
Arguments (at most three):
1. <argument> — supporting fact: <fact>
2. ...
What would change my mind: <one sentence>
```

## Step 3 — anonymous review and verdict (Chair)

A sixth `Agent`, `subagent_type: "general-purpose"`, **with no `model`** (inherits the session
model: synthesis and judgment use the best available level).

Give it the dossier and the five answers **labeled A–E in random order**, without the role
names: it should judge the arguments, not who made them. The Chair:

1. **Peer review**: for each answer, identify its strongest and weakest point; then rank A–E
   by the quality of the arguments (not by agreement with the Chair).
2. **Verdict, under 250 words**:
   - recommended decision (or “do not decide yet; first, X is needed”);
   - the strongest reason in favor;
   - the biggest risk, and how to spot it coming;
   - the first concrete step, with an estimate in minutes/hours;
   - one line on the honest limitation (same model, five roles).

## Step 4 — what to return to the user

Only the following, in this order (use this schema as is):
1. the neutral question considered (one line);
2. the Chair's complete verdict;
3. one line per adviser with their position, now labeled with the role name;
4. the strongest disagreement that remains, if the Chair dismissed it.

No play-by-play, and no full adviser responses unless requested.

If a decision is made, it is a decision: record it in the brain using the "Direct writing"
procedure in the `idea` skill.

Finish only when the response contains all four items from step 4 and the verdict states the
honest limitation.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py consiglio` and apply what it prints (it may print nothing).
