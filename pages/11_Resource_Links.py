"""Resource Links — every external research tool the team uses, in one place."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.styles import md_html, inject_css, sidebar_brand, page_header, NAVY, SLATE, GREEN

inject_css()
sidebar_brand()

page_header("Reference", "Resource Links",
            "The external tools behind the research — funding, risk, procurement, "
            "and competitive intelligence. All verified links.")


def link_card(icon, title, url, why):
    md_html(f"""
    <div class="gn-card teal" style="padding:0.85rem 1.1rem;margin-bottom:0.55rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
        <div style="min-width:260px;flex:1;">
          <div style="font-weight:800;color:{NAVY};">{icon} {title}</div>
          <div style="font-size:0.88rem;color:#262A2D;">{why}</div>
        </div>
        <a href="{url}" target="_blank" style="background:{GREEN};color:{NAVY};font-weight:700;
           padding:6px 16px;border-radius:8px;white-space:nowrap;">Open ↗</a>
      </div>
    </div>""")


st.markdown("### 💰 Funding & awards")
link_card("📃", "Grants.gov", "https://grants.gov/search-grants",
          "Where federal NOFOs post first. Check before promising a window is open.")
link_card("🏛️", "USASpending.gov award search", "https://www.usaspending.gov/search",
          "Search federal awards by program, state, county, and date — see who already holds money.")
link_card("🌪️", "FEMA disaster declarations", "https://www.fema.gov/disaster/declarations",
          "A declaration in the last 24 months = HMGP post-disaster money open statewide.")
link_card("🧾", "FEMA Grants Portal (go.fema.gov)", "https://go.fema.gov",
          "Where agencies apply — and where awarded grants by program and state are tracked.")
link_card("✍️", "Lexipol grant services", "https://www.lexipol.com/services/grant-services/",
          "The grant-writing partner: bring them in once the agency agrees to pursue funding. "
          "GrantFinder tracks ~15,000 programs.")

st.markdown("### ⚠️ Risk & hazard data")
link_card("📈", "FEMA RAPT (National Risk Index data)",
          "https://experience.arcgis.com/experience/0a317e8998534c30a9b2d3861c814d42",
          "County risk ratings for 18 hazards. FEMA retired the standalone NRI site in Dec 2025 — "
          "the data lives here now. Search the county, open the pop-up.")
link_card("🧭", "CDC Social Vulnerability Index map",
          "https://www.atsdr.cdc.gov/place-health/php/svi/svi-interactive-map.html",
          "Top-quartile SVI = populations phone alerts miss. County percentile drives the equity play.")
link_card("🌊", "National Inventory of Dams", "https://nid.usace.army.mil/#/",
          "High-hazard dams by county — the downstream-warning (HHPD/HMGP) play.")
link_card("🔥", "Wildfire Risk to Communities", "https://apps.wildfirerisk.org/explore/",
          "USDA Forest Service wildfire risk percentile per county — the WUI conversation starter.")

st.markdown("### 🛒 Procurement & competitive")
link_card("🤝", "Sourcewell contract #030425-GYS",
          "https://www.sourcewell-mn.gov/cooperative-purchasing/030425-gys",
          "The RFP bypass — Genasys's national cooperative contract, valid through July 2029. "
          "Membership check on the same site.")
link_card("📡", "SAM.gov opportunity search",
          "https://sam.gov/search/?keywords=%22mass%20notification%22%20OR%20%22long%20range%20acoustic%22",
          "Live federal RFPs/RFQs for mass notification and acoustic systems, plus award history.")
link_card("📊", "ClearGov", "https://cleargov.com",
          "Municipal budget benchmarking — public-safety spend per capita vs. neighbors.")
link_card("🕵️", "GovSpend", "https://app.govspend.com",
          "The team's purchasing-intelligence platform: contracts, POs, and renewal dates. "
          "Use it to validate what this app surfaces — and to time displacement plays.")

st.markdown("### 🧭 Pipeline")
link_card("🧡", "HubSpot", "https://app.hubspot.com",
          "All prospect tracking lives in HubSpot. Add promising agencies at the Initial Sales Stage "
          "with the funding source and the signal that triggered outreach in the deal notes.")

st.markdown(f'<div style="font-size:0.85rem;color:{SLATE};margin-top:0.8rem;">County-specific '
            f'deep links (hazard plans, budgets, agendas) are generated per account on the '
            f'<b>Research Specific Account/Target</b> page.</div>', unsafe_allow_html=True)
