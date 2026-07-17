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
                          hclean, hurl, GREEN, NAVY, TEAL, SLATE)
from utils.data_loader import (load_department_types, load_states, load_counties,
                               get_state_row, load_contact_ladders, load_deployments,
                               load_incidents, load_em_directories)
from utils.recommend import recommend

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

# ---- resolve the contact ladder (used by live research + the people section)
ladders = load_contact_ladders()
_acct_l = account.lower()
if "sheriff" in _acct_l or (selected_seg == "Police / Law Enforcement" and "county" in _acct_l):
    ladder = next((l for l in ladders if l["segment"] == "Sheriff (county law enforcement)"), None)
else:
    ladder = next((l for l in ladders if l["segment"] == selected_seg), None)
if ladder is None:
    ladder = next(l for l in ladders if l["segment"] == "Emergency Management Agencies")

# ---- Live research: the app researches this account on the web, right now
from utils import live_research

lr_key = f"lr::{jurisdiction}::{selected_state}::{selected_seg}"
lr = st.session_state.get(lr_key)

if live_research.is_configured():
    bc1, bc2 = st.columns([1, 2], gap="medium")
    with bc1:
        run_lr = st.button("🔎 Run live research", type="primary", use_container_width=True,
                           disabled=lr is not None,
                           help="Searches the web right now for this account's real roster, "
                                "incumbent alerting vendor, and recent events. Typically 2–4 min; "
                                "cached 7 days.")
    with bc2:
        st.caption("**Live research** pulls the actual command roster (names → titles → emails), "
                   "the alerting vendor they use today, and recent local incidents — sourced live, "
                   "not from a stored database. First run per account takes **2–4 minutes** "
                   "(you'll see each search as it happens); after that it's cached for a week. "
                   "Stay on this page while it runs.")
    if run_lr:
        hierarchy_text = "\n".join(
            f"  {d['division']}: " + " → ".join(d["titles"]) for d in ladder["divisions"]
        )
        with st.status(f"Researching {jurisdiction} live — this takes 2–4 minutes…",
                       expanded=True) as lr_status:
            try:
                lr = live_research.research_account(
                    jurisdiction, county_label or "", selected_state,
                    selected_seg, hierarchy_text,
                    _progress=lambda msg: lr_status.update(label=msg))
                st.session_state[lr_key] = lr
                lr_status.update(label=f"✅ Research done — results below (cached 7 days)",
                                 state="complete", expanded=False)
            except Exception as e:
                lr_status.update(label="Research hit a snag", state="error")
                st.error(f"Live research failed: {e}. The manual finder below still works — "
                         "try again in a minute.")
else:
    st.markdown(f"""
    <div class="gn-card warn" style="padding:1.2rem 1.4rem;">
      <div style="font-weight:800;color:{NAVY};font-size:1.05rem;">🔎 Live research is built in — one step from being on</div>
      <div style="font-size:0.92rem;color:#262A2D;margin-top:6px;">
        When connected, a <b>“Run live research”</b> button appears right here: the app searches the web
        for this account's <b>real command roster (names → titles → emails), the alerting vendor they
        use today, and recent local incidents</b> — sourced live, nothing stored in the app.
      </div>
      <div style="font-size:0.9rem;color:#262A2D;margin-top:10px;">
        <b>To switch it on (admin, one time):</b><br/>
        1&nbsp;·&nbsp;Create an API key at <b>console.anthropic.com</b> (Settings → API Keys)<br/>
        2&nbsp;·&nbsp;In <b>share.streamlit.io</b> open this app → ⋮ → <b>Settings → Secrets</b><br/>
        3&nbsp;·&nbsp;Add <code>ANTHROPIC_API_KEY = "sk-ant-…"</code> and save — the app restarts itself
      </div>
      <div style="font-size:0.82rem;color:{SLATE};margin-top:8px;">
        Each lookup costs roughly $0.10–0.25 and is cached for 7 days. Until then, the manual finder below works for every account.
      </div>
    </div>""", unsafe_allow_html=True)

if lr:
    ag = lr.get("agency") or {}
    inc = lr.get("incumbent") or {}
    events = lr.get("recent_events") or []
    contacts = lr.get("contacts") or []

    st.markdown(f"### 📞 Live research results <span style='font-size:0.85rem;color:{SLATE};font-weight:400;'>— sourced just now; verify before you dial</span>", unsafe_allow_html=True)

    meta_bits = []
    if ag.get("website"):
        meta_bits.append(f"<a href='{hurl(ag['website'])}' target='_blank'>{hclean(ag.get('official_name'), 'Website')} ↗</a>")
    if ag.get("email_pattern"):
        meta_bits.append(f"Email pattern: <b>{hclean(ag['email_pattern'])}</b>")
    if ag.get("main_phone"):
        meta_bits.append(f"Main line: <b>{hclean(ag['main_phone'])}</b>")
    if meta_bits:
        st.markdown(f'<div class="gn-card green" style="padding:0.8rem 1.1rem;font-size:0.9rem;">'
                    f'{" · ".join(meta_bits)}</div>', unsafe_allow_html=True)

    if contacts:
        rows = ""
        for c in sorted(contacts, key=lambda x: x.get("rank_order", 99)):
            email = (hclean(c.get("email")) or
                     (f"{hclean(c['email_guess'])} <span style='color:{SLATE};'>(pattern guess)</span>"
                      if c.get("email_guess") else "—"))
            phone = hclean(c.get("phone"), "—")
            rows += (f"<tr><td style='padding:6px 10px;font-weight:700;color:{NAVY};'>{hclean(c.get('rank_order'))}</td>"
                     f"<td style='padding:6px 10px;'><b>{hclean(c.get('name'))}</b></td>"
                     f"<td style='padding:6px 10px;'>{hclean(c.get('title'))}<br>"
                     f"<span style='font-size:0.78rem;color:{SLATE};'>{hclean(c.get('division'))}</span></td>"
                     f"<td style='padding:6px 10px;font-size:0.88rem;'>{email}</td>"
                     f"<td style='padding:6px 10px;font-size:0.88rem;'>{phone}</td>"
                     f"<td style='padding:6px 10px;'><a href='{hurl(c.get('source_url'))}' target='_blank'>src ↗</a></td></tr>")
        st.markdown(f"""
        <div class="gn-card navy" style="padding:0.6rem 0.8rem;overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;font-size:0.92rem;">
          <thead><tr style="text-align:left;color:{SLATE};font-size:0.75rem;text-transform:uppercase;">
            <th style="padding:6px 10px;">#</th><th style="padding:6px 10px;">Name</th>
            <th style="padding:6px 10px;">Title</th><th style="padding:6px 10px;">Email</th>
            <th style="padding:6px 10px;">Phone</th><th style="padding:6px 10px;">Source</th>
          </tr></thead><tbody>{rows}</tbody></table></div>""", unsafe_allow_html=True)
        dossier_md.append("\n## Contacts (live research — verify before use)\n")
        for c in sorted(contacts, key=lambda x: x.get("rank_order", 99)):
            dossier_md.append(f"{c.get('rank_order', '')}. **{c.get('name', '')}** — {c.get('title', '')}"
                              f" ({c.get('division', '')}) · {c.get('email') or c.get('email_guess') or 'no email found'}"
                              f" · {c.get('phone') or ''} · source: {c.get('source_url', '')}")
    else:
        st.info("No verifiable named contacts surfaced — use the roster links below; small agencies "
                "often list command staff only in budget PDFs.")

    lc1, lc2 = st.columns(2, gap="medium")
    with lc1:
        if inc.get("vendor"):
            st.markdown(f"""
            <div class="gn-card warn" style="padding:0.9rem 1.1rem;">
              <div style="font-weight:800;color:{NAVY};">📡 Incumbent: {hclean(inc['vendor'])}
                {f"({hclean(inc['product'])})" if inc.get('product') else ''}</div>
              <div style="font-size:0.88rem;">{hclean(inc.get('evidence'))}
                {f"<a href='{hurl(inc['source_url'])}' target='_blank'>↗</a>" if inc.get('source_url') else ''}</div>
              <div style="font-size:0.82rem;color:{SLATE};margin-top:4px;">
                {hclean(inc.get('contract_note'), 'Check GovSpend for the contract renewal date — outreach lands best 6–9 months out.')}</div>
            </div>""", unsafe_allow_html=True)
            dossier_md.append(f"\n**Incumbent vendor (live):** {inc['vendor']} — {inc.get('evidence', '')} [{inc.get('source_url', '')}]")
    with lc2:
        if events:
            ev_html = "".join(
                f'<div style="padding:4px 0;border-bottom:1px solid #EEF1F2;font-size:0.85rem;">'
                f'<b>{hclean(e.get("year"))}</b> — {hclean(e.get("what_happened"))}<br>'
                f'<span style="color:{SLATE};font-size:0.8rem;">{hclean(e.get("sales_relevance"))}</span> '
                f'<a href="{hurl(e.get("source_url"))}" target="_blank">↗</a></div>'
                for e in events)
            st.markdown(f'<div class="gn-card teal" style="padding:0.9rem 1.1rem;">'
                        f'<div style="font-weight:800;color:{NAVY};">🗞️ Recent events</div>{ev_html}</div>',
                        unsafe_allow_html=True)
            for e in events:
                dossier_md.append(f"- EVENT {e.get('year', '')}: {e.get('what_happened', '')} "
                                  f"(relevance: {e.get('sales_relevance', '')}) [{e.get('source_url', '')}]")
    if lr.get("notes"):
        st.caption(f"📝 {lr['notes']}")
        dossier_md.append(f"\n_Research notes: {lr['notes']}_")

st.markdown("---")

# ---- A0. The people
st.markdown(f"### 👥 The people to call <span style='font-size:0.85rem;color:{SLATE};font-weight:400;'>— highest rank first, no skipping command staff</span>", unsafe_allow_html=True)

lcol, rcol = st.columns([3, 2], gap="large")
with lcol:
    st.markdown(f"""
    <div class="gn-card navy" style="padding:1rem 1.2rem;">
      <div class="gn-label">Why these people</div>
      <div style="font-size:0.9rem;color:#262A2D;margin-bottom:0.6rem;">{ladder["why_them"]}</div>
      <div style="font-size:0.82rem;color:{SLATE};font-style:italic;">{ladder["rules"]}</div>
    </div>""", unsafe_allow_html=True)

    for div in ladder["divisions"]:
        rows_html = ""
        for i, title in enumerate(div["titles"]):
            t_clean = title.split(" (")[0]
            li = ("https://www.linkedin.com/search/results/people/?keywords=" +
                  urllib.parse.quote_plus(f'"{jurisdiction}" "{t_clean}"'))
            gq = g(f'"{jurisdiction}" "{t_clean}" (email OR contact)')
            rows_html += (
                f'<div style="display:flex;align-items:center;gap:10px;padding:5px 0;'
                f'border-bottom:1px solid #EEF1F2;">'
                f'<span class="gn-step" style="width:22px;height:22px;flex:0 0 22px;font-size:0.75rem;">{i+1}</span>'
                f'<span style="flex:1;font-size:0.92rem;color:#262A2D;font-weight:{700 if i == 0 else 500};">{title}</span>'
                f'<a href="{li}" target="_blank" style="font-size:0.8rem;">LinkedIn ↗</a>'
                f'<a href="{gq}" target="_blank" style="font-size:0.8rem;">Google ↗</a>'
                f'</div>')
        st.markdown(f"""
        <div class="gn-card teal" style="padding:0.9rem 1.2rem;">
          <div style="font-weight:800;color:{NAVY};margin-bottom:0.35rem;">{div["division"]}</div>
          {rows_html}
        </div>""", unsafe_allow_html=True)
        dossier_md.append(f"\n**Contacts — {div['division']}** (work top to bottom):\n" +
                          "\n".join(f"{i+1}. {t} — Name: ____ · Email: ____ · Phone: ____"
                                    for i, t in enumerate(div["titles"])))

with rcol:
    roster_q = " OR ".join(f'"{p}"' for p in ladder["roster_page_names"][:3])
    link_row("🗂️", "Their roster / command staff page",
             g(f'"{jurisdiction}" ({roster_q})'),
             "The agency's own leadership page — names and often direct emails, in rank order.",
             "a staff directory or org chart; PDFs often include emails")
    link_row("🧾", "Org chart (PDF)",
             g(f'"{jurisdiction}" organizational chart filetype:pdf'),
             "Budget books and org-chart PDFs name every division head.",
             "the public-safety org page — division heads = your call list")
    link_row("💼", "Everyone at the agency on LinkedIn",
             "https://www.linkedin.com/search/results/people/?keywords=" + urllib.parse.quote_plus(f'"{jurisdiction}"'),
             "Full people search scoped to the agency name — filter by title from the ladder.",
             "current employees with command titles; check 'About' for tenure")
    em_dirs = load_em_directories()
    dir_row = em_dirs[em_dirs["state"] == selected_state]
    if not dir_row.empty:
        d = dir_row.iloc[0]
        link_row("📖", f"{selected_state} county EM contact directory",
                 d["url"],
                 f"Official state-published directory — {d['contains']}.",
                 f"the {county_label or 'county'} row: names, phones, often direct emails")
        dossier_md.append(f"- **{selected_state} EM contact directory**: {d['url']}")

    st.markdown(f"""
    <div class="gn-card green" style="padding:0.9rem 1.2rem;">
      <div style="font-weight:800;color:{NAVY};margin-bottom:0.3rem;">✉️ Email pattern</div>
      <div style="font-size:0.85rem;color:#262A2D;">{ladder["email_domains_hint"]}.
      Once you have ONE real email from the roster page or a press release, the pattern
      (first.last@ / flast@ / first@) applies to every name on the ladder. Log every
      verified contact in HubSpot immediately.</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

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

# ---- B2. Competitive landscape & incidents map
st.markdown(f"### 🗺️ Who's running what nearby <span style='font-size:0.85rem;color:{SLATE};font-weight:400;'>— references, incumbents, and incidents that opened doors</span>", unsafe_allow_html=True)
from utils.mapview import render_landscape
dossier_md.extend(render_landscape(selected_state, county_label, jurisdiction))

# ---- C. The money
st.markdown("### 💰 The money — three layers, ranked for this account", unsafe_allow_html=True)

state_row = get_state_row(selected_state)
result = recommend(selected_seg, selected_state, [])
recs = result["recommendations"][:5]

lc, rc = st.columns([3, 2], gap="large")
with lc:
    seg_singular = selected_seg.split(" (")[0].lower().replace("ies", "y") if selected_seg.lower().endswith("ies") \
        else selected_seg.split(" (")[0].lower().removesuffix("s")
    st.markdown(f"**Layer 1 · Federal pass-through** — flows FEMA/DHS → state → local {seg_singular}. The biggest lever.")
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
    if st.button("🎯 Find more targets like this →", use_container_width=True,
                 help="Build the ICP-ranked target list for this state and segment."):
        st.switch_page("pages/2_Find_Potential_Focus.py")

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
