---
name: usabilita
description: "Check usability before delivering a page or component: clear hierarchy, labeled fields, accessible actions, readable tables, complete states, destructive-action confirmations, mobile rendering, and browser verification. Use it for every new or modified interface."
---

# Usability — the check before delivery

A page is not finished until users can use it without explanation. Apply the entire checklist,
then verify the interface in a browser at the relevant widths.

## Sources and components

- Use `web-design-guidelines` to review the code.
- Apply usability principles: visible system status, match between the system and the user's language, error prevention, and recognition rather than recall.
- Prefer `@suite/design-system`, the Life package in `packages/design-system`; if a
  required component is missing, compose accessible primitives consistent with the project.
- Do not replace an interactive control with clickable text.

## Checklist

1. **Clear purpose**: a title and one sentence explain what to do; every section has a heading.
2. **Starting point**: the initial view says what is missing and how to proceed.
3. **Fields**: visible label, help when the value is not obvious, secrets masked.
4. **Fixed values**: use Select or Combobox, not free text.
5. **Actions**: real buttons with text; icon-only buttons require `aria-label` and a tooltip. Keep
   short actions associated with a record on the same line.
6. **Data**: tables with consistent headers, sorting where useful, and states shown as badges;
   show human-readable labels instead of raw identifiers.
7. **Language**: translate types, states, and technical levels into understandable words.
8. **Interface states**: loading state identifies the operation, empty state gives the next
   action, and errors explain the cause clearly and provide a “Retry” button.
9. **Remedy near the problem**: place a button or copyable command next to the warning.
10. **Destructive actions**: ask for confirmation and explain what will be lost.
11. **Phone**: at 375 px, the page does not scroll horizontally; wide content scrolls
    within its own container.
12. **Wide tables**: for 7 or more columns, or overflow at 1280 px:
    - use `DataTable` from `@suite/design-system` with accessible horizontal scrolling;
    - for long tables, make scrolling available at the top too and synchronize it;
    - show dates on two lines, day above and time below, without seconds;
    - use compact cells, short headers, controlled wrapping, and an accessible but visually
      hidden actions header;
    - remove only columns that are not needed to identify or choose the row, after the
      user's consent.
13. **Tests**: add at least one test that locates controls by role and label, for
    example `getByRole("button", { name })` and `getByLabelText`.

## Required verification

1. Run the relevant build and tests.
2. Open the interface in a browser and capture screenshots of every modified view and state.
3. Inspect the screenshots at desktop and mobile widths; make corrections and repeat.
4. For new pages or redesigns, request an independent visual review.
5. In the handoff, say where to see the result and which states were verified.

Finish only when the checklist passes against real behavior, not just the code.

## Instance specifics

Run `python <this skill's base directory>/../../scripts/skill-overlay.py usabilita` and apply what it prints (it may print nothing).
