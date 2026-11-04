# Storia: perché il controllo dei `@` è fatto così

- **2026-08-11**: su 4 progetti (Offerte, Cruscotto, Configuratore, OCR-Autoletture) un CLAUDE.md conteneva `@.claude/agents/*.md` e `@.claude/docs/*.md`, cioè senza `./` né `~/` davanti. Quella forma è un `@`-include valido come le altre: iniettava intere directory di agent e doc (fino a circa 850 righe) a ogni sessione. Il grep di allora cercava solo `@~/.claude`, `@./`, `@/home` e `@.claude/` con un `**` che bash non espande senza `globstar`: non lo vedeva.
- Il pattern attuale cerca ogni `@` seguito da un percorso (con una barra), a inizio riga o dopo uno spazio, in tutti i `CLAUDE.md` sotto la radice.
