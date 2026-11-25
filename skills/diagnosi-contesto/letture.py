#!/usr/bin/env python3
"""Quanti file legge Claude Code nei tuoi progetti, quali rilegge, e quanto usa i file di contesto.

Legge le trascrizioni in ~/.claude/projects. Solo lettura, nessuna richiesta di rete.

Uso:  python3 letture.py [--progetto testo] [--json] [--livelli 2] [--top 12]
"""
import argparse, collections, glob, json, os, re, sys

CLAUDE = os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
CWD = re.compile(r'"cwd":"((?:[^"\\]|\\.)*)"')
LETTURA = re.compile(r'"name":"Read","input":\{"file_path":"((?:[^"\\]|\\.)*)"')
MODIFICA = re.compile(r'"name":"(?:Edit|Write|MultiEdit)","input":\{[^{}]*?"file_path":"((?:[^"\\]|\\.)*)"')
TEMPORANEI = re.compile(r"^(/private)?/(tmp|var/folders)/|/scratchpad/")
# File pensati per dare il contesto senza leggere il resto
CONTESTO = re.compile(r"(^|/)(CLAUDE|STATO|README|AGENTS|MEMORY)\.md$|Indice\.md$|(^|/)(index|stato-progetto)\.md$", re.I)


def progetto(cwd, livelli):
    home = os.path.expanduser("~")
    p = cwd[len(home):] if cwd.startswith(home) else cwd
    return "/".join([x for x in p.split("/") if x][-livelli:]) or "/"


def percorso(grezzo):
    try:
        return json.loads('"' + grezzo + '"')
    except ValueError:
        return grezzo


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--progetto", help="mostra solo i progetti il cui nome contiene questo testo")
    ap.add_argument("--livelli", type=int, default=2)
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    P = collections.defaultdict(lambda: {"sessioni": 0, "letture": 0, "riletture": 0, "contesto": 0, "mai_modificati": 0,
                                         "letti": 0, "file": collections.Counter()})
    for f in glob.glob(os.path.join(CLAUDE, "projects", "*", "*.jsonl")):
        nome, letti, modificati = None, collections.Counter(), set()
        try:
            with open(f, errors="ignore") as fh:
                for riga in fh:
                    if nome is None:
                        m = CWD.search(riga)
                        if m:
                            nome = progetto(percorso(m.group(1)), a.livelli)
                    if '"tool_use"' not in riga:
                        continue
                    for m in LETTURA.finditer(riga):
                        x = percorso(m.group(1))
                        if not TEMPORANEI.search(x):  # schermate e file di prova: rileggerli è normale
                            letti[x] += 1
                    for m in MODIFICA.finditer(riga):
                        modificati.add(percorso(m.group(1)))
        except OSError:
            continue
        nome = nome or "(sconosciuto)"
        if a.progetto and a.progetto.lower() not in nome.lower():
            continue
        p = P[nome]
        p["sessioni"] += 1
        p["letture"] += sum(letti.values())
        p["riletture"] += sum(n - 1 for n in letti.values())          # stesso file riletto nella stessa sessione
        p["contesto"] += sum(n for x, n in letti.items() if CONTESTO.search(x))
        p["letti"] += len(letti)
        p["mai_modificati"] += sum(1 for x in letti if x not in modificati)
        p["file"].update(letti)
    if a.json:
        json.dump({k: {**v, "file": dict(v["file"].most_common(a.top))} for k, v in P.items()}, sys.stdout, indent=2, ensure_ascii=False)
        return
    print(f"{'PROGETTO':40} {'SESS':>4} {'LETTURE':>7} {'/SESS':>5} {'RILETTE':>7} {'CONTESTO':>8} {'SOLO LETTI':>10}")
    for n, p in sorted(P.items(), key=lambda x: -x[1]["letture"])[:20]:
        if not p["letture"]:
            continue
        L = p["letture"]
        print(f"{n[:40]:40} {p['sessioni']:>4} {L:>7} {L // p['sessioni']:>5} {p['riletture'] * 100 // L:>6}% {p['contesto'] * 100 // L:>7}% "
              f"{p['mai_modificati'] * 100 // max(p['letti'], 1):>9}%")
    print("\nRILETTE = letture ripetute dello stesso file nella stessa sessione")
    print("CONTESTO = letture di file di contesto (CLAUDE.md, STATO.md, README, indici)")
    print("SOLO LETTI = file letti e mai modificati in quella sessione")
    tot = collections.Counter()
    for p in P.values():
        tot.update(p["file"])
    print(f"\nFILE PIÙ LETTI (primi {a.top})")
    home = os.path.expanduser("~")
    for x, n in tot.most_common(a.top):
        print(f"  {n:>4}  {x.replace(home, '~')}")


if __name__ == "__main__":
    assert LETTURA.findall('{"type":"tool_use","name":"Read","input":{"file_path":"/a/b.md"}}') == ["/a/b.md"]
    assert CONTESTO.search("/x/STATO.md") and CONTESTO.search("Alfa — Indice.md") and not CONTESTO.search("/x/src/app.ts")
    main()
