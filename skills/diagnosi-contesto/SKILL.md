---
name: diagnosi-contesto
description: Riduce i file che Claude Code legge per orientarsi in un progetto. Misura quante letture fa ogni sessione, quante sono riletture e quanto vengono usati i file di contesto, poi controlla che regole, stato e indice del progetto siano aggiornati e li sistema. Usala quando l'utente dice "leggi troppi file", "ottimizza il contesto", "riduci i token", "aggiorna il wiki del progetto", "l'indice è vecchio", "sistema i file md del progetto".
---

# Diagnosi contesto

Principio: un progetto si apre leggendo **tre file brevi**, non esplorando le cartelle.

| File | Risponde a | Lunghezza |
|---|---|---|
| regole (`CLAUDE.md`) | cos'è il progetto, convenzioni, comandi: ciò che cambia di rado | fino a 80 righe |
| stato (`STATO.md`) | cosa è in corso, prossimi passi, decisioni aperte | fino a 60 righe |
| indice (`<Progetto> — Indice.md`) | dove sta ogni cosa: una riga per cartella e per documento chiave | fino a 150 righe |

Se questi tre sono giusti, ogni altra lettura è mirata. Se sono vecchi, Claude smette di fidarsi e torna a esplorare.

## 1. Misura come si legge oggi
```bash
python3 <cartella di questa skill>/letture.py                  # tutti i progetti
python3 <cartella di questa skill>/letture.py --progetto alfa  # uno solo, con i file più letti
```
| Colonna | Sopra questa soglia | Vuol dire |
|---|---|---|
| `/SESS` | 15 | si esplora invece di andare a colpo sicuro |
| `RILETTE` | 30% | lo stesso file viene riaperto: sessioni troppo lunghe, oppure file troppo grandi letti a pezzi |
| `CONTESTO` | sotto il 5% | stato e indice non vengono usati come punto di partenza |
| `SOLO LETTI` | 90% | quasi tutto ciò che si legge serve solo a capire: è lavoro che un indice eviterebbe |

Le regole (`CLAUDE.md`) vengono caricate da sole a ogni sessione e non compaiono come letture.

## 2. Controlla i file di contesto
```bash
python3 <cartella di questa skill>/wiki.py <cartella del progetto> [altre cartelle]
```
Segnala: file mancante o troppo lungo, stato fermo mentre le note cambiano, indice che punta a cose inesistenti, cartelle non citate nell'indice, note nuove non citate, note oltre 400 righe, nomi di nota ripetuti.

## 3. Sistema, in quest'ordine
**Mostra cosa cambierai e aspetta conferma. Non cancellare né spostare note: qui si aggiornano solo i tre file.**

1. **Indice**: togli i riferimenti rotti, aggiungi le cartelle mancanti, cita le note nuove che contano (non tutte: quelle da cui si parte). Una riga per voce, con il percorso. Per sapere cosa contengono le note nuove leggi titolo e prime righe, non il file intero.
2. **Stato**: se è fermo, ricostruiscilo dalle note cambiate di recente e da `git log`; taglia ciò che è concluso.
3. **Regole**: se superano il limite, sposta nell'indice o in una nota i dettagli che non servono a ogni sessione.
4. **Note oltre 400 righe**: non accorciarle. Aggiungi in cima un sommario di 5-10 righe e, nell'indice, indica che esiste: così si legge il sommario e poi solo la sezione che serve.
5. **Nomi ripetuti**: nell'indice usa il percorso, non il solo nome.

Rilancia `wiki.py`: i segnali corretti devono sparire.

## 4. Regole di lettura da lasciare nel file di regole personale
Proponi di aggiungerle a `~/.claude/CLAUDE.md` se mancano:

- A inizio sessione leggi stato e indice del progetto; apri altri file solo se il compito lo richiede.
- Cerca prima di leggere: trova il punto con una ricerca, poi leggi solo quelle righe.
- File oltre 400 righe: leggi il sommario o l'intervallo che serve, mai tutto.
- Non rileggere un file già letto in questa sessione, salvo che sia cambiato.
- Esplorazioni larghe (più di 5-6 file per capire qualcosa) vanno a un agente di ricerca, che riporta solo la conclusione.
- Quando crei o sposti un documento importante, aggiorna l'indice nella stessa sessione.

## Limiti da dichiarare
- `wiki.py` verifica i percorsi a partire dalla radice del progetto: un percorso scritto in forma abbreviata (relativo a una sottocartella) risulta inesistente anche se il file c'è. Controlla a mano prima di toglierlo dall'indice.
- Le letture contano solo lo strumento di lettura file, non ciò che arriva da ricerche o comandi.
- File temporanei e schermate sono esclusi: rileggerli è normale.
- Una cartella di codice ha molti file `.md` di librerie: `wiki.py` salta le cartelle ricreabili più comuni, ma su un repository grande i conteggi delle note restano indicativi.
