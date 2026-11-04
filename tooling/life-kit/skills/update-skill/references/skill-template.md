---
name: {{skill-name}}
description: "{{What it does, in third person.}} Use it when {{conditions and trigger phrases, in quotes}}."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# {{Title}} — {{short subtitle}}

This is a **starting point; adapt it**: keep only the sections the skill needs and delete this block. The complete 12 rules are in `~/.claude/docs/controllo-skill.md`.

Reminders:

- Describe the skill in third person: “<What it does>. Use it when…”. Say what it does and when, not the steps. A “When it activates” section that repeats this is unnecessary.
- Keep `SKILL.md` under 500 lines; put details in `references/` and link each from here. Files over 100 lines start with an `Index:`.
- Use imperatives, put each rule's reason beside it, and avoid excessive capitalization.
- Include only what Claude would not already know (internal rules, names, commands, variable-based paths).
- Keep `allowed-tools` to the minimum.

Folder structure:

```
skill-name/
├── SKILL.md
├── references/   on-demand details (history.md for incidents and dates)
├── scripts/      reusable commands
├── evals/        tests.md (3 real requests), and evals.json / val.json if needed
└── assets/       files used in output
```

---

# {{Title}} — {{short subtitle}}

Index: {{file sections in order; only if the file exceeds 100 lines}}

{{One or two sentences: what the skill does and why it exists. Put critical instructions at the top.}}

## Branch

<!-- Only when the workflow differs by case. -->

| Case | Path |
|---|---|
| {{create}} | steps 1, 2, 3 |
| {{modify}} | steps 2, 4 |

## Requirements

<!-- Only if the skill uses packages or programs. -->

- {{program or package}}: `{{installation command}}`

## Steps

<!-- For more than 3–4 ordered steps, use a “Copy and check” list with a “go back” instruction. -->

1. {{Step, imperative.}}
2. {{Step.}}
3. {{Step.}}

Copy and check:

- [ ] {{measurable check}} — if it fails, return to step {{N}}.
- [ ] {{measurable check}} — if it fails, return to step {{N}}.

## Output template

<!-- Only if there is a format to follow. State: “use it as-is” or “this is a starting point; adapt it.” -->

```
{{format}}
```

## Final check

- [ ] {{compare the result with a list or guide}}

Finish only when every check passes.

## Related files

- `references/{{descriptive-name}}.md` — {{what it contains and when to open it}}
- `scripts/{{name}}` — {{what it does; run it or read it}}
- `evals/tests.md` — three test requests. Try them with and without the skill in a new conversation.
