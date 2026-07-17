"""Buyer Personas — Outcome Owners vs Problem Owners, from the Growth Playbook."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.styles import inject_css, sidebar_brand, page_header
from utils.data_loader import load_personas, load_trends

inject_css()
sidebar_brand()

page_header(
    "Who you're selling to",
    "Buyer Personas",
    "From the Growth Playbook: every deal has an Outcome Owner (strategic/political) and a "
    "Problem Owner (operational/tactical). Know both, ask each the right questions.",
)

personas = load_personas()
trends = load_trends()

tabs = st.tabs([p["market"] for p in personas])

for tab, p in zip(tabs, personas):
    with tab:
        st.markdown(f"""
        <div class="gn-card teal">
            <div class="gn-label">Primary products</div>
            <div class="gn-value"><strong>{p['primary_products']}</strong> &nbsp;·&nbsp; Focus: {p['focus']}</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2, gap="large")
        for col, key in ((c1, "outcome_owner"), (c2, "problem_owner")):
            o = p[key]
            with col:
                st.markdown(f"#### {o['title']}")
                st.markdown("**Roles:** " + ", ".join(o["roles"]))
                st.markdown("**Objectives:**")
                for x in o["objectives"]:
                    st.markdown(f"- {x}")
                st.markdown("**Challenges:**")
                for x in o["challenges"]:
                    st.markdown(f"- {x}")
                st.markdown("**Personal value (what's in it for them):**")
                for x in o["personal_value"]:
                    st.markdown(f"- {x}")
                st.markdown("**Questions to ask:**")
                for x in o["questions"]:
                    st.markdown(f"> {x}")

st.markdown("---")
st.markdown("### Trends — open any conversation as an advisor")
tc = st.columns(len(trends))
for col, t in zip(tc, trends):
    with col:
        st.markdown(f"""
        <div class="gn-card green" style="height:100%;">
            <h4 style="font-size:0.95rem;">{t['title']}</h4>
            <div class="gn-value" style="font-size:0.85rem;"><strong>{t['stat']}</strong></div>
            <div class="gn-label" style="margin-top:0.4rem;">{t['source']}</div>
            <div class="gn-value" style="font-size:0.85rem;margin-top:0.4rem;">{t['use_it']}</div>
        </div>
        """, unsafe_allow_html=True)
