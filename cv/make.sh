#!/bin/bash
python generate.py > publication_list.tex
pdflatex Fried-CV-web.tex
python generate_bib.py > publications.bib
./to_html.sh
