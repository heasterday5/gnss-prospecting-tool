"""Page 2: State Explorer — drill into a state's risk profile and funding."""

import streamlit as st
from utils.auth import check_password
check_password()

import plotly.graph_objects as go
from utils.data_loader import load_states, load_cities, load_funding, load_state_grants
from utils.styles import inject_css, tier_badge, score_pill, status_badge

st.set_page_config(page_title="State Explorer | GNSS", page_icon="🗺️", layout="wide")
inject_css()

st.title("🗺️ State Explorer")

states = load_states()
cities = load_cities()
funding = load_funding()
grants = load_state_grants()

# State selector
state_list = sorted(states["state"].tolist())
selected = st.selectbox("Select a state", state_list, index=state_list.index("Texas") if "Texas" in state_list else 0)

row = states[states["state"] == selected].iloc[0]

# Header card
c1, c2, c3 = st.columns([4, 1, 1])
with c1:
    st.markdown(f"## {selected}")
    st.markdown(f"**Key Hazards:** {row['key_hazards']}")
with c2:
    st.markdown(tier_badge(row["priority_tier"]), unsafe_allow_html=True)
with c3:
    st.markdown(f"### {score_pill(row['composite_score'])}", unsafe_allow_html=True)

st.markdown("---")

# Risk dimension chart
risk_dims = ["Wildfire", "Flood", "Earthquake", "Hurricane", "Tornado", "Tsunami",
             "Terrorism", "Prep Gap", "Funding Potential"]
risk_keys = ["wildfire", "flood", "earthquake", "hurricane", "tornado", "tsunami",
             "terrorism", "prep_gap", "funding_potential"]
values = [row[k] for k in risk_keys]

colors = ["#DC2626" if v >= 8 else "#CA8A04" if v >= 5 else "#16A34A" for v in values]

fig = go.Figure(go.Bar(
    y=risk_dims, x=values, orientation="h",
    marker_color=colors,
    text=values, textposition="outside",
))
fig.update_layout(
    title=f"{selected} — Risk Dimensions (1-10 scale)",
    xaxis=dict(range=[0, 11], title="Score"),
    yaxis=dict(autorange="reversed"),
    height=380, margin=dict(l=120, r=40, t=50, b=30),
    plot_bgcolor="white",
)
st.plotly_chart(fig, use_container_width=True)

# Cities in this state
st.subheader(f"Cities in {selected}")
state_cities = cities[cities["state"] == selected.split()[0][:2] if len(selected) > 2 else selected]
# Match by state abbreviation
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
    st.info(f"No priority city targets currently listed in {selected}. Check the City Targets page for the full list.")
else:
    for _, c in state_cities.iterrows():
        with st.expander(f"{c['city_metro']} — Score: {c['composite_priority_score']}"):
            st.markdown(f"**Primary Risk:** {c['primary_disaster_risk']}  \n"
                       f"**Secondary Risks:** {c['secondary_risks']}  \n"
                       f"**Infrastructure at Risk:** {c['infrastructure_at_risk']}  \n"
                       f"**Target Departments:** {c['target_dept_types']}  \n"
                       f"**Funding Programs:** {c['primary_funding_programs']}  \n"
                       f"**UASI Designated:** {c['uasi_designated']}  \n"
                       f"**Notes:** {c.get('recent_funding_notes', '')}")

# Funding programs that mention this state
st.subheader("Applicable Funding Programs")
st.markdown(f"**Top Programs:** {row['top_programs']}")

# Parse top_programs to highlight matching ones
top_progs = [p.strip() for p in str(row["top_programs"]).split(",")]
for _, fp in funding.iterrows():
    # Show programs that are in the state's top list or are broadly available
    prog_name = fp["program_name"]
    match = any(t.lower() in prog_name.lower() or prog_name.lower().startswith(t.lower().split()[0])
                for t in top_progs)
    if match:
        st.markdown(f"""
        <div class="funding-card">
            <strong>{prog_name}</strong> {status_badge(fp['status'])}
            <br><small>{fp['fy2025_funding']} — {fp['eligible_applicants']}</small>
            <br><em>{fp['key_eligible_uses'][:120]}...</em>
        </div>
        """, unsafe_allow_html=True)

# State grant directory links
st.subheader("State Grant Resources")
grant_row = grants[grants["State"].str.strip() == selected]
if not grant_row.empty:
    gr = grant_row.iloc[0]
    em_url = str(gr.get("Emergency Management Agency URL", "")).strip()
    grants_url = str(gr.get("EM/Homeland Security Grants Page", "")).strip()
    portal_url = str(gr.get("Statewide Grant/Funding Portal", "")).strip()

    link_cols = st.columns(3)
    if em_url and em_url != "nan":
        link_cols[0].markdown(f"[EM Agency Website]({em_url})")
    if grants_url and grants_url != "nan":
        link_cols[1].markdown(f"[Grants Page]({grants_url})")
    if portal_url and portal_url != "nan":
        link_cols[2].markdown(f"[State Portal]({portal_url})")
else:
    st.info("Grant directory links not available for this state.")
