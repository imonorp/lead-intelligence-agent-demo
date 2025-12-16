import os
import pandas as pd

# -------------------------------
# DAY 4 ENRICHMENT FUNCTIONS
# -------------------------------

def generate_email(name, affiliation):
    """
    Create a placeholder email in the format:
    firstname.lastname@affiliation.com
    """
    if pd.isna(name) or name.strip() == "":
        return ""
    
    # sanitize name
    parts = name.strip().lower().split()
    if len(parts) < 2:
        parts.append("unknown")
    first, last = parts[0], parts[-1]

    # sanitize affiliation
    if pd.isna(affiliation) or affiliation.strip() == "":
        domain = "example.com"
    else:
        domain = "".join(c for c in affiliation.lower() if c.isalnum())
        domain += ".com"

    return f"{first}.{last}@{domain}"

def assign_location(affiliation):
    """
    Simple heuristic: if city/country keywords exist, return them,
    otherwise return 'Unknown'
    """
    if pd.isna(affiliation) or affiliation.strip() == "":
        return "Unknown"

    affiliation_lower = affiliation.lower()
    hubs = ["boston", "cambridge", "bay area", "basel", "uk"]
    for hub in hubs:
        if hub in affiliation_lower:
            return hub.title()
    return "Unknown"


# -------------------------------
# LOAD PAPERS AND CREATE LEADS
# -------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(BASE_DIR, "data", "processed", "papers.csv")
papers_df = pd.read_csv(input_path)

# Prepare person-level leads
leads = []

for _, row in papers_df.iterrows():
    authors_cell = row.get("authors", "")
    
    if pd.isna(authors_cell) or authors_cell.strip() == "":
        continue  # skip papers with no authors

    authors = authors_cell.split(", ")
    for author in authors:
        if author.strip() == "":
            continue
        leads.append({
            "name": author.strip(),
            "paper_title": row.get("title", ""),
            "affiliation": row.get("affiliation", ""),
            "year": row.get("year", "")
        })

# Convert to DataFrame
leads_df = pd.DataFrame(leads)
leads_df = leads_df.drop_duplicates(subset=["name", "paper_title"])

# -------------------------------
# APPLY ENRICHMENT
# -------------------------------
leads_df["email"] = leads_df.apply(lambda row: generate_email(row["name"], row["affiliation"]), axis=1)
leads_df["person_location"] = leads_df["affiliation"].apply(assign_location)
leads_df["company_hq"] = leads_df["person_location"]  # placeholder

# -------------------------------
# SAVE ENRICHED LEADS
# -------------------------------
output_path = os.path.join(BASE_DIR, "data", "processed", "leads_enriched.csv")
leads_df.to_csv(output_path, index=False)

print(f"Saved {len(leads_df)} enriched leads to {output_path}")
