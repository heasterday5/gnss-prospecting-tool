"""Start Here — type an account, get the research done.

One box in, full research dossier out: the account's plans and budgets, its
documented risk profile, the three funding layers that could pay, live
procurement checks, and the next actions — with every link either a verified
deep link or a surgical pre-built search.
"""

import urllib.parse

import streamlit as st
from utils.auth import check_password
check_password()

from utils.styles import (inject_css, sidebar_brand, page_header, status_badge,
                          GREEN, NAVY, TEAL, SLATE)
from utils.data_loader import (load_department_types, load_states, load_counties,
                               get_state_row)
from utils.recommend import recommend

st.set_page_config(page_title="Start Here | Genasys", page_icon="🛡️", layout="wide")
inject_css()
sidebar_brand()

page_header(
    "Start here · 2 minutes",
    "Account Research, Done For You",
    "Type the account you're targeting. Get their plans, their documented risks, "
    "the money that fits, and your next action — without opening twelve tabs.",
)

# ---------------------------------------------------------------- helpers

STATE_ABBRS = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
    "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota",
    "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}
NAME_TO_ABBR = {v: k for k, v in STATE_ABBRS.items()}

SEGMENT_KEYWORDS = [
    (("fire", "ems", "rescue", "esd"), "Fire / EMS Departments"),
    (("police", "sheriff", "pd ", " pd", "law enforcement", "public safety dept"), "Police / Law Enforcement"),
    (("911", "dispatch", "psap", "communications center", "comm center"), "Emergency Management Agencies"),
    (("oes", "emergency management", "emergency services", "ema", "dem ", "homeland"), "Emergency Management Agencies"),
    (("water", "electric", "power", "gas", "utility", "utilities", "public works", "flood control", "dam"), "Utilities (Power, Water, Gas)"),
    (("port ", "airport", "transit", "rail", "refinery", "plant"), "Critical Infrastructure Operators"),
    (("tribe", "tribal", "nation", "band of", "pueblo", "rancheria"), "Tribal Nations"),
    (("stadium", "arena", "speedway", "fairground", "venue", "university", "college", "school"), "Events / Venues / Mass Gatherings"),
    (("base", "fort ", "camp ", "naval", "air force", "army", "guard"), "Armed Forces / Military"),
]


def guess_state(text: str):
    for name in STATE_ABBRS.values():
        if name.lower() in text.lower():
            return name
    for abbr in STATE_ABBRS:
        if f", {abbr}" in text.upper() or text.upper().endswith(f" {abbr}"):
            return STATE_ABBRS[abbr]
    return None


def guess_segment(text: str):
    t = " " + text.lower() + " "
    for keywords, seg in SEGMENT_KEYWORDS:
        if any(k in t for k in keywords):
            return seg
    return None


def guess_county(text: str, counties_in_state):
    t = text.lower()
    for c in counties_in_state:
        stem = c.lower().replace(" county", "").replace(" parish", "").replace(" borough", "")
        if stem and stem in t:
            return c
    return None


def g(query: str) -> str:
    """Pre-built Google search link."""
    return "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)


def link_row(icon, title, url, why, find=""):
    find_html = (f'<div style="font-size:0.82rem;color:{SLATE};margin-top:2px;">'
                 f'<b>Look for:</b> {find}</div>') if find else ""
    st.markdown(f"""
    <div class="gn-card teal" style="padding:0.85rem 1.1rem;margin-bottom:0.55rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
        <div style="min-width:260px;flex:1;">
          <div style="font-weight:800;color:{NAVY};">{icon} {title}</div>
          <div style="font-size:0.88rem;color:#262A2D;">{why}</div>
          {find_html}
        </div>
        <a href="{url}" target="_blank" style="background:{GREEN};color:{NAVY};font-weight:700;
           padding:6px 16px;border-radius:8px;white-space:nowrap;">Open ↗</a>
      </div>
    </div>""", unsafe_allow_html=True)


# ---------------------------------------------------------------- inputs

dept_types = load_department_types()
states_df = load_states()
counties_df = load_counties()
state_list = sorted(states_df["state"].tolist())

account = st.text_input(
    "Who's the account?",
    placeholder="e.g., Sacramento County OES · City of Boulder Fire · Cherokee Nation Emergency Management",
    help="Agency, department, city, county, tribe, utility, campus — anything you'd put in HubSpot.",
)

guessed_state = guess_state(account) if account else None
guessed_seg = guess_segment(account) if account else None

c1, c2, c3 = st.columns(3)
with c1:
    selected_state = st.selectbox(
        "State", state_list,
        index=state_list.index(guessed_state) if guessed_state in state_list else
              (state_list.index("Texas") if "Texas" in state_list else 0),
    )
with c2:
    counties_in_state = counties_df[counties_df["state"] == selected_state]["county"].tolist()
    guessed_cty = guess_county(account, counties_in_state) if account else None
    county_options = ["(pick the county — it drives the risk data)"] + counties_in_state
    selected_county = st.selectbox(
        "County", county_options,
        index=county_options.index(guessed_cty) if guessed_cty else 0,
        help="If your target is a city, district, or campus, pick the county it sits in — "
             "hazard plans and risk data are county-level.",
    )
with c3:
    seg_names = [d["department_type"] for d in dept_types]
    selected_seg = st.selectbox(
        "Segment", seg_names,
        index=seg_names.index(guessed_seg) if guessed_seg in seg_names else
              seg_names.index("Emergency Management Agencies"),
    )

has_county = not selected_county.startswith("(")
jurisdiction = account.strip() if account.strip() else (selected_county if has_county else selected_state)
county_label = selected_county if has_county else None
state_abbr = NAME_TO_ABBR.get(selected_state, "")
fips = None
if has_county:
    m = counties_df[(counties_df["state"] == selected_state) & (counties_df["county"] == selected_county)]
    if not m.empty:
        fips = m.iloc[0]["fips"]

if not account.strip():
    st.info("👆 Type the account name — the dossier builds itself from there. State, county, and "
            "segment auto-fill when they're in the name (e.g., *“Boulder County OEM, Colorado”*).")
    st.stop()

st.markdown("---")

# ---------------------------------------------------------------- dossier

dossier_md = [f"# Research Dossier — {jurisdiction}",
              f"_{selected_seg} · {selected_county if has_county else '—'} · {selected_state} · built with the Genasys Funding Intelligence tool_\n"]

# ---- A. Plans & budgets
st.markdown(f"### 📄 Their plans & budgets <span style='font-size:0.85rem;color:{SLATE};font-weight:400;'>— the documents that authorize the spend</span>", unsafe_allow_html=True)
st.caption("These are pre-built searches — the plan is almost always the first result. One click each.")

hmp_target = county_label or jurisdiction
plan_links = [
    ("🗺️", "Hazard Mitigation Plan",
     g(f'"{hmp_target}" "{selected_state}" "hazard mitigation plan" filetype:pdf'),
     "Required every 5 years for FEMA mitigation money. Their own risk assessment, in their own words.",
     "\"siren\", \"evacuation\", \"notification\", \"warning\", \"communication gap\" — a named gap is a pre-justified project"),
    ("🚨", "Emergency Operations Plan",
     g(f'"{jurisdiction}" "emergency operations plan" filetype:pdf'),
     "How they say they'll warn and evacuate today. Gaps between the EOP and reality are your opening.",
     "the alert & warning annex and evacuation annex"),
    ("🏗️", "Capital Improvement Plan (CIP)",
     g(f'"{county_label or jurisdiction}" "capital improvement" plan public safety'),
     "Multi-year capital projects with named funding sources. Money that is already appropriated.",
     "the Public Safety section and \"projects by funding source\" table — comms/warning line items"),
    ("💵", "Adopted budget (FY2026–27)",
     g(f'"{county_label or jurisdiction}" adopted budget "fiscal year" 2027 public safety'),
     "Operating money. Smaller buys (a vehicle-mounted LRAD) often come straight from here — no grant needed.",
     "public-safety department budgets, equipment/communications lines, unspent contingency"),
    ("🏛️", "Council / board agendas",
     g(f'"{county_label or jurisdiction}" (council OR commissioners OR supervisors) agenda ("mass notification" OR siren OR evacuation OR alerting)'),
     "Approvals in flight, stalled purchases you can revive, and the exact language leadership uses.",
     "consent-calendar equipment approvals and any tabled/postponed alerting item"),
    ("📊", "ClearGov / transparency portal",
     f"https://cleargov.com/{selected_state.lower().replace(' ', '-')}",
     "Benchmark their public-safety spend per capita against neighbors — instant credibility stat for your call.",
     f"search for {county_label or 'the jurisdiction'} once the state page loads"),
]
for row in plan_links:
    link_row(*row)
    dossier_md.append(f"- **{row[1]}**: {row[2]}\n  - {row[3]}")

# ---- B. Risk profile
st.markdown(f"### ⚠️ Their documented risk profile", unsafe_allow_html=True)
if has_county:
    st.caption(f"County-level deep links for {selected_county} (FIPS {fips}) — the same data their grant reviewers see.")
else:
    st.warning("Pick the county above to sharpen these links — risk data is county-keyed.")

risk_links = [
    ("📈", "FEMA risk data — RAPT (search your county)",
     "https://experience.arcgis.com/experience/0a317e8998534c30a9b2d3861c814d42",
     f"FEMA retired the standalone National Risk Index in Dec 2025 — the 18-hazard county ratings now live "
     f"inside the Resilience Analysis & Planning Tool. Search “{selected_county if has_county else 'your county'}” "
     f"and open the pop-up.",
     "the top-3 resilience challenges and hazard ratings — quote them back to the buyer"),
    ("🌪️", f"Federal disaster declarations — {selected_state}",
     f"https://www.fema.gov/disaster/declarations?field_dv2_state_territory_tribal_value={state_abbr}",
     "A declaration in the last 24 months = HMGP post-disaster money is open statewide right now.",
     f"any declaration touching {selected_county if has_county else 'your county'} since mid-2024"),
    ("🧭", "CDC Social Vulnerability Index map",
     "https://www.atsdr.cdc.gov/place-health/php/svi/svi-interactive-map.html",
     "Top-quartile SVI = the populations phone alerts miss (dead zones, language, smartphone access). "
     "That's the equity-gap play.",
     "the county percentile — 0.75+ unlocks the High-SVI signal play"),
    ("🌊", "National Inventory of Dams",
     "https://nid.usace.army.mil/#/",
     "A high-hazard dam upstream = downstream warning obligation = the dam-safety play (HHPD/HMGP).",
     f"high-hazard-potential dams in {selected_county if has_county else 'the county'} with EAPs"),
    ("🔥", "Wildfire Risk to Communities (USDA)",
     "https://apps.wildfirerisk.org/explore/",
     "Forest Service wildfire risk percentile — the WUI/evacuation-zone conversation starter.",
     "risk to homes percentile vs. the rest of the state"),
]
for row in risk_links:
    link_row(*row)
    dossier_md.append(f"- **{row[1]}**: {row[2]}\n  - {row[3]}")

# ---- C. The money
st.markdown("### 💰 The money — three layers, ranked for this account", unsafe_allow_html=True)

state_row = get_state_row(selected_state)
result = recommend(selected_seg, selected_state, [])
recs = result["recommendations"][:5]

lc, rc = st.columns([3, 2], gap="large")
with lc:
    st.markdown(f"**Layer 1 · Federal pass-through** — flows FEMA/DHS → state → {selected_seg.lower().rstrip('s')}. The biggest lever.")
    for r in recs:
        fp = r["program"]
        st.markdown(f"""
        <div class="gn-card navy" style="padding:0.8rem 1.1rem;margin-bottom:0.5rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <div style="font-weight:800;color:{NAVY};">{fp['program_name']}</div>
            <div>{status_badge(fp['status'])}</div>
          </div>
          <div style="font-size:0.85rem;color:#262A2D;">{fp['funding_level']} · {fp['window_note']}</div>
        </div>""", unsafe_allow_html=True)
        dossier_md.append(f"- **{fp['program_name']}** ({fp['status']}): {fp['funding_level']} — {fp['window_note']}")
    st.caption("Full ranking, plays, and draft emails → Funding Pathfinder (button below).")

with rc:
    st.markdown(f"**Your state gatekeeper** — locals can't apply to FEMA directly; the state administers it.")
    if state_row is not None:
        st.markdown(f"""
        <div class="gn-card green" style="padding:0.9rem 1.1rem;">
          <div style="font-weight:800;color:{NAVY};">{state_row['Agency Name']}</div>
          <div style="font-size:0.88rem;margin-top:4px;">
            <a href="{state_row['Emergency Management Agency URL']}" target="_blank">Agency site ↗</a> ·
            <a href="{state_row['EM/Homeland Security Grants Page']}" target="_blank">Grants page ↗</a>
          </div>
          <div style="font-size:0.8rem;color:{SLATE};margin-top:4px;">Links verified Jun 2026</div>
        </div>""", unsafe_allow_html=True)
        dossier_md.append(f"- **State gatekeeper:** {state_row['Agency Name']} — {state_row['EM/Homeland Security Grants Page']}")

    st.markdown("**Layer 2 · Their own budget** — already-appropriated CIP/operating money (see the CIP and budget links above). No grant cycle, no wait.")
    st.markdown("**Layer 3 · Sector-specific:**")
    LAYER3 = {
        "Fire / EMS Departments": "AFG direct-to-department money (no state pass-through) + state fire-safety grants.",
        "Police / Law Enforcement": "LETPA set-aside (35% of state HSGP **must** fund law-enforcement terrorism prevention) + asset forfeiture funds.",
        "Emergency Management Agencies": "EMPG annual allocation (they always have it) + 911/NG911 surcharge funds if they run dispatch.",
        "Utilities (Power, Water, Gas)": "Wildfire Mitigation Plans filed with the state PUC — rate-recovered capital for PSPS and community notification. Search the PUC docket.",
        "Critical Infrastructure Operators": "Port/Transit Security Grant Programs + owner capital budgets driven by insurer and regulator pressure.",
        "Cities / Counties / Municipalities": "General fund + CIP + municipal bonds; ARPA-era interest earnings still being obligated in many councils.",
        "Events / Venues / Mass Gatherings": "World Cup 2026 security supplemental ($625M) for host metros + venue operating budgets + NCS4 safety standards pressure.",
        "Tribal Nations": "THSGP direct federal allocation + BIA emergency funds — no state pass-through needed.",
        "Armed Forces / Military": "Force-protection O&M and procurement lines — track DoD OSBP acquisition forecasts and SAM.gov, not FEMA grants.",
    }
    st.markdown(f'<div class="gn-card teal" style="padding:0.8rem 1.1rem;font-size:0.9rem;">{LAYER3.get(selected_seg, "")}</div>', unsafe_allow_html=True)
    dossier_md.append(f"- **Sector-specific layer:** {LAYER3.get(selected_seg, '')}")

# ---- D. Live procurement
st.markdown("### 🛒 Deal mechanics — live bids & the buying vehicle", unsafe_allow_html=True)
proc_links = [
    ("📡", "SAM.gov — live federal solicitations",
     "https://sam.gov/search/?keywords=%22mass%20notification%22%20OR%20%22long%20range%20acoustic%22",
     "Live RFPs/RFQs for mass notification and acoustic systems. Also shows who bought what (award history).",
     f"opportunities with place of performance in {selected_state}"),
    ("📃", "Grants.gov — open federal notices",
     "https://grants.gov/search-grants?query=%22emergency%20communications%22",
     "Where NOFOs post first. Check before promising a window is open.",
     "FEMA/DHS notices matching the programs above"),
    ("🤝", "Sourcewell contract #030425-GYS (Genasys)",
     "https://www.sourcewell-mn.gov/cooperative-purchasing/030425-gys",
     "The RFP bypass. If the entity is a Sourcewell member (most are), they can PO directly off this contract — valid through July 2029.",
     "confirm the entity's membership on the same site (free, instant)"),
    ("🏷️", "Council agenda award search",
     g(f'site:legistar.com OR site:granicus.com "{county_label or jurisdiction}" (notification OR siren OR alerting)'),
     "Past purchases and stalled items in the official record — a postponed buy is a warm lead.",
     "items marked 'tabled', 'postponed', or 'referred to committee'"),
]
for row in proc_links:
    link_row(*row)
    dossier_md.append(f"- **{row[1]}**: {row[2]}\n  - {row[3]}")

# ---- E. Next actions
st.markdown("### ✅ Turn it into pipeline", unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)
with b1:
    if st.button("🧭 Funding Pathfinder →", type="primary", use_container_width=True,
                 help="Pre-filled with this state and segment — add the signals you spotted, get the email."):
        st.session_state["pf_dept"] = selected_seg
        st.session_state["pf_state"] = selected_state
        st.switch_page("pages/1_Funding_Pathfinder.py")
with b2:
    if st.button("📇 Meeting Prep battlecard →", use_container_width=True):
        st.session_state["mp_agency"] = jurisdiction
        st.session_state["mp_state"] = selected_state
        st.switch_page("pages/4_Meeting_Prep.py")
with b3:
    if st.button("🎯 Score it in the Lead Scorer →", use_container_width=True):
        st.switch_page("pages/3_Lead_Scorer.py")

dossier_md.append("\n## 15-minute research routine\n"
                  "1. CIP + adopted budget → public-safety comms line + funding source\n"
                  "2. State grants page → current HSGP/EMPG status + open windows\n"
                  "3. Hazard mitigation plan → named warning/evacuation gaps\n"
                  "4. RAPT → county hazard ratings; declarations page → HMGP trigger\n"
                  "5. SAM.gov + agenda search → live bids or a stalled buy to revive\n"
                  "6. Sourcewell membership check → confirm the fast vehicle (#030425-GYS)\n")

st.download_button(
    "⬇️ Download this dossier (Markdown)",
    "\n".join(dossier_md),
    file_name=f"dossier_{jurisdiction.lower().replace(' ', '_').replace(',', '')}.md",
    mime="text/markdown",
)
