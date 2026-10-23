# -*- coding: utf-8 -*-
"""Controllo di coerenza numerica del report contro la fonte unica (§9.2).

Due controlli distinti:

  1. valori OBSOLETI ancora presenti  -> errore
  2. la stessa grandezza scritta con valori DIVERSI -> errore;
     scritta con precisione diversa ma coerente all'arrotondamento -> ok

Il secondo distingue "95,29 e 95,3" (stessa cifra, precisione diversa:
legittimo fra una tabella di dettaglio e il testo) da "95,3 e 94,8"
(due numeri diversi: refuso).
"""
import pathlib
import re
import sys

# grandezza: (valore canonico, regex delle occorrenze, obsoleti)
GRANDEZZE = [
    # --- progetto finale: E3M0016120K, R_g 5/12.5 ohm, 260 ns, modello V08 ---
    # I valori del primo dispositivo (178,17 W, 95,29 degC...) restano nel
    # testo dove sono citati come storia: per questo non stanno fra gli
    # obsoleti, che cercano solo le forme che non devono piu' comparire.
    ("Potenza di uscita",      25.477, r"25\.4\d?(?=\}\{\\kilo\\watt)", ["25.49}{\\kilo"]),
    ("Rendimento",             99.50,  r"99\.\d+(?=\}\{\\percent)", ["99.31"]),
    ("cos(phi) di progetto",    0.949, r"\b0\.949\b",              []),
    # 22,5 A resta in appendice A.9, dove si racconta che il valore vecchio
    # era sbagliato: e' una citazione voluta, non un residuo
    ("Corrente di bus",        32.0,   r"32\.\d(?=\}\{\\ampere)",  ["32.1}{\\ampere"]),
    ("Larghezza pista bus",    10.4,   r"10\.4(?=\}\{\\milli\\metre)", []),
    ("P_cond",                 57.64,  r"57\.6\d?(?=\}\{\\watt)",  ["151.1}{\\watt"]),
    ("P_sw",                   70.6,  r"70\.\d+(?=\}\{\\watt)",   []),
    ("P_tot",                 128.52,  r"128\.\d+(?=\}\{\\watt)",  ["178.2}{\\watt"]),
    ("P per dispositivo",      21.42, r"21\.\d+(?=\}\{\\watt)",   ["29.7}{\\watt"]),
    ("T_heatsink",             66.29,  r"66\.2\d?(?=\}\{\\celsius)", ["66.78"]),
    ("T_case",                 76.96,  r"76\.9\d?(?=\}\{\\celsius)", ["81.63"]),
    ("T_giunzione",            81.84,  r"81\.8\d?(?=\}\{\\celsius)", []),
    ("Margine termico",        68.11,  r"68\.\d+(?=\}\{\\celsius)", ["54.71"]),
    ("R_th,JC",                 0.22864, r"0\.22864|0\.23(?=\}\{\\celsius\\per\\watt)", ["0.46020"]),
    ("Pad massimo a C1",        0.62,  r"0\.6\d(?=\}\{\\celsius\\per\\watt)", ["1.18}{\\celsius"]),
    ("T_j rotore bloccato 65",  111.04, r"111\.\d+(?=\}\{\\celsius)", ["105.1}{\\celsius"]),
    # l'obsoleto 110,9 (primo dispositivo, liquido a 70 degC) e' stato tolto il
    # 11/10/2026: lo stesso numero ricompare, legittimo, nella tab. coolalt
    # (dissipatore di rame, caso peggiore) e il controllo non li distingue
    ("T_j rotore bloccato 70",  116.82, r"116\.\d+(?=\}\{\\celsius)", []),
    # ancorata all'unita': senza, 10,16 mm (passo dei pin) verrebbe
    # scambiata per una costante di tempo
    ("tau termica",            10.2047, r"10\.\d+(?=\}\{\\second)", []),
    ("Picco di corrente",      43.0,   r"\b43\.0\b",               []),
    ("I_C caso peggiore",      16.28,  r"16\.\d+(?=\}\{\\ampere)", ["16.48"]),
    ("Energia commutazione",  596.9, r"59[67](?:\.\d)?(?=\}\{\\micro\\joule)", ["231.4"]),
    ("Induttanza package",     14.6,   r"1[45]\.\d(?=\}\{\\nano\\henry)", ["15.5}{\\nano"]),
    ("Picco V_DS 20 nH",     1073.5,   r"107[34](?:\.\d)?(?=\}\{\\volt)", ["998.3"]),
    # --- revisione dopo il cambio di dispositivo: soglie e caso peggiore ---
    ("Soglia induttanza C2",   22.6,  r"22\.6(?=\}\{\\nano\\henry)", []),
    ("Soglia recupero C2",     23.6,  r"23\.6(?=\}\{\\nano\\henry)", []),
    ("Caso peggiore simult.", 140.4,  r"140\.\d(?=\}\{\\celsius)",     []),
    ("Soglia t_SC",             0.83, r"0\.83(?=\}\{\\micro\\second)", []),
    ("T_j DPWM-MAX",           93.83, r"93\.\d+(?=\}\{\\celsius)",   []),
    ("R_g,off",                12.5,   r"12\.5(?=\}\{\\ohm)",      []),
    ("Tempo morto",           260.0,   r"26\d(?=\}\{\\nano\\second)", []),
    # 5,45 mm resta nel testo di proposito: il riquadro di §9 spiega perche'
    # e' sbagliato. Cercarlo fra gli obsoleti darebbe un falso positivo, e
    # 5,45 A/ns e' comunque un di/dt legittimo.
    ("Passo TO-247-4L",         5.08,  r"\b5\.(?:08|45)(?=\}\{\\milli\\metre)", []),

    # --- grandezze introdotte da D5/D7: interfaccia analogica e confine ---
    ("Ripple di fase pp",       2.463, r"\b2\.463\b",                        []),
    ("Ripple % del picco",      5.80,  r"5\.80(?=\}\{\\percent)",          ["0.004}{\\percent"]),
    ("Creepage drain-source",   3.24,  r"\b3\.24\b",                         []),

    # --- coordinamento dell'isolamento (Parte 1) ---
    # tutte ancorate all'unita': senza, 2.40 e 4.00 pescherebbero numeri
    # che non c'entrano niente, e 4.10 e' anche un errore percentuale
    # rivalutati a 900 V (tensione massima continuativa); 9,00 mm e' sia il
    # base in gruppo IIIa sia il rinforzato in gruppo I: stessa cifra
    ("Creepage PD1",            2.80,  r"2\.[48]0(?=\}\{\\milli\\metre)", ["2.40}{\\milli"]),
    ("Creepage PD2 gruppo I",   4.50,  r"4\.[05]0(?=\}\{\\milli\\metre)", ["4.00}{\\milli"]),
    ("Creepage PD2 gruppo II",  6.35,  r"6\.35(?=\}\{\\milli\\metre)",   []),
    ("Creepage PD2 gruppo IIIa", 9.00, r"9\.00(?=\}\{\\milli\\metre)",   ["8.00}{\\milli"]),
    ("Rinforzato PD1",          5.60,  r"[45]\.[68]0(?=\}\{\\milli\\metre)", ["4.80}{\\milli"]),
    ("Coppia di piani",         0.188, r"\b0\.188\b",                        []),
    # --- clearance e tenuta a impulso (Parte 1 del quinto giro) ---
    ("Impulso nominale",       2.5,   r"2\.5(?=\}\{\\kilo\\volt)",       []),
    ("Clearance a 2,5 kV",     1.50,  r"1\.50(?=\}\{\\milli\\metre)",    []),
    ("Clearance a 4 kV",       3.00,  r"3\.00(?=\}\{\\milli\\metre)",    []),
    ("Clearance a 6 kV",       5.50,  r"5\.50(?=\}\{\\milli\\metre)",    []),
    ("Picco V_DS a 50 nH",  1147.8,   r"114[78](?:\.\d)?(?=\}\{\\volt)",    ["1130.0"]),
    ("Clearance meccanica",    5.0,   r"5\.0(?=\}\{\\milli\\metre)",     []),
    # --- pad isolante in PD2, capacita' e transitorio ---
    ("Regola funzionale PCB",  4.5,   r"4\.5(?=\}\{\\milli\\metre)",     ["3.0}{\\milli\\metre"]),
    ("C dai nodi commutanti",  131.0, r"\b131\b",                             []),
    ("Sovratensione a 35 A",   5.1,   r"5\.1(?=\}\{\\volt)",               []),
    ("Perdite a cos(phi) = 1, 30 A", 131.4, r"131.4(?=\}\{\\watt)", []),
    ("T_j a cos(phi) = 1, 30 A",   82.3, r"82\.3(?=\}\{\\celsius)", []),
]


# Valori che compaiono di proposito accanto al canonico, e che quindi NON
# sono incoerenze: il testo li mette a confronto apposta.
ECCEZIONI = {
    # 99,59 %: rendimento con il diodo Schottky esterno (sezione sbd), non il progetto
    "Rendimento": {"99.59"},
    # il capitolo termico confronta la tau identificata con quella attesa
    "tau termica": {"10.0", "10.00"},
    # il riquadro di §9 cita il passo sbagliato per correggerlo
    "Passo TO-247-4L": {"5.45"},
    # 76,9 degC e' la T_j a 10 kHz nella tabella in frequenza
    "T_case": {"76.9"},
    # 111,6 degC e' l'E3M0021120K a 2,5 ohm nel confronto di selezione
    # 16,9 A e' il caso reattivo a m = 1,15, non il caso peggiore
    "I_C caso peggiore": {"16.9"},
    # 1073 V e' la riga 12,5/12,5 ohm della scansione (1073,2 V)
    # 4,60 mm e' il cammino sul bordo, non il rinforzato
    "Rinforzato PD1": {"4.60"},
    # 111,05 degC e' il dettaglio della tabella del rotore bloccato: 111,06 +-
    # 0,02 fra due esecuzioni, che arrotondato a un decimale da' 111,1
    # 111,05: metodo nel tempo nella tabella di confronto del cap. 5
    "T_j rotore bloccato 65": {"111.6", "111.05"},
    # 1074,2 V e' la riga a 21 nH della scansione fine della soglia
    "Picco V_DS 20 nH": {"1073", "1074.2"},
    # 128,52 W e 81,89 degC sono lo steady-state nativo, messo a confronto
    # col metodo nel tempo nel cap. 5
    # 128,09: metodo nel tempo nella tabella di confronto del cap. 5
    "P_tot": {"128.09"},
    "T_giunzione": {"81.89"},
    # 21,2 W e' la conduzione di A1 a rotore bloccato, non la perdita media
    "P per dispositivo": {"21.2"},
    # 0,60 degC/W e' il pad a +20 % nel caso peggiore, non il limite
    "Pad massimo a C1": {"0.60"},
    # 116,9 degC e' il modello analitico (tab. worstcase), PLECS da' 116,82
    # 116,7 degC e' il caso peggiore del TO-247 isolato internamente (tab. coolalt)
    "T_j rotore bloccato 70": {"116.9", "116.7"},
    # 93,27 degC e' la T_case a R_cs 1,2 nello sweep del pad
    # 93,37: T_case con pad 1,2 nella tabella del pad, non DPWM
    "T_j DPWM-MAX": {"93.27", "93.37"},
}


def main():
    base = pathlib.Path(__file__).resolve().parent
    testo = "\n".join(p.read_text(encoding="utf-8")
                      for p in sorted((base / "chapters").glob("*.tex")))

    errori = []
    print("%-24s %-9s %s" % ("GRANDEZZA", "ESITO", "VALORI TROVATI"))
    print("-" * 74)
    for nome, canonico, pattern, obsoleti in GRANDEZZE:
        rimasti = [o for o in obsoleti if o in testo]
        trovati = sorted(set(re.findall(pattern, testo)), key=float)
        if rimasti:
            print("%-24s %-9s obsoleto: %s" % (nome, "ERRORE", ", ".join(rimasti)))
            errori.append(nome)
            continue
        if not trovati:
            print("%-24s %-9s -" % (nome, "assente"))
            continue
        # tutte le varianti devono coincidere col canonico una volta
        # arrotondate alla precisione della piu' grossolana
        prec = min(len(v.split(".")[1]) if "." in v else 0 for v in trovati)
        rif = round(canonico, prec)
        ammessi = ECCEZIONI.get(nome, set())
        incoerenti = [v for v in trovati
                      if abs(round(float(v), prec) - rif) > 1e-9
                      and v not in ammessi]
        if incoerenti:
            print("%-24s %-9s %s  <-- non coincidono con %s"
                  % (nome, "ERRORE", ", ".join(trovati), canonico))
            errori.append(nome)
        elif len(trovati) > 1:
            print("%-24s %-9s %s  (stessa cifra, precisione diversa)"
                  % (nome, "ok", ", ".join(trovati)))
        else:
            print("%-24s %-9s %s" % (nome, "ok", trovati[0]))

    print()
    if errori:
        print("%d grandezze incoerenti: %s" % (len(errori), ", ".join(errori)))
    else:
        print("nessuna incoerenza: ogni grandezza compare con un solo valore")
    return 1 if errori else 0


if __name__ == "__main__":
    sys.exit(main())
