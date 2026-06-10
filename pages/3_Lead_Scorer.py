"""Lead Scorer — rank target accounts by four public funding-readiness indicators."""

import streamlit as st
from utils.auth import check_password
check_password()

import pandas as pd
from utils.styles import inject_css, sidebar_brand, page_header, pill

st.set_page_config(page_title="Lead Scorer | Genasys", page_icon="🛡️", layout="wide")
inject_css()
sidebar_brand()

page_header(
    "Prioritize the list",
    "Lead Scorer",
    "Four public indicators predict which accounts are mathematically primed to win funding. "
    "Score each target 0–4, work the 4s first. All four lookups are free and take under a minute each.",
)

# ---- Indicator reference ----
c1, c2, c3, c4 = st.columns(4)
indicator_cards = [
    ("High SVI", "Community is in the top 25% of the CDC Social Vulnerability Index — populations that phone-based alerts miss.",
     "https://www.atsdr.cdc.gov/place-health/php/svi/svi-interactive-map.html", "CDC SVI interactive map"),
    ("High-Hazard Dam", "National Inventory of Dams lists a non-federal high-hazard dam upriver of the community.",
     "https://nid.usace.army.mil", "National Inventory of Dams"),
    ("CRS Participant", "Community participates in FEMA's Community Rating System — proven proactive flood-program spender; warning systems earn Activity 610 credit.",
     "https://www.fema.gov/floodplain-management/community-rating-system", "FEMA CRS program"),
    ("Recent Declaration", "Federal Major Disaster Declaration in the county within the last 24 months — HMGP money is flowing.",
     "https://www.fema.gov/disaster/declarations", "FEMA declarations"),
]
for col, (name, desc, url, link_label) in zip((c1, c2, c3, c4), indicator_cards):
    with col:
        st.markdown(f"""
        <div class="gn-card teal" style="height:100%;">
            <h4 style="font-size:0.95rem;">{name}</h4>
            <div class="gn-value" style="font-size:0.85rem;">{desc}</div>
            <div style="margin-top:0.4rem;"><a href="{url}">{link_label} →</a></div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("#### Score your accounts")
st.caption("Check each indicator you've verified. The score and tier update automatically. "
           "Add rows for each account on your list; download as CSV when done.")

DEFAULT = pd.DataFrame([
    {"Account": "", "State": "", "High SVI": False, "High-Hazard Dam": False,
     "CRS Participant": False, "Recent Declaration": False},
])

edited = st.data_editor(
    st.session_state.get("scorer_df", DEFAULT),
    num_rows="dynamic", use_container_width=True, key="scorer_editor",
    column_config={
        "Account": st.column_config.TextColumn(width="medium"),
        "State": st.column_config.TextColumn(width="small"),
        "High SVI": st.column_config.CheckboxColumn(help="Top 25% of CDC SVI"),
        "High-Hazard Dam": st.column_config.CheckboxColumn(help="Non-federal high-hazard dam upriver (NID)"),
        "CRS Participant": st.column_config.CheckboxColumn(help="Listed in FEMA Community Rating System"),
        "Recent Declaration": st.column_config.CheckboxColumn(help="Major Disaster Declaration in last 24 months"),
    },
)

IND_COLS = ["High SVI", "High-Hazard Dam", "CRS Participant", "Recent Declaration"]
scored = edited.copy()
scored["Score"] = scored[IND_COLS].fillna(False).astype(bool).sum(axis=1)


def tier_of(score):
    if score >= 4:
        return "Tier 1 — Critical target"
    if score >= 2:
        return "Tier 2 — Strong prospect"
    return "Tier 3 — Opportunistic"


scored["Tier"] = scored["Score"].apply(tier_of)
ranked = scored[scored["Account"].astype(str).str.strip() != ""].sort_values("Score", ascending=False)

if not ranked.empty:
    st.markdown("#### Ranked list")
    for _, r in ranked.iterrows():
        score = int(r["Score"])
        fg, bg = ("#B91C1C", "#FEE2E2") if score >= 4 else ("#C2410C", "#FFEDD5") if score >= 2 else ("#15803D", "#DCFCE7")
        hits = [c for c in IND_COLS if bool(r[c])]
        st.markdown(f"""
        <div class="gn-card green">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
                <strong>{r['Account']}{(' — ' + str(r['State'])) if str(r['State']).strip() else ''}</strong>
                {pill(f"{score}/4 · {r['Tier'].split(' — ')[0]}", fg, bg)}
            </div>
            <div class="gn-value" style="margin-top:0.3rem;"><strong>Indicators:</strong> {', '.join(hits) if hits else 'none yet — keep researching'}</div>
        </div>
        """, unsafe_allow_html=True)

    st.download_button("Download scored list (.csv)",
                       ranked[["Account", "State"] + IND_COLS + ["Score", "Tier"]].to_csv(index=False),
                       file_name="genasys_lead_scores.csv")

st.markdown("---")
st.markdown("#### What each tier means")
st.markdown("""
<div class="gn-card green">
    <h4>Score 4 — Tier 1: Critical target</h4>
    <div class="gn-value">Mathematically primed for mitigation funding. Lead with a <strong>combined
    Genasys Protect + Acoustics proposal</strong>. Run the account through the Funding Pathfinder with
    all four signals checked, build the Meeting Prep battlecard, and start outreach this week.</div>
</div>
<div class="gn-card teal">
    <h4>Score 2–3 — Tier 2: Strong prospect</h4>
    <div class="gn-value">Tailor the pitch to the <strong>specific active indicators</strong> — if the dam
    box is checked, lead with downstream voice sirens (HHPD play); if the declaration box is checked,
    lead with HMGP. The Signal Playbook has the play for each indicator.</div>
</div>
<div class="gn-card navy">
    <h4>Score 0–1 — Tier 3: Opportunistic</h4>
    <div class="gn-value">Don't prioritize cold grant-led outreach. Monitor for budget changes,
    contract expirations, and new disaster declarations — any of which moves them up a tier.</div>
</div>
""", unsafe_allow_html=True)
