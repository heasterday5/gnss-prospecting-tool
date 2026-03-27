"""GNSS Sales Prospecting Tool — Main Entry Point."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.styles import inject_css
from utils.data_loader import load_metrics

st.set_page_config(
    page_title="GNSS Prospecting Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# Sidebar branding
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0;">
        <h2 style="margin:0;font-size:1.4rem;">🎯 GNSS</h2>
        <p style="margin:0;font-size:0.85rem;opacity:0.8;">Sales Prospecting Tool</p>
    </div>
    <hr style="border-color:rgba(255,255,255,0.2);margin:0.5rem 0;">
    """, unsafe_allow_html=True)

    metrics = load_metrics()
    st.caption(f"Data updated: {metrics.get('last_updated', 'N/A')}")

# Landing page content
st.title("GNSS Sales Prospecting Tool")
st.markdown("Use the **sidebar pages** to explore targets, find funding, and build your sales strategy.")

metrics = load_metrics()
cols = st.columns(4)
for i, card in enumerate(metrics.get("cards", [])):
    with cols[i]:
        st.metric(label=card["label"], value=card["value"], help=card.get("detail", ""))

st.markdown("---")
st.markdown("""
**Quick Start:**
- **Home & Search** — Search any city, state, disaster type, or funding program
- **State Explorer** — Drill into a state's risk profile and funding options
- **City Targets** — Filter and sort 30 priority metro areas
- **Funding Finder** — "I am a ___ in ___" → see your matching grants
- **Department Playbook** — Sales approach by buyer type
- **Add to HubSpot** — Log promising prospects in the Initial Sales Stage
- **Global Targets** — International high-risk metros
""")
