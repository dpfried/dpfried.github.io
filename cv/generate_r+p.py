import yaml

MY_NAME = "Daniel Fried"

keys_and_headers = {
    'journal-papers': "Refereed Journal Papers - Published", 
    'conference-workshop-papers': "Refereed Conference / Workshop Papers",
    'preprints': "Technical Reports",
}

venue_emph = {
    'journal-papers': "emph", 
    'conference-workshop-papers': "textbf",
    'preprints': "emph",
}

with open('publications.yaml') as f:
    publications_data = yaml.safe_load(f)

publications_data['conference-workshop-papers'] = sorted(
    publications_data['conference-papers'] + publications_data['workshop-papers'],
    key=lambda paper: paper['year'],
    reverse=True
)

latex_items = ["\\section{}", "\\begin{enumerate}[leftmargin=-1mm,partopsep=0pt]"]
for key, header in keys_and_headers.items():
    item = "\\item[]\\hspace{-7em}{\\small \\sc \\textbf{" + header + "}}"
    latex_items.append(item)
    for paper in publications_data[key]:
        #authors = paper['authors-long'] if 'authors-long' in paper else paper['authors']
        authors = paper['authors']
        if MY_NAME in authors:
            authors = authors.replace(MY_NAME, f"\\underline{{{MY_NAME}}}")
        item = f"\\item {authors} ({paper['year']}). {paper['title']}. In \\{venue_emph[key]}{{{paper['venue']}}}."
        latex_items.append(item)

latex_items.append("\\end{enumerate}")
latex_items.append("\\textbf{*,**}: equal contribution")

latex_output = "\n\n".join(latex_items)

print(latex_output)
