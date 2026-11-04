---
name: ui-mockup-review
description: >
  Use to redesign a node's UI one screen at a time through HTML mockups published as
  Artifacts, built on the Life design-system tokens, before touching code. Covers the
  tools (Artifact quickstart, the token kit, the theme-token extractor, brain notes)
  and the review loop (today vs proposal, annotated reasons, working interactions,
  open questions). Trigger: "rivediamo graficamente", "facciamo un mockup",
  "revisione grafica", "non si capisce questa pagina", "/ui-mockup-review".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Artifact, Skill
---

# UI mockup review

Born in the Scheduler redesign (2026-10-31), approved by the owner as the model for every node;
since 2026-11-02 it is **the frontend base of the Life suite** (`docs/frontend-standard.md`): every new page
or redesign in any node starts here, with this kit and this loop.
Reference mockups: Prepara settimana https://claude.ai/artifact/NxrpGuxQj9dDpSfYrNaxzn,
Dashboard https://claude.ai/artifact/HqSmoiih5iv3JyqnsWFkPm, LLM «Servizi» (drill-down down to the atom,
executor tags, step flow + side panel) https://claude.ai/artifact/MPrdexcpemntsN3otNLD2r.

## Tools

| Tool | What for |
|---|---|
| `Artifact` `action: quickstart`, `intent: "other"`, `design_systems: false` | once per new mockup: gives the page contract; then publish a plain HTML page |
| `assets/mockup-kit.html` | the head to copy: Life tokens (Eclisse 2, light + dark), Life `Button` 1:1, choice tiles, chips, stepper, lists, `TimeBudget` bar, agenda, banner, FAB, annotation box, lucide icon sprite; v8 block: app frame with tabs, executor tags, hero + stat tiles, grouped rows, step flow + side panel, action rows, run trace with «why», tree picker with collapsible branches |
| `scripts/theme_tokens.py [theme]` | prints a theme's tokens from `packages/design-system/themes/`; use it if the node uses another theme or the base changed |
| `Grep`/`Read` on the node's `frontend/src` | inventory before drawing: pages, `components/ui` (local copies to replace), feature cards, what each card really shows |
| `packages/design-system/src/index.ts` | what already exists (Stepper, Segmented, PageHeader, Callout, Card, EmptyState…): propose those, never new look-alikes |
| skill `idea` (direct write) | every decision goes to the brain at once: `nodes/<node>/facts/<date>-redesign-<screen>.md`, updated as answers arrive |

## Loop (one screen per Artifact)

1. **Read the screen**: page component + its cards + local `ui/` components. Name what is
   confusing in the user's words (e.g. "card without a title, 4 equal buttons").
2. **Draw** from `mockup-kit.html` (keep its head, write the body):
   - an "Oggi" note or column listing the problems (✕ notes);
   - the proposal with realistic domain data (real people, sources, times, units);
   - a `.ann` note under each block saying *why* (→ notes); every label in the user's
     language, never the data model (`work_extra` → "Lavoro di più");
   - the key interaction working (drag, popover, toggle), touch fallback included;
   - "Da decidere" at the bottom: numbered, answerable in one word each.
3. **Publish** (same file path = same URL on every iteration), answer in a few lines:
   what changed, the open questions, what is invented or needs backend.
4. **Apply answers** with `Edit` + republish in the same response; move resolved
   questions to "Deciso"; update the brain fact.
5. Next screen: a new file, a new Artifact. Code only when the mockup round is closed.

## Rules that came out of the review

- Buttons = `@suite/design-system` `Button` (primary/secondary/ghost/destructive/link),
  one primary per view, verb + icon; edit = icon-only pencil with aria-label; row actions
  as ghost/link; a choice among peers = tiles with icon + one line of what happens.
- A node's local `components/ui/Button` copy is a finding: propose replacing it.
- Summary first, editor on demand; show "same / changed from now on / this week only"
  instead of re-showing everything.
- State in form: chips (ok/warn/bad), a card turns red only on something blocking.
- No native browser controls, both themes, phone width (FAB for quick actions).
- Every visible string is an `@suite/i18n` key from the start (English dictionary is the
  source, Italian second); composed sentences are templates with placeholders, never
  concatenated fragments. A new language = one cheap LLM-gateway pass over `en.ts`, then a
  review; missing keys fall back to English. Mockups stay in the user's language, but the
  note under each block says which strings become keys.
- Data that comes from another node is editable here too: the change is sent to the source
  node and the row shows "sent, waiting" until it confirms.
- Long lists: groups that collapse, a whole group can be paused, a compact view.
- Charts: load the `dataviz` skill first and run its `validate_palette.js` on the category
  colors (light and dark). The kit's `--c-*` palette passed all checks on 2026-10-31; one axis,
  hover tooltip, a "see as table" fallback, and a stat-tile row before the charts.
- Theme: each person picks the style; the default is the one set in Life.
- Who does the work is always visible: a step, task or row done by an LLM, by code or by a person
  carries the executor tag (`.xb.llm` violet + spark, `.xb.code` teal + `</>`, `.xb.human` amber +
  person), the same in lists, detail and history; sub-parts carry a how-tag (prompt / code / input).
- Drill-down pages keep context: the sequence stays on the left with the current item highlighted,
  its detail opens in a side panel on the right (below on phones); breadcrumbs plus a `depth` label.
- Explanations go in a note under the app frame, never inside it: the frame looks like the real page.
- Node pickers are trees: multi-select, search, branches that collapse (arrow next to each node with
  children).
