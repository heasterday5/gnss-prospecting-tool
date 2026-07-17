"""State Explorer — risk profile, verified grant links, and priority programs by state."""

import streamlit as st
from utils.auth import check_password
check_password()

import plotly.graph_objects as go
from utils.data_loader import load_states, load_cities, load_funding, load_state_grants
from utils.styles import (inject_css, sidebar_brand, page_header, tier_badge,
                          score_pill, status_badge, NAVY, GREEN)

inject_css()
sidebar_brand()

page_header("Reference", "State Explorer",
            "Risk profile, verified funding links (re-checked June 2026), and priority programs for every state.")

states = load_states()
cities = load_cities()
funding = load_funding()
grants = load_state_grants()

state_list = sorted(states["state"].tolist())
selected = st.selectbox("Select a state", state_list,
                        index=state_list.index("Texas") if "Texas" in state_list else 0)

row = states[states["state"] == selected].iloc[0]

c1, c2, c3 = st.columns([4, 1, 1])
with c1:
    st.markdown(f"## {selected}")
    st.markdown(f"**Key hazards:** {row['key_hazards']}")
with c2:
    st.markdown(tier_badge(row["priority_tier"]), unsafe_allow_html=True)
with c3:
    st.markdown(f"### {score_pill(row['composite_score'])}", unsafe_allow_html=True)

# ---- Verified state links up top (the thing reps actually click) ----
grant_row = grants[grants["State"].str.strip() == selected]
if not grant_row.empty:
    gr = grant_row.iloc[0]
    em_url = str(gr.get("Emergency Management Agency URL", "")).strip()
    grants_url = str(gr.get("EM/Homeland Security Grants Page", "")).strip()
    portal_url = str(gr.get("Statewide Grant/Funding Portal", "")).strip()
    links = []
    if em_url and em_url != "nan":
        links.append(f'<a href="{em_url}">{gr["Agency Name"]}</a>')
    if grants_url and grants_url != "nan":
        links.append(f'<a href="{grants_url}">Grants page</a>')
    if portal_url and portal_url != "nan":
        links.append(f'<a href="{portal_url}">Statewide funding portal</a>')
    st.markdown(f"""
    <div class="gn-card green">
        <div class="gn-label">Verified funding links · {gr['Link Status']}</div>
        <div class="gn-value" style="font-size:1.02rem;">{' &nbsp;·&nbsp; '.join(links)}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---- Risk chart ----
risk_dims = ["Wildfire", "Flood", "Earthquake", "Hurricane", "Tornado", "Tsunami",
             "Terrorism", "Prep Gap", "Funding Potential"]
risk_keys = ["wildfire", "flood", "earthquake", "hurricane", "tornado", "tsunami",
             "terrorism", "prep_gap", "funding_potential"]
values = [row[k] for k in risk_keys]
colors = ["#B91C1C" if v >= 8 else "#CA8A04" if v >= 5 else "#15803D" for v in values]

fig = go.Figure(go.Bar(y=risk_dims, x=values, orientation="h",
                       marker_color=colors, text=values, textposition="outside"))
fig.update_layout(
    title=dict(text=f"{selected} — risk dimensions (1–10)", font=dict(family="Inter", color=NAVY)),
    xaxis=dict(range=[0, 11], title="Score"),
    yaxis=dict(autorange="reversed"),
    height=380, margin=dict(l=120, r=40, t=50, b=30),
    plot_bgcolor="white", font=dict(family="Inter"),
)
st.plotly_chart(fig, use_container_width=True)

# ---- Priority programs ----
st.subheader("Priority funding programs")
st.markdown(f"**State playbook:** {row['top_programs']}")
top_progs = [p.strip() for p in str(row["top_programs"]).split(",")]
for _, fp in funding.iterrows():
    prog_name = fp["program_name"]
    match = any(t.lower() in prog_name.lower() or prog_name.lower().startswith(t.lower().split()[0])
                for t in top_progs if t)
    if match:
        st.markdown(f"""
        <div class="gn-card green">
            <strong>{prog_name}</strong> &nbsp;{status_badge(fp['status'])}
            <div class="gn-value" style="margin-top:0.25rem;">{fp['funding_level']} — {fp['eligible_applicants']}</div>
            <div class="gn-value" style="margin-top:0.25rem;color:#1D7A8C;">{fp['sales_note']}</div>
        </div>
        """, unsafe_allow_html=True)

# ---- Cities in state ----
st.subheader(f"Priority metros in {selected}")
state_abbrevs = {
    "Texas": "TX", "California": "CA", "Florida": "FL", "Louisiana": "LA",
    "Oklahoma": "OK", "Washington": "WA", "Oregon": "OR", "Colorado": "CO",
    "Georgia": "GA", "South Carolina": "SC", "North Carolina": "NC",
    "Tennessee": "TN", "Alabama": "AL", "Iowa": "IA", "Pennsylvania": "PA",
    "New York": "NY", "Mississippi": "MS", "Kansas": "KS", "Idaho": "ID",
    "Utah": "UT", "Nevada": "NV", "Arizona": "AZ", "South Dakota": "SD",
    "Illinois": "IL", "Virginia": "VA", "Hawaii": "HI", "Massachusetts": "MA",
    "New Jersey": "NJ", "Michigan": "MI", "Maryland": "MD", "Missouri": "MO",
    "Indiana": "IN", "Minnesota": "MN", "Arkansas": "AR", "Kentucky": "KY",
    "Nebraska": "NE", "Ohio": "OH", "Connecticut": "CT", "Delaware": "DE",
    "Montana": "MT", "Wisconsin": "WI", "West Virginia": "WV",
    "New Hampshire": "NH", "New Mexico": "NM", "Maine": "ME", "Vermont": "VT",
    "Wyoming": "WY", "Rhode Island": "RI", "North Dakota": "ND",
    "District of Columbia": "DC",
}
abbrev = state_abbrevs.get(selected, "")
state_cities = cities[cities["state"] == abbrev]

if state_cities.empty:
    st.info(f"No priority metros currently listed in {selected} — see City Targets for the full national list.")
else:
    for _, c in state_cities.iterrows():
        with st.expander(f"{c['city_metro']} — score {c['composite_priority_score']}"):
            st.markdown(f"**Primary risk:** {c['primary_disaster_risk']}  \n"
                        f"**Secondary risks:** {c['secondary_risks']}  \n"
                        f"**Infrastructure at risk:** {c['infrastructure_at_risk']}  \n"
                        f"**Target departments:** {c['target_dept_types']}  \n"
                        f"**Funding programs:** {c['primary_funding_programs']}  \n"
                        f"**UASI designated:** {c['uasi_designated']}  \n"
                        f"**Notes:** {c.get('recent_funding_notes', '')}")
