# Catalogo degli assi di attacco

Scegli **un asse per agente**. Assi diversi = lenti diverse = findings diversi.
Cinque agenti sullo stesso asse producono cinque volte lo stesso finding generico.

---

## A. Claims vs reality (forense)

L'agente più sottovalutato. Verifica che ciò che è *dichiarato fatto* sia *fatto*.

- `git log` / `git show --stat` / `gh issue view N`: i commit corrispondono alle fasi dichiarate?
- Gli artefatti promessi esistono su disco? (directory, migrazioni, container, file di config)
- Il working tree è pulito? File cancellati ancora importati? Il progetto compila davvero?
- I test dichiarati: esegui la suite e riporta **numeri reali**, mai stimati
- Documenti citati: esistono? sono committati? l'ultima modifica è coerente con la data dichiarata?
- Stato runtime: `docker ps`, health endpoint, migrazioni a head?

Regola: ogni finding deve citare **il comando eseguito e il suo output**.

## B. Neutralità / accoppiamento

Quando un piano promette un'astrazione ("motore generico", "layer neutro", "plugin"),
verifica che l'astrazione regga invece di limitarsi a spostare il problema.

- Il modello "neutro" porta campi che esistono solo per il caso d'uso originale?
- Il core referenzia ancora entità del dominio specifico?
- Esistono **due percorsi** (vecchio e nuovo)? Sono equipotenti? Elenca ogni feature
  raggiungibile solo dal percorso vecchio — è il debito nascosto
- Chi dereferenzia le relazioni che il percorso nuovo lascia `NULL`?
- Quanta UI presume l'entità locale che sta per sparire?

Domanda finale obbligatoria: *dopo il refactoring, il caso d'uso originale funziona ancora
passando **solo** dalla nuova astrazione?* Se no, elenca esattamente cosa manca.

## C. Contratto (API fra servizi / moduli)

- **Idempotenza**: retry parziale, duplicati interni al batch, race di due scritture, atomicità
- **Cancellazione / tombstone**: come sa il consumer che una risorsa non esiste più?
  Esiste un full-sync di riconciliazione o solo l'incrementale? Record fantasma?
- **Versioning**: il contratto ha una versione? Come evolve senza rompere il consumer?
- **Fallimenti parziali**: si sa *quali* record hanno fallito e *perché*? Errori per-record o
  tutto-o-niente?
- **Auth**: confronto a tempo costante, rotazione del segreto, un origin può spacciarsi per un altro?
- **Validazione**: campi mutuamente esclusivi, range, riferimenti a entità inesistenti,
  **dipendenze cicliche**, valori che scavallano la mezzanotte
- **Identità**: due database, due tabelle utenti — chi è la fonte di verità? Cosa se divergono?
- **Tempo**: fuso, DST, settimana ISO, chi decide la finestra
- **Read-back**: paginazione, consistenza durante una scrittura, come sa il consumer che c'è
  qualcosa di nuovo (polling? push? webhook?)
- **Osservabilità**: si riesce a diagnosticare "il mio X non è arrivato" distinguendo
  *non inviato* / *inviato ma rifiutato* / *accettato ma scartato dalla logica*?

## D. Il piano — cosa NON dice

Il piano descrive il percorso felice. Attacca tutto il resto.

- **Migrazione dati**: esistono dati reali? Mapping degli id? FK che attraversano il nuovo
  confine? Backfill? **Rollback?**
- **Identità / auth**: l'utente deve autenticarsi due volte? Cookie, domini, CORS fra le porte?
- **Proprietà**: chi possiede il bot / il canale / il job schedulato / il cron?
- **Frontend**: due SPA? l'utente naviga fra due porte? shell unica? Il piano lo elude?
- **Realtime**: i dati stanno di qua, i nomi di là — denormalizzazione o N+1 cross-servizio?
- **Sequenza e reversibilità**: quando si cancella il vecchio codice? C'è **dual-run**?
  Come si verifica l'equivalenza *prima* di cancellare (shadow run, confronto degli output)?
- **Test**: come si testa un flusso che attraversa due servizi? Contract test? E i test
  esistenti che toccano il dominio spostato, dove vanno?
- **Scope reale**: conta davvero (`wc -l`, `git ls-files | wc -l`). Il piano è sottodimensionato?
- **Rimandi**: "questo lo dettagliamo just-in-time" è spesso una scusa per rimandare le
  decisioni difficili. Elencale.

Finding obbligatorio: *eseguito alla lettera, questo piano lascia il sistema non funzionante
per quanto tempo?*

## E. Cross-cutting / operazioni

- **Deploy**: ordine fra componenti con contratto condiviso, migrazioni, downtime
- **Backup / restore**: due DB non hanno un backup transazionalmente coerente — come si gestisce?
- **Segreti**: come si genera, si condivide e si **ruota** un segreto fra due repo?
- **Dipendenze condivise**: pacchetti linkati in più posti — versioning, drift, chi aggiorna
- **Osservabilità**: log correlati? request id propagato? Se un job notturno fallisce,
  qualcuno se ne accorge?
- **Porte / risorse**: sono davvero libere e registrate?

## F. Raggiungibilità a runtime — l'asse che tutti dimenticano

Gli assi A–E guardano al **cambiamento**. Questo guarda a **ciò che c'è già**, e chiede una sola
cosa: *il percorso dichiarato funzionante è davvero percorribile da un client reale, oggi?*

- Ogni componente "pronto" è **montato** e **raggiungibile**? Middleware, gate, auth, proxy,
  CORS, firewall: qualcuno risponde 403/404 prima ancora che il codice giusto venga eseguito?
- Le funzioni "nuove" hanno **chiamanti di produzione**? (`grep` del nome: se compare solo nella
  sua definizione e nei docstring, non è collegata a niente)
- I test verdi provano il percorso reale, o girano con un **bypass** attivo (`APP_ENV=test`,
  mock del middleware, fixture che salta l'auth)? Un gate disattivato nei test è un punto cieco
  per definizione: 400 test verdi non dicono nulla su quel percorso.
- Il codice deployato coincide con quello del repo? Il container ha ricostruito?

Vale la pena dedicargli **un agente intero**. In un red team sullo split di questo progetto,
cinque auditor puntati sul cambiamento hanno prodotto 89 finding senza accorgersi che il
contratto al centro dell'epica rispondeva 403 a chiunque, perché il middleware non lo esentava
e i test giravano col gate spento. L'ha trovato il sintetizzatore, per caso, verificando altro.

## G. La domanda scomoda (sempre presente)

Un agente deve argomentare **contro** la tesi del progetto, con dati:

> "Questo approccio è necessario? Qual è l'alternativa più economica che ottiene lo stesso
> obiettivo?"

Deve portare numeri reali (righe di codice, endpoint, utenti, frequenza d'uso) e i criteri
di decisione trovati nelle fonti, non opinioni. È il finding che nessun altro agente produrrà
spontaneamente, perché tutti gli altri lavorano *dentro* la premessa.

---

# Assi di ricerca prior art

Un agente per filone. Ogni prompt chiude con una **domanda avversariale** che cerca i fallimenti.

| Filone | Cosa cercare |
|---|---|
| **Prodotti concorrenti** | OSS che risolve lo stesso problema: modello dati, meccanismi, UX. Chi ha un motore vero e chi si limita a regole semplici, con quale esito |
| **Algoritmo / libreria** | Docs ufficiali + esempi reali del repo upstream + primer della community + blog degli autori. Pattern concreti, non teoria |
| **Architettura di riferimento** | Chi ha fatto la stessa separazione su scala maggiore, e come modella il confine |
| **Pattern di integrazione** | Idempotency key, outbox, CDC, riconciliazione, bulk con errori per-record, contract testing |
| **Decisione strategica** | Letteratura *a favore e contro* la scelta architetturale, con criteri e casi di ripensamento documentati |

## Query che funzionano

- `<problema> site:github.com` poi **apri le issue**, non solo il README
- `<tecnologia> post mortem` / `why we moved away from <X>` / `<X> regret`
- `<progetto> wontfix` — le issue chiuse dicono più della roadmap
- `site:reddit.com/r/<sottoreddit> <problema>` — l'esperienza d'uso reale
- `<pattern> antipattern` — la letteratura critica esiste quasi sempre
- Cerca anche nella lingua dell'utente: la community locale ha casi diversi
