"""City Targets — filterable, sortable priority metros."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.data_loader import load_cities
from utils.styles import inject_css, sidebar_brand, page_header, tier_badge, score_pill

inject_css()
sidebar_brand()

page_header("Reference", "City & Metro Targets",
            "Priority metro areas ranked by disaster risk, preparedness gaps, and funding potential.")

cities = load_cities()

with st.sidebar:
    st.subheader("Filters")
    tier_options = sorted(cities["priority_tier"].dropna().unique().tolist())
    selected_tiers = st.multiselect("Priority Tier", tier_options, default=tier_options)
    state_options = sorted(cities["state"].dropna().unique().tolist())
    selected_states = st.multiselect("State", state_options)

    disaster_types = set()
    for risks in cities["primary_disaster_risk"].dropna():
        for r in str(risks).split(","):
            disaster_types.add(r.strip())
    selected_disasters = st.multiselect("Disaster Type", sorted(disaster_types))

    dept_types = set()
    for depts in cities["target_dept_types"].dropna():
        for d in str(depts).split(","):
            dept_types.add(d.strip())
    selected_depts = st.multiselect("Department Type", sorted(dept_types))

    uasi_filter = st.selectbox("UASI Designated", ["All", "Yes", "No"])

filtered = cities.copy()
if selected_tiers:
    filtered = filtered[filtered["priority_tier"].isin(selected_tiers)]
if selected_states:
    filtered = filtered[filtered["state"].isin(selected_states)]
if selected_disasters:
    filtered = filtered[filtered["primary_disaster_risk"].apply(
        lambda x: any(d.lower() in str(x).lower() for d in selected_disasters))]
if selected_depts:
    filtered = filtered[filtered["target_dept_types"].apply(
        lambda x: any(d.lower() in str(x).lower() for d in selected_depts))]
if uasi_filter != "All":
    filtered = filtered[filtered["uasi_designated"].str.strip() == uasi_filter]

sort_col = st.selectbox("Sort by", ["composite_priority_score", "priority_rank", "risk_score",
                                    "funding_potential", "city_metro"], index=0)
sort_asc = sort_col in ("priority_rank", "city_metro")
filtered = filtered.sort_values(sort_col, ascending=sort_asc)

st.markdown(f"**Showing {len(filtered)} of {len(cities)} metros**")

for _, row in filtered.iterrows():
    with st.expander(f"{row['priority_rank']}. {row['city_metro']}, {row['state']} — score {row['composite_priority_score']}"):
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(tier_badge(row["priority_tier"]), unsafe_allow_html=True)
        c2.markdown(f"**Risk:** {score_pill(row['risk_score'])}", unsafe_allow_html=True)
        c3.markdown(f"**Funding potential:** {score_pill(row['funding_potential'])}", unsafe_allow_html=True)
        c4.markdown(f"**Population:** {row['population']}")
        st.markdown(f"""
**Primary disaster risk:** {row['primary_disaster_risk']}
**Secondary risks:** {row['secondary_risks']}
**Infrastructure at risk:** {row['infrastructure_at_risk']}
**Preparedness gap:** {row['preparedness_gap_notes']}
**Target departments:** {row['target_dept_types']}
**Funding programs:** {row['primary_funding_programs']}
**UASI designated:** {row['uasi_designated']}
**Recent notes:** {row.get('recent_funding_notes', '')}
""")
