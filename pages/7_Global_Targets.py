"""Page 7: Global Targets — international high-risk metros."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.data_loader import load_global_targets
from utils.styles import inject_css, score_pill

st.set_page_config(page_title="Global Targets | GNSS", page_icon="🌍", layout="wide")
inject_css()

st.title("🌍 Global High-Risk Targets")
st.markdown("International metros with high natural disaster risk and infrastructure gaps.")

targets = load_global_targets()

# Sort option
sort_by = st.selectbox("Sort by", ["priority_rank", "risk_score", "city_metro", "country"])
asc = sort_by in ("priority_rank", "city_metro", "country")
targets_sorted = targets.sort_values(sort_by, ascending=asc)

# Display as expandable cards
for _, row in targets_sorted.iterrows():
    label = f"{row['priority_rank']}. {row['city_metro']}, {row['country']}  —  Risk: {row['risk_score']}/10"
    with st.expander(label):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.markdown(f"**Population at Risk:** {row['population_at_risk']}")
            st.markdown(f"**Primary Hazards:** {row['primary_hazards']}")
            wri = row.get('world_risk_index', '')
            if wri and str(wri).strip():
                st.markdown(f"**World Risk Index:** {wri}")
        with c2:
            st.markdown(f"**Infrastructure Gap:** {row['infrastructure_gap']}")
            st.markdown(f"**Procurement Path:** {row['funding_procurement_path']}")
        with c3:
            st.markdown(f"**Risk Score:**")
            st.markdown(score_pill(row["risk_score"]), unsafe_allow_html=True)

        if row.get("notes"):
            st.caption(row["notes"])
