import os
from Bio import Entrez
import pandas as pd
from datetime import datetime

# REQUIRED: always tell NCBI who you are
Entrez.email = "pronomibiswas@gmail.com"

# Search terms based on internship description
SEARCH_TERMS = [
    "Drug-Induced Liver Injury",
    "3D cell culture",
    "Organ-on-chip",
    "Hepatic toxicity"
]

MAX_RESULTS = 50  # keep small for prototype
CURRENT_YEAR = datetime.now().year


def search_pubmed(term):
    handle = Entrez.esearch(
        db="pubmed",
        term=term,
        retmax=MAX_RESULTS
    )
    record = Entrez.read(handle)
    return record["IdList"]


def fetch_details(id_list):
    if not id_list:
        return []

    handle = Entrez.efetch(
        db="pubmed",
        id=",".join(id_list),
        retmode="xml"
    )
    records = Entrez.read(handle)
    return records["PubmedArticle"]


def extract_paper_data(records):
    papers = []

    for article in records:
        medline = article["MedlineCitation"]
        article_data = medline.get("Article", {})

        title = article_data.get("ArticleTitle", "")
        abstract = ""
        if "Abstract" in article_data:
            abstract = " ".join(article_data["Abstract"].get("AbstractText", []))

        journal = article_data.get("Journal", {}).get("Title", "")

        year = None
        try:
            year = int(article_data["Journal"]["JournalIssue"]["PubDate"]["Year"])
        except Exception:
            continue

        if CURRENT_YEAR - year > 2:
            continue

        authors_list = article_data.get("AuthorList", [])
        authors = []
        affiliation = ""

        for author in authors_list:
            if "LastName" in author and "ForeName" in author:
                authors.append(f"{author['ForeName']} {author['LastName']}")
                if "AffiliationInfo" in author and author["AffiliationInfo"]:
                    affiliation = author["AffiliationInfo"][0].get("Affiliation", "")

        papers.append({
            "title": title,
            "authors": ", ".join(authors),
            "journal": journal,
            "year": year,
            "abstract": abstract,
            "affiliation": affiliation
        })

    return papers



def main():
    all_papers = []

    for term in SEARCH_TERMS:
        ids = search_pubmed(term)
        records = fetch_details(ids)
        papers = extract_paper_data(records)
        all_papers.extend(papers)

    df = pd.DataFrame(all_papers)

    # Remove duplicates
    df = df.drop_duplicates(subset="title")

    # Save output
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(BASE_DIR, "data", "processed")

# Ensure directory exists (IMPORTANT on Windows)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "papers.csv")

    df.to_csv(output_path, index=False)


    print(f"Saved {len(df)} papers to {output_path}")


if __name__ == "__main__":
    main()
