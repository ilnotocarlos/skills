#!/usr/bin/env python3
"""Quali skill di Claude Code sono installate e quanto le usi davvero.

Legge le trascrizioni in ~/.claude/projects e le skill in ~/.claude/skills.
Solo lettura: non installa, non aggiorna e non rimuove nulla.

Uso:  python3 uso.py [--giorni 30] [--json]
"""
import argparse, collections, glob, json, os, re, sys, time

CLAUDE = os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
# Skill lanciata dal modello (strumento Skill) oppure digitata dall'utente (/nome)
CHIAMATA = re.compile(r'"name":"Skill","input":\{"skill":"([^"]+)"|<command-name>/([^<\s]+)</command-name>')


def uso():
    """{nome: [conteggio, timestamp ultimo uso]} da tutte le trascrizioni."""
    u = collections.defaultdict(lambda: [0, 0.0])
    for f in glob.glob(os.path.join(CLAUDE, "projects", "*", "*.jsonl")):
        try:
            quando = os.path.getmtime(f)  # shortcut: data del file, non della riga; passare al campo timestamp se serve il giorno esatto
            with open(f, errors="ignore") as fh:
                for riga in fh:
                    if '"Skill"' not in riga and "<command-name>" not in riga:
                        continue
                    for m in CHIAMATA.finditer(riga):
                        r = u[m.group(1) or m.group(2)]
                        r[0] += 1
                        r[1] = max(r[1], quando)
        except OSError:
            continue
    return u


def installate():
    """[(nome, tipo, timestamp installazione)] delle skill personali."""
    base = os.path.join(CLAUDE, "skills")
    try:  # registro di `npx skills`: una skill gestita può essere una copia, non solo un link
        gestite = set(json.load(open(os.path.expanduser("~/.agents/.skill-lock.json")))["skills"])
    except (OSError, ValueError, KeyError):
        gestite = set()
    out = []
    for nome in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        p = os.path.join(base, nome)
        if not os.path.isfile(os.path.join(p, "SKILL.md")):
            continue  # cartelle di servizio, link rotti
        tipo = "gestita" if os.path.islink(p) or nome in gestite else "cartella"
        out.append((nome, tipo, os.lstat(p).st_mtime))
    return out


def giorni(ts, ora):
    return int((ora - ts) / 86400)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--giorni", type=int, default=30, help="soglia per 'mai usata' e 'ferma' (default 30)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    ora, u, righe = time.time(), uso(), []
    for nome, tipo, inst in installate():
        n, ultimo = u.get(nome, (0, 0.0))
        eta = giorni(inst, ora)
        if n == 0:
            esito = "mai usata" if eta >= a.giorni else "nuova"
        else:
            esito = "ferma" if giorni(ultimo, ora) >= a.giorni else "in uso"
        righe.append({"skill": nome, "tipo": tipo, "usi": n, "ultimo_uso_giorni": giorni(ultimo, ora) if n else None,
                      "installata_da_giorni": eta, "esito": esito})
    plugin = collections.Counter()
    for nome, (n, _) in u.items():
        if ":" in nome:
            plugin[nome.split(":")[0]] += n
    if a.json:
        json.dump({"skill": righe, "plugin": dict(plugin)}, sys.stdout, indent=2, ensure_ascii=False)
        return
    righe.sort(key=lambda r: (-r["usi"], r["skill"]))
    print(f"{'SKILL':32} {'TIPO':9} {'USI':>4} {'ULTIMO USO':>11} {'INSTALLATA':>11}  ESITO")
    for r in righe:
        ult = f"{r['ultimo_uso_giorni']}g fa" if r["usi"] else "-"
        print(f"{r['skill'][:32]:32} {r['tipo']:9} {r['usi']:>4} {ult:>11} {str(r['installata_da_giorni']) + 'g fa':>11}  {r['esito']}")
    if plugin:
        print("\nSkill dei plugin (si tolgono disattivando il plugin):")
        for nome, n in plugin.most_common():
            print(f"  {nome:30} {n:>4} usi")
    da_togliere = [r["skill"] for r in righe if r["esito"] in ("mai usata", "ferma")]
    if da_togliere:
        print(f"\nCandidate alla rimozione (soglia {a.giorni} giorni): " + ", ".join(da_togliere))


if __name__ == "__main__":
    # autoverifica del riconoscimento delle chiamate
    assert [m.group(1) or m.group(2) for m in CHIAMATA.finditer(
        '{"name":"Skill","input":{"skill":"a:b"}} <command-name>/c-d</command-name>')] == ["a:b", "c-d"]
    main()
