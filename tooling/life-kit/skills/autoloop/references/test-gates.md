# Test-gates — "test genuini, non solo green" (anti reward-hacking)

Dettaglio operativo dei gate citati in `SKILL.md`. Obiettivo: l'agente non deve poter chiudere il loop
imbrogliando sui test. Ordinati per importanza.

## 1. Fail-to-pass + Pass-to-pass (gold standard, da SWE-bench)

Il fix deve:
- far passare i test che **prima fallivano** (fail-to-pass) → dimostra che il problema è risolto;
- non rompere i test che **già passavano** (pass-to-pass) → nessuna regressione.

Implementazione nel loop:
1. Prima di iniziare, esegui la suite e registra l'insieme `PASS_BEFORE`.
2. Definisci i `NEW_TESTS` (derivati dalla spec) che devono diventare verdi.
3. STOP solo se: `NEW_TESTS` tutti verdi **AND** `PASS_BEFORE` ancora tutti verdi.
4. **Congela** i file di test/regression: l'agente del loop NON può modificarli. Se serve cambiarli, è una
   decisione umana esplicita, fuori dal loop.

## 2. Test-writer separato dall'implementer

Se lo stesso agente scrive test e codice nello stesso passo, li addomestica a vicenda (scrive il test che il
suo codice già passa).

- Subagent A (**test-writer**): legge SOLO `SPEC.md`/UAT, NON il codice di implementazione. Produce i test.
- Subagent B (**implementer**): riceve i test come contratto immutabile, scrive il codice per soddisfarli.
- In Claude Code: `gsd-add-tests` (test dai criteri UAT) per A; `subagent-driven-development` per B.

## 3. verification-before-completion (superpowers)

Vietato dichiarare "fatto / fixed / passing" senza:
- aver eseguito il comando reale;
- aver incollato l'output reale (exit code, conteggio test).

"Evidence before assertions." Elimina il "dovrebbe funzionare". È il gate culturale più importante.

## 4. Reviewer avversariale indipendente

Un subagent **fresco** (senza il contesto di chi ha implementato) il cui compito è **rompere** il lavoro:
- `gsd-code-review` — bug, sicurezza, qualità;
- `code-reviewer` / `security-auditor`;
- `silent-failure-hunter` — try/catch che ingoiano errori, fallback che mascherano problemi;
- `pr-test-analyzer` — i test coprono davvero i casi limite?

Il loop NON chiude se il reviewer trova problemi reali. (È lo stesso principio della verifica avversariale
3-voti dei workflow.)

## 5. Forza i test contro il gaming

- **Mutation testing**: muta il codice; se i test non falliscono, sono deboli → rafforzali.
- **Property-based** (Hypothesis): genera input casuali contro invarianti, non solo esempi cherry-picked.
- **Golden / snapshot** su comportamento reale osservato.
- **E2E** (Playwright) oltre agli unit: `gsd-integration-checker` per i flussi utente completi.
- Vieta asserzioni vuote/tautologiche (`assert True`, mock che verificano sé stessi).

## 6. Eval ancorata all'intento, non al verde (GSD)

- `gsd-verify-work` — UAT conversazionale: la feature fa ciò che la spec prometteva?
- `gsd-validate-phase` (Nyquist auditor) — colma i gap di copertura della fase.
- `gsd-audit-uat` / `gsd-audit-milestone` — il consegnato coincide con l'intento originale prima di archiviare.

## 7. Criteri di stop misurabili (no giudizi soggettivi)

STOP_CMD deve essere una congiunzione di comandi con exit code, più i due gate umani-simulati (reviewer, UAT):

```
STOP =  pytest(new+regression)==0
    AND lint==0 AND type==0
    AND frontend_lint==0 AND frontend_test==0
    AND reviewer_subagent == APPROVED
    AND gsd-verify-work == UAT_PASS
```

Niente "sembra a posto", "dovrebbe funzionare", "tono pulito". Solo condizioni verificabili.

## Anti-pattern da bloccare esplicitamente

- Cancellare/commentare un test che fallisce per "farlo passare".
- Indebolire un'asserzione (`assertEqual` → `assertIsNotNone`).
- `try/except: pass` per nascondere un errore e rendere il test verde.
- Scrivere il test dopo aver visto il codice, modellandolo sull'implementazione.
- Hardcodare l'output atteso uguale all'output corrente (snapshot del bug).
- Skippare/xfail un test senza una motivazione scritta e una data di rimozione.
