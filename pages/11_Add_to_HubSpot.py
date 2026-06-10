"""Add Prospects to HubSpot — pipeline handoff + funded-agency research resources."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.styles import inject_css, sidebar_brand, page_header

st.set_page_config(page_title="Add to HubSpot | Genasys", page_icon="🛡️", layout="wide")
inject_css()
sidebar_brand()

page_header("Pipeline", "Add Prospects to HubSpot",
            "Found a funded prospect? Log it where the team can see pipeline build.")

st.markdown("""
<div class="gn-hero" style="padding:1.8rem 2rem;">
    <h1 style="font-size:1.5rem;">Add them to the Initial Sales Stage</h1>
    <p>This tool is for research and discovery. All prospect tracking happens in HubSpot —
    add promising agencies to the <strong>Initial Sales Stage</strong> so the full team has
    visibility into pipeline activity. Include the funding source you identified in the deal notes.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("#### What to capture in the deal record")
st.markdown("""
- **Funding source identified** (program + status, e.g. "HMGP — DR-4781 declared 03/2025")
- **Signal that triggered outreach** (from the Signal Playbook)
- **Buyer roles engaged** (Outcome Owner / Problem Owner names)
- **Next milestone** (discovery call, grant scoping with Lexipol, Sourcewell quote)
""")

st.markdown("---")
st.subheader("Research resources — find agencies that already hold money")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **USASpending.gov** — search federal awards by Assistance Listing Number
    (see the table on the Funding Programs page), state, county, and date range.
    [Open award search](https://www.usaspending.gov/search)

    **FEMA Grants Portal** — check awarded grants by program and state:
    [go.fema.gov](https://go.fema.gov)

    **FEMA disaster declarations** — the HMGP trigger:
    [fema.gov/disaster/declarations](https://www.fema.gov/disaster/declarations)
    """)
with col2:
    st.markdown("""
    **Lexipol GrantFinder** — tracks ~15,000 grant programs; filter by department
    type and location, set alerts for new announcements.

    **National Inventory of Dams** — find high-hazard dams by county for the
    HHPD play: [nid.usace.army.mil](https://nid.usace.army.mil)

    **County Hazard Mitigation Plans** — Google "[county] hazard mitigation plan"
    and search for siren/evacuation/communication gaps.
    """)
