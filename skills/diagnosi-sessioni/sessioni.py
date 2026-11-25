#!/usr/bin/env python3
"""Salute delle sessioni di Claude Code: lunghezza, compattazioni, agenti e modelli.

Legge le trascrizioni in ~/.claude/projects. Solo lettura, nessuna richiesta di rete.

Uso:  python3 sessioni.py [--json] [--livelli 2] [--mb 20]
"""
import argparse, collections, glob, json, os, re, sys

CLAUDE = os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
CWD = re.compile(r'"cwd":"((?:[^"\\]|\\.)*)"')
AGENTE = re.compile(r'"name":"(?:Agent|Task)","input":\{')
TIPO = re.compile(r'"subagent_type":"([^"]+)"')
MODELLO = re.compile(r'"model":"([^"]+)"')


def progetto(cwd, livelli):
    home = os.path.expanduser("~")
    p = cwd[len(home):] if cwd.startswith(home) else cwd
    return "/".join([x for x in p.split("/") if x][-livelli:]) or "/"


def agenti_in(riga):
    """[(tipo, modello)] per ogni agente lanciato in una riga di trascrizione."""
    out = []
    for m in AGENTE.finditer(riga):
        pezzo = riga[m.end():m.end() + 6000]
        fine = pezzo.find('"type":"tool_use"')  # non sconfinare nella chiamata successiva
        pezzo = pezzo if fine < 0 else pezzo[:fine]
        t, mo = TIPO.search(pezzo), MODELLO.search(pezzo)
        out.append((t.group(1) if t else "(predefinito)", mo.group(1) if mo else "(eredita)"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--livelli", type=int, default=2)
    ap.add_argument("--mb", type=float, default=20, help="soglia in MB per 'sessione lunga' (default 20)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    prog = collections.defaultdict(lambda: {"sessioni": 0, "mb": 0.0, "compattazioni": 0, "lunghe": 0})
    tipi, modelli = collections.Counter(), collections.Counter()
    for f in glob.glob(os.path.join(CLAUDE, "projects", "*", "*.jsonl")):
        nome, comp = None, 0
        try:
            with open(f, errors="ignore") as fh:
                for riga in fh:
                    if nome is None:
                        m = CWD.search(riga)
                        if m:
                            nome = progetto(json.loads('"' + m.group(1) + '"'), a.livelli)
                    if '"isCompactSummary":true' in riga:
                        comp += 1
                    if '"subagent_type"' in riga or '"name":"Agent"' in riga or '"name":"Task"' in riga:
                        for t, mo in agenti_in(riga):
                            tipi[t] += 1
                            modelli[mo] += 1
            mb = os.path.getsize(f) / 1e6
        except OSError:
            continue
        p = prog[nome or "(sconosciuto)"]
        p["sessioni"] += 1; p["mb"] += mb; p["compattazioni"] += comp; p["lunghe"] += mb >= a.mb
    if a.json:
        json.dump({"progetti": prog, "agenti_per_tipo": tipi, "agenti_per_modello": modelli}, sys.stdout, indent=2, ensure_ascii=False)
        return
    tot = sum(p["sessioni"] for p in prog.values())
    print(f"{tot} sessioni, {sum(p['mb'] for p in prog.values()) / 1000:.1f} GB di trascrizioni\n")
    print(f"{'PROGETTO':44} {'SESS':>4} {'MB':>6} {'COMPATT.':>8} {'LUNGHE':>6}")
    for n, p in sorted(prog.items(), key=lambda x: -x[1]["mb"])[:20]:
        print(f"{n[:44]:44} {p['sessioni']:>4} {p['mb']:>6.0f} {p['compattazioni']:>8} {p['lunghe']:>6}")
    n_ag = sum(tipi.values())
    if n_ag:
        generici = tipi["general-purpose"] + tipi["(predefinito)"]
        print(f"\nAGENTI: {n_ag} lanciati, {generici} generici ({generici * 100 // n_ag}%), "
              f"{modelli['(eredita)']} sul modello principale ({modelli['(eredita)'] * 100 // n_ag}%)")
        print("  per tipo:    " + ", ".join(f"{t}={n}" for t, n in tipi.most_common(8)))
        print("  per modello: " + ", ".join(f"{t}={n}" for t, n in modelli.most_common()))
    print("\nSEGNALI")
    molte = [n for n, p in prog.items() if p["compattazioni"] > p["sessioni"]]
    if molte:
        print("  - più compattazioni che sessioni (sessioni troppo lunghe): " + ", ".join(molte))
    if n_ag >= 20 and generici * 100 // n_ag >= 70:
        print("  - gli agenti sono quasi tutti generici: definisci agenti specializzati con un modello più economico")
    if n_ag >= 20 and modelli["(eredita)"] * 100 // n_ag >= 80:
        print("  - quasi nessun agente cambia modello: letture e ricerche girano sul modello più costoso")
    if not molte and n_ag < 20:
        print("  - nessuno")


if __name__ == "__main__":
    assert agenti_in('{"name":"Agent","input":{"description":"x","subagent_type":"Explore","model":"haiku"}}') == [("Explore", "haiku")]
    assert agenti_in('{"name":"Task","input":{"prompt":"y"}}') == [("(predefinito)", "(eredita)")]
    main()
