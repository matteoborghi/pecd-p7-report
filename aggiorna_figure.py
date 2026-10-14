# -*- coding: utf-8 -*-
"""Copia le figure (PDF, e PNG per le viste 3D) dentro il progetto LaTeX con nomi privi di spazi.

I PDF vettoriali vivono in cartelle che hanno spazi nel nome
("01 - PLECS figures/01 - Electrical"). LaTeX ci convive male, e un report
da consegnare conviene che sia autocontenuto. Questo script li copia in
latex/figures/ rinominandoli con un prefisso che dice da dove vengono, e
risolvendo la collisione fra il 12 di PLECS e il 12 di SPICE.

Va rilanciato dopo ogni rigenerazione delle figure.
"""
import hashlib
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
    # schema, strati e viste 3D del progetto KiCad (02 - KiCAD/figure_report.py)
    (RADICE / "02 - KiCAD" / "figure", "kicad"),
    # raffreddamento e vita dei componenti (04 - Python/termica, 11/10/2026)
    (RADICE / "04 - Python" / "termica" / "figure", "termica"),
    # emissioni condotte stimate (04 - Python/emc, 11/10/2026)
    (RADICE / "04 - Python" / "emc" / "figure", "emc"),
]


def impronta(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def main():
    DEST.mkdir(exist_ok=True)
    copiati, invariati, mancanti = 0, 0, []

    visti = set()
    for cartella, prefisso in SORGENTI:
        if not cartella.is_dir():
            mancanti.append(str(cartella))
            continue
        # PNG solo dalle viste 3D di KiCad: nelle cartelle PLECS ci sono schermate da decine di MB
        png = list(cartella.glob("*.png")) if prefisso == "kicad" else []
        for src in sorted(list(cartella.glob("*.pdf")) + png):
            nome = "%s_%s" % (prefisso, src.name.replace(" ", "_"))
            if nome in visti:
                print("!! collisione di nome:", nome)
                return 1
            visti.add(nome)
            dst = DEST / nome
            if dst.exists() and impronta(dst) == impronta(src):
                invariati += 1
                continue
            shutil.copy2(src, dst)
            print("  copiata %s" % nome)
            copiati += 1

    # figure non piu' prodotte: si segnalano, non si cancellano
    orfane = [p.name for p in list(DEST.glob("*.pdf")) + list(DEST.glob("*.png")) if p.name not in visti]

    print("\n%d copiate, %d gia' aggiornate" % (copiati, invariati))
    if mancanti:
        print("cartelle sorgente mancanti:")
        for m in mancanti:
            print("  ", m)
    if orfane:
        print("in figures/ ma non piu' prodotte (rimuovere a mano se inutili):")
        for o in orfane:
            print("  ", o)
    print("\nfigure disponibili per il report: %d" % len(visti))
    for n in sorted(visti):
        print("  ", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
