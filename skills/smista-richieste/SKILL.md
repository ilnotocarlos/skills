---
name: smista-richieste
description: Metodo per affrontare molte richieste insieme su un progetto grande - le inventaria, le ordina, decide per ognuna quali controlli servono davvero e riporta l'esito in una tabella. Usala quando l'utente porta un elenco di richieste, più issue, una mail del cliente con tanti punti, un giro di feedback, o dice "ci sono tante cose da fare", "organizza queste richieste", "che controlli servono".
---

# Smista richieste

Davanti a molte richieste l'errore tipico è partire dalla prima e leggere codice. Il risultato: contesto pieno a metà elenco, controlli fatti a memoria, alcuni applicati a tutto e altri dimenticati. Qui si ragiona in quattro tempi e **si legge codice solo dal terzo**.

## 1. Inventario (senza aprire codice)
Una riga per richiesta. Se una richiesta ne contiene due, dividila.

| # | Cosa chiede | Tipo | Dove | Dimensione | Cosa non so |
|---|---|---|---|---|---|

- **Tipo**: difetto, funzione nuova, modifica, dato da correggere, testo, domanda.
- **Dove**: area o app, dall'indice del progetto o con una ricerca; non serve ancora il file.
- **Dimensione**: piccola (un punto), media (una funzionalità), grande (più aree o schema dei dati).
- **Cosa non so**: solo ciò che cambierebbe il lavoro. Una domanda che non cambia nulla non si scrive.

## 2. Ordine
- **Doppioni e contraddizioni** fra richieste, o fra una richiesta e una regola del progetto: si segnalano subito, prima di lavorare.
- **Stessi file**: richieste che toccano gli stessi file vanno in fila, nell'ordine dichiarato.
- **Indipendenti**: si possono fare in parallelo; se il progetto prevede agenti, uno per richiesta, su copie separate.
- **Prima** ciò che sblocca altro e i difetti in produzione; **ultime** le richieste con domande aperte, così la risposta può arrivare nel frattempo.

## 3. Controlli: solo quelli che la richiesta fa scattare
Leggi la matrice del progetto (`CONTROLLI.md` alla radice, o il file indicato nelle regole). Per ogni richiesta segna **quali righe scattano in base a ciò che tocca**, non per tipo di richiesta e non tutte per prudenza.

Se la matrice non c'è, proponi di crearla dal modello `CONTROLLI-modello.md` in questa cartella, ricavando le righe dalle regole del progetto: una riga per ogni controllo che oggi è scritto in prosa.

Tre famiglie, trattate in modo diverso:

| Famiglia | Esempi | Come si esegue |
|---|---|---|
| **Meccanici** | tipi, lint, test, traduzioni, build | un comando, **una volta per ramo alla fine**, non dopo ogni modifica; l'output si incolla nel resoconto |
| **Di giudizio** | permessi, dati personali, coerenza con il design, casi limite | elenco puntuale di domande preso dalla matrice; se il progetto lo prevede, a un agente di revisione che riceve il diff e l'elenco, non la conclusione |
| **Dell'utente** | rilascio in produzione, scelte di prodotto, comunicazioni al cliente | si prepara tutto e ci si ferma: comando pronto, bozza pronta |

Mostra il piano in una tabella (richiesta, ordine, controlli che scattano, domande) e chiedi solo le decisioni che spettano all'utente. Poi procedi senza aspettare sulle richieste che non dipendono dalla risposta.

## 4. Esecuzione e resoconto
- Una richiesta alla volta fino in fondo: modifica, controlli che scattano, esito. Non aprire la successiva con controlli in sospeso.
- Per ogni richiesta leggi solo i file che modifichi e quelli che li chiamano.
- Un controllo non eseguibile si dichiara **saltato, con il motivo**: mai verde per supposizione.
- Se l'elenco è lungo, a metà salva l'avanzamento nel file di stato del progetto: la sessione successiva riparte dalla tabella.

Resoconto finale, una riga per richiesta:

| # | Richiesta | Esito | Controlli passati | Saltati o falliti (perché) | Resta da fare |
|---|---|---|---|---|---|

## Quando la matrice va aggiornata
Ogni volta che un controllo ha trovato un difetto che nessuna riga prevedeva, o che l'utente corregge il metodo: aggiungi o modifica la riga nella stessa sessione. La matrice è l'unico posto dove i controlli si accumulano; le regole di progetto restano brevi.
