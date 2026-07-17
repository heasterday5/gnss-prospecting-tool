"""Meeting Prep — generate a one-page battlecard for a specific agency conversation."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.styles import md_html, inject_css, sidebar_brand, page_header, status_badge
from utils.data_loader import (load_department_types, load_states, load_signals,
                               load_personas, load_trends, get_state_row)
from utils.recommend import recommend
from utils.identity import rep_identity_sidebar

inject_css()
sidebar_brand()
rep_identity_sidebar()

page_header(
    "Step 2 · Before the meeting",
    "Meeting Prep",
    "Build a one-page battlecard: live funding status, the Growth Playbook discovery questions "
    "for both buyers in the room, conversation-starter trends, and your next steps.",
)

dept_types = load_department_types()
states_df = load_states()
signals = load_signals()
personas = load_personas()
trends = load_trends()

MARKET_MAP = {
    "Fire / EMS Departments": "Fire & Emergency Management",
    "Emergency Management Agencies": "Fire & Emergency Management",
    "Cities / Counties / Municipalities": "Fire & Emergency Management",
    "Tribal Nations": "Fire & Emergency Management",
    "Police / Law Enforcement": "Law Enforcement",
    "Events / Venues / Mass Gatherings": "Law Enforcement",
    "Utilities (Power, Water, Gas)": "Enterprise (Utilities, Oil & Gas, Critical Infrastructure)",
    "Critical Infrastructure Operators": "Enterprise (Utilities, Oil & Gas, Critical Infrastructure)",
    "Armed Forces / Military": "Military & Defense",
}

c1, c2, c3 = st.columns([2, 2, 2])
with c1:
    agency = st.text_input("Agency / organization", placeholder="e.g. Travis County OEM",
                           key="mp_agency")
with c2:
    selected_dept = st.selectbox("Buyer type", [d["department_type"] for d in dept_types])
with c3:
    state_list = sorted(states_df["state"].tolist())
    if "mp_state" not in st.session_state and "Texas" in state_list:
        st.session_state["mp_state"] = "Texas"
    selected_state = st.selectbox("State", state_list, key="mp_state")

sig_labels = {s["label"]: s["id"] for s in signals}
chosen_sigs = st.multiselect("Signals you've confirmed for this account", list(sig_labels.keys()))
signal_ids = [sig_labels[l] for l in chosen_sigs]

if st.button("Build battlecard", type="primary"):
    st.session_state["mp_built"] = True

if st.session_state.get("mp_built"):
    agency_name = agency or f"{selected_dept} prospect"
    result = recommend(selected_dept, selected_state, signal_ids)
    recs = result["recommendations"][:4]
    fired = result["fired_signals"]
    market = MARKET_MAP.get(selected_dept, "Fire & Emergency Management")
    persona = next((p for p in personas if p["market"] == market), personas[0])
    dept_info = next((d for d in dept_types if d["department_type"] == selected_dept), None)
    state_row = get_state_row(selected_state)
    srow = states_df[states_df["state"] == selected_state]
    hazards = str(srow.iloc[0]["key_hazards"]) if not srow.empty else ""

    st.markdown("---")
    st.markdown(f"## Battlecard — {agency_name} ({selected_state})")
    st.caption(f"Market: {market} · Products: {persona['primary_products']} · Focus: {persona['focus']}")

    bc1, bc2 = st.columns(2, gap="large")
    with bc1:
        st.markdown("#### Funding to lead with")
        for r in recs:
            fp = r["program"]
            md_html(f"""
            <div class="gn-card green">
                <strong>{fp['program_name']}</strong> &nbsp;{status_badge(fp['status'])}
                <div class="gn-value" style="margin-top:0.25rem;">{fp['funding_level']} · {fp['window_note']}</div>
                <div class="gn-value" style="margin-top:0.25rem;color:#1D7A8C;">{fp['sales_note']}</div>
            </div>
            """)

        st.markdown("#### State context")
        st.markdown(f"**Key hazards:** {hazards}")
        if state_row is not None:
            st.markdown(f"**SAA / EM agency:** {state_row['Agency Name']} — "
                        f"[grants page]({state_row['EM/Homeland Security Grants Page']})")

        if fired:
            st.markdown("#### Confirmed signals → talk tracks")
            for s in fired:
                st.markdown(f"- **{s['label']}** — {s['talk_track']}")

    with bc2:
        st.markdown("#### Questions for the room")
        st.markdown(f"**{persona['outcome_owner']['title']}**  \n"
                    f"*({', '.join(persona['outcome_owner']['roles'][:3])})*")
        for q in persona["outcome_owner"]["questions"]:
            st.markdown(f"- {q}")
        st.markdown(f"**{persona['problem_owner']['title']}**  \n"
                    f"*({', '.join(persona['problem_owner']['roles'][:3])})*")
        for q in persona["problem_owner"]["questions"]:
            st.markdown(f"- {q}")
        if fired:
            st.markdown("**Signal-specific:**")
            for s in fired[:2]:
                for q in s["discovery_questions"][:2]:
                    st.markdown(f"- {q}")

        st.markdown("#### What they care about")
        st.markdown("**Strategic buyer:** " + " · ".join(persona["outcome_owner"]["personal_value"]))
        st.markdown("**Operational buyer:** " + " · ".join(persona["problem_owner"]["personal_value"]))

        st.markdown("#### Conversation starters (trends)")
        for t in trends[:3]:
            st.markdown(f"- **{t['title']}** — {t['stat']} ({t['source']}). {t['use_it']}")

    # ---- Downloadable markdown ----
    lines = [
        f"# Battlecard — {agency_name} ({selected_state})",
        f"Market: {market} | Products: {persona['primary_products']} | Focus: {persona['focus']}",
        "",
        "## Funding to lead with",
    ]
    for r in recs:
        fp = r["program"]
        lines += [f"- **{fp['program_name']}** [{fp['status']}] — {fp['funding_level']}. {fp['window_note']}",
                  f"  - Play: {fp['sales_note']}"]
    lines += ["", "## State context", f"- Key hazards: {hazards}"]
    if state_row is not None:
        lines += [f"- SAA / EM agency: {state_row['Agency Name']}",
                  f"- Grants page: {state_row['EM/Homeland Security Grants Page']}"]
    if fired:
        lines += ["", "## Confirmed signals"]
        for s in fired:
            lines += [f"- **{s['label']}** — {s['talk_track']}"]
    lines += ["", f"## Questions — {persona['outcome_owner']['title']}"]
    lines += [f"- {q}" for q in persona["outcome_owner"]["questions"]]
    lines += ["", f"## Questions — {persona['problem_owner']['title']}"]
    lines += [f"- {q}" for q in persona["problem_owner"]["questions"]]
    lines += ["", "## Conversation starters"]
    lines += [f"- {t['title']}: {t['stat']} ({t['source']})" for t in trends[:3]]
    lines += ["", "## After the meeting",
              "1. Send the post-discovery procurement email (Email Library) within 24 hours",
              "2. On verbal yes → Lexipol handoff email + scoping call",
              "3. Log in HubSpot at Initial Sales Stage",
              "4. Procurement fast path: Sourcewell contract 030425-GYS (valid through July 2029)"]

    st.download_button("Download battlecard (.md)", "\n".join(lines),
                       file_name=f"battlecard_{(agency or 'prospect').replace(' ', '_').lower()}.md",
                       use_container_width=True)
