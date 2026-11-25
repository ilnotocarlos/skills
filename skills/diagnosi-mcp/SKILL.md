---
name: diagnosi-mcp
description: Diagnosi dei server MCP e dei connettori di Claude Code - misura quali vengono usati davvero e in quali progetti, trova doppioni e server mai autenticati, e imposta regole per caricare in ogni progetto solo quelli che servono. Usala quando l'utente dice "troppi MCP", "le sessioni partono con tutti i connettori", "fai pulizia degli MCP", "quali MCP uso", o vuole ridurre contesto e tempi di avvio.
---

# Diagnosi MCP

Obiettivo: ogni progetto carica solo i server che usa. Procedi in ordine e **mostra la proposta prima di scrivere qualsiasi impostazione**.

## 1. Misura
```bash
python3 <cartella di questa skill>/uso_mcp.py      # chiamate per server e per progetto
claude mcp list                                     # server caricati qui, con stato
```
Nelle trascrizioni i nomi sono normalizzati: `claude.ai Gmail` diventa `claude_ai_Gmail`, `plugin:figma:figma` diventa `plugin_figma_figma`. Nelle impostazioni va scritto il nome esatto di `claude mcp list`.

## 2. Classifica ogni server
| Caso | Come si riconosce | Cosa proporre |
|---|---|---|
| Mai usato | zero chiamate, oppure `Needs authentication` / `Not configured` | spegnerlo ovunque |
| Doppione | stesso servizio da due fonti (connettore claude.ai, plugin, `.mcp.json` di progetto) | tenere quello più usato; se esiste quello di progetto, tenere quello |
| Usato in pochi progetti | chiamate concentrate in 1-3 progetti | accenderlo solo lì |
| Usato ovunque | chiamate in molti progetti | lasciarlo |

Controlla anche i plugin: uno solo può dichiarare decine di server. Se le sue skill non vengono usate, conviene disattivare il plugin intero (`"<nome>@<origine>": false` in `enabledPlugins`) invece di spegnere i server uno a uno.

## 3. Scrivi le regole
Fai prima una copia di ogni file di impostazioni che modifichi.

| Ambito | File | Chiave |
|---|---|---|
| Ovunque | `~/.claude/settings.json` | `"deniedMcpServers": [{"serverName": "nome esatto"}]` |
| Un progetto | `<progetto>/.claude/settings.local.json` | stessa chiave |
| Un progetto, tutti i connettori claude.ai | `<progetto>/.claude/settings.local.json` | `"disableClaudeAiConnectors": true` |
| Un plugin intero | `~/.claude/settings.json` | `"enabledPlugins": {"<nome>@<origine>": false}` |

Non modificare `~/.claude.json` mentre una sessione è aperta: Claude Code lo riscrive di continuo.

## 4. Verifica
Rilancia `claude mcp list` da ogni cartella toccata e confronta con la proposta. **Fallo sempre**: spegnere un server può farne comparire un altro (vedi sotto).

## Comportamenti verificati sul campo
- **Non esiste "spento ovunque, acceso dove serve" per i connettori claude.ai.** Se li spegni a livello utente (`disableClaudeAiConnectors` o `ENABLE_CLAUDEAI_MCP_SERVERS=false`), né le impostazioni di progetto né la variabile d'ambiente li riaccendono. Funziona solo il contrario: accesi di default, spenti progetto per progetto.
- **Le impostazioni di progetto non si ereditano dalle cartelle madri.** Valgono per le sessioni avviate esattamente da quella cartella: elenca a parte le sottocartelle da cui si lavora spesso.
- **I doppioni si nascondono a vicenda.** Quando due fonti offrono lo stesso servizio Claude Code ne mostra una sola; spegnendola compare l'altra. Dopo ogni modifica ricontrolla l'elenco e spegni anche quella.
- **Le variabili in `env` delle impostazioni arrivano anche alla shell della sessione in corso**: per le prove usa `env -u NOME claude mcp list`, altrimenti misuri il valore sbagliato.
- Le modifiche valgono dalle sessioni nuove.

## Limiti da dichiarare
Il conteggio vede solo le trascrizioni presenti su questo computer. Un server a zero chiamate può servire a un progetto appena iniziato: chiedi prima di spegnerlo dove l'utente non ha ancora storico.
