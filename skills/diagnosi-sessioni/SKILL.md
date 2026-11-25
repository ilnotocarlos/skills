---
name: diagnosi-sessioni
description: Diagnosi di come vengono usate le sessioni di Claude Code - sessioni troppo lunghe, compattazioni ripetute, agenti sempre generici, nessun cambio di modello in base alla difficoltà. Propone correzioni concrete. Usala quando l'utente dice "ottimizza il mio uso di Claude Code", "consumo troppo", "le sessioni si riempiono", "gli agenti sono sempre generici", o chiede un controllo periodico.
---

# Diagnosi sessioni

Misura prima, proponi dopo. **Non modificare impostazioni, agenti o file di regole senza conferma.**

## 1. Misura
```bash
python3 <cartella di questa skill>/sessioni.py            # tabella e segnali
python3 <cartella di questa skill>/sessioni.py --json
```
Per progetto: numero di sessioni, peso delle trascrizioni, compattazioni, sessioni oltre la soglia (`--mb`, default 20). Per gli agenti: quanti lanciati, quanti generici, quanti sul modello principale.

## 2. Leggi i segnali
| Segnale | Cosa vuol dire | Correzione |
|---|---|---|
| Più compattazioni che sessioni in un progetto | le sessioni durano troppo: ogni compattazione perde dettaglio e ogni messaggio rilegge un contesto pieno | chiudere prima: salvare lo stato in un file del progetto (cosa è fatto, prossimi passi, decisioni aperte) e ripartire da lì con `/clear` |
| Molte sessioni oltre la soglia | lo stesso | lo stesso; un filo di lavoro per sessione |
| Oltre il 70% di agenti generici | nessuna specializzazione: ogni agente riparte senza istruzioni di ruolo | definire pochi agenti in `~/.claude/agents/` (vedi sotto) |
| Oltre l'80% di agenti sul modello principale | letture e ricerche pagano il modello più costoso | dare a ogni agente il modello minimo che basta |
| Stesso progetto diviso in più righe (radice e sottocartelle) | le sessioni partono da cartelle diverse: regole e storico si frammentano | avviare sempre dalla stessa radice |

## 3. Agenti specializzati
Proponi al massimo quattro o cinque agenti, ricavati da ciò che l'utente delega davvero (guarda le descrizioni degli agenti lanciati nelle trascrizioni). Uno schema che funziona:

| Agente | Compito | Modello | Scrive file |
|---|---|---|---|
| lettura | leggere, riassumere, estrarre da materiale già individuato | il più economico | no |
| ricerca | cercare in molti file o sul web, confrontare opzioni | intermedio | no |
| esecuzione | applicare modifiche già decise, test, script | intermedio | sì |
| revisione | rilettura indipendente prima di consegnare | il più capace | no |

Ogni agente è un file `~/.claude/agents/<nome>.md` con `name`, `description`, `model` e, per quelli in sola lettura, `disallowedTools: Edit, Write, NotebookEdit`. La `description` deve dire **quando usarlo e quando no**: è l'unica cosa che il modello principale legge per scegliere.

Aggiungi anche una regola in `~/.claude/CLAUDE.md`: scegliere l'agente più economico che basta, usare quello generico solo per problemi aperti, indicare sempre il modello.

## 4. Verifica
Dopo qualche giorno di lavoro rilancia `sessioni.py` e confronta le percentuali. Se gli agenti restano generici, la regola o le descrizioni sono troppo vaghe: rendile più precise.

## Limiti da dichiarare
- Il peso in MB è un indicatore della lunghezza, non il numero di token.
- Il conteggio vede solo le trascrizioni presenti su questo computer, e le percentuali includono tutto lo storico: dopo una correzione migliorano lentamente.
