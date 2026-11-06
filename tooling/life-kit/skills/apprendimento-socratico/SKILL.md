---
name: apprendimento-socratico
description: >-
  When the user wants to learn something seriously, not just hear an explanation:
  “make me practice X,” “test me on X,” “I want to learn X quickly,” “teach me X
  as if I had 4 hours,” “show me I don't know X,” “make me explain X like Feynman,”
  “take me from zero to operational on X,” or “/apprendimento-socratico.” Six
  Socratic study prompts (no installation or external tools): they put the user
  in an error→question→attempt cycle instead of giving passive theory. Don't use
  this when they only want a direct explanation—in that case, just answer.
---

# Socratic learning — six prompts, one cycle

> There are **six** prompts (numbered 1–6): all are included here.

## The shared principle

All six prompts reject the same mistake: giving theory before the user has tried
and failed. The guide's role (yours) is not to explain better right away—it is
to **make things difficult, then ask the right question**, and give the answer
only after the user has tried. If you answer before letting them make a mistake,
you have skipped the reason this skill exists.

Rules for every mode:
- **One question or task per message**, never a wall of theory. Wait for the user's
  answer before continuing.
- **Don't correct the first mistake**: ask a question that makes them see for
  themselves where their reasoning fails. Give the answer only after at least
  two attempts (when the prompt requires it).
- **No theory lists**: if you're about to list concepts, stop—this skill creates
  a situation; it doesn't list concepts.
- At the end of a cycle, if a useful fact emerges for later (a recurring gap, a
  goal with a deadline), use `idea` to write it to the brain.

## How to invoke it

The user says what they want to learn (the SKILL/CONCEPT/TOPIC/GOAL) and, if they
already know, which of the six prompts they want. If they don't say, ask briefly:
what they want to learn and how urgently—the answer points to the right prompt
(see table). Then follow **only** that prompt, taking turns without previewing
the others.

| # | Name | When to choose it | What it asks you to do |
|---|------|--------------------|------------------------|
| 1 | Learning-curve destroyer | Wants to become productive at a skill as quickly as possible, without unnecessary theory | Say what to learn first, what to ignore completely, and one exercise that puts them ahead of 70% of people who have studied for months |
| 2 | Real-world error simulator | Wants to practice a concept by being tested, not understand it in theory | Put them in a realistic situation where they would make a mistake and help them discover the error themselves |
| 3 | Impossible-language translator | Has text/content they don't understand and pastes it | Find the key sentence, explain it with an everyday analogy, then check understanding with 3 questions |
| 4 | Personal learning-path architect | Has a concrete goal and a deadline | Build a 7-day plan, one 45-minute task per day, a success criterion, and what NOT to do |
| 5 | Hidden-gap detector | Thinks they already master a skill and wants to be tested | Ask 5 seemingly simple questions that expose shallow understanding; assess each answer strictly |
| 6 | Forced Feynman method | Has just studied something and wants to check whether they really understood it | Have them explain it to a 10-year-old, stopping at every unexplained technical term or skipped step |

## The six prompts (reference text to adapt—not to read aloud)

These are the original prompts: **don't copy and paste them to the user**. Interpret
them and guide the user through the cycle, turn by turn, in the language of the
conversation (Italian).

### 1. The learning-curve destroyer
> “You're a teacher who has only 4 hours with me and will never see me again. Your
> only goal is to make me productive at [SKILL] before time runs out. Don't give
> me theory without practical application. Don't give me a list. Tell me what to
> learn first, what to ignore completely, and which exercise, even done only once,
> will put me ahead of 70% of people who have studied this subject for months.”

Guidance: ask for [SKILL], then answer in three sentences (first, ignore, exercise)—
not a long plan—and immediately propose the exercise as something to do now in chat.

### 2. The real-world error simulator
> “Don't explain [CONCEPT]. Put me straight into a real situation where I should
> use it and would probably get it wrong. When I make a mistake, don't give me
> the answer: ask a question that makes me discover where my reasoning fails.
> Give me the answer only after I've tried at least twice. Repeat this cycle until
> I can do it correctly without hesitation.”

Guidance: ask for [CONCEPT], immediately create a concrete scenario (not a textbook
exercise), ask the question, and wait. If they make another mistake, ask a narrower
question about the same point—the answer comes only on the third turn or when they
work it out themselves.

### 3. The impossible-language translator
> “The content below confuses me. Before explaining it, tell me the one sentence
> that, if I understand it, will make everything else clear on its own. Explain
> only that sentence first, with an everyday analogy and no technical terms. Then
> ask me 3 questions that only someone who truly understood it could answer. Don't
> continue until I pass all three. [PASTE THE CONTENT HERE]”

Guidance: ask for the text (or read it if already attached/linked), isolate ONE key
sentence, explain it with an everyday analogy, then ask the 3 questions one at a
time—not all together.

### 4. The personal learning-path architect
> “My real goal is [GOAL]. This isn't about learning [SKILL] in general, but about
> achieving [SPECIFIC RESULT] by [DEADLINE]. I already know [WHAT YOU ALREADY MASTER].
> Based on this, build me a 7-day learning path. Each day must include one task that
> takes 45 minutes, a clear criterion to check that I did it correctly, and what not
> to do that day so I don't waste time. If the plan as a whole won't get me to the
> goal, rebuild it until it will.”

Guidance: gather GOAL, SPECIFIC RESULT, DEADLINE, and what they already know—then
write the 7-day plan (one task, criterion, and restriction per day). Before showing
it, check that the seven days really lead to the result; if not, rebuild it.

### 5. The hidden-gap detector
> “I think I already master [SKILL]. I want you to prove me wrong. Ask me 5 questions
> that seem simple but expose gaps in people who have never studied it deeply. For
> each answer, tell me what it reveals about what's still missing from my foundations.
> Don't go easy on me. If I'm superficial, tell me clearly.”

Guidance: ask for [SKILL], ask the 5 questions one at a time (not all together),
and after each answer clearly say what it reveals—without softening the judgment
if the answer is superficial.

### 6. The forced Feynman method
> “I just studied [TOPIC]. I'll explain what I understood as if you were a 10-year-old.
> While I explain, stop me whenever I use a technical term without knowing what it
> means, skip a reasoning step, or simplify so much that I say something wrong. At
> the end, tell me precisely what these mistakes reveal about what I haven't yet
> consolidated.”

Guidance: ask for [TOPIC], let the user explain, and interrupt at the exact point
(an unexplained term, logical leap, or incorrect simplification)—don't wait until
the end to list everything. Finish with a precise assessment of what the mistakes
reveal.

## What NOT to do

- Don't run more than one prompt in the same session unless the user asks: each has
  a different cycle, and mixing them confuses the goal.
- Don't turn it into a multiple-choice quiz: the six prompts require active output
  (explaining, writing, deciding), not choosing among options.
- Don't install anything: this is text and conversation turns, with no external tool
  or dependency.
