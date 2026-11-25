# Skills per Claude Code

[English](README.md) · **Italiano**

Skill per tenere in ordine Claude Code stesso: cosa è installato, cosa viene caricato a ogni sessione, come vengono usate le sessioni.

Sono nate da un'ottimizzazione reale. Su un computer con 260 sessioni di lavoro la diagnosi ha trovato 79 server MCP caricati a ogni avvio (ne servivano tra 2 e 8 a seconda del progetto), skill installate e mai aperte, e 491 agenti lanciati di cui il 95% sul modello più costoso. Ogni skill qui contiene lo script che ha prodotto quei numeri e le correzioni che hanno funzionato.

```bash
npx skills add ilnotocarlos/skills -g
```

Per installarne una sola: `npx skills add ilnotocarlos/skills -g --skill diagnosi-mcp`

| Skill | Chiedi a Claude | Ottieni |
|---|---|---|
| [gestisci-skills](skills/gestisci-skills) | "fai pulizia delle skill" | quali skill usi davvero, aggiornamento, rimozione di quelle ferme |
| [diagnosi-mcp](skills/diagnosi-mcp) | "troppi MCP, fai pulizia" | uso reale di ogni server per progetto, doppioni, regole per progetto |
| [diagnosi-sessioni](skills/diagnosi-sessioni) | "ottimizza il mio uso di Claude Code" | sessioni troppo lunghe, agenti generici, modelli sprecati |
| [diagnosi-contesto](skills/diagnosi-contesto) | "leggi troppi file, sistema il wiki del progetto" | quanto si legge e si rilegge, indice e stato del progetto rimessi in pari |
| [smista-richieste](skills/smista-richieste) | "ecco quindici richieste, organizzale" | un inventario, un ordine, e per ogni richiesta solo i controlli che fa scattare davvero |

Tutte seguono la stessa regola: **prima misurano, poi propongono, e non cambiano nulla senza il tuo sì.** Gli script leggono solo file locali (`~/.claude`) e non fanno richieste di rete. Servono Python 3 e Node; nessuna dipendenza da installare.

---

## gestisci-skills

Installare una skill costa dieci secondi, quindi se ne accumulano. Ognuna aggiunge la propria descrizione a ogni sessione, e dopo qualche mese non sai più quali ti servono.

```
SKILL                            TIPO       USI  ULTIMO USO  INSTALLATA  ESITO
riepilogo-riunione               cartella    18       1g fa      37g fa  in uso
frontend-design                  gestita      9       0g fa       9g fa  in uso
gsap-core                        gestita      0           -      40g fa  mai usata
home-assistant-best-practices    gestita      0           -      41g fa  mai usata
intervista                       cartella     0           -       0g fa  nuova

Skill dei plugin (si tolgono disattivando il plugin):
  figma                           115 usi
  legal                             2 usi

Candidate alla rimozione (soglia 30 giorni): gsap-core, home-assistant-best-practices
```

| Chiedi | Succede |
|---|---|
| "c'è una skill per i changelog?" | cerca nel catalogo aperto, propone al massimo tre candidate con installazioni e autore |
| "installa quella" | legge prima il suo `SKILL.md` e segnala se esegue comandi o invia dati, poi installa |
| "aggiorna le skill" | aggiorna quelle che hanno una fonte e dice quali non possono essere aggiornate |
| "togli quelle che non servono" | propone solo `mai usata` e `ferma`, chiede conferma, rimuove nel modo giusto per ogni tipo |

Una skill appena installata risulta `nuova` e non viene proposta per la rimozione. Le skill copiate a mano finiscono nel Cestino, quindi restano recuperabili.

## diagnosi-mcp

Connettori dell'account, plugin e file di progetto dichiarano server MCP ognuno per conto suo. Il risultato tipico: decine di server caricati ovunque, molti mai autenticati, alcuni doppi.

```
262 sessioni in 42 progetti

SERVER                                 CHIAMATE PROGETTI  DOVE (primi 3)
plugin_figma_figma                         1934       14  sito/web=454, clienti/alfa=377, clienti/beta=221
claude_ai_Gmail                            1538       19  clienti/alfa=532, alfa/piattaforma=479
supabase                                   1567        2  alfa/piattaforma=1562
claude_ai_Supabase                          184        8  clienti/alfa=114, alfa/piattaforma=29
claude_ai_Qonto                              74        6  casa/amministrazione=53

PER PROGETTO (server usati almeno una volta)
  casa/amministrazione: claude_ai_Qonto=53, claude_ai_Gmail=7
```

Da qui la skill classifica ogni server (mai usato, doppione, usato in pochi progetti, usato ovunque), propone le regole e le scrive nei file di impostazioni, poi verifica con `claude mcp list` cartella per cartella.

Contiene anche quattro comportamenti di Claude Code scoperti provando, che fanno perdere tempo a chi non li conosce:

- i connettori dell'account non si possono spegnere ovunque e riaccendere in un progetto, solo il contrario;
- le impostazioni di progetto non si ereditano dalle cartelle madri;
- due fonti dello stesso servizio si nascondono a vicenda: ne spegni una e compare l'altra;
- le variabili d'ambiente delle impostazioni arrivano anche alla shell della sessione aperta e falsano le prove.

## diagnosi-sessioni

```
262 sessioni, 3.2 GB di trascrizioni

PROGETTO                                     SESS     MB COMPATT. LUNGHE
alfa/piattaforma                               62    684       67     13
clienti/alfa                                   29    327       20      4

AGENTI: 491 lanciati, 426 generici (86%), 471 sul modello principale (95%)
  per tipo:    general-purpose=394, web-fetch=44, Explore=8
  per modello: (eredita)=471, opus=14, sonnet=6

SEGNALI
  - più compattazioni che sessioni (sessioni troppo lunghe): alfa/piattaforma
  - gli agenti sono quasi tutti generici: definisci agenti specializzati con un modello più economico
  - quasi nessun agente cambia modello: letture e ricerche girano sul modello più costoso
```

Per ogni segnale la skill propone la correzione: chiudere le sessioni prima salvando lo stato in un file, definire quattro agenti specializzati (lettura, ricerca, esecuzione, revisione) ognuno con il modello minimo che basta, e la regola per farli scegliere.

## diagnosi-contesto

Un progetto si dovrebbe aprire leggendo tre file brevi (regole, stato, indice), non esplorando le cartelle. Funziona finché quei file sono aggiornati: quando l'indice punta a cose che non esistono più, Claude smette di fidarsi e torna a leggere tutto.

```
PROGETTO                                 SESS LETTURE /SESS RILETTE CONTESTO SOLO LETTI
clienti/alfa                               29     218     7     47%      10%        70%
clienti/beta                               13      53     4     43%      26%        73%
esperimenti/gamma                           3      50    16      0%       0%        98%
```

```
== clienti/alfa
   note: 501   ferme da oltre 30g: 139
   regole  CLAUDE.md  (54 righe, aggiornato 13g fa)
   stato   STATO.md  (45 righe, aggiornato 0g fa)
   indice  Alfa — Indice.md  (85 righe, aggiornato 29g fa)
   SEGNALI:
    - l'indice punta a 4 cose che non esistono: app/, prototipo/, documentazione/
    - 31 note create o cambiate dopo l'ultimo aggiornamento dell'indice e non citate lì
    - 11 note oltre 400 righe (costose da leggere per intero)
```

La skill misura, poi rimette in pari i tre file nell'ordine giusto (indice, stato, regole) senza cancellare né spostare note, e propone sei regole di lettura: cercare prima di leggere, non rileggere, leggere solo l'intervallo che serve dei file lunghi.

## smista-richieste

Su un progetto grande, un blocco di richieste va storto in modo prevedibile: si parte dalla prima e si legge codice, a metà elenco il contesto è pieno, e i controlli si applicano a memoria, alcuni a tutto e altri dimenticati.

La skill ragiona in quattro tempi e legge codice solo dal terzo:

| Tempo | Cosa succede |
|---|---|
| Inventario | una riga per richiesta: cosa, tipo, dove, dimensione, cosa non si sa. Ancora nessun file aperto |
| Ordine | doppioni e contraddizioni segnalati subito; richieste sugli stessi file in fila, quelle indipendenti in parallelo |
| Controlli | per ogni richiesta, solo le righe della matrice del progetto che scattano **in base a ciò che tocca** |
| Resoconto | una riga per richiesta: esito, controlli passati, saltati o falliti e perché |

I controlli sono divisi in tre famiglie, trattate in modo diverso: **meccanici** (un comando, una volta per ramo, alla fine), **di giudizio** (un elenco puntuale di domande, dato a un agente di revisione insieme al diff) e **dell'utente** (produzione, scelte di prodotto, comunicazioni al cliente: si prepara e ci si ferma).

La matrice vive nel progetto come `CONTROLLI.md`; la skill ne porta un modello. È l'unico posto dove i controlli si accumulano, così le regole del progetto restano brevi.

---

## Usare solo gli script

```bash
python3 ~/.claude/skills/gestisci-skills/uso.py --giorni 60
python3 ~/.claude/skills/diagnosi-mcp/uso_mcp.py
python3 ~/.claude/skills/diagnosi-sessioni/sessioni.py --mb 30
python3 ~/.claude/skills/diagnosi-contesto/letture.py --progetto alfa
python3 ~/.claude/skills/diagnosi-contesto/wiki.py ~/progetti/alfa
```

Tutti tranne `wiki.py` accettano `--json`.

## Limiti

- I conteggi vedono solo le sessioni ancora presenti sul computer: non quelle cancellate o fatte altrove.
- "Ultimo uso" e peso in MB sono indicatori, non misure al minuto o al token.
- I nomi dei progetti negli esempi sono inventati.

## Licenza

MIT
