"""Page 5: Department Playbook — buyer personas and sales approaches."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.data_loader import load_department_types, load_cities
from utils.styles import inject_css

st.set_page_config(page_title="Department Playbook | GNSS", page_icon="📋", layout="wide")
inject_css()

st.title("📋 Department Playbook")
st.markdown("Select a buyer type to see the full sales approach, funding sources, and decision process.")

dept_types = load_department_types()
cities = load_cities()

# Icons for department types (emoji fallback)
dept_icons = {
    "Fire / EMS Departments": "🔥",
    "Police / Law Enforcement": "🛡️",
    "Emergency Management Agencies": "⚠️",
    "Utilities (Power, Water, Gas)": "⚡",
    "Critical Infrastructure Operators": "🏗️",
    "Cities / Counties / Municipalities": "🏛️",
    "Events / Venues / Mass Gatherings": "👥",
    "Tribal Nations": "🏔️",
    "Armed Forces / Military": "✈️",
}

# 3x3 grid of department cards
cols_per_row = 3
for i in range(0, len(dept_types), cols_per_row):
    cols = st.columns(cols_per_row)
    for j, col in enumerate(cols):
        idx = i + j
        if idx < len(dept_types):
            d = dept_types[idx]
            icon = dept_icons.get(d["department_type"], "📌")
            with col:
                st.markdown(f"""
                <div class="dept-card">
                    <h4>{icon} {d['department_type']}</h4>
                    <p><strong>Buyer:</strong> {d['typical_buyer_title'][:60]}...</p>
                    <p><strong>Product Fit:</strong> {d['product_fit'][:80]}...</p>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")

# Detailed view
selected = st.selectbox("Select department for full detail",
                         [d["department_type"] for d in dept_types])

dept = next(d for d in dept_types if d["department_type"] == selected)
icon = dept_icons.get(selected, "📌")

st.markdown(f"## {icon} {selected}")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### Buyer Profile")
    st.markdown(f"**Typical Buyer Title:** {dept['typical_buyer_title']}")
    st.markdown(f"**Product Fit:** {dept['product_fit']}")
    st.markdown(f"**Pain Points:** {dept['pain_points']}")

with col_b:
    st.markdown("### Funding Sources")
    st.markdown(f"**Primary:** {dept['primary_funding']}")
    st.markdown(f"**Secondary:** {dept['secondary_funding']}")
    st.markdown(f"**Budget Cycle:** {dept['budget_cycle_timing']}")

st.markdown("### Sales Approach")
st.info(dept["sales_approach"])

st.markdown("### Decision Process")
st.markdown(dept["decision_process"])

# Matching cities
st.markdown("---")
st.subheader("Matching City Targets")
filter_key = dept.get("dept_filter_key", "")
if filter_key:
    matching_cities = cities[cities["target_dept_types"].str.contains(filter_key, case=False, na=False)]
    if not matching_cities.empty:
        display_df = matching_cities[["priority_rank", "city_metro", "state",
                                       "composite_priority_score", "primary_disaster_risk",
                                       "primary_funding_programs"]].copy()
        display_df.columns = ["Rank", "City", "State", "Score", "Primary Risk", "Funding"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No city targets currently matched for this department type.")
else:
    st.info("Filter key not available for this department type.")
