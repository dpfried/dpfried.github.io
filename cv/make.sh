#!/bin/bash
python generate.py cv > publication_list.tex
pdflatex Fried-CV-web.tex
./to_html.sh
