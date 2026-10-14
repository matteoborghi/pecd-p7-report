# Report LaTeX — Project 7

Progetto del report d'esame. **In inglese**, perché è il deliverable da
discutere; i documenti di lavoro in `04 - Python/` e `05 - Ausiliari/`
restano in italiano.

## Come compilare

```bash
python aggiorna_figure.py     # sincronizza i PDF vettoriali in figures/
latexmk -pdf main.tex         # oppure: make
```

**Se `latexmk` non parte** (manca perl, come su questa macchina l'11/10/2026):
`pdflatex main`, `biber main`, `pdflatex main`, `pdflatex main`.

Verificato l'11/10/2026: **0 errori, 119 pagine**; un solo avviso, "float
too large" di 5 pt sulla tabella dei requisiti di sistema (cap. 8).

Le figure dei capitoli 9 e 10 vengono dal progetto KiCad: prima
`uv run --no-project --with pillow python figure_report.py` da
`02 - KiCAD/`, poi `aggiorna_figure.py` le copia con prefisso `kicad_`.

`aggiorna_figure.py` copia i PDF dalle tre cartelle in cui vengono prodotti
(`03 - Report/01 - PLECS figures/…` e `05 - Ausiliari/figure/`) dentro
`figures/`, con un prefisso che dice da dove vengono. Va rilanciato dopo ogni
rigenerazione delle figure.

## Una nota sul preambolo

Il preambolo **non usa siunitx**, pur essendo scritto con la sua sintassi.
Su questa macchina MiKTeX ha siunitx 3.5.12 (2026-09-08) su un kernel LaTeX2e
2023-11-01: il pacchetto usa variabili che quel kernel non definisce e
fallisce anche su un documento minimo di quattro righe. Le macro `\SI`, `\si`,
`\num` sono quindi reimplementate in `preamble.tex` in LaTeX puro.

I punti di chiamata sono identici a siunitx: quando MiKTeX verrà aggiornato
basta cancellare quel blocco e togliere il commento alle righe in fondo.

## Struttura

| File | Contenuto |
|---|---|
| `main.tex` | frontespizio, indice, sequenza dei capitoli |
| `preamble.tex` | pacchetti, unità, riquadri, macro di progetto |
| `references.bib` | datasheet, norme, letteratura |
| `chapters/*.tex` | un file per capitolo |
| `figures/*.pdf` | figure sincronizzate, non modificare a mano |

## Indice ragionato dei capitoli

Stato: **scritto** = completo; **stub** = struttura e argomenti fissati, da
riempire quando il materiale esiste.

| # | Capitolo | Stato | Contenuto | Figure e tabelle |
|---|---|---|---|---|
| — | Abstract | **scritto** | risultati in un colpo d'occhio, e le tre discrepanze trovate | — |
| 1 | Introduction | **scritto** | contesto, metodo in quattro stadi, dichiarazione esplicita di cosa il report non nasconde | — |
| 2 | Specification and topology | **scritto** | requisiti; perché 2L e non multilivello; perché SiC e non IGBT; scelta del dispositivo | Tab. 2.1–2.4 |
| 3 | Analytical design | **scritto** | punto di lavoro, limite SV-PWM, dimensionamento del DC-link per ripple e per corrente RMS, scelta di f_sw | eq. 3.1–3.4 |
| 4 | Modulation and dead time | **scritto** | iniezione di sequenza zero; confronto con SPWM e DPWM; budget e costo del dead time | Fig. 4.1–4.5, Tab. 4.1–4.2 |
| 5 | Simulation model and validation | **scritto** | struttura del modello, campionamento coerente per le FFT, **verifica delle tabelle di perdita**, tre validazioni indipendenti | Fig. 5.1–5.3, Tab. 5.1 |
| 6 | Loss analysis | **scritto** | bilancio, sweep in frequenza, **correzione del dead time**, studio SPICE della cella di commutazione, valore del pin di Kelvin | Fig. 6.1–6.4, Tab. 6.1–6.5 |
| 7 | Thermal design | **scritto** | catena termica, anello perdite-temperatura, **sensibilità su R_th,CS**, transitorio, monitoraggio | Fig. 7.1–7.2, Tab. 7.1–7.2 |
| 8 | Auxiliary circuits | **scritto** | gate driver, protezioni, sensing e posizione dello shunt, precarica e scarica, interlock hardware | Tab. 8.1–8.5 |
| 9 | Schematic design | **scritto** (11/10) | gerarchia, classi di net, riferimenti, decisioni D8–D14, verifica contro il modello, i dieci fogli | Tab. 9.1–9.3, fogli da KiCad |
| 10 | PCB layout | **scritto** (11/10) | la scheda com'è (pianta, strati, loop di gate misurato), stack-up, conduttori, EMC, isolamento, regole implementate, verifiche di congelamento | viste 3D, strati, dettaglio del ramo |
| 11 | Conclusions | **stub** | risultati contro specifica, cosa resta al banco, sviluppi | da scrivere per ultimo |
| A | Open assumptions | **scritto** | 14 ipotesi ordinate per quanto cambierebbero il risultato | — |

### Perché i tre stub sono stub

Non è materiale mancante: è materiale che **non esiste ancora**. Il capitolo 9
ha bisogno dei fogli KiCad disegnati, il 10 del board layout, e l'11 di
entrambi. La struttura, i vincoli numerici e i riferimenti incrociati sono già
al loro posto, quindi riempirli è scrivere testo attorno a numeri già fissati.

I tre stub contengono già le parti che **non** dipendono dal disegno: il
criterio di gerarchia, la correzione sul passo del TO-247-4L, il budget di
induttanza di maglia e il calcolo della corrente di modo comune.

## Fonte unica dei numeri

Tutti i valori numerici vengono dal **§9.2 di
`05 - Ausiliari/progetto_ausiliari.md`**. Se un numero cambia là, va cambiato
qui; nel report non c'è nessun valore calcolato indipendentemente.

Nei documenti di lavoro ogni numero porta la marca [DS]/[CALC]/[SIM]/[IPOTESI];
nel report quella marcatura diventa una citazione bibliografica normale, come
si conviene a un documento da consegnare.
