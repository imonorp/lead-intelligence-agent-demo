import os
import pandas as pd

# -------------------------------
# CONFIG: WEIGHTS (from PDF)
# -------------------------------

WEIGHTS = {
    "role_fit": 30,            # title keywords
    "company_intent": 20,      # funding or tech usage
    "technographic": 25,       # similar tech + NAMs
    "location": 10,            # hubs
    "scientific_intent": 40    # recent publications
}

ROLE_KEYWORDS = ["toxicology", "safety", "hepatic", "3d"]
HUBS = ["boston", "cambridge", "bay area", "basel", "uk"]
TECH_KEYWORDS = ["3d", "invitro", "nam", "new approach"]

CURRENT_YEAR = pd.Timestamp.now().year

# -------------------------------
# LOAD ENRICHED LEADS
# -------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(BASE_DIR, "data", "processed", "leads_enriched.csv")
leads_df = pd.read_csv(input_path)

# -------------------------------
# SCORING FUNCTION
# -------------------------------

def calculate_score(row):
    score = 0

    # Role Fit: check paper title and affiliation
    title_affil = str(row["paper_title"] + " " + str(row["affiliation"])).lower()
    if any(word in title_affil for word in ROLE_KEYWORDS):
        score += WEIGHTS["role_fit"]

    # Technographic: check for tech keywords
    if any(word in title_affil for word in TECH_KEYWORDS):
        score += WEIGHTS["technographic"]

    # Location: check person location
    if str(row["person_location"]).lower() in HUBS:
        score += WEIGHTS["location"]

    # Scientific Intent: recent publication (last 2 years)
    try:
        if int(row["year"]) >= CURRENT_YEAR - 2:
            score += WEIGHTS["scientific_intent"]
    except:
        pass

    # Company Intent: placeholder (assume all get full points for now)
    score += WEIGHTS["company_intent"]

    # Cap score at 100
    return min(score, 100)

# -------------------------------
# APPLY SCORING
# -------------------------------

leads_df["probability_score"] = leads_df.apply(calculate_score, axis=1)

# Rank leads by probability_score (highest first)
leads_df = leads_df.sort_values(by="probability_score", ascending=False).reset_index(drop=True)
leads_df["rank"] = leads_df.index + 1

# -------------------------------
# SAVE RANKED LEADS
# -------------------------------

output_path = os.path.join(BASE_DIR, "data", "processed", "leads_ranked.csv")
leads_df.to_csv(output_path, index=False)

print(f"Saved {len(leads_df)} ranked leads to {output_path}")
