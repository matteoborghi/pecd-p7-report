# -*- coding: utf-8 -*-
"""Copia in latex/figures/ le figure che il report usa davvero (PDF, e PNG di KiCad).

Le sorgenti vivono in cartelle con spazi nel nome ("01 - PLECS figures/01 - Electrical") e LaTeX
ci convive male; un report da consegnare conviene che sia autocontenuto. Lo script copia solo
le figure citate con \\includegraphics dai capitoli che main.tex include, rinominandole con un
prefisso che dice da dove vengono (plecs_, spice_, kicad_, termica_).

Va rilanciato dopo ogni rigenerazione delle figure. Segnala le figure citate senza sorgente e
quelle presenti in figures/ ma non piu' citate; non cancella nulla.
"""
import hashlib
import re
import shutil
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent.parent
DEST = QUI / "figures"

SORGENTI = [
    (RADICE / "03 - Report" / "01 - PLECS figures" / "01 - Electrical", "plecs"),
    (RADICE / "03 - Report" / "01 - PLECS figures" / "02 - Thermal", "plecs"),
    (RADICE / "05 - Ausiliari" / "figure", "spice"),
    # schema, strati e viste 3D del modulo (02 - KiCAD/figure_report.py e figure_modulo.py)
    (RADICE / "02 - KiCAD" / "figure", "kicad"),
    # raffreddamento e vita dei componenti (04 - Python/termica)
    (RADICE / "04 - Python" / "termica" / "figure", "termica"),
]


def impronta(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def figure_citate():
    """Nomi dei file citati da \\includegraphics nei capitoli inclusi da main.tex."""
    main = (QUI / "main.tex").read_text(encoding="utf-8")
    capitoli = re.findall(r"^\\input\{(chapters/[^}]+)\}", main, re.M)
    citate = set()
    for c in capitoli:
        t = (QUI / (c + ".tex")).read_text(encoding="utf-8")
        for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", t):
            citate.add(Path(m.group(1)).name)
    return citate


def main():
    DEST.mkdir(exist_ok=True)
    citate = figure_citate()
    copiati, invariati, mancanti, trovate = 0, 0, [], set()

    for cartella, prefisso in SORGENTI:
        if not cartella.is_dir():
            mancanti.append(str(cartella))
            continue
        png = list(cartella.glob("*.png")) if prefisso == "kicad" else []
        for src in sorted(list(cartella.glob("*.pdf")) + png):
            nome = "%s_%s" % (prefisso, src.name.replace(" ", "_"))
            if nome not in citate:
                continue
            if nome in trovate:
                print("!! collisione di nome:", nome)
                return 1
            trovate.add(nome)
            dst = DEST / nome
            if dst.exists() and impronta(dst) == impronta(src):
                invariati += 1
                continue
            shutil.copy2(src, dst)
            print("  copiata %s" % nome)
            copiati += 1

    print("\n%d copiate, %d gia' aggiornate, %d citate dal report" % (copiati, invariati, len(citate)))
    senza = sorted(citate - trovate)
    if senza:
        print("citate dal report ma senza sorgente:")
        for n in senza:
            print("  ", n)
    for m in mancanti:
        print("cartella sorgente mancante:", m)
    orfane = sorted(p.name for p in list(DEST.glob("*.pdf")) + list(DEST.glob("*.png")) if p.name not in citate)
    if orfane:
        print("in figures/ ma non piu' citate (rimuovere a mano se inutili):")
        for o in orfane:
            print("  ", o)
    return 1 if senza else 0


if __name__ == "__main__":
    sys.exit(main())
