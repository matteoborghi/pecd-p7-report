# -*- coding: utf-8 -*-
"""Grafici radar (spider plot) dei confronti del report, scritti come TikZ (18/10/2026).

Ogni grafico e' un dizionario: assi, opzioni e punteggi da 1 (peggio) a 5 (meglio). Dove il
report ha un numero, il punteggio viene da quel numero (scritto accanto nel commento); dove il
confronto e' qualitativo il punteggio e' una scala d'ordine, dichiarata nella didascalia.

Uso:   python radar.py      (scrive figures/tikz/radar_*.tex, inclusi dai capitoli con \\input)
"""
import math
from pathlib import Path

QUI = Path(__file__).resolve().parent
COLORI = ["fblu", "farancio", "fverde"]

GRAFICI = {
    "topologia": {
        "assi": ["few devices", "few gate signals", "output voltage\\\\quality", "simple\\\\layout",
                 "simple\\\\control", "low voltage\\\\per device"],
        "serie": [
            # dispositivi 6 / 18 / 12; driver 6 / 12 / 12; livelli 3 / 5 / 5 (tab. topologia);
            # maglie di commutazione 1 / piu' asimmetriche / piu'; bilanciamento del punto neutro no / si / si;
            # classe di tensione 1200 / 650 / 650+1200 V
            ("two-level", [5, 5, 2, 5, 5, 2]),
            ("three-level NPC", [1, 2, 4, 1, 2, 5]),
            ("three-level T-type", [3, 2, 4, 3, 2, 3]),
        ],
    },
    "tecnologia": {
        "assi": ["low switching\\\\loss", "low total\\\\loss", "thermal\\\\margin", "low loss at\\\\partial load",
                 "simple\\\\gate drive", "low cost"],
        "serie": [
            # commutazione per dispositivo 11,8 W contro 69 W; inverter 128 W contro 643 W;
            # T_j al punto nominale 81,8 contro 151 degC
            ("SiC MOSFET", [5, 5, 5, 5, 2, 2]),
            ("Si IGBT", [1, 1, 1, 2, 4, 4]),
        ],
    },
    "candidati": {
        "assi": ["margin at\\\\locked rotor", "low loss", "overshoot\\\\simulated (C2)", "short circuit\\\\declared (C5)",
                 "vendor loss\\\\model", "standard gate\\\\supply"],
        "serie": [
            # T_j a rotore bloccato 111,1 contro 97-110 degC; perdite 128 contro 97-128 W;
            # modello SPICE del costruttore si / no; t_SC dichiarato no / 1,5 us;
            # descrizione termica del costruttore si / costruita dai grafici; gate +15 V / +20 V
            ("E3M0016120K", [3, 3, 5, 1, 5, 4]),
            ("AIMZH120R020M1T", [4, 4, 1, 5, 2, 3]),
        ],
    },
    "raffreddamento": {
        "assi": ["margin at\\\\locked rotor", "margin in the\\\\worst case", "small\\\\volume",
                 "sealed\\\\enclosure", "no extra\\\\coolant loop"],
        "serie": [
            # stesso passante AlN con interfaccia a cambio di fase, T_j a rotore bloccato / caso peggiore:
            # liquido 97,9 / 117,8 degC; aria forzata un ventilatore 108,3 / 129,1 degC;
            # convezione naturale 188 degC a rotore bloccato (pad prudente), fuori da ogni limite.
            # volume: dissipatore ad aria circa dieci volte la barra; involucro chiuso: l'aria deve
            # attraversare la scheda; anello liquido: gia' presente sul veicolo (tab. ipotesi) ma
            # aria e convezione non ne hanno bisogno
            ("liquid rail", [5, 5, 5, 5, 1]),
            ("forced air", [4, 4, 2, 2, 5]),
            ("natural convection", [1, 1, 1, 4, 5]),
        ],
    },
    "modulazione": {
        "assi": ["DC-link\\\\utilisation", "low switching\\\\loss", "low current\\\\ripple",
                 "low $T_\\mathrm{j}$ at\\\\locked rotor", "simple\\\\implementation"],
        "serie": [
            # M_f massimo 0,500 / 0,577 / 0,577; commutazione -33 % con DPWM; ripple base / simile /
            # peggiore (tab. modulazione); T_j a rotore bloccato 111,1 / 111,1 / 93,9 degC
            # (con tensione d'uscita nulla SPWM e SVPWM coincidono); m0 costante / max e min / logica
            ("SPWM", [3, 3, 4, 3, 5]),
            ("SV-PWM", [5, 3, 4, 3, 4]),
            ("DPWM", [5, 5, 2, 5, 2]),
        ],
    },
}


def tikz(g):
    n = len(g["assi"])
    r = 2.6                      # raggio del livello 5, cm
    ang = [90 - 360.0 * i / n for i in range(n)]
    pt = lambda a, v: (r * v / 5 * math.cos(math.radians(a)), r * v / 5 * math.sin(math.radians(a)))
    L = ["% Generato da radar.py: non modificare a mano.",
         "\\begin{tikzpicture}[font=\\footnotesize]"]
    for liv in range(1, 6):
        poly = " -- ".join("(%.3f,%.3f)" % pt(a, liv) for a in ang)
        L.append("  \\draw[black!%d] %s -- cycle;" % (18 if liv < 5 else 40, poly))
    for a, testo in zip(ang, g["assi"]):
        x, y = pt(a, 5)
        L.append("  \\draw[black!25] (0,0) -- (%.3f,%.3f);" % (x, y))
        lx, ly = pt(a, 5.35)
        c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
        anc = "south" if sn > 0.9 else "north" if sn < -0.9 else ("west" if c > 0 else "east")
        L.append("  \\node[align=center, inner sep=2pt, anchor=%s] at (%.3f,%.3f) {%s};" % (anc, lx, ly, testo))
    for liv in (1, 3, 5):
        x, y = pt(90, liv)
        L.append("  \\node[black!45, font=\\scriptsize, anchor=west] at (%.3f,%.3f) {%d};" % (x + 0.05, y, liv))
    for (nome, val), col in zip(g["serie"], COLORI):
        poly = " -- ".join("(%.3f,%.3f)" % pt(a, v) for a, v in zip(ang, val))
        L.append("  \\draw[%s, very thick, fill=%s, fill opacity=0.12] %s -- cycle;" % (col, col, poly))
    # legenda: una sola riga centrata sotto il grafico, le voci non si sovrappongono
    voci = " \\quad ".join("\\tikz[baseline=-0.6ex]\\draw[%s, very thick] (0,0) -- (0.45,0); %s" % (col, nome)
                           for (nome, _), col in zip(g["serie"], COLORI))
    L.append("  \\node[anchor=north] at (0,%.2f) {%s};" % (-r - 1.35, voci))
    L.append("\\end{tikzpicture}")
    return "\n".join(L) + "\n"


def main():
    for nome, g in GRAFICI.items():
        p = QUI / "figures" / "tikz" / ("radar_%s.tex" % nome)
        p.write_text(tikz(g), encoding="utf-8")
        print("scritto", p.name)


if __name__ == "__main__":
    main()
