"""Funding Pathfinder — who + where + what you see → the money, the talk track, the email."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.styles import (md_html, inject_css, sidebar_brand, page_header, status_badge,
                          pill, steps_html, GREEN, NAVY, TEAL)
from utils.data_loader import (load_department_types, load_states, load_signals,
                               get_template, get_state_row)
from utils.recommend import recommend
from utils.emails import render, tokens_in
from utils.identity import rep_identity_sidebar

inject_css()
sidebar_brand()
sender = rep_identity_sidebar()

page_header(
    "Step 1 · Before outreach",
    "Funding Pathfinder",
    "Tell it who you're talking to, where, and what you've observed. "
    "Get the ranked funding stack, the reasoning, and a ready-to-send email.",
)

# ---------- Inputs ----------
dept_types = load_department_types()
states_df = load_states()
signals = load_signals()

c1, c2 = st.columns(2)
with c1:
    selected_dept = st.selectbox("I'm talking to a…", [d["department_type"] for d in dept_types],
                                 key="pf_dept")
with c2:
    state_list = sorted(states_df["state"].tolist())
    if "pf_state" not in st.session_state and "Texas" in state_list:
        st.session_state["pf_state"] = "Texas"
    selected_state = st.selectbox("in…", state_list, key="pf_state")

st.markdown('<div class="gn-label" style="margin-top:0.8rem;">What have you spotted? (select all that apply)</div>',
            unsafe_allow_html=True)

URGENCY_DOT = {"high": "🔴", "medium": "🟡", "low": "⚪"}
selected_signal_ids = []
sig_cols = st.columns(2)
for i, s in enumerate(signals):
    with sig_cols[i % 2]:
        if st.checkbox(f"{URGENCY_DOT.get(s['urgency'], '⚪')} {s['label']}", key=f"sig_{s['id']}"):
            selected_signal_ids.append(s["id"])

st.markdown("---")

# ---------- Results ----------
result = recommend(selected_dept, selected_state, selected_signal_ids)
recs = result["recommendations"]
fired = result["fired_signals"]

dept_info = next((d for d in dept_types if d["department_type"] == selected_dept), None)
state_row = get_state_row(selected_state)
saa_name = state_row["Agency Name"] if state_row is not None else f"the {selected_state} emergency management agency"

left, right = st.columns([3, 2], gap="large")

with left:
    dept_singular = selected_dept.split(" (")[0].lower().replace("ies", "y") if selected_dept.lower().endswith("ies") \
        else selected_dept.split(" (")[0].lower().removesuffix("s")
    st.markdown(f"### Funding stack for a {dept_singular} in {selected_state}")
    if not selected_signal_ids:
        st.caption("Showing department-eligible programs. Check signals above to sharpen the ranking and unlock the plays.")

    for r in recs[:7]:
        fp = r["program"]
        why_bits = []
        if r["signal_reasons"]:
            why_bits.append("Triggered by: " + "; ".join(r["signal_reasons"][:2]))
        if r["dept_eligible"]:
            why_bits.append(f"{selected_dept} eligible")
        if r["state_priority"]:
            why_bits.append(f"Priority program for {selected_state}")
        why = " · ".join(why_bits)

        md_html(f"""
        <div class="gn-card green">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
                <strong style="font-size:1.05em;">{fp['program_name']}</strong>
                {status_badge(fp['status'])}
            </div>
            <div class="gn-value" style="margin:0.35rem 0;"><strong>{fp['funding_level']}</strong> — {fp['administering_agency']} · {fp['eligible_applicants']}</div>
            <div class="gn-value" style="margin:0.25rem 0;">{fp['status_detail']}</div>
            <div class="gn-value" style="margin:0.25rem 0;"><strong>Funds:</strong> {fp['key_eligible_uses']}</div>
            <div class="gn-value" style="margin:0.35rem 0;color:#1D7A8C;"><strong>The play:</strong> {fp['sales_note']}</div>
            <div class="gn-label" style="margin-top:0.4rem;">{why}</div>
        </div>
        """)

    # State resources
    if state_row is not None:
        st.markdown(f"#### {selected_state} resources <span style='font-size:0.75rem;color:#5A6B75;'>({state_row['Link Status']})</span>", unsafe_allow_html=True)
        lc = st.columns(3)
        em_url = str(state_row.get("Emergency Management Agency URL", "")).strip()
        grants_url = str(state_row.get("EM/Homeland Security Grants Page", "")).strip()
        portal_url = str(state_row.get("Statewide Grant/Funding Portal", "")).strip()
        if em_url and em_url != "nan":
            lc[0].markdown(f"[{state_row['Agency Name'].split('(')[0].strip()}]({em_url})")
        if grants_url and grants_url != "nan":
            lc[1].markdown(f"[State grants page]({grants_url})")
        if portal_url and portal_url != "nan":
            lc[2].markdown(f"[Statewide funding portal]({portal_url})")

with right:
    if fired:
        st.markdown("### Your plays")
        for s in fired:
            with st.expander(f"{URGENCY_DOT.get(s['urgency'])} {s['label']}", expanded=len(fired) == 1):
                st.markdown(f"**What it means:** {s['what_it_means']}")
                st.markdown(f"**Talk track:** {s['talk_track']}")
                st.markdown("**Discovery questions:**")
                for q in s["discovery_questions"]:
                    st.markdown(f"- {q}")
                st.markdown("**Next steps:**")
                st.markdown(steps_html(s["next_steps"]), unsafe_allow_html=True)
    elif dept_info:
        st.markdown("### Buyer snapshot")
        md_html(f"""
        <div class="gn-card teal">
            <div class="gn-label">Typical buyer</div>
            <div class="gn-value">{dept_info['typical_buyer_title']}</div>
            <div class="gn-label" style="margin-top:0.6rem;">Product fit</div>
            <div class="gn-value">{dept_info['product_fit']}</div>
            <div class="gn-label" style="margin-top:0.6rem;">Pain points</div>
            <div class="gn-value">{dept_info['pain_points']}</div>
            <div class="gn-label" style="margin-top:0.6rem;">Decision process</div>
            <div class="gn-value">{dept_info['decision_process']}</div>
        </div>
        """)

# ---------- Email draft ----------
st.markdown("---")
st.markdown("### Draft the outreach email")

template_ids = []
for s in fired:
    if s.get("email_template") and s["email_template"] not in template_ids:
        template_ids.append(s["email_template"])
if not template_ids:
    template_ids = ["empg_em_director", "post_discovery"]

templates = [get_template(tid) for tid in template_ids if get_template(tid)]
tmpl_names = [t["name"] for t in templates]
chosen_name = st.selectbox("Template (matched to your signals)", tmpl_names)
tmpl = templates[tmpl_names.index(chosen_name)]
st.caption(f"**When to use:** {tmpl['when_to_use']}")

# Token inputs (auto-fill what we know)
auto = {
    "state": selected_state,
    "saa_name": saa_name,
    **sender,
}
needed = [t for t in tokens_in(tmpl) if t not in auto or not auto.get(t)]
vals = dict(auto)
if needed:
    tcols = st.columns(min(3, max(1, len(needed))))
    for i, tok in enumerate(needed):
        with tcols[i % len(tcols)]:
            vals[tok] = st.text_input(tok.replace("_", " ").title(), key=f"tok_{tmpl['id']}_{tok}")

rendered = render(tmpl, vals)
st.text_input("Subject", value=rendered["subject"], key=f"subj_{tmpl['id']}", disabled=True)
st.code(rendered["body"], language=None)
st.caption("Use the copy icon in the corner of the box above, then paste into your email client. "
           f"**Follow-up guidance:** {tmpl.get('follow_up', '')}")

# ---------- Lexipol handoff ----------
st.markdown("---")
md_html(f"""
<div class="gn-card navy">
    <div class="gn-label">When they say yes</div>
    <h4>Hand off to Lexipol for the grant draft</h4>
    <div class="gn-value">Once the agency agrees to pursue funding, do not let the application
    sit with their staff. Use the <strong>Lexipol grant-support introduction</strong> email in the
    Email Library (it includes the SAM.gov registration checklist that stalls most applications),
    and log the opportunity in HubSpot at the Initial Sales Stage.</div>
</div>
""")
