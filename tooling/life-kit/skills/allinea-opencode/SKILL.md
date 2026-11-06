---
name: allinea-opencode
description: Allinea OpenCode a un nodo Life (mirror degli agenti, `opencode.json` con suite-mcp, config globale, link `@suite/*`). Usala quando si dice «allinea opencode», «setup opencode per questo progetto», «opencode per il nodo», «prepara opencode come Claude Code», una volta per nodo o quando OpenCode su un nodo non vede suite-mcp o gli agenti.
---

# Allinea OpenCode a un nodo Life

OpenCode su un nodo Life è **derivato** dal lato Claude Code, non copiato a mano:
skills si caricano già da `~/.claude/skills/`, gli agenti vengono *mirror-ati*, la
config globale (`~/.config/opencode/opencode.jsonc`) e l'`opencode.json` di nodo
sono **generati** dalla suite. La regola: **una fonte (`~/.claude`) + un generatore
(`suite_core.blueprint.opencode`) + zero sync manuale**.

## Serve

- Il venv di Life con `suite_core` installato (il pacchetto sta in `$PATH_LIFE/packages/shared`): `.venv/bin/python` su Linux, `.venv/Scripts/python` su Windows. Se manca il venv: `python3.13 -m venv .venv` (Linux) o `py -3.13 -m venv .venv` (Windows), poi `.venv/bin/pip install -e packages/shared` dalla radice di Life. Verifica con `python -c "import suite_core"`.
- OpenCode installato: `npm install -g opencode-ai`.

## Bivio: quale caso?

- **Primo setup di un nodo**: il nodo non ha `.opencode/`. Crea la cartella (`mkdir .opencode`) e poi lancia tutti i comandi qui sotto.
- **Nodo già allineato che non vede suite-mcp o gli agenti**: salta `mkdir`, lancia `apply --nearest` e `opencode <dir>`, poi la verifica.
- **Config globale cambiata** (nuovi agenti in `~/.claude/agents/`): basta `opencode --global`.

## Il comando unico (per un nodo)

Dal device, con il Python del venv di Life (qui scritto `python`):

```
python -m suite_core.nodes apply --nearest <dir>   # .mcp.json + opencode.json + agents + mirror .opencode
python -m suite_core.nodes opencode --global        # agenti globali + ~/.config/opencode/opencode.jsonc
python -m suite_core.nodes opencode <dir>           # mirror .opencode/agents del nodo
python -m suite_core.nodes link <dir>               # link @suite/design-system|i18n nel frontend
```

Poi **riavvia OpenCode** (la config non è hot-reload).

## Verifica finale

- [ ] 1. `<nodo>/opencode.json` esiste e il suo `command` punta a un interprete che esiste su questo device (`test -x <path>`). Se no, rilancia `apply --nearest <dir>`.
- [ ] 2. `<nodo>/.opencode/agents/` contiene gli stessi agenti di `<nodo>/.claude/agents/`. Se no, rilancia `opencode <dir>`.
- [ ] 3. Riavvia OpenCode ed elenca i tool di `suite-mcp` (`opencode mcp list`, oppure dall'interfaccia): devono comparire. Se no, torna al passo 1.

Finisci solo quando i tre controlli passano.

## Opt-in: la cartella `.opencode/`

Come per il mirror degli agenti, il nodo entra nel circuito OpenCode **con la
presenza di `.opencode/`**: senza quella cartella `apply` non genera `opencode.json`
e `opencode <dir>` non scrive il mirror. Per attivare un nodo basta `mkdir .opencode`.

## Cosa genera cosa

| File | Generato da | Contenuto |
|---|---|---|
| `~/.config/opencode/opencode.jsonc` | `opencode --global` | MCP globali (context7, playwright, chrome-devtools) + `instructions` → `CLAUDE.shared.md` |
| `~/.config/opencode/agents/*.md` | `opencode --global` | mirror di `~/.claude/agents/` |
| `<nodo>/.opencode/agents/*.md` | `apply` / `opencode <dir>` | mirror di `<nodo>/.claude/agents/` |
| `<nodo>/opencode.json` | `apply` (se `.opencode/` presente) | `suite-mcp` in formato OpenCode (`type: local`, `command` array, `environment`) |

## Perché `opencode.json` è generato e gitignored

Porta il **path assoluto** dell'interprete suite-mcp e il `VAULT_PATH` assoluto:
device-specific, quindi gitignored (blocco managed, accanto a `.mcp.json`) e
rigenerato per-device da `apply`. Il bug storico (path di scratchpad Claude morto)
nasceva da un `opencode.json` **scritto a mano**: ora `emit_opencode_json` riscrive
sempre command+environment, quindi non può più marcire.

## Limite noto: niente hook dinamici

OpenCode non replica gli hook di Claude Code (SessionStart `suite-apply`, Stop
auto-commit/push) con lo stesso meccanismo: ha i **plugin** (`config`/`event`/
`tool.execute.before/after`). La parte statica è coperta dal generatore; quella
dinamica richiederebbe un plugin JS/TS dedicato — non ancora scritto.

## Prove

`evals/prove.md`: tre richieste vere con il risultato atteso. Provale senza e con la skill, in una conversazione nuova.
