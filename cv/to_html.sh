#!/bin/bash
# name should be contained in refs_pandoc.bib
pandoc Fried-CV-html.tex -C -f latex -t html -s \
  -o Fried-CV.html \
  --metadata link-citations=true \
  --metadata title="Daniel Fried: CV" \
  --metadata date="`date +'%B %d, %Y'`" \
  --css style.css \
  --toc

# remove <b> from the title
# old_rep=${name}
# new_rep="<b>${name}<\/b>"
# sed -i "s/${old_rep}/${new_rep}/g" $output
# sed -i "0,/${new_rep}/{s/${new_rep}/${old_rep}/}" $output
