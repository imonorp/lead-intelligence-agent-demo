import streamlit as st
import pandas as pd
import os

# -------------------------------
# LOAD DATA
# -------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(BASE_DIR, "data", "processed", "leads_ranked.csv")
leads_df = pd.read_csv(input_path)

# -------------------------------
# DASHBOARD TITLE
# -------------------------------
st.title("Lead Intelligence Dashboard")
st.markdown("Dynamic, ranked lead list for 3D in-vitro models")

# -------------------------------
# FILTER BY LOCATION
# -------------------------------
locations = ["All"] + sorted(leads_df["person_location"].dropna().unique().tolist())
selected_location = st.selectbox("Filter by Person Location:", locations)

if selected_location != "All":
    filtered_df = leads_df[leads_df["person_location"] == selected_location]
else:
    filtered_df = leads_df.copy()

# -------------------------------
# SEARCH BY NAME OR PAPER
# -------------------------------
search_text = st.text_input("Search Name or Paper Title:")

if search_text:
    filtered_df = filtered_df[
        filtered_df["name"].str.contains(search_text, case=False, na=False) |
        filtered_df["paper_title"].str.contains(search_text, case=False, na=False)
    ]

# -------------------------------
# SHOW TABLE
# -------------------------------
st.dataframe(filtered_df)

# -------------------------------
# DOWNLOAD CSV
# -------------------------------
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="Download Filtered Leads as CSV",
    data=csv,
    file_name="filtered_leads.csv",
    mime="text/csv"
)
