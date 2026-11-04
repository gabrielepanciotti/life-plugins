---
name: usabilita
description: "Review a page or component for usability before delivery: clear hierarchy, labeled fields, accessible actions, readable tables, complete states, destructive-action confirmations, mobile layout, and browser verification. Use it for every new or changed interface."
---

# Usability — the pre-delivery review

A page is not finished until people can use it without extra explanations. Apply the full checklist, then verify the interface in a browser at the relevant widths.

## Sources and components

- Use `web-design-guidelines` for code review.
- Apply usability principles: visible status, user language, error prevention, and recognition rather than recall.
- Prefer `@suite/design-system`, the Life package in `packages/design-system`; if a required component is missing, compose accessible primitives that fit the project.
- Do not replace an interactive control with clickable text.

## Checklist

1. **Clear purpose**: a title and one sentence explain the task; each section has a heading.
2. **Starting point**: the initial view says what is missing and how to proceed.
3. **Fields**: visible labels, help when a value is unclear, masked secrets.
4. **Closed values**: use Select or Combobox, not free text.
5. **Actions**: use real buttons with text; icon-only buttons need `aria-label` and a tooltip. Keep short actions associated with a record on the same row.
6. **Data**: use tables with consistent headers, sorting where useful, and badge states; show human-readable labels instead of raw identifiers.
7. **Language**: translate types, states, and technical levels into understandable words.
8. **Interface states**: show the operation while loading, the next action when empty, and an understandable cause with a “Retry” button on errors.
9. **Remedy near the issue**: put a button or copyable command beside the warning.
10. **Destructive actions**: ask for confirmation and explain what will be lost.
11. **Phone**: at 375 px the page does not scroll horizontally; wide content scrolls within its own container.
12. **Wide tables**: for 7 or more columns, or overflow at 1280 px:
    - use `DataTable` from `@suite/design-system` with accessible horizontal scrolling;
    - for long tables, make scrolling available at the top too and synchronize it;
    - show dates on two lines, day above time, without seconds;
    - use compact cells, short headers, controlled wrapping, and an accessible but visually hidden actions header;
    - remove only columns that are not needed to identify or choose a row, after user consent.
13. **Tests**: add at least one test that locates controls by role and label, such as `getByRole("button", { name })` and `getByLabelText`.

## Required verification

1. Run the relevant build and tests.
2. Open the interface in a browser and capture screenshots of every changed view and state.
3. Inspect screenshots at desktop and mobile widths; fix issues and repeat.
4. For new pages or redesigns, request an independent visual review.
5. In the delivery note, say where to see the result and which states were verified.

Finish only when the checklist passes against real behavior, not just the code.
