PDF = main.pdf

all: figures $(PDF)

figures:
	python aggiorna_figure.py

$(PDF): main.tex preamble.tex references.bib $(wildcard chapters/*.tex)
	latexmk -pdf -interaction=nonstopmode main.tex

clean:
	latexmk -c

distclean:
	latexmk -C

.PHONY: all figures clean distclean
