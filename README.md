# Report LaTeX, Project 7: versione d'esame (branch `for-exam`)

Report della consegna d'esame: **solo lo stadio di potenza** di un inverter
trifase a due livelli (800 V, 30 A rms a qualsiasi fattore di potenza,
20 kHz, ondulazione di corrente trascurabile, ondulazione sul condensatore
sotto lo 0,5 %, raffreddamento ad aria forzata o a liquido, ambiente 50 °C).
Contiene le equazioni di progetto, la scelta dei componenti, le scelte
progettuali e la discussione delle simulazioni. È **in inglese**; i documenti
di lavoro in `04 - Python/` e `05 - Ausiliari/` restano in italiano.

La versione completa (149 pagine: ausiliari, schema e PCB dell'intera scheda,
EMC, costi) è sul branch `main`, tag `report-full`. Su questo branch si toglie,
non si cancella.

## Come compilare

```bash
python aggiorna_figure.py     # copia in figures/ le figure citate dal report
pdflatex main; biber main; pdflatex main; pdflatex main
```

`latexmk` non parte su questa macchina (manca perl): si compila a mano come
sopra. Stato del 15/10/2026: **90 pagine, 0 errori, 0 overfull, 0 rimandi non
definiti**.

Le figure del modulo vengono dal progetto KiCad
(`02 - KiCAD/figure_modulo.py`, che legge il riquadro del modulo sul layer
`User.1` del PCB) e dai fogli dello schema (`figure_report.py`); le altre dal
modello PLECS, dallo studio SPICE e dal modello termico di `04 - Python`.
`aggiorna_figure.py` copia solo quelle citate da `\includegraphics`, con un
prefisso che dice da dove vengono (`plecs_`, `spice_`, `kicad_`, `termica_`).

## Una nota sul preambolo

Il preambolo **non usa siunitx**, pur essendo scritto con la sua sintassi.
Su questa macchina MiKTeX ha siunitx 3.5.12 su un kernel LaTeX2e 2023-11-01:
il pacchetto usa variabili che quel kernel non definisce e fallisce anche su
un documento minimo. Le macro `\SI`, `\si`, `\num` sono reimplementate in
`preamble.tex`; quando MiKTeX verrà aggiornato basta togliere quel blocco.

## Struttura

| File | Contenuto |
|---|---|
| `main.tex` | frontespizio, indici, sequenza dei capitoli |
| `preamble.tex` | pacchetti, unità, riquadri, macro di progetto |
| `references.bib` | datasheet, norme, letteratura |
| `chapters/*.tex` | un file per capitolo |
| `figures/` | figure copiate da `aggiorna_figure.py` e schemi TikZ in `figures/tikz/` |
| `coerenza.py` | una grandezza, un solo valore in tutto il testo |
| `controllo_lingua.py` | parole italiane nelle figure |

## Capitoli

| # | Capitolo | Che cosa risponde alla consegna |
|---|---|---|
| — | Abstract | i risultati contro i cinque requisiti |
| 1 | Introduction | confini del modulo, metodo, indice sulle quattro voci della consegna |
| 2 | Specification and topology | requisiti, ipotesi sul sistema, topologia, **scelta del dispositivo** (criteri C1–C5) |
| 3 | Analytical design | **equazioni di progetto**: punto di lavoro, DC-link (ripple e corrente RMS), frequenza |
| 4 | Modulation and dead time | SVPWM, tempo morto, ondulazione di corrente |
| 5 | Simulation model and validation | modello PLECS e validazione contro le formule chiuse |
| 6 | Loss analysis | perdite, fattore di potenza, studio SPICE della cella (Rg, livelli di gate) |
| 7 | Thermal design | catena termica, rotore bloccato, aria contro liquido, pad, componenti |
| 8 | Schematic design | modulo power stage: fogli, interfaccia a 23 segnali, tabella dei componenti |
| 9 | PCB layout | piazzamento, stack-up, maglia di commutazione, conduttori, isolamento dei pin, barra di raffreddamento |
| 10 | Conclusions | tabella risultati contro la consegna, punto aperto, sviluppi |
| A | Open assumptions | dodici ipotesi con conseguenza e modo di chiuderle |

## Fonte unica dei numeri

I valori numerici vengono da `04 - Python/risultati/metriche.json`, dai
modelli termici di `04 - Python/termica` e dal §9.2 di
`05 - Ausiliari/progetto_ausiliari.md`. Se un numero cambia là, va cambiato
qui: `coerenza.py` segnala una grandezza scritta con due valori diversi.
