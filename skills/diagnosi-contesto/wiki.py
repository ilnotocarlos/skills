#!/usr/bin/env python3
"""Controlla i file di contesto di una cartella di progetto: regole, stato, indice e note.

Verifica che chi apre il progetto possa orientarsi leggendo pochi file aggiornati.
Solo lettura, nessuna richiesta di rete.

Uso:  python3 wiki.py <cartella> [<cartella> ...] [--giorni 30] [--righe 400]
"""
import argparse, collections, os, re, sys, time

SALTA = {"node_modules", ".git", ".next", ".turbo", ".venv", "dist", "build", ".build", "__pycache__", ".obsidian",
         "test-results", "playwright-report", "archivio", "Archivio", "vendor", "Pods", "DerivedData",
         ".claude", ".agents", "worktrees"}
WIKILINK = re.compile(r"\[\[([^\]|#]+)")
PERCORSO = re.compile(r"`([^`\s]+/[^`\s]*|[^`\s]+\.(?:md|pdf|pptx|docx|xlsx))`|\]\(([^)#\s]+)\)")


def note(radice):
    """[(percorso relativo, righe, timestamp)] di tutti i file .md, senza cartelle ricreabili o archiviate."""
    out = []
    for d, sotto, file in os.walk(radice):
        sotto[:] = [s for s in sotto if s not in SALTA and not s.endswith("-venv")]
        for f in file:
            if f.endswith(".md"):
                p = os.path.join(d, f)
                try:
                    with open(p, errors="ignore") as fh:
                        righe = sum(1 for _ in fh)
                    out.append((os.path.relpath(p, radice), righe, os.path.getmtime(p)))
                except OSError:
                    pass
    return out


def controlla(radice, giorni, max_righe):
    ora, segnali = time.time(), []
    eta = lambda ts: int((ora - ts) / 86400)
    tutte = note(radice)
    per_nome = collections.defaultdict(list)
    for p, _, _ in tutte:
        per_nome[os.path.basename(p)[:-3].lower()].append(p)
    in_radice = {p: (r, t) for p, r, t in tutte if os.sep not in p}

    def trova(*nomi):
        for p in in_radice:
            if any(p.lower() == n or p.lower().endswith(n) for n in nomi):
                return p
    regole, stato = trova("claude.md", "agents.md"), trova("stato.md")
    indice = trova("indice.md", "index.md") or trova("readme.md")

    print(f"\n== {radice}")
    print(f"   note: {len(tutte)}   ferme da oltre {giorni}g: {sum(1 for _, _, t in tutte if eta(t) > giorni)}")
    for etichetta, p, limite in (("regole", regole, 80), ("stato", stato, 60), ("indice", indice, 150)):
        if not p:
            print(f"   {etichetta:7} MANCA")
            segnali.append(f"manca il file di {etichetta}")
            continue
        r, t = in_radice[p]
        print(f"   {etichetta:7} {p}  ({r} righe, aggiornato {eta(t)}g fa)")
        if r > limite:
            segnali.append(f"{p} ha {r} righe (oltre {limite}): viene letto a ogni sessione, va accorciato")
    if stato and eta(in_radice[stato][1]) > giorni and any(eta(t) <= giorni for p, _, t in tutte if p != stato):
        segnali.append(f"{stato} è fermo da {eta(in_radice[stato][1])}g ma altre note sono cambiate dopo: lo stato non è aggiornato")

    if indice:
        testo = open(os.path.join(radice, indice), errors="ignore").read()
        rotti = [w.strip() for w in WIKILINK.findall(testo) if os.path.basename(w.strip()).lower() not in per_nome
                 and not os.path.exists(os.path.join(radice, w.strip()))]
        for a, b in PERCORSO.findall(testo):
            p = (a or b).strip()
            if "/" not in p or p.startswith(("http", "mailto", "#", "~", "/")) or "<" in p or "*" in p:  # nomi senza cartella: non verificabili
                continue
            if not os.path.exists(os.path.join(radice, p)):
                rotti.append(p)
        if rotti:
            segnali.append(f"l'indice punta a {len(rotti)} cose che non esistono: " + ", ".join(sorted(set(rotti))[:6]))
        cartelle = [d for d in sorted(os.listdir(radice)) if os.path.isdir(os.path.join(radice, d)) and not d.startswith(".") and d not in SALTA]
        assenti = [d for d in cartelle if d not in testo]
        if assenti:
            segnali.append("cartelle non citate nell'indice: " + ", ".join(assenti))
        freschi = [p for p, _, t in tutte if t > in_radice[indice][1] + 86400 and os.path.basename(p)[:-3] not in testo and p not in (stato, regole)]
        if len(freschi) > 5:
            segnali.append(f"{len(freschi)} note create o cambiate dopo l'ultimo aggiornamento dell'indice e non citate lì")

    grandi = sorted(((r, p) for p, r, _ in tutte if r > max_righe), reverse=True)
    if grandi:
        segnali.append(f"{len(grandi)} note oltre {max_righe} righe (costose da leggere per intero): " + ", ".join(f"{p} ({r})" for r, p in grandi[:4]))
    doppi = {n: ps for n, ps in per_nome.items() if len(ps) > 1 and n not in ("readme", "claude", "index", "stato", "changelog", "license")}
    if doppi:
        segnali.append(f"{len(doppi)} nomi di nota ripetuti (i link [[nome]] diventano ambigui): " + ", ".join(sorted(doppi)[:6]))
    print("   SEGNALI:" + ("" if segnali else " nessuno"))
    for s in segnali:
        print("    - " + s)
    return len(segnali)


if __name__ == "__main__":
    assert WIKILINK.findall("vedi [[nota-a]] e [[b|testo]]") == ["nota-a", "b"]
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cartelle", nargs="+")
    ap.add_argument("--giorni", type=int, default=30)
    ap.add_argument("--righe", type=int, default=400)
    a = ap.parse_args()
    for c in a.cartelle:
        if os.path.isdir(c):
            controlla(c.rstrip("/"), a.giorni, a.righe)
        else:
            print(f"salto (non è una cartella): {c}", file=sys.stderr)
