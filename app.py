"""Genasys Funding Intelligence — entry point & navigation.

Page titles and grouping live here (st.navigation); page files carry content only.
"""

import streamlit as st

st.set_page_config(
    page_title="Genasys Funding Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.auth import check_password
check_password()

pg = st.navigation({
    "": [
        st.Page("pages/Home.py", title="Home", icon="🏠", default=True),
    ],
    "Find & research": [
        st.Page("pages/2_Find_Potential_Focus.py", title="Find Potential Focus", icon="🎯"),
        st.Page("pages/0_Start_Here.py", title="Research Specific Account/Target", icon="🔎"),
        st.Page("pages/1_Funding_Pathfinder.py", title="Funding Pathfinder", icon="🧭"),
    ],
    "Engage": [
        st.Page("pages/4_Meeting_Prep.py", title="Meeting Prep", icon="📇"),
        st.Page("pages/5_Procurement_Toolkit.py", title="Procurement Toolkit", icon="📋"),
        st.Page("pages/6_Email_Library.py", title="Email Library", icon="✉️"),
        st.Page("pages/7_Buyer_Personas.py", title="Buyer Personas", icon="🧑‍🤝‍🧑"),
    ],
    "Reference": [
        st.Page("pages/11_Resource_Links.py", title="Resource Links", icon="🔗"),
        st.Page("pages/10_Funding_Programs.py", title="Funding Programs", icon="💰"),
        st.Page("pages/8_State_Explorer.py", title="State Explorer", icon="🗺️"),
        st.Page("pages/9_City_Targets.py", title="City Targets", icon="🏙️"),
        st.Page("pages/12_Global_Targets.py", title="Global Targets", icon="🌐"),
    ],
})
pg.run()
