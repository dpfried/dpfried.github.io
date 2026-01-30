import yaml
import re
from collections import OrderedDict
import argparse
from datetime import datetime

MY_NAME = "Daniel Fried"

NAME_TRANSFORM = {
    "Daniel Fried": "\\underline{D. Fried}",
}

def generate_cv(publications_data):
    keys_and_headers = {
        'journal-papers': "Journal Publications", 
        'conference-papers': "Conference Publications",
        'workshop-papers': "Workshop Publications", 
        'preprints': "Preprints",
    }

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
    return latex_output

def get_author_list(authors: str) -> list[str]:
    authors = authors.replace("*", "")
    authors = authors.replace(", and ", ", ").replace(" and ", ", ").split(",")
    authors = [author.strip() for author in authors]
    return authors

def generate_bib(publications_data, transform_name=True):
    is_journal = {
        'journal-papers': True,
        'conference-papers': False,
        'workshop-papers': False,
        'preprints': True,
    }

    bibtex_items = []
    for key in is_journal.keys():
        for paper in publications_data[key]:
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
                if transform_name and author in NAME_TRANSFORM:
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
    return bibtex_output

def generate_r_and_p(publications_data):
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

    # Use already-loaded publications_data; derive combined section in-memory
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
    return latex_output

def generate_html(publications_data, template_file='paper-template.html', group_previous_year=2020, non_preprints_to_include=['conference-papers', 'journal-papers', 'theses', 'workshop-papers']):
    data = publications_data
	# written by ChatGPT
    from jinja2 import Environment, FileSystemLoader

    def process_paper(paper):
        # shorten the venue
        short_venue = re.search('\((.*)\)', paper['venue'])
        if short_venue is not None:
            paper['venue'] = short_venue.group(1)

        # remove {} from the title
        paper['title'] = paper['title'].replace('{', '').replace('}', '')
        return paper

    for key in publications_data.keys():
        publications_data[key] = [
            process_paper(paper) for paper in publications_data[key]
        ]

	# Organize papers by year
    papers_by_year = {'Preprints': publications_data['preprints']}
    data = []
    for key in non_preprints_to_include:
        data += publications_data[key]

    for paper in sorted(data, key=lambda paper: paper['year'], reverse=True):
        year = paper['year']
        if year <= group_previous_year:
            year = f'{group_previous_year} and before'
        if year not in papers_by_year:
            papers_by_year[year] = []

        papers_by_year[year].append(paper)

    # Set up the Jinja2 environment and load the template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_file)

    # Render the template with the data
    html_output = template.render(papers_by_year=papers_by_year)
    return html_output

def generate_collaborators(publications_data):
    collaborators = set()
    for key in publications_data.keys():
        for paper in publications_data[key]:
            collaborators.update(get_author_list(paper.get('authors-long', paper['authors'])))
    return '\n'.join(sorted(collaborators))

def parse_paper_date(paper):
    # First, try to parse from arxiv URL
    url = paper.get('url', '')
    if 'arxiv.org' in url:
        # Match patterns like arxiv.org/abs/YYMM.NNNNN or arxiv.org/abs/YYMM.NNNNNVN
        match = re.search(r'arxiv\.org/abs/(\d{4})\.', url)
        if match:
            yymm = match.group(1)
            try:
                year = int(yymm[:2])
                month = int(yymm[2:])
                # Convert 2-digit year to 4-digit (assume 20xx for now, 19xx if >= 91)
                full_year = 2000 + year if year < 91 else 1900 + year
                # Use last day of the month
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    day = 31
                elif month in [4, 6, 9, 11]:
                    day = 30
                elif month == 2:
                    # Simple leap year check
                    day = 29 if (full_year % 4 == 0 and full_year % 100 != 0) or (full_year % 400 == 0) else 28
                else:
                    day = 1
                return datetime(full_year, month, day)
            except Exception:
                pass
    
    # Fall back to explicit date field
    s = str(paper.get('date', '')).strip()
    if s:
        parts = s.split('-')
        try:
            y = int(parts[0])
            m = int(parts[1]) if len(parts) > 1 else 1
            d = int(parts[2]) if len(parts) > 2 else 1
            return datetime(y, m, d)
        except Exception:
            pass
    
    # Fall back to year field with December 31st
    try:
        year = int(paper.get('year', 0))
        if year:
            return datetime(year, 12, 31)
    except Exception:
        pass
    return None

def load_affiliations_map(path):
    with open(path) as f:
        items = yaml.safe_load(f) or []
    name_to_affil = {}
    for it in items:
        name = it.get('NAME') or it.get('name')
        if name:
            name_to_affil[name] = it.get('affiliation', '')
    return name_to_affil

def generate_coa_collaborators(publications_data, years_back=4, affiliations_path=None):
    aff_map = load_affiliations_map(affiliations_path) if affiliations_path else {}
    now = datetime.now()
    min_date = now.replace(year=now.year - years_back)
    name_to_dates = {}
    name_to_affil = {}
    def name_last_first(name: str) -> str:
        parts = name.split()
        if len(parts) <= 1:
            return name
        *given, last = parts
        return f"{last}, {' '.join(given)}"
    for section, papers in publications_data.items():
        if not isinstance(papers, list):
            continue
        for paper in papers:
            d = parse_paper_date(paper)
            if d is None or d < min_date:
                continue
            authors_str = paper.get('authors-long', paper['authors'])
            for author in get_author_list(authors_str):
                if author == MY_NAME:
                    continue
                name_to_dates.setdefault(author, set()).add(d.strftime('%-m/%-d/%y'))
                if author not in name_to_affil:
                    name_to_affil[author] = aff_map.get(author, '')
    rows = []
    for name, dates in name_to_dates.items():
        ds = sorted(dates)
        display_name = name_last_first(name)
        # email column left blank per requirement
        rows.append((display_name, name_to_affil.get(name, ''), '', ds[-1]))
    rows.sort(key=lambda r: r[0].lower())
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['name', 'affiliation', 'email', 'most_recent_date'])
    for r in rows:
        writer.writerow(r)
    out = output.getvalue().strip().split('\n')
    return '\n'.join(out)

def update_affiliations(publications_data, affiliations_path='yaml/affiliations.yaml', 
                       default_affiliation='Carnegie Mellon University', years_back=4):
    """
    Update affiliations YAML file with missing collaborators.
    Prompts user for affiliation of each missing collaborator.
    Only considers collaborators from papers within the last years_back years.
    """
    # Get all collaborators from recent publications
    now = datetime.now()
    min_date = now.replace(year=now.year - years_back)
    
    all_collaborators = set()
    for key in publications_data.keys():
        if not isinstance(publications_data[key], list):
            continue
        for paper in publications_data[key]:
            d = parse_paper_date(paper)
            if d is None or d < min_date:
                continue
            authors_str = paper.get('authors-long', paper['authors'])
            for author in get_author_list(authors_str):
                if author != MY_NAME:
                    all_collaborators.add(author)
    
    # Load existing affiliations
    try:
        with open(affiliations_path) as f:
            affiliations_list = yaml.safe_load(f) or []
    except FileNotFoundError:
        affiliations_list = []

    # Deduplicate the affiliations list by name (keeping the last occurrence)
    deduped = {}
    for item in affiliations_list:
        # Use lower case for name for better robustness
        name = item.get('name') or item.get('NAME')
        if name:
            deduped[name] = item
    affiliations_list = list(deduped.values())
    
    # Build set of existing names
    existing_names = set()
    for item in affiliations_list:
        name = item.get('NAME') or item.get('name')
        if name:
            existing_names.add(name)
    
    # Find missing collaborators
    missing = sorted(all_collaborators - existing_names)
    
    if not missing:
        print(f"All collaborators from the last {years_back} years already have affiliations recorded.")
    else:
        print(f"\nFound {len(missing)} collaborator(s) from the last {years_back} years without affiliations.\n")
        
        # Prompt for each missing collaborator
        new_entries = []
        for name in missing:
            affiliation = input(f"Affiliation for '{name}' (press Enter for default '{default_affiliation}'): ").strip()
            if not affiliation:
                affiliation = default_affiliation
            new_entries.append({
                'name': name,
                'affiliation': affiliation
            })
            print(f"  Added: {name} -> {affiliation}")
        
        # Append new entries to existing list
        affiliations_list.extend(new_entries)
    
        print(f"\nSuccessfully updated {affiliations_path} with {len(new_entries)} new affiliation(s).")
    
    # Sort by "last" name for cleaner YAML
    affiliations_list.sort(key=lambda x: (x.get('name') or x.get('NAME', '')).lower().split()[-1])
    
    # Write updated affiliations back to file
    with open(affiliations_path, 'w') as f:
        yaml.dump(affiliations_list, f, default_flow_style=False, sort_keys=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    functions = {
        'cv': generate_cv,
        'bib': generate_bib,
        'bib_no_underline': lambda data: generate_bib(data, transform_name=False),
        'html': generate_html,
        'r_and_p': generate_r_and_p,
        'collaborators': generate_collaborators,
        'coa_collaborators': lambda data: generate_coa_collaborators(
            data, years_back=args.years_back, affiliations_path=args.affiliations_file
        ),
        'update_affiliations': lambda data: update_affiliations(
            data, affiliations_path=args.affiliations_file, 
            default_affiliation=args.default_affiliation,
            years_back=args.years_back
        ),
    }
    parser.add_argument("output_type", choices=functions.keys())
    parser.add_argument("--yaml_file", default="yaml/publications.yaml")
    parser.add_argument("--years_back", type=int, default=4)
    parser.add_argument("--affiliations_file", default="yaml/affiliations.yaml")
    parser.add_argument("--default_affiliation", default="Carnegie Mellon University")
    args = parser.parse_args()

    with open(args.yaml_file) as f:
        publications_data = yaml.safe_load(f)

    function = functions[args.output_type]
    print(function(publications_data))
