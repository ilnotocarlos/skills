# <Progetto> — matrice dei controlli

Quali controlli scattano in base a **ciò che una modifica tocca**. Una riga per controllo. I dettagli restano dove sono già scritti: qui c'è il rimando.

| Se la modifica tocca… | Controlla | Come | Chi |
|---|---|---|---|
| qualsiasi codice | tipi, lint, test, build | `<comando unico>`, una volta per ramo | meccanico |
| schema o regole dei dati | test sulle regole, permessi, migrazione numerata e registrata | `<comando>` + elenco in `<file>#<sezione>` | meccanico + giudizio |
| un modulo o un'azione che scrive | input validato, la scrittura arriva davvero ai dati | `<file>#<sezione>` | giudizio |
| interfaccia visibile | componenti e token del design system, tutte le lingue, voce di menu | `<comandi>` + prova nel browser | meccanico + giudizio |
| dati personali | niente dati sensibili in file, richieste di modifica o mail | `<file>#<sezione>` | giudizio |
| qualcosa che l'utente finale nota | manuale, nota di rilascio, comunicazione al cliente | bozza pronta, invio all'utente | utente |
| produzione | applicazione delle modifiche ai dati, rilascio | comando pronto, lo lancia l'utente | utente |

**Chi**: *meccanico* = un comando dà l'esito; *giudizio* = serve rileggere con un elenco di domande; *utente* = si prepara e ci si ferma.
