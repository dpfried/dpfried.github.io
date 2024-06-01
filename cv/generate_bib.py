import yaml
import re
from collections import OrderedDict

NAME_TRANSFORM = {
    "Daniel Fried": "\\underline{D. Fried}",
}

is_journal = {
    'journal-papers': True,
    'conference-papers': False,
    'workshop-papers': False,
    'preprints': True,
}

with open('publications.yaml') as f:
    publications_data = yaml.safe_load(f)

bibtex_items = []
for key in is_journal.keys():
    for paper in publications_data[key]:
        #paper["title"] = f'{{{paper["title"]}}}'
        this_attrs = OrderedDict(**{
            k: paper[k] 
            for k in ["title", "year", "url"]
            if k in paper
        })
        authors = paper.get("authors-long", paper["authors"])
        authors = authors.replace("*", "")
        authors = authors.replace(", and ", ", ").replace(" and ", ", ").split(",")
        new_authors = []
        first_author = None
        for author in authors:
            author = author.strip()
            if first_author is None:
                first_author = author.split()[-1].lower()
            if author in NAME_TRANSFORM:
                new_author = NAME_TRANSFORM[author]
            else:
                *given, last = author.split()
                new_author = f"{last}, {' '.join(given)}"
            new_authors.append(new_author)
        authors = " and ".join(new_authors)
        title_keyword = re.sub(r'[^[a-zA-z]', '', paper["title"].split()[0].lower())
        this_attrs["author"] = authors
        if is_journal[key]:
            this_attrs["journal"] = paper["venue"]
            entry_type = "article"
        else:
            this_attrs["booktitle"] = paper["venue"]
            entry_type = "inproceedings"

        entry = f'@{entry_type}{{{first_author}-{paper["year"]}-{title_keyword},\n'
        for attr, val in this_attrs.items():
            entry += f'    {attr} = "{val}",\n'
        entry += '}'
        bibtex_items.append(entry)

bibtex_output = "\n\n".join(bibtex_items)

print(bibtex_output)
