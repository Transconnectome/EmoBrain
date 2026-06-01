# FEELIN Phase 1 wrap-up report build
# Requires: module load texlive/2024  (on NERSC)
#
# Usage:
#   make             # build both PDFs
#   make main        # main report only
#   make supp        # supplementary only
#   make clean       # remove aux files
#   make distclean   # remove aux + PDFs

PDFLATEX = pdflatex -interaction=nonstopmode -halt-on-error

.PHONY: all main supp clean distclean

all: main supp

main: main.pdf

supp: supplementary.pdf

main.pdf: main.tex figs/*.png
	$(PDFLATEX) main.tex >/dev/null
	$(PDFLATEX) main.tex >/dev/null
	@echo "[done] main.pdf"

supplementary.pdf: supplementary.tex
	@/pscratch/sd/s/sjmoon/swift_PTL2/bin/python gen_supp_tex.py
	$(PDFLATEX) supplementary.tex >/dev/null
	$(PDFLATEX) supplementary.tex >/dev/null
	@echo "[done] supplementary.pdf"

clean:
	rm -f *.aux *.log *.out *.toc *.lof *.lot *.synctex.gz

distclean: clean
	rm -f *.pdf
