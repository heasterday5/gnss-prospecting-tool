"""Page 4: Funding Finder — 'I am a [dept type] in [state]' → matching grants."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.data_loader import load_funding, load_states, load_department_types, load_state_grants
from utils.styles import inject_css, status_badge, tier_badge

st.set_page_config(page_title="Funding Finder | GNSS", page_icon="💰", layout="wide")
inject_css()

st.title("💰 Funding Finder")
st.markdown("### I am a...")

dept_types = load_department_types()
funding = load_funding()
states_df = load_states()
grants_df = load_state_grants()

# Dept-type to column mapping for funding CSV
dept_col_map = {
    "Fire / EMS Departments": "fire_ems",
    "Police / Law Enforcement": "police",
    "Emergency Management Agencies": "emergency_mgmt",
    "Utilities (Power, Water, Gas)": "utilities",
    "Critical Infrastructure Operators": "critical_infra",
    "Cities / Counties / Municipalities": "cities_counties",
    "Events / Venues / Mass Gatherings": "events_venues",
    "Tribal Nations": None,  # match on eligible_applicants containing "Tribal"
    "Armed Forces / Military": None,  # match on program name or notes
}

c1, c2 = st.columns(2)
with c1:
    dept_names = [d["department_type"] for d in dept_types]
    selected_dept = st.selectbox("Department Type", dept_names)

with c2:
    state_list = sorted(states_df["state"].tolist())
    selected_state = st.selectbox("State", state_list)

st.markdown("---")

# Find matching dept info
dept_info = next((d for d in dept_types if d["department_type"] == selected_dept), None)

# Filter funding programs
col_key = dept_col_map.get(selected_dept)
if col_key and col_key in funding.columns:
    matched = funding[funding[col_key].str.strip() == "X"]
elif selected_dept == "Tribal Nations":
    matched = funding[funding["eligible_applicants"].str.contains("Trib", case=False, na=False)]
elif selected_dept == "Armed Forces / Military":
    matched = funding[
        funding["program_name"].str.contains("DOD|Military", case=False, na=False) |
        funding["notes_strategy"].str.contains("military|DOD|GSA", case=False, na=False)
    ]
else:
    matched = funding

# Show matching programs
st.subheader(f"Matching Funding Programs ({len(matched)})")

if matched.empty:
    st.info("No specific programs matched. Check the full funding list or consult your state EM agency.")
else:
    for _, fp in matched.iterrows():
        st.markdown(f"""
        <div class="funding-card">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <strong style="font-size:1.1em;">{fp['program_name']}</strong>
                {status_badge(fp['status'])}
            </div>
            <div style="margin:0.5rem 0;">
                <strong>{fp['fy2025_funding']}</strong> — {fp['administering_agency']}
            </div>
            <div style="margin:0.3rem 0;"><strong>Eligible:</strong> {fp['eligible_applicants']}</div>
            <div style="margin:0.3rem 0;"><strong>Key Uses:</strong> {fp['key_eligible_uses']}</div>
            <div style="margin:0.3rem 0;color:#2563EB;"><strong>Strategy:</strong> {fp['notes_strategy']}</div>
            <div style="margin-top:0.5rem;"><small>Portal: {fp['application_portal']}</small></div>
        </div>
        """, unsafe_allow_html=True)

# State grant links
st.markdown("---")
st.subheader(f"State Resources — {selected_state}")

state_row = states_df[states_df["state"] == selected_state]
if not state_row.empty:
    sr = state_row.iloc[0]
    st.markdown(f"{tier_badge(sr['priority_tier'])} **Composite Score:** {sr['composite_score']}", unsafe_allow_html=True)
    st.markdown(f"**Top Programs:** {sr['top_programs']}")

grant_row = grants_df[grants_df["State"].str.strip() == selected_state]
if not grant_row.empty:
    gr = grant_row.iloc[0]
    link_cols = st.columns(3)
    em_url = str(gr.get("Emergency Management Agency URL", "")).strip()
    grants_url = str(gr.get("EM/Homeland Security Grants Page", "")).strip()
    portal_url = str(gr.get("Statewide Grant/Funding Portal", "")).strip()
    if em_url and em_url != "nan":
        link_cols[0].markdown(f"[EM Agency Website]({em_url})")
    if grants_url and grants_url != "nan":
        link_cols[1].markdown(f"[Grants Page]({grants_url})")
    if portal_url and portal_url != "nan":
        link_cols[2].markdown(f"[State Portal]({portal_url})")

# Department sales playbook section
if dept_info:
    st.markdown("---")
    st.subheader(f"Sales Playbook — {selected_dept}")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**Typical Buyer:** {dept_info['typical_buyer_title']}")
        st.markdown(f"**Product Fit:** {dept_info['product_fit']}")
        st.markdown(f"**Pain Points:** {dept_info['pain_points']}")
    with col_b:
        st.markdown(f"**Primary Funding:** {dept_info['primary_funding']}")
        st.markdown(f"**Secondary Funding:** {dept_info['secondary_funding']}")
        st.markdown(f"**Budget Cycle:** {dept_info['budget_cycle_timing']}")

    st.markdown(f"**Sales Approach:** {dept_info['sales_approach']}")
    st.markdown(f"**Decision Process:** {dept_info['decision_process']}")
