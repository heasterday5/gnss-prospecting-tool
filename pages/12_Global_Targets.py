"""Global Targets — international high-risk metros."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.data_loader import load_global_targets
from utils.styles import inject_css, sidebar_brand, page_header, score_pill

inject_css()
sidebar_brand()

page_header("Reference", "Global High-Risk Targets",
            "International metros with high natural-disaster risk and infrastructure gaps.")

targets = load_global_targets()

sort_by = st.selectbox("Sort by", ["priority_rank", "risk_score", "city_metro", "country"])
asc = sort_by in ("priority_rank", "city_metro", "country")
targets_sorted = targets.sort_values(sort_by, ascending=asc)

for _, row in targets_sorted.iterrows():
    label = f"{row['priority_rank']}. {row['city_metro']}, {row['country']}  —  Risk: {row['risk_score']}/10"
    with st.expander(label):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.markdown(f"**Population at risk:** {row['population_at_risk']}")
            st.markdown(f"**Primary hazards:** {row['primary_hazards']}")
            wri = row.get("world_risk_index", "")
            if wri and str(wri).strip():
                st.markdown(f"**World Risk Index:** {wri}")
        with c2:
            st.markdown(f"**Infrastructure gap:** {row['infrastructure_gap']}")
            st.markdown(f"**Procurement path:** {row['funding_procurement_path']}")
        with c3:
            st.markdown("**Risk score:**")
            st.markdown(score_pill(row["risk_score"]), unsafe_allow_html=True)
        if row.get("notes"):
            st.caption(row["notes"])
