---
name: gestisci-skills
description: Gestisce tutto il ciclo di vita delle skill di Claude Code - cerca e installa skill nuove, aggiorna quelle installate, misura quali usi davvero e rimuove quelle ferme. Usala quando l'utente chiede "c'è una skill per X", "trova una skill", "aggiorna le skill", "quali skill uso", "fai pulizia delle skill", "togli le skill che non servono".
---

# Gestisci skills

Cinque azioni. Scegli quella che corrisponde alla richiesta; per "fai pulizia" esegui **Controlla** e poi **Rimuovi**.

Lo strumento sottostante è `npx skills` (ecosistema aperto, catalogo su https://skills.sh). `uso.py` sta nella cartella di questa skill.

## 1. Cerca
```bash
npx -y skills find <parole chiave>            # es. "react performance"
npx -y skills add <owner/repo> --list         # elenca le skill di un repository senza installare
```
Prima di proporre un risultato controlla: quante installazioni ha, chi la pubblica, quando è stata aggiornata. Presenta al massimo tre candidate con una riga ciascuna su cosa fa. Se non trovi nulla di affidabile, dillo e offri di scriverne una (`npx -y skills init <nome>`).

## 2. Installa
```bash
npx -y skills add <owner/repo@skill> -g -y
```
Installa solo dopo che l'utente ha scelto. Prima leggi il `SKILL.md` della candidata: una skill è testo di istruzioni che entrerà nelle sessioni, quindi segnala qualunque passaggio che esegue comandi, scarica codice o invia dati all'esterno.

## 3. Aggiorna
```bash
npx -y skills list -g          # cosa è installato e da dove
npx -y skills update -g -y     # aggiorna tutte le skill gestite
```
Aggiorna solo le skill installate con `npx skills` (in `uso.py` hanno tipo `gestita`). Le skill di tipo `cartella` sono copie locali: non hanno una fonte da cui aggiornarsi, dillo invece di fingere di averle aggiornate. Riporta quali sono cambiate.

## 4. Controlla l'uso
```bash
python3 <cartella di questa skill>/uso.py            # tabella
python3 <cartella di questa skill>/uso.py --giorni 60 --json
```
Legge le trascrizioni locali e, per ogni skill personale, mostra tipo, numero di usi, ultimo uso, età ed esito:

| Esito | Significato |
|---|---|
| `in uso` | usata entro la soglia |
| `ferma` | usata in passato, non più entro la soglia |
| `mai usata` | installata da più della soglia, zero usi |
| `nuova` | zero usi ma installata da poco: non è ancora giudicabile |

In fondo elenca gli usi delle skill dei plugin, raggruppati per plugin.

## 5. Rimuovi
Proponi la rimozione solo per `mai usata` e `ferma`. **Mostra l'elenco e aspetta la conferma dell'utente prima di togliere qualsiasi cosa.**

| Tipo | Come si toglie |
|---|---|
| `gestita` | `npx -y skills remove <nome> -g -y` |
| `cartella` | sposta `~/.claude/skills/<nome>` nel Cestino (non `rm`): resta recuperabile |
| skill di un plugin (`plugin:nome`) | non si toglie da sola: si disattiva l'intero plugin con `claude plugin disable <plugin>` |

Dopo la rimozione rilancia `uso.py` e riporta cosa resta. Le modifiche valgono dalle sessioni nuove.

## Limiti da dichiarare
- Il conteggio vede solo le trascrizioni ancora presenti su questo computer.
- Una skill a zero usi può essere stata appena installata: per questo esiste l'esito `nuova`.
