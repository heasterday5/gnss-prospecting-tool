"""Page 3: City Targets — filterable, sortable table of 30 metro areas."""

import streamlit as st
from utils.auth import check_password
check_password()

import pandas as pd
from utils.data_loader import load_cities, load_funding
from utils.styles import inject_css, tier_badge, score_pill, status_badge

st.set_page_config(page_title="City Targets | GNSS", page_icon="🏙️", layout="wide")
inject_css()

st.title("🏙️ City & Metro Targets")

cities = load_cities()
funding = load_funding()

# Sidebar filters
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
    disaster_list = sorted(disaster_types)
    selected_disasters = st.multiselect("Disaster Type", disaster_list)

    dept_types = set()
    for depts in cities["target_dept_types"].dropna():
        for d in str(depts).split(","):
            dept_types.add(d.strip())
    dept_list = sorted(dept_types)
    selected_depts = st.multiselect("Department Type", dept_list)

    uasi_filter = st.selectbox("UASI Designated", ["All", "Yes", "No"])

    score_range = st.slider("Composite Score Range",
                            min_value=float(cities["composite_priority_score"].min()),
                            max_value=float(cities["composite_priority_score"].max()),
                            value=(float(cities["composite_priority_score"].min()),
                                   float(cities["composite_priority_score"].max())),
                            step=0.5)

# Apply filters
filtered = cities.copy()

if selected_tiers:
    filtered = filtered[filtered["priority_tier"].isin(selected_tiers)]

if selected_states:
    filtered = filtered[filtered["state"].isin(selected_states)]

if selected_disasters:
    mask = filtered["primary_disaster_risk"].apply(
        lambda x: any(d.lower() in str(x).lower() for d in selected_disasters))
    filtered = filtered[mask]

if selected_depts:
    mask = filtered["target_dept_types"].apply(
        lambda x: any(d.lower() in str(x).lower() for d in selected_depts))
    filtered = filtered[mask]

if uasi_filter != "All":
    filtered = filtered[filtered["uasi_designated"].str.strip() == uasi_filter]

filtered = filtered[
    (filtered["composite_priority_score"] >= score_range[0]) &
    (filtered["composite_priority_score"] <= score_range[1])
]

# Sort
sort_col = st.selectbox("Sort by", ["composite_priority_score", "priority_rank", "risk_score",
                                     "funding_potential", "city_metro"],
                         index=0)
sort_asc = st.checkbox("Ascending", value=(sort_col == "priority_rank" or sort_col == "city_metro"))
filtered = filtered.sort_values(sort_col, ascending=sort_asc)

st.markdown(f"**Showing {len(filtered)} of {len(cities)} cities**")

# Display as expandable rows
for _, row in filtered.iterrows():
    label = f"{row['priority_rank']}. {row['city_metro']}, {row['state']}  —  Score: {row['composite_priority_score']}"
    with st.expander(label):
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(tier_badge(row["priority_tier"]), unsafe_allow_html=True)
        c2.markdown(f"**Risk Score:** {score_pill(row['risk_score'])}", unsafe_allow_html=True)
        c3.markdown(f"**Funding Potential:** {score_pill(row['funding_potential'])}", unsafe_allow_html=True)
        c4.markdown(f"**Population:** {row['population']}")

        st.markdown(f"""
        **Primary Disaster Risk:** {row['primary_disaster_risk']}
        **Secondary Risks:** {row['secondary_risks']}
        **Infrastructure at Risk:** {row['infrastructure_at_risk']}
        **Preparedness Gap:** {row['preparedness_gap_notes']}
        **Target Departments:** {row['target_dept_types']}
        **Funding Programs:** {row['primary_funding_programs']}
        **UASI Designated:** {row['uasi_designated']}
        **Recent Notes:** {row.get('recent_funding_notes', '')}
        """)
