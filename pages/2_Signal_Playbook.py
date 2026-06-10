"""Signal Playbook — 'If you see X, the money is Y' — browsable plays."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.styles import inject_css, sidebar_brand, page_header, steps_html, pill
from utils.data_loader import load_signals, load_funding

st.set_page_config(page_title="Signal Playbook | Genasys", page_icon="🛡️", layout="wide")
inject_css()
sidebar_brand()

page_header(
    "If you see it, fund it",
    "Signal Playbook",
    "Every signal below means an agency can buy — usually before anything shows up in GovSpend. "
    "Each play tells you how to spot it, what the money is, what to say, and the email to send.",
)

signals = load_signals()
funding = load_funding()
prog_names = dict(zip(funding["program_key"], funding["program_name"]))

URGENCY = {
    "high": ("Act now", "#B91C1C", "#FEE2E2"),
    "medium": ("This quarter", "#B45309", "#FEF3C7"),
    "low": ("Opportunistic", "#15803D", "#DCFCE7"),
}

categories = []
for s in signals:
    if s["category"] not in categories:
        categories.append(s["category"])

cat_filter = st.multiselect("Filter by category", categories, default=[])
urg_filter = st.multiselect("Filter by urgency", ["high", "medium", "low"], default=[],
                            format_func=lambda u: URGENCY[u][0])

shown = [s for s in signals
         if (not cat_filter or s["category"] in cat_filter)
         and (not urg_filter or s["urgency"] in urg_filter)]

# Sort: high urgency first
shown.sort(key=lambda s: {"high": 0, "medium": 1, "low": 2}.get(s["urgency"], 3))

for s in shown:
    label, fg, bg = URGENCY.get(s["urgency"], URGENCY["low"])
    prog_pills = " ".join(
        pill(prog_names.get(pk, pk).split(" (")[0], "#163443", "#E8F4E0") for pk in s["programs"][:4]
    )
    st.markdown(f"""
    <div class="gn-card green">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px;">
            <h4 style="margin:0;">IF: {s['label']}</h4>
            {pill(label, fg, bg)}
        </div>
        <div class="gn-label" style="margin-top:0.4rem;">{s['category']} · Consider: </div>
        <div style="margin:0.25rem 0 0.5rem;">{prog_pills}</div>
        <div class="gn-value"><strong>Why this is money:</strong> {s['what_it_means']}</div>
        <div class="gn-value" style="margin-top:0.4rem;"><strong>How to spot it (before GovSpend can):</strong> {s['how_to_spot']}</div>
        <div class="gn-value" style="margin-top:0.4rem;"><strong>Product angle:</strong> {s['products']}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Open the full play — talk track, questions, next steps"):
        st.markdown(f"**Talk track:** {s['talk_track']}")
        st.markdown("**Discovery questions:**")
        for q in s["discovery_questions"]:
            st.markdown(f"- {q}")
        st.markdown("**Next steps:**")
        st.markdown(steps_html(s["next_steps"]), unsafe_allow_html=True)
        st.markdown(f"**Matched email template:** `{s['email_template']}` — open it in the Email Library "
                    "or run this signal through the Funding Pathfinder to auto-draft it.")
