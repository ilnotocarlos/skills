#!/usr/bin/env python3
"""Quali server MCP usi davvero, e in quali progetti.

Legge le trascrizioni in ~/.claude/projects. Solo lettura, nessuna richiesta di rete.

Uso:  python3 uso_mcp.py [--json] [--livelli 2]
"""
import argparse, collections, glob, json, os, re, sys

CLAUDE = os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
CHIAMATA = re.compile(r'"type":"tool_use","id":"[^"]+","name":"mcp__(.+?)__[^"]*"')
CWD = re.compile(r'"cwd":"((?:[^"\\]|\\.)*)"')


def progetto(cwd, livelli):
    """Accorcia il percorso alle ultime `livelli` cartelle, senza la home."""
    home = os.path.expanduser("~")
    p = cwd[len(home):] if cwd.startswith(home) else cwd
    return "/".join([x for x in p.split("/") if x][-livelli:]) or "/"


def leggi(livelli):
    uso = collections.defaultdict(collections.Counter)   # server -> progetto -> chiamate
    sessioni = collections.Counter()                      # progetto -> sessioni
    for f in glob.glob(os.path.join(CLAUDE, "projects", "*", "*.jsonl")):
        prog, trovati = None, collections.Counter()
        try:
            with open(f, errors="ignore") as fh:
                for riga in fh:
                    if prog is None:
                        m = CWD.search(riga)
                        if m:
                            prog = progetto(json.loads('"' + m.group(1) + '"'), livelli)
                    if '"tool_use"' in riga and "mcp__" in riga:
                        for m in CHIAMATA.finditer(riga):
                            trovati[m.group(1)] += 1
        except OSError:
            continue
        prog = prog or "(sconosciuto)"
        sessioni[prog] += 1
        for server, n in trovati.items():
            uso[server][prog] += n
    return uso, sessioni


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--livelli", type=int, default=2, help="quante cartelle finali usare come nome del progetto (default 2)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    uso, sessioni = leggi(a.livelli)
    if a.json:
        json.dump({"server": {s: dict(c) for s, c in uso.items()}, "sessioni": dict(sessioni)}, sys.stdout, indent=2, ensure_ascii=False)
        return
    print(f"{sum(sessioni.values())} sessioni in {len(sessioni)} progetti\n")
    print(f"{'SERVER':38} {'CHIAMATE':>8} {'PROGETTI':>8}  DOVE (primi 3)")
    for s, c in sorted(uso.items(), key=lambda x: -sum(x[1].values())):
        dove = ", ".join(f"{p}={n}" for p, n in c.most_common(3))
        print(f"{s[:38]:38} {sum(c.values()):>8} {len(c):>8}  {dove}")
    print("\nPER PROGETTO (server usati almeno una volta)")
    per = collections.defaultdict(dict)
    for s, c in uso.items():
        for p, n in c.items():
            per[p][s] = n
    for p in sorted(per, key=lambda p: -sum(per[p].values())):
        print(f"  {p}: " + ", ".join(f"{s}={n}" for s, n in sorted(per[p].items(), key=lambda x: -x[1])))
    vuoti = sorted(p for p in sessioni if p not in per)
    if vuoti:
        print("\nProgetti che non hanno mai chiamato un server MCP: " + ", ".join(vuoti))


if __name__ == "__main__":
    assert CHIAMATA.findall('{"type":"tool_use","id":"x","name":"mcp__claude_ai_Gmail__search_threads"}') == ["claude_ai_Gmail"]
    assert progetto(os.path.expanduser("~/a/b/c"), 2) == "b/c"
    main()
