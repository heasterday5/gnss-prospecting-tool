"""Page 6: Funded Agency Tracker — track outreach to agencies with recent awards."""

import streamlit as st
from utils.auth import check_password
check_password()

import pandas as pd
from utils.data_loader import load_tracker, save_tracker
from utils.styles import inject_css

st.set_page_config(page_title="Funded Agency Tracker | GNSS", page_icon="📊", layout="wide")
inject_css()

st.title("📊 Funded Agency Tracker")

# Instructions
with st.expander("How to Find Funded Agencies", expanded=False):
    st.markdown("""
    ### Step-by-Step: Identify Agencies That Received Funding

    **1. USASpending.gov** — Search federal awards by:
    - Assistance Listing Number (CFDA): `97.067` = HSGP, `97.111` = NGWSGP, `97.044` = AFG
    - Filter by state/county, date range, recipient
    - [USASpending Award Search](https://www.usaspending.gov/search)

    **2. FEMA Grants Portal** — Check awarded grants:
    - [go.fema.gov](https://go.fema.gov) → search by program and state

    **3. Lexipol GrantFinder** — Tracks ~15,000 grant programs:
    - Filter by department type and location
    - Set alerts for new funding announcements

    **4. Distill.io / Visualping** — Monitor web pages for changes:
    - Set up monitoring on state EM agency grant pages
    - Get notified when new awards are posted

    ### Key Assistance Listing Numbers
    | Number | Program |
    |--------|---------|
    | 97.067 | HSGP (Homeland Security) |
    | 97.111 | NGWSGP (Warning Systems) |
    | 97.044 | AFG (Firefighter Grants) |
    | 97.083 | SAFER (Staffing) |
    | 97.039 | HMGP (Hazard Mitigation) |
    | 97.047 | EMPG (Emergency Mgmt) |
    """)

# Load current tracker data
tracker = load_tracker()

st.subheader("Tracked Agencies")

# Status filter
status_options = ["All"] + sorted(tracker["outreach_status"].dropna().unique().tolist())
status_filter = st.selectbox("Filter by outreach status", status_options)

display = tracker.copy()
if status_filter != "All":
    display = display[display["outreach_status"] == status_filter]

# Editable dataframe
edited = st.data_editor(
    display,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "outreach_status": st.column_config.SelectboxColumn(
            "Status",
            options=["Not contacted", "Initial outreach", "Meeting scheduled",
                     "Proposal sent", "Closed-Won", "Closed-Lost", "Follow-up needed"],
        ),
        "department_type": st.column_config.SelectboxColumn(
            "Dept Type",
            options=["Fire/EMS", "Police", "Emergency Mgmt", "Utility",
                     "Critical Infra", "City/County", "Events", "Tribal", "Military"],
        ),
    },
    hide_index=True,
)

# Save and download buttons
c1, c2 = st.columns(2)
with c1:
    if st.button("Save Changes", type="primary"):
        save_tracker(edited)
        st.success("Tracker saved!")
        st.rerun()

with c2:
    csv_data = tracker.to_csv(index=False)
    st.download_button("Download as CSV", csv_data,
                       file_name="genasys_funded_agency_tracker.csv",
                       mime="text/csv")

# Add new entry form
st.markdown("---")
st.subheader("Add New Agency")

with st.form("add_agency"):
    fc = st.columns(3)
    agency = fc[0].text_input("Agency Name")
    state = fc[1].text_input("State")
    city = fc[2].text_input("City/County")

    fc2 = st.columns(3)
    dept = fc2[0].selectbox("Department Type",
                             ["Fire/EMS", "Police", "Emergency Mgmt", "Utility",
                              "Critical Infra", "City/County", "Events", "Tribal", "Military"])
    program = fc2[1].text_input("Grant Program")
    amount = fc2[2].text_input("Award Amount")

    fc3 = st.columns(3)
    date = fc3[0].text_input("Award Date (YYYY-MM-DD)")
    listing = fc3[1].text_input("Assistance Listing #")
    contact = fc3[2].text_input("Contact Info")

    notes = st.text_area("Notes")

    if st.form_submit_button("Add to Tracker"):
        if agency:
            new_row = pd.DataFrame([{
                "agency_name": agency, "state": state, "city_county": city,
                "department_type": dept, "grant_program": program,
                "award_amount": amount, "award_date": date,
                "assistance_listing": listing, "usaspending_id": "",
                "contact_info": contact, "outreach_status": "Not contacted",
                "notes": notes,
            }])
            updated = pd.concat([tracker, new_row], ignore_index=True)
            save_tracker(updated)
            st.success(f"Added {agency}!")
            st.rerun()
        else:
            st.warning("Please enter an agency name.")
