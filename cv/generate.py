import yaml

MY_NAME = "Daniel Fried"

keys_and_headers = {
    'journal-papers': "Journal Publications", 
    'conference-papers': "Conference Publications",
    'workshop-papers': "Workshop Publications", 
    'preprints': "Preprints",
}

with open('publications.yaml') as f:
    publications_data = yaml.safe_load(f)

latex_items = ["\\section{}", "\\begin{enumerate}[leftmargin=-1mm,partopsep=0pt]"]
for key, header in keys_and_headers.items():
    item = "\\item[]\\hspace{-7em}{\\small \\sc \\textbf{" + header + "}}"
    latex_items.append(item)
    for paper in publications_data[key]:
        authors = paper['authors']
        if MY_NAME in authors:
            authors = authors.replace(MY_NAME, f"\\underline{{{MY_NAME}}}")
        if 'url' in paper:
            item = f"\\item \\href{{{paper['url']}}}{{\\textbf{{{paper['title']}}}}} \\\\"
        else:
            item = f"\\item \\textbf{{{paper['title']}}} \\\\"
        item += f"\n  {authors}\\\\"
        item += f"\n  \\emph{{{paper['venue']}}}, {paper['year']}"
        if 'awards' in paper:
            item += f". \\textbf{{{paper['awards']}}}"
        latex_items.append(item)

latex_items.append("\\end{enumerate}")
latex_items.append("\\textbf{*,**}: equal contribution")

latex_output = "\n\n".join(latex_items)

print(latex_output)
