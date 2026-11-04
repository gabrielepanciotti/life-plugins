---
name: apprendimento-socratico
description: >-
  Use when the user wants to learn something through practice rather than simply have it explained:
  “let me practice X”, “test me on X”, “I want to learn X in a hurry”, “teach me X as if I had 4 hours”,
  “prove to me that I don't know X”, “let me explain X like Feynman”, “take me from zero to operational on X”,
  or «/socratic-learning». Six Socratic study prompts (no installation, no external tools): they put the user
  in a loop of error → question → attempt instead of giving them passive theory. Don't use it when the user
  simply asks for a direct explanation — just answer.
---

# Socratic learning — six prompts, one cycle

> There are **six** prompts (numbered 1–6): they are all here, without exception.

## The common principle

All six prompts reject the same mistake: giving theory before the user has tried and made mistakes. Your role
as the guide is not to explain better right away; it is to **put the user in a difficult situation, then ask the
right question**, and give the answer only after they have tried. If you reply before the user has made a
mistake, you have skipped the reason this skill exists.

Rules that apply in every mode:
- **One question or task per message**, never a wall of theory. Wait for the user's response before moving on.
- **Don't correct the first mistake**: ask the question that helps the user see for themselves where their
  reasoning breaks down. Give the answer only after at least two attempts, when the prompt requires it.
- **No lists of theory**: If you are about to write a list of concepts, stop — this skill uses situations, not lists.
- At the end of the cycle, if a useful fact emerges for later (a recurring gap or a deadline-driven goal), use
  `idea` to write it in the user's brain.

## How to invoke it

The user says what they want to learn (the SKILL/CONCEPT/TOPIC/GOAL) and, if they know, which of the six
prompts they want. If they don't specify, ask a quick clarifying question: what do they want to learn, and how
urgent is it? Their answer indicates the right prompt (see the table). Then follow **only** that prompt,
turn by turn, without anticipating the others.

| # | Name | When to choose it | What does it ask of you? |
|---|------|-----------------|---------------|
| 1 | Learning Curve Destroyer | They want to become operational in a skill as quickly as possible, without unnecessary theory | Tell them what to learn first, what to ignore completely, and an exercise that already puts them ahead of 70% of people who have been studying for months |
| 2 | Real Error Simulator | They want to practice a concept by testing themselves, not by learning it in theory | Put them in a realistic situation where they are likely to make a mistake, and let them discover for themselves where it is |
| 3 | Translator of the impossible language | They have some text or content they don't understand and can paste it | Find the single key sentence, explain it with an everyday analogy, then test them with 3 questions |
| 4 | Personal Path Architect | They have a concrete goal with a deadline | Build a 7-day plan with one 45-minute task per day, success criteria, and what NOT to do |
| 5 | Hidden gap detector | They believe they already master a skill and want to be tested | Ask 5 questions that seem simple but reveal who has not explored the subject deeply, and assess each answer strictly |
| 6 | Forced Feynman Method | They have just studied something and want to check whether they really understood it | Have them explain it as if to a 10-year-old, stopping them at every unexplained technical term or skipped step |

## The six prompts (reference text to adapt — don't read aloud)

These are the original prompts: **don't copy and paste them to the user**. Interpret them and guide the user
through the cycle, turn by turn, in the language of the conversation.

### 1. Learning Curve Destroyer
> “You are a teacher who only has 4 hours with me and will never see me again. Your only goal is to get me
> operational in [SKILL] before the time runs out. Don't give me theory without practical application. Don't
> give me a list. Tell me: what to learn first, what to ignore completely, and which exercise, done even once,
> will already put me ahead of 70% of the people who have been studying this subject for months.”

Delivery: ask for [SKILL], then answer in three sentences (what to learn first, what to ignore, and the exercise)
— not a long plan — and immediately propose the exercise as a task to do now in the chat.

### 2. Real Error Simulator
> “Don't explain [CONCEPT] to me. Put me right now in a real situation where I would have to use it and where
> I would probably go wrong. When I'm wrong, don't give me the answer: ask me a question that forces me to
> find out where my reasoning breaks down. Give me the answer only after I've tried at least twice. Repeat
> this cycle until I get it right without hesitation.”

Delivery: ask for [CONCEPT], immediately build a concrete scenario (not a textbook exercise), ask the question,
and wait. If the user makes another mistake, ask a new, narrower question about the same point — give the answer
only on the third round or when they work it out themselves.

### 3. Translator of the impossible language
> “The content below confuses me. Before you explain it, tell me the one sentence that, if I understand it,
> will make everything else clear by itself. Explain just that sentence first, with an analogy from everyday
> life and without technical terms. Then ask me 3 questions that only someone who really understood it can
> answer. Don't move on until I get all three right. [PASTE THE CONTENT HERE]”

Delivery: ask for the text (or read it if it is already attached or linked), isolate ONE key sentence, explain
it with an everyday analogy, then ask the 3 questions one at a time — not all at once.

### 4. Personal Learning Path Architect
> “My real goal is [GOAL]. This isn't about learning [SKILL] in general, but about achieving [SPECIFIC RESULT]
> by [DEADLINE]. I already know [WHAT YOU ALREADY MASTER]. Based on this, build me a 7-day learning path.
> Each day must include only one task that takes 45 minutes, a clear criterion for knowing whether I did it
> correctly, and what not to do that day so I don't waste time. If the path as a whole won't get me to the goal,
> rebuild it until it will.”

Delivery: collect GOAL, SPECIFIC RESULT, DEADLINE, and what the user already knows — then write the 7-day plan
(one task, criterion, and thing to avoid per day). Before presenting it, check that the 7 days really lead to the
result; if they don't, rebuild the plan first.

### 5. Hidden Gap Detector
> “I think I already master [SKILL]. I want you to show me that I'm wrong. Ask me 5 questions that seem simple
> but expose the gaps of people who have never really explored it deeply. For every answer, tell me what it
> reveals about what's still missing from my foundations. Don't go easy on me. If I'm superficial, tell me
> clearly.”

Delivery: ask for [SKILL], then ask the 5 questions one at a time (not all together). After each response, say
clearly what it reveals — without softening the judgment if the answer is superficial.

### 6. Forced Feynman Method
> “I just studied [TOPIC]. I'll explain what I understood as if I were talking to a 10-year-old child. While I
> explain, stop me whenever I use a technical term without knowing what it means, skip a step in the reasoning,
> or simplify so much that I say something wrong. At the end, tell me precisely what these errors reveal about
> what I haven't yet consolidated.”

Delivery: ask for [TOPIC], let the user explain, and interrupt at the exact point (unclear term, logical leap, or
incorrect simplification) — don't wait until the end to report everything together. Close with a precise
assessment of what the errors reveal.

## What NOT to do

- Don't run more than one prompt in the same round unless the user asks for it: each has a different cycle, and
  mixing them confuses the goal.
- Don't turn this into a multiple-choice quiz: the six prompts call for active production (explaining, writing,
  deciding), not choosing between options.
- Don't install anything: this uses text and conversation turns, with no external tools or dependencies.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py apprendimento-socratico` and apply what it prints (it may print nothing).
