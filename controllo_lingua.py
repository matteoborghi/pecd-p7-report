# -*- coding: utf-8 -*-
"""Cerca parole italiane nel testo estratto dai PDF delle figure.

E' il controllo definitivo: non guarda il sorgente Python ma il PDF
prodotto, quindi cattura anche le stringhe costruite a runtime.
"""
import pathlib
import re
import subprocess
import sys

PDFTOTEXT = (r"C:\Users\acer\AppData\Local\Programs\MiKTeX\miktex\bin"
             r"\x64\pdftotext.exe")

# Parole italiane che non sono anche inglesi o simboli tecnici.
IT = re.compile(
    r"(?i)\b(misurat[oa]|simulat[oa]|analitic[oa]|teoric[oa]|stimat[oa]|"
    r"identificat[oa]|estrapolazione|estrapolat[oa]|tensione|corrente|"
    r"correnti|perdite|perdita|tempo|frequenza|temperatura|"
    r"potenza|rendimento|carico|valore|scelt[oa]|figura|tabella|capitolo|"
    r"commutazione|conduzione|fase|polo|regime|condensatore|liquido|caso|"
    r"peggiore|regola|ramo|modello|modulante|modulanti|iniezione|sequenza|"
    r"livelli|individuati|attesi|discreti|fondamentale|periodo|"
    r"ripartizione|variare|transitorio|sensibilita|montaggio|isolante|"
    r"decide|margine|resistenza|termica|dissipatore|campioni|comando|"
    r"picco|limite|spettro|armoniche|totale|troncato|salita|attesa|"
    r"confermato|minimo|induttanza|energia|energie|sovratensione|"
    r"compromesso|meno|piu|dall|della|delle|nel|nella|con|del|"
    # aggiunte l'11/10/2026: erano sfuggite in una legenda; "per" tolta perche'
    # e' anche inglese ("per device") e dava falsi allarmi
    r"regressione|ciclo|cicli|dispositivo|giunzione)\b")


def testo(pdf):
    out = subprocess.run([PDFTOTEXT, "-layout", str(pdf), "-"],
                         capture_output=True)
    return out.stdout.decode("utf-8", "replace")


def main():
    base = pathlib.Path(__file__).resolve().parent
    pdfs = sorted((base / "figures").glob("*.pdf"))
    if not pdfs:
        print("nessuna figura in figures/: lanciare prima aggiorna_figure.py")
        return 1

    problemi = 0
    for p in pdfs:
        t = testo(p)
        trovate = sorted(set(m.group(0) for m in IT.finditer(t)))
        if trovate:
            problemi += 1
            print("%-42s %s" % (p.name, ", ".join(trovate)))
    if not problemi:
        print("nessuna parola italiana nelle %d figure" % len(pdfs))

    # controllo del simbolo ohm nel report
    principale = base / "main.pdf"
    if principale.exists():
        t = testo(principale)
        n_ohm = t.count("\u03a9") + t.count("\u2126")
        # "W" preceduta da un numero e uno spazio, dove ci si aspetta ohm
        sospette = re.findall(r"\d[.,]?\d*\s*m?W\b", t)
        print()
        print("main.pdf: %d simboli ohm estratti correttamente" % n_ohm)
        print("          %d occorrenze di 'W' dopo un numero "
              "(watt legittimi + eventuali ohm rotti)" % len(sospette))
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
