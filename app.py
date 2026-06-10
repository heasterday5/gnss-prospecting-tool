"""Genasys Funding Intelligence — Main Entry Point."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.styles import inject_css, sidebar_brand, hero, metric_card, status_badge
from utils.data_loader import load_metrics, load_funding, load_states, load_cities
from utils.search import search_all

st.set_page_config(
    page_title="Genasys Funding Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
sidebar_brand()

metrics = load_metrics()
with st.sidebar:
    st.caption(f"Data verified: {metrics.get('last_updated', 'N/A')}")

hero(
    "Genasys Funding Intelligence",
    'Walk in with the money <span class="accent">already identified.</span>',
    "Built for the BDR and sales team: identify the funding source before the first conversation, "
    "lead with it in outreach, and hand a ready application path to the agency — then bring in "
    "Lexipol to draft the grant. Stay ahead of what GovSpend can see.",
)

# ---- Urgent now ----
funding = load_funding()
open_now = funding[funding["status"].str.upper() == "OPEN"]
if not open_now.empty:
    for _, fp in open_now.iterrows():
        st.markdown(f"""
        <div class="gn-card warn">
            <div class="gn-label" style="color:#B45309;">⏰ Closing soon — act this week</div>
            <h4>{fp['program_name']} — {fp['funding_level']}</h4>
            <div class="gn-value">{fp['status_detail']}</div>
            <div class="gn-value" style="margin-top:0.4rem;"><strong>The play:</strong> {fp['sales_note']}</div>
        </div>
        """, unsafe_allow_html=True)

# ---- Metrics ----
cols = st.columns(4)
for i, card in enumerate(metrics.get("cards", [])[:4]):
    with cols[i]:
        st.markdown(metric_card(card["label"], card["value"], card.get("detail", "")),
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---- Search ----
query = st.text_input(
    "Search everything",
    placeholder="Search a city, state, disaster type, or funding program — e.g. Houston, wildfire, NGWSGP",
)

if query:
    states = load_states()
    cities = load_cities()
    results = search_all(query, states, cities, funding)
    total = len(results["states"]) + len(results["cities"]) + len(results["funding"])
    st.markdown(f"**{total} results** for *{query}*")

    from utils.styles import tier_badge, score_pill
    if not results["funding"].empty:
        st.subheader(f"Funding Programs ({len(results['funding'])})")
        for _, row in results["funding"].iterrows():
            st.markdown(f"""
            <div class="gn-card green">
                <strong>{row['program_name']}</strong> &nbsp;{status_badge(row['status'])}
                <div class="gn-value" style="margin-top:0.3rem;">{row['funding_level']} — {row['eligible_applicants']}</div>
                <div class="gn-value" style="margin-top:0.3rem;">{row['sales_note']}</div>
            </div>
            """, unsafe_allow_html=True)
    if not results["states"].empty:
        st.subheader(f"States ({len(results['states'])})")
        for _, row in results["states"].iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"**{row['state']}** — {str(row.get('key_hazards', ''))[:90]}")
            c2.markdown(tier_badge(row["priority_tier"]), unsafe_allow_html=True)
            c3.markdown(score_pill(row["composite_score"]), unsafe_allow_html=True)
    if not results["cities"].empty:
        st.subheader(f"Cities ({len(results['cities'])})")
        for _, row in results["cities"].iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"**{row['city_metro']}**, {row['state']} — {row.get('primary_disaster_risk', '')}")
            c2.markdown(tier_badge(row["priority_tier"]), unsafe_allow_html=True)
            c3.markdown(score_pill(row["composite_priority_score"]), unsafe_allow_html=True)
    if total == 0:
        st.info("No results. Try broader terms — a state name, disaster type, or program acronym.")

else:
    # ---- Workflow cards ----
    st.markdown('<div class="gn-kicker">How to use this tool</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="gn-card green">
            <div class="gn-label">Before outreach</div>
            <h4>1 · Funding Pathfinder</h4>
            <div class="gn-value">Tell it who you're calling, where, and what you've spotted.
            Get the ranked funding stack, the talk track, and the email — in 60 seconds.</div>
        </div>
        <div class="gn-card green">
            <div class="gn-label">Know the plays</div>
            <h4>2 · Signal Playbook</h4>
            <div class="gn-value">"If you see X, the money is Y." Fourteen signals that mean an
            agency can buy — and how to spot each one before it hits GovSpend.</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="gn-card teal">
            <div class="gn-label">Before the meeting</div>
            <h4>3 · Meeting Prep</h4>
            <div class="gn-value">One-page battlecard: funding sources with live status, persona
            discovery questions from the Growth Playbook, and the conversation starters.</div>
        </div>
        <div class="gn-card teal">
            <div class="gn-label">After agreement</div>
            <h4>4 · Procurement Toolkit</h4>
            <div class="gn-value">Grant narrative, AEL codes, Sourcewell 030425-GYS, SAFECOM
            alignment, budget table — copy/paste ready for the agency's application.</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="gn-card navy">
            <div class="gn-label">Reference</div>
            <h4>State & City Intelligence</h4>
            <div class="gn-value">Risk profiles, verified grant links for all 50 states
            (re-checked June 2026), priority metros, and the full program database.</div>
        </div>
        <div class="gn-card navy">
            <div class="gn-label">Pipeline</div>
            <h4>Log it in HubSpot</h4>
            <div class="gn-value">Found a funded prospect? Add them to the Initial Sales Stage
            so the team sees the pipeline build.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption(
        "The edge over GovSpend: GovSpend shows you agencies that already published reports and contracts — "
        "everyone sees those. This tool finds the money *before* the agency acts: open grant windows, "
        "post-disaster allocations, documented mitigation-plan gaps, and expiring contracts."
    )
