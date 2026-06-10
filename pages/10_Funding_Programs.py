"""Funding Programs — the full database with live statuses (verified June 2026)."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.data_loader import load_funding
from utils.styles import inject_css, sidebar_brand, page_header, status_badge

st.set_page_config(page_title="Funding Programs | Genasys", page_icon="🛡️", layout="wide")
inject_css()
sidebar_brand()

page_header("Reference", "Funding Programs",
            "Every relevant federal program with current status, windows, and the sales play. "
            "Statuses verified June 2026 — the funding landscape has been volatile, check back often.")

funding = load_funding()

statuses = funding["status"].unique().tolist()
selected_status = st.multiselect("Filter by status", statuses, default=[])

dept_cols = {
    "Police": "police", "Fire/EMS": "fire_ems", "Emergency Mgmt": "emergency_mgmt",
    "Utilities": "utilities", "Critical Infra": "critical_infra",
    "Cities/Counties": "cities_counties", "Events/Venues": "events_venues", "Tribal": "tribal",
}
selected_dept = st.multiselect("Filter by who can use it", list(dept_cols.keys()))

shown = funding.copy()
if selected_status:
    shown = shown[shown["status"].isin(selected_status)]
for label in selected_dept:
    col = dept_cols[label]
    shown = shown[shown[col].astype(str).str.strip() == "X"]

order = {"OPEN": 0, "ACTIVE": 1, "POST-DISASTER": 2, "DELAYED": 3, "UNCERTAIN": 4, "CANCELED": 5}
shown = shown.sort_values(by="status", key=lambda s: s.str.upper().map(order).fillna(9))

for _, fp in shown.iterrows():
    eligible = [label for label, col in dept_cols.items()
                if str(fp.get(col, "")).strip() == "X"]
    st.markdown(f"""
    <div class="gn-card green">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
            <strong style="font-size:1.08em;">{fp['program_name']}</strong>
            {status_badge(fp['status'])}
        </div>
        <div class="gn-value" style="margin:0.35rem 0;"><strong>{fp['funding_level']}</strong> — {fp['administering_agency']} · {fp['eligible_applicants']}</div>
        <div class="gn-value" style="margin:0.25rem 0;">{fp['status_detail']}</div>
        <div class="gn-value" style="margin:0.25rem 0;"><strong>Funds:</strong> {fp['key_eligible_uses']}</div>
        <div class="gn-value" style="margin:0.25rem 0;"><strong>Window:</strong> {fp['window_note']} · <strong>Apply via:</strong> {fp['application_portal']}</div>
        <div class="gn-value" style="margin:0.35rem 0;color:#1D7A8C;"><strong>The play:</strong> {fp['sales_note']}</div>
        <div class="gn-label" style="margin-top:0.3rem;">Fits: {', '.join(eligible) if eligible else '—'}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.subheader("Key Assistance Listing Numbers (for USASpending award searches)")
st.markdown("""
| Number | Program |
|--------|---------|
| 97.067 | HSGP (SHSP / UASI / THSGP) |
| 97.111 | NGWSGP (Warning Systems) |
| 97.044 | AFG (Firefighter Grants) |
| 97.083 | SAFER (Staffing) |
| 97.039 | HMGP (Hazard Mitigation) |
| 97.047 | EMPG (Emergency Mgmt) |
| 97.041 | HHPD (Dam Safety) |
| 10.766 | USDA Community Facilities |
""")
