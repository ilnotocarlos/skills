# Skills for Claude Code

**English** · [Italiano](README.it.md)

Skills that keep Claude Code itself in order: what is installed, what gets loaded into every session, and how sessions are actually used.

They came out of a real clean-up. On one machine with 260 work sessions, the diagnosis found 79 MCP servers loaded at every start (each project needed between 2 and 8), skills that were installed and never opened, and 491 subagents launched, 95% of them on the most expensive model. Each skill here ships the script that produced those numbers and the fixes that worked.

```bash
npx skills add ilnotocarlos/skills -g
```

To install just one: `npx skills add ilnotocarlos/skills -g --skill diagnosi-mcp`

| Skill | Ask Claude | You get |
|---|---|---|
| [gestisci-skills](skills/gestisci-skills) | "clean up my skills" | which skills you really use, updates, removal of the idle ones |
| [diagnosi-mcp](skills/diagnosi-mcp) | "too many MCP servers, clean them up" | real usage of each server per project, duplicates, per-project rules |
| [diagnosi-sessioni](skills/diagnosi-sessioni) | "optimize how I use Claude Code" | sessions that run too long, generic subagents, wasted model spend |
| [diagnosi-contesto](skills/diagnosi-contesto) | "you read too many files, fix the project wiki" | how much gets read and re-read, project index and status brought back up to date |
| [smista-richieste](skills/smista-richieste) | "here are fifteen requests, organize them" | an inventory, an order, and for each request only the checks it really triggers |

All of them follow the same rule: **measure first, then propose, and change nothing without your yes.** The scripts only read local files (`~/.claude`) and make no network requests. You need Python 3 and Node; there are no dependencies to install.

> **Language.** The skill instructions and the script output are in Italian. The example output below is shown as the scripts print it; there is a [glossary](#glossary) at the end.

---

## gestisci-skills

*Manage skills.* Installing a skill takes ten seconds, so they pile up. Each one adds its description to every session, and after a few months you no longer know which ones you need.

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

| You ask | What happens |
|---|---|
| "is there a skill for changelogs?" | searches the open catalog and proposes at most three candidates, with install counts and author |
| "install that one" | reads its `SKILL.md` first and flags anything that runs commands or sends data, then installs |
| "update my skills" | updates the ones that have a source and tells you which cannot be updated |
| "remove the ones I don't need" | proposes only `mai usata` (never used) and `ferma` (idle), asks for confirmation, removes each the right way for its type |

A freshly installed skill is marked `nuova` (new) and is not proposed for removal. Skills copied in by hand go to the Trash, so they stay recoverable.

## diagnosi-mcp

*MCP diagnosis.* Account connectors, plugins and project files each declare MCP servers on their own. The usual result: dozens of servers loaded everywhere, many never authenticated, some duplicated.

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

From there the skill classifies each server (never used, duplicate, used in a few projects, used everywhere), proposes the rules, writes them into the settings files, and verifies with `claude mcp list` folder by folder.

It also records four Claude Code behaviors found by testing, which cost time if you don't know them:

- account connectors cannot be turned off everywhere and back on in one project, only the other way round;
- project settings are not inherited from parent folders;
- two sources of the same service hide each other: turn one off and the other appears;
- environment variables set in the settings also reach the shell of the open session and skew your tests.

## diagnosi-sessioni

*Session diagnosis.*

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

The three signals above read: more compactions than sessions (sessions run too long); almost all subagents are generic; almost no subagent switches model, so reading and searching run on the most expensive one.

For each signal the skill proposes the fix: close sessions earlier by saving the state to a file, define four specialized subagents (reading, research, execution, review) each on the cheapest model that is enough, and add the rule that makes Claude pick them.

## diagnosi-contesto

*Context diagnosis.* A project should open by reading three short files (rules, status, index), not by exploring folders. That works as long as those files are current: once the index points to things that no longer exist, Claude stops trusting it and goes back to reading everything.

```
PROGETTO                                 SESS LETTURE /SESS RILETTE CONTESTO SOLO LETTI
clienti/alfa                               29     218     7     47%      10%        70%
clienti/beta                               13      53     4     43%      26%        73%
esperimenti/gamma                           3      50    16      0%       0%        98%
```

Columns: file reads, reads per session, share that are re-reads of the same file in one session, share that are context files, share of files read but never edited.

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

Here: the index points to 4 things that do not exist, 31 notes changed after the index was last updated and are not listed in it, and 11 notes are over 400 lines.

The skill measures, then brings the three files back up to date in the right order (index, status, rules) without deleting or moving any note, and proposes six reading rules, such as: search before reading, do not re-read, read only the range you need from long files.

## smista-richieste

*Triage requests.* On a large project, a batch of requests fails in a predictable way: you start from the first one and read code, the context is full halfway down the list, and checks are applied from memory, some to everything and some forgotten.

The skill works in four steps and reads code only from the third:

| Step | What happens |
|---|---|
| Inventory | one row per request: what, type, where, size, what is unknown. No code opened yet |
| Order | duplicates and contradictions flagged first; requests on the same files in sequence, independent ones in parallel |
| Checks | for each request, only the rows of the project's check matrix that are triggered **by what it touches** |
| Report | one row per request: outcome, checks passed, checks skipped or failed and why |

Checks are split into three families, handled differently: **mechanical** (one command, once per branch, at the end), **judgment** (a specific list of questions, handed to a review subagent together with the diff), and **the user's** (production, product choices, messages to the client: prepared, then stop).

The matrix lives in the project as `CONTROLLI.md`; a template ships with the skill. It is the one place where checks accumulate, so the project rules can stay short.

---

## Using the scripts on their own

```bash
python3 ~/.claude/skills/gestisci-skills/uso.py --giorni 60
python3 ~/.claude/skills/diagnosi-mcp/uso_mcp.py
python3 ~/.claude/skills/diagnosi-sessioni/sessioni.py --mb 30
python3 ~/.claude/skills/diagnosi-contesto/letture.py --progetto alfa
python3 ~/.claude/skills/diagnosi-contesto/wiki.py ~/projects/alfa
```

All except `wiki.py` accept `--json`. `--giorni` is the threshold in days, `--progetto` filters by project name.

## Limits

- The counts only see sessions still on the machine: not deleted ones, and not ones run elsewhere.
- "Last used" and size in MB are indicators, not per-minute or per-token measurements.
- Project names in the examples are made up.

## Glossary

| Italian | English |
|---|---|
| usi, chiamate, letture | uses, calls, reads |
| ultimo uso, installata, `Ng fa` | last used, installed, N days ago |
| tipo: `gestita` / `cartella` | type: managed by `npx skills` / plain folder |
| esito: `in uso`, `ferma`, `mai usata`, `nuova` | verdict: in use, idle, never used, new |
| progetti, sessioni, compattazioni, lunghe | projects, sessions, compactions, long |
| agenti, generici, `(eredita)` | subagents, generic, inherits the main model |
| rilette, contesto, solo letti | re-read, context files, read only |
| regole, stato, indice, note | rules, status, index, notes |
| segnali | signals |

## License

MIT
