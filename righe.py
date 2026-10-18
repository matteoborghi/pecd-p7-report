# -*- coding: utf-8 -*-
"""Filetto sottile fra le righe del corpo delle tabelle (18/10/2026).

In ogni tabular/tabularx/longtable di un capitolo, fra \\midrule e \\bottomrule, aggiunge \\hl
dopo ogni fine riga tranne l'ultima, e mette \\zebra (piu' aria fra le righe) prima della
tabella se manca. Idempotente: le righe che hanno gia' \\hl non si toccano.

Uso:   python righe.py chapters/02_specifications.tex [altri file]
"""
import re
import sys
from pathlib import Path

AMB = re.compile(r"(\\begin\{(tabularx|tabular|longtable)\}.*?\\end\{\2\})", re.S)


def corpo(tab):
    i = tab.find("\\midrule")
    j = tab.rfind("\\bottomrule")
    if i < 0 or j < 0 or j < i:
        return tab
    testa, mezzo, coda = tab[:i], tab[i:j], tab[j:]
    righe = mezzo.split("\n")
    # indici delle righe che chiudono una riga di tabella
    fini = [k for k, r in enumerate(righe) if r.rstrip().endswith("\\\\")]
    for k in fini[:-1]:
        r = righe[k]
        if "\\hl" in r or (k + 1 < len(righe) and righe[k + 1].strip().startswith(("\\midrule", "\\hl"))):
            continue
        righe[k] = r.rstrip() + " \\hl"
    return testa + "\n".join(righe) + coda


def main():
    for nome in sys.argv[1:]:
        p = Path(nome)
        s = p.read_text(encoding="utf-8")
        n = 0

        def sost(m):
            nonlocal n
            n += 1
            return corpo(m.group(1))

        s = AMB.sub(sost, s)
        # \zebra prima di ogni tabella che non l'ha (dentro l'ambiente table, prima del tabular)
        s = re.sub(r"(?<!\\zebra\n)(\\begin\{(?:tabularx|tabular)\})", r"\\zebra\n\1", s)
        s = s.replace("\\zebra\n\\zebra\n", "\\zebra\n")
        p.write_text(s, encoding="utf-8", newline="\n")
        print(p.name, n, "tabelle")


if __name__ == "__main__":
    main()
