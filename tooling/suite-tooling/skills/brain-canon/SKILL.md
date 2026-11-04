---
name: brain-canon
description: >
  Extract the golden facts from sources/ — no invented facts. Plan what to
  extract, await user approval, write coherent canon, then split into atomic
  notes via [[brain-note]]. Numbers must reconcile. Reads only sources/;
  writes content notes outside sources/. Trigger: "extract the canon",
  "/brain-canon", "consolidate the sources".
argument-hint: "[node-dir | sources-dir]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# brain-canon

Consolidate the hard facts from a node's `sources/` according to the golden rule:
**no invented facts**. Read ONLY raw inputs in `sources/`; write coherent,
verified content notes outside `sources/`.

1. **Read the sources** (`sources/*.md`, `.txt`, `.json`, etc.). Note the
   discrete facts (numbers, dates, relationships, definitions) and their
   causal relationships.

2. **Propose a plan**: a `## Extraction plan` section with:
   - Central topic/question (e.g. "company history", "pricing model")
   - Key facts identified for each (with source citation: "source:
     `file.md` line N")
   - Numerical checks: sums, counts, and proportions must add up (e.g.
     "team total 15 = eng 8 + sales 4 + ops 3")
   - Caution notes if a fact is ambiguous or contradicted

3. **Wait for approval**: show the plan. The user notes whether facts are
   missing, checks have gaps, or two sources conflict. If necessary,
   explain the plan again and start over from step 1.

4. **Write the coherent canon**: a **verified content** document that
   summarizes the facts in a readable account, with all citations inline
   (e.g. "The company was founded in 2015 (source: about.md) by 3 partners
   (team-structure.md)")

5. **Split into atomic notes**: the canon is still rough and long. Use
   [[brain-note]] for each identified topic (`self-…`, `history-…`,
   `model-…`, etc.), **always citing the canon as the source** (reciprocal
   wikilinks). Each atomic note inherits the plan's numerical verification.

6. **Invent nothing**: if a fact is NOT in the sources, do NOT write it.
   If the answer to a question is not in the sources, leave it blank and
   note "not present in the sources".

   See [[brain-note]], [[brain-gate]].
