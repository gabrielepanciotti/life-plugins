// Template Workflow — Gate A (prior art) + Gate B (red team) combinati.
// Replace the placeholders <...>. For a single gate, delete the other section.
// Dimensionamento: 5 audit + 5 refutatori + 5 ricercatori + 1 sintesi = 16 agenti.

export const meta = {
  name: "<gate-slug>",
  description:
    "<one line: what is being attacked and what to search for online>",
  phases: [
    { title: "Audit", detail: "adversarial auditors on the repo" },
    { title: "Verify", detail: "independent refutation of every finding" },
    {
      title: "PriorArt",
      detail: "ricercatori web: GitHub, docs, blog, forum, paper",
    },
    {
      title: "Synthesis",
      detail: "single report: confirmed flaws + ideas borrowed from leaders",
    },
  ],
};

const REPO = "<<srv>/Progetto>";

// CONTEXT is the most important lever: agents start from zero.
// It must include: domain, stack, epic goal, key documents,
// and the anomalies found during manual grounding (marked "verify these; do not assume they are true").
const CONTEXT = `
## Context (read before acting)
Repo: ${REPO}
<watch for junctions/symlinks: if two different paths point to the same volume, say so and provide a workaround>
 git -c safe.directory=<real-path> for "dubious ownership">

Domain: <what the system does, for whom, with real user/data counts>
Stack: <linguaggi, framework, DB, infra>
Current goal: <the epic, with component boundaries and their contracts>

## Key documents
- Spec: <path>
- Piano: <path>  <segnala se untracked>
- Memoria progetto: CLAUDE.md, .claude/docs/*

## Anomalies already found by the orchestrator (verify them; do NOT assume they are true)
A) <specific anomaly found during manual grounding>
B) <...>
`;

const FINDINGS_SCHEMA = {
  type: "object",
  additionalProperties: false,
  properties: {
    summary: {
      type: "string",
      description: "Sintesi in italiano, max 8 righe",
    },
    findings: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        properties: {
          id: { type: "string" },
          title: { type: "string" },
          severity: {
            type: "string",
            enum: ["critical", "high", "medium", "low"],
          },
          area: { type: "string" },
          claim: {
            type: "string",
            description: "What is wrong or missing, in one sentence",
          },
          evidence: {
            type: "string",
            description: "File:line references or commands run",
          },
          why_it_breaks: {
            type: "string",
            description: "Concrete failure scenario",
          },
          suggested_fix: { type: "string" },
        },
        required: [
          "id",
          "title",
          "severity",
          "area",
          "claim",
          "evidence",
          "why_it_breaks",
          "suggested_fix",
        ],
      },
    },
  },
  required: ["summary", "findings"],
};

const VERDICT_SCHEMA = {
  type: "object",
  additionalProperties: false,
  properties: {
    verdicts: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        properties: {
          id: { type: "string" },
          verdict: {
            type: "string",
            enum: ["CONFIRMED", "PARTIAL", "REFUTED"],
          },
          corrected_severity: {
            type: "string",
            enum: ["critical", "high", "medium", "low"],
          },
          reason: {
            type: "string",
            description: "Prova o contro-prova concreta, con file:riga",
          },
        },
        required: ["id", "verdict", "corrected_severity", "reason"],
      },
    },
    missed: {
      type: "array",
      items: { type: "string" },
      description: "Flaws the auditor did NOT see",
    },
  },
  required: ["verdicts", "missed"],
};

const PRIOR_ART_SCHEMA = {
  type: "object",
  additionalProperties: false,
  properties: {
    summary: { type: "string" },
    sources: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        properties: {
          name: { type: "string" },
          url: { type: "string" },
          kind: {
            type: "string",
            enum: ["github-repo", "docs", "blog", "forum", "paper", "product"],
          },
          what_it_is: { type: "string" },
          key_takeaway: {
            type: "string",
            description: "What they solved and HOW, concretely",
          },
          verdict: {
            type: "string",
            enum: ["adopt", "adapt", "study", "ignore"],
          },
          why: { type: "string" },
        },
        required: [
          "name",
          "url",
          "kind",
          "what_it_is",
          "key_takeaway",
          "verdict",
          "why",
        ],
      },
    },
    antipatterns: { type: "array", items: { type: "string" } },
    recommendations: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        properties: {
          recommendation: { type: "string" },
          rationale: { type: "string" },
          impact: { type: "string", enum: ["high", "medium", "low"] },
          effort: { type: "string", enum: ["high", "medium", "low"] },
        },
        required: ["recommendation", "rationale", "impact", "effort"],
      },
    },
  },
  required: ["summary", "sources", "antipatterns", "recommendations"],
};

const WEB_PREAMBLE = `
You are a PRIOR ART researcher. Goal: do not reinvent the wheel — find who has already solved
these problems, how, and what we can adopt or avoid.

FIRST load the web tools: call ToolSearch with query "select:WebSearch,WebFetch".
If the context-mode plugin is installed, you can use its fetch and indexing tools
(ctx_fetch_and_index, then ctx_search) to keep raw bytes out of the context.

Regole:
- Cerca in inglese E in italiano. Copri: repo GitHub (README, docs e ISSUE rilevanti),
  official documentation, technical blogs, forums (relevant Reddit communities, Hacker News, StackOverflow,
  project mailing lists), and papers if the problem is algorithmic.
- At least 8 REAL sources with verifiable URLs. If a source will not open, say so — never make one up.
- Extract the concrete MECHANISM from each source (pattern name, data structure, API shape,
  model variables), not vague descriptions.
- Be adversarial: explicitly look for those who TRIED and FAILED, or regretted it.
`;

// ─── GATE B: red team ────────────────────────────────────────────────────────
phase("Audit");

// One attack angle per agent — see references/attack-catalog.md
const AUDITS = [
  {
    key: "claims-vs-reality",
    prompt: `You are a forensic auditor...\n${CONTEXT}\n## Assignment: <...>`,
  },
  {
    key: "<neutralita>",
    prompt: `You are an ADVERSARIAL auditor...\n${CONTEXT}\n## Assignment: <...>`,
  },
  { key: "<contratto>", prompt: `...` },
  { key: "<piano>", prompt: `...` },
  { key: "<crosscutting>", prompt: `...` },
];

const auditResults = await pipeline(
  AUDITS,
  (a) =>
    agent(a.prompt, {
      label: `audit:${a.key}`,
      phase: "Audit",
      schema: FINDINGS_SCHEMA,
    }),
  (res, a) => {
    if (!res || !res.findings || res.findings.length === 0) {
      return { key: a.key, findings: [], verdicts: [], missed: [] };
    }
    return agent(
      `You are the REFUTER. Another agent produced adversarial findings about repo ${REPO}.
Your job is to PROVE THEM WRONG. Assume every finding is mistaken or overstated,
and look for counterevidence in the actual code. Mark it CONFIRMED only if you cannot refute it.
${CONTEXT}

Area auditata: ${a.key}

Finding to refute (JSON):
${JSON.stringify(res.findings, null, 1)}

For EVERY finding, open the cited files and check that the evidence exists and says what the auditor claims
sostiene. Verdetti:
- REFUTED: the evidence does not hold, or the issue is already handled elsewhere (cite where).
- PARTIAL: it exists, but the severity is overstated or the scenario is unrealistic for this system.
- CONFIRMED: you tried to disprove it and could not.
Calibrate severity: "critical" only if it blocks the project or corrupts data.
In the "missed" field, list REAL flaws in this area that the auditor did NOT see.`,
      { label: `verify:${a.key}`, phase: "Verify", schema: VERDICT_SCHEMA },
    ).then((v) => ({
      key: a.key,
      findings: res.findings,
      summary: res.summary,
      verdicts: (v && v.verdicts) || [],
      missed: (v && v.missed) || [],
    }));
  },
);

// ─── GATE A: prior art ───────────────────────────────────────────────────────
phase("PriorArt");

const RESEARCH = [
  {
    key: "<competitor-products>",
    prompt: `${WEB_PREAMBLE}\n## Research: <...>\n<starting points to verify>\n<mandatory adversarial question>`,
  },
  { key: "<algoritmo-libreria>", prompt: `${WEB_PREAMBLE}\n## Ricerca: <...>` },
  { key: "<architettura>", prompt: `${WEB_PREAMBLE}\n## Ricerca: <...>` },
  {
    key: "<integration-pattern>",
    prompt: `${WEB_PREAMBLE}\n## Ricerca: <...>`,
  },
  {
    key: "<decisione-strategica>",
    prompt: `${WEB_PREAMBLE}\n## Ricerca: <...>`,
  },
];

const priorArt = await parallel(
  RESEARCH.map(
    (r) => () =>
      agent(r.prompt, {
        label: `prior:${r.key}`,
        phase: "PriorArt",
        schema: PRIOR_ART_SCHEMA,
      }),
  ),
);

// ─── Sintesi ─────────────────────────────────────────────────────────────────
phase("Synthesis");

// Apply the verdicts and discard REFUTED findings — ordinary code, not an agent.
const surviving = auditResults.filter(Boolean).map((r) => {
  const vmap = {};
  (r.verdicts || []).forEach((v) => {
    vmap[v.id] = v;
  });
  const kept = (r.findings || [])
    .map((f) => ({
      ...f,
      verdict: (vmap[f.id] || {}).verdict || "CONFIRMED",
      severity: (vmap[f.id] || {}).corrected_severity || f.severity,
      refutation: (vmap[f.id] || {}).reason || "",
    }))
    .filter((f) => f.verdict !== "REFUTED");
  return {
    area: r.key,
    summary: r.summary || "",
    findings: kept,
    missed: r.missed || [],
  };
});

const totalKept = surviving.reduce((n, s) => n + s.findings.length, 0);
log(
  `Findings that survived refutation: ${totalKept} across ${surviving.length} areas`,
);

const REPORT = `${REPO}/docs/superpowers/reviews/<data>-<tema>.md`;

const report = await agent(
  `You are the final synthesizer. Write the definitive review document.
${CONTEXT}

## Input 1 — Findings that SURVIVED refutation (JSON)
${JSON.stringify(surviving, null, 1)}

## Input 2 — Prior art raccolta online (JSON)
${JSON.stringify(priorArt.filter(Boolean), null, 1)}

Use the Write tool to create the file: ${REPORT}  (create the directory if needed)
In ENGLISH, with proper punctuation. Keep code and file names in English.

Struttura:
1. Verdict in 10 lines — can we proceed, yes or no
2. Immediate blockers — include the exact command to resolve each
3. Confirmed flaws by severity — evidence file:line, scenario, fix, and phase
4. Gaps the auditors missed ("missed" field)
5. What to adopt from leaders — source + URL + mechanism + adopt/adapt/study/ignore. ACTIONABLE.
6. Antipatterns to avoid — with the source documenting them
7. The uncomfortable question: is this approach justified? — with data and the cheaper alternative
8. Revised plan — sequence, verification milestones, exit criteria, decisions to make before coding
9. Open decisions — numbered, with options and a recommendation

No filler. Every technical claim must cite file:line or a source URL.
If two inputs contradict each other, say so explicitly.
After writing the file, return only the schema JSON.`,
  {
    label: "synthesize:report",
    phase: "Synthesis",
    agentType: "general-purpose", // the Write tool is required
    schema: {
      type: "object",
      additionalProperties: false,
      properties: {
        report_path: { type: "string" },
        verdict: { type: "string" },
        blockers: { type: "array", items: { type: "string" } },
        top_findings: { type: "array", items: { type: "string" } },
        top_prior_art: { type: "array", items: { type: "string" } },
        open_decisions: { type: "array", items: { type: "string" } },
      },
      required: [
        "report_path",
        "verdict",
        "blockers",
        "top_findings",
        "top_prior_art",
        "open_decisions",
      ],
    },
  },
);

return {
  report,
  findingsKept: totalKept,
  areas: surviving.map((s) => ({ area: s.area, n: s.findings.length })),
};
