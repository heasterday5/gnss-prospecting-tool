"""Page 1: Home / Search — search bar + metrics + top targets."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.data_loader import load_states, load_cities, load_funding, load_metrics
from utils.styles import inject_css, tier_badge, score_pill, metric_card
from utils.search import search_all

st.set_page_config(page_title="Search | GNSS", page_icon="🔍", layout="wide")
inject_css()

st.title("🔍 Search & Discover")

# Metric cards
metrics = load_metrics()
cols = st.columns(4)
for i, card in enumerate(metrics.get("cards", [])):
    with cols[i]:
        st.markdown(metric_card(card["label"], card["value"], card.get("detail", "")),
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Search bar
query = st.text_input("Search cities, states, disaster types, funding programs...",
                       placeholder="e.g. Houston, wildfire, NGWSGP, earthquake, Texas")

states = load_states()
cities = load_cities()
funding = load_funding()

if query:
    results = search_all(query, states, cities, funding)

    total = len(results["states"]) + len(results["cities"]) + len(results["funding"])
    st.markdown(f"**{total} results** for *{query}*")

    # State results
    if not results["states"].empty:
        st.subheader(f"States ({len(results['states'])})")
        for _, row in results["states"].iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"**{row['state']}** — {row.get('key_hazards', '')[:80]}...")
            with c2:
                st.markdown(tier_badge(row["priority_tier"]), unsafe_allow_html=True)
            with c3:
                st.markdown(score_pill(row["composite_score"]), unsafe_allow_html=True)

    # City results
    if not results["cities"].empty:
        st.subheader(f"Cities ({len(results['cities'])})")
        for _, row in results["cities"].iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"**{row['city_metro']}**, {row['state']} — {row.get('primary_disaster_risk', '')}")
            with c2:
                st.markdown(tier_badge(row["priority_tier"]), unsafe_allow_html=True)
            with c3:
                st.markdown(score_pill(row["composite_priority_score"]), unsafe_allow_html=True)

    # Funding results
    if not results["funding"].empty:
        st.subheader(f"Funding Programs ({len(results['funding'])})")
        for _, row in results["funding"].iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"**{row['program_name']}** — {row.get('fy2025_funding', '')}")
            with c2:
                from utils.styles import status_badge
                st.markdown(status_badge(row["status"]), unsafe_allow_html=True)
            with c3:
                st.markdown(f"*{row.get('eligible_applicants', '')[:40]}...*")

    if total == 0:
        st.info("No results found. Try broader terms like a state name, disaster type, or 'fire'.")

else:
    # Default view: Top Tier 1 targets
    st.subheader("Top Priority Targets")
    tier1_cities = cities[cities["priority_tier"].str.contains("Tier 1", na=False)].head(15)

    header_cols = st.columns([1, 3, 1, 2, 1, 1])
    headers = ["Rank", "City / Metro", "State", "Primary Risk", "Score", "Tier"]
    for col, h in zip(header_cols, headers):
        col.markdown(f"**{h}**")

    for _, row in tier1_cities.iterrows():
        c = st.columns([1, 3, 1, 2, 1, 1])
        c[0].write(row["priority_rank"])
        c[1].write(row["city_metro"])
        c[2].write(row["state"])
        c[3].write(row["primary_disaster_risk"])
        c[4].markdown(score_pill(row["composite_priority_score"]), unsafe_allow_html=True)
        c[5].markdown(tier_badge(row["priority_tier"]), unsafe_allow_html=True)
