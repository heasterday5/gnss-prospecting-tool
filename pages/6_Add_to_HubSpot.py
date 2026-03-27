"""Page 6: Add Prospects to HubSpot — redirect sales team to HubSpot for tracking."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.styles import inject_css

st.set_page_config(page_title="Add to HubSpot | GNSS", page_icon="📊", layout="wide")
inject_css()

st.title("📊 Add Prospects to HubSpot")

st.markdown("""
<div style="background:linear-gradient(135deg, #163443 0%, #56C8DA 100%);
            color:white; padding:2rem; border-radius:12px; margin:1rem 0 2rem;">
    <h2 style="color:white; margin:0 0 0.5rem;">Found a promising prospect or funded agency?</h2>
    <p style="font-size:1.1rem; opacity:0.95; margin:0;">
        Add them directly to the <strong>Initial Sales Stage</strong> in HubSpot.
        This keeps all prospect tracking in one place where the full team can see pipeline activity.
    </p>
</div>
""", unsafe_allow_html=True)

st.info("💡 **This tool is for research and discovery only.** All prospect tracking happens in HubSpot — add promising agencies to the Initial Sales Stage so the full team has visibility.")

st.markdown("---")

# Keep the research reference section — still useful for finding funded agencies
st.subheader("Research Resources")
st.markdown("Use these tools to identify agencies that have received funding, then add them to HubSpot.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **USASpending.gov** — Search federal awards by:
    - Assistance Listing Number (CFDA)
    - Filter by state/county, date range, recipient
    - [Open USASpending Award Search](https://www.usaspending.gov/search)

    **FEMA Grants Portal** — Check awarded grants:
    - [go.fema.gov](https://go.fema.gov) — search by program and state
    """)

with col2:
    st.markdown("""
    **Lexipol GrantFinder** — Tracks ~15,000 grant programs:
    - Filter by department type and location
    - Set alerts for new funding announcements

    **Distill.io / Visualping** — Monitor grant pages:
    - Set up monitoring on state EM agency grant pages
    - Get notified when new awards are posted
    """)

st.markdown("---")

st.subheader("Key Assistance Listing Numbers")
st.markdown("""
| Number | Program |
|--------|---------|
| 97.067 | HSGP (Homeland Security) |
| 97.111 | NGWSGP (Warning Systems) |
| 97.044 | AFG (Firefighter Grants) |
| 97.083 | SAFER (Staffing) |
| 97.039 | HMGP (Hazard Mitigation) |
| 97.047 | EMPG (Emergency Mgmt) |
""")
