"""Find Potential Focus — pick a state + segment, get the ICP-ranked target list.

Territory prospecting: the app sweeps public sources statewide, scores every
candidate against the Genasys ICP for the chosen segment (best-fit attributes
up, caution signals down), returns the top 15-20, and researches the actual
decision makers (names, roles, emails, phones) per organization on demand.
"""

import json

import pandas as pd
import streamlit as st
from utils.auth import check_password
check_password()

from utils.styles import (inject_css, sidebar_brand, page_header, pill,
                          GREEN, NAVY, TEAL, SLATE)
from utils.data_loader import load_states, load_icp_profiles, load_contact_ladders
from utils import live_prospecting, live_research

inject_css()
sidebar_brand()

page_header(
    "Territory planning · state by state",
    "Find Potential Focus",
    "Pick the state you're working and who you want to reach. Get the 15–20 "
    "organizations that best match the Genasys ICP — ranked, scored, and sourced — "
    "then pull the decision makers for the best fits.",
)

TIER_STYLE = {
    "Prime": ("#15803D", "#DCFCE7"),
    "Strong": ("#0E7490", "#CFFAFE"),
    "Worth a look": ("#A16207", "#FEF9C3"),
}

PRODUCTS = {
    "Evertel": "CJIS-compliant secure mobile collaboration for law enforcement — FOIA-auditable "
               "messaging, Regional Rooms for cross-agency intel, replaces WhatsApp/Signal risk",
    "Protect": "Zone-based evacuation management and mass notification SaaS — common operating "
               "picture, IPAWS/WEA integration, no-signup public reach by zone",
    "Acoustics": "Fixed acoustic arrays / voice sirens — solar/battery-backed outdoor voice "
                 "alerting that works when power and cellular fail",
    "LRAD": "Long-range acoustic devices (vehicle, handheld, fixed) — directed voice at 300–1,000m "
            "for tactical operations, crowds, perimeter security, and escalation-of-force compliance",
}

DEFAULT_PRODUCTS = {
    "fire_em": ["Protect", "Acoustics"],
    "law_enforcement": ["Evertel", "LRAD"],
    "military": ["LRAD", "Acoustics"],
    "critical_infra": ["Protect", "LRAD"],
    "cities_counties": ["Protect", "Acoustics"],
}

# ---------------------------------------------------------------- inputs

states_df = load_states()
icps = load_icp_profiles()
state_list = sorted(states_df["state"].tolist())
icp_labels = {p["label"]: p for p in icps}

c1, c2, c3 = st.columns([2, 3, 3])
with c1:
    sel_state = st.selectbox("State", state_list,
                             index=state_list.index("Texas") if "Texas" in state_list else 0)
with c2:
    sel_label = st.selectbox("Who do you want to reach?", list(icp_labels.keys()))
icp = icp_labels[sel_label]
with c3:
    sel_products = st.multiselect(
        "Products", list(PRODUCTS.keys()),
        default=DEFAULT_PRODUCTS.get(icp["id"], ["Protect"]),
        key=f"fpf_products_{icp['id']}",
        help="What you're leading with — the ranking and product angles follow this selection.")
if not sel_products:
    sel_products = DEFAULT_PRODUCTS.get(icp["id"], ["Protect"])

with st.expander(f"📋 What “ideal” means for {icp['label']} (the ICP this list is scored against)"):
    bc1, bc2 = st.columns(2, gap="large")
    with bc1:
        st.markdown("**Best-fit attributes** — more matches, higher score")
        for group, items in icp["best_fit"].items():
            st.markdown(f"*{group}*")
            st.markdown("\n".join(f"- {i}" for i in items))
    with bc2:
        st.markdown("**Caution signals** — each one drags the score down")
        st.markdown("\n".join(f"- {c}" for c in icp["caution_signals"]))
        st.markdown("**Decision makers to reach**")
        st.markdown("\n".join(f"- {d}" for d in icp["decision_makers"]))

# ---------------------------------------------------------------- engine gate

if not live_prospecting.is_configured():
    st.markdown(f"""
    <div class="gn-card warn" style="padding:1.2rem 1.4rem;">
      <div style="font-weight:800;color:{NAVY};font-size:1.05rem;">⚡ This page needs the live-research connection</div>
      <div style="font-size:0.9rem;color:#262A2D;margin-top:6px;">
        Add <code>ANTHROPIC_API_KEY</code> in the app's Streamlit secrets (same key that powers
        live research on the Research Specific Account/Target page) and this page activates.
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

products_key = tuple(sorted(sel_products))
run_key = f"fpf::{sel_state}::{icp['id']}::{'+'.join(products_key)}"

go = st.button(f"🎯 Build the {sel_state} target list — {' + '.join(sel_products)}", type="primary",
               help="Statewide sweep + ICP scoring. Takes 2–4 minutes; cached for 7 days per state/segment/products.")

if go:
    status = st.status(f"Building the {sel_state} · {icp['label']} target list…", expanded=True)
    try:
        result = live_prospecting.find_prospects(
            sel_state, icp["id"], json.dumps(icp, sort_keys=True),
            products_key, json.dumps({p: PRODUCTS[p] for p in products_key}, sort_keys=True),
            _progress=lambda m: status.write(m))
        st.session_state[run_key] = result
        status.update(label="Target list ready", state="complete", expanded=False)
    except Exception as e:
        status.update(label="Prospecting failed", state="error")
        st.error(f"Prospecting failed: {e}. Try again in a minute — partial rate limits pass quickly.")

result = st.session_state.get(run_key)

# ---------------------------------------------------------------- results

if result:
    prospects = result.get("prospects") or []
    if result.get("market_notes"):
        st.markdown(f'<div class="gn-card teal" style="padding:0.9rem 1.2rem;font-size:0.93rem;">'
                    f'<b>Market read:</b> {result["market_notes"]}</div>', unsafe_allow_html=True)

    st.caption(f"{len(prospects)} prospects ranked · scored against the {icp['label']} ICP · "
               "every claim sourced — spot-check before you commit the quarter. Cached 7 days; "
               "results exclude existing Genasys customers.")

    # ---- downloads
    if prospects:
        flat = pd.DataFrame([{
            "rank": p.get("rank"), "name": p.get("name"), "county": p.get("county"),
            "population": p.get("population_served"), "fit_score": p.get("fit_score"),
            "tier": p.get("tier"), "why_fit": " | ".join(p.get("why_fit") or []),
            "caution_flags": " | ".join(p.get("caution_flags") or []),
            "incumbent": p.get("incumbent"), "recent_events": p.get("recent_events"),
            "product_angle": p.get("product_angle"),
            "sources": " ".join(p.get("source_urls") or []),
        } for p in prospects])
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("⬇️ Download as CSV (for HubSpot import / pipeline review)",
                               flat.to_csv(index=False),
                               file_name=f"targets_{sel_state.lower().replace(' ', '_')}_{icp['id']}.csv",
                               mime="text/csv", use_container_width=True)
        with d2:
            md = [f"# Target list — {sel_state} · {icp['label']}",
                  f"_Scored against the Genasys ICP · built with the Funding Intelligence tool_\n"]
            for p in prospects:
                md.append(f"## {p.get('rank')}. {p.get('name')} — {p.get('fit_score')}/100 ({p.get('tier')})")
                md.append(f"{p.get('county') or ''} · pop {p.get('population_served') or '?'} · "
                          f"incumbent: {p.get('incumbent') or 'unknown'}")
                md.extend(f"- {w}" for w in (p.get("why_fit") or []))
                if p.get("product_angle"):
                    md.append(f"- **Angle:** {p['product_angle']}")
            st.download_button("⬇️ Download territory plan (Markdown)",
                               "\n".join(md),
                               file_name=f"territory_{sel_state.lower().replace(' ', '_')}_{icp['id']}.md",
                               mime="text/markdown", use_container_width=True)

    # ---- ladder for decision-maker research
    ladders = load_contact_ladders()

    def ladder_for(prospect_name: str):
        seg = icp["funding_segment"]
        if icp["id"] == "law_enforcement" and "sheriff" in prospect_name.lower():
            seg = "Sheriff (county law enforcement)"
        match = next((l for l in ladders if l["segment"] == seg), ladders[0])
        return "\n".join(f"  {d['division']}: " + " → ".join(d["titles"]) for d in match["divisions"])

    # ---- prospect cards
    for p in prospects:
        fg, bg = TIER_STYLE.get(p.get("tier"), TIER_STYLE["Worth a look"])
        prime = p.get("tier") == "Prime"
        flags = p.get("caution_flags") or []
        flags_html = ("".join(f'<div style="font-size:0.84rem;color:#B45309;">⚠ {f}</div>' for f in flags)
                      if flags else "")
        why_html = "".join(f'<div style="font-size:0.9rem;">• {w}</div>' for w in (p.get("why_fit") or []))
        srcs = " · ".join(f'<a href="{u}" target="_blank">src{i+1} ↗</a>'
                          for i, u in enumerate((p.get("source_urls") or [])[:3]))
        inc = f'<span class="gn-pill" style="color:#B45309;background:#FEF3C7;">Incumbent: {p["incumbent"]}</span>' \
            if p.get("incumbent") else ""

        st.markdown(f"""
        <div class="gn-card {'green' if prime else 'navy'}" style="padding:1.1rem 1.3rem;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">
            <div style="flex:1;min-width:300px;">
              <div style="font-weight:800;color:{NAVY};font-size:1.08rem;">
                {p.get('rank')}. {p.get('name')}
                <span class="gn-pill" style="color:{fg};background:{bg};margin-left:8px;">{p.get('tier')}</span>
                {inc}
              </div>
              <div style="font-size:0.85rem;color:{SLATE};margin:2px 0 8px 0;">
                {p.get('county') or ''} · pop {p.get('population_served') or '?'}
                {(' · ' + p['recent_events']) if p.get('recent_events') else ''}
              </div>
              {why_html}
              {flags_html}
              <div style="font-size:0.88rem;margin-top:8px;color:{NAVY};"><b>Lead with:</b> {p.get('product_angle') or ''}</div>
              <div style="font-size:0.82rem;margin-top:4px;">{srcs}</div>
            </div>
            <div style="text-align:center;min-width:86px;">
              <div style="font-size:2rem;font-weight:900;color:{NAVY};">{p.get('fit_score')}</div>
              <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.08em;color:{SLATE};">ICP FIT / 100</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        ckey = f"fpfc::{sel_state}::{p.get('name')}"
        contacts_res = st.session_state.get(ckey)
        if contacts_res is None:
            if st.button(f"📞 Get decision makers — {p.get('name')}", key=f"btn_{ckey}",
                         help="Live web research: names, roles, emails, phones. ~1–2 min; cached 7 days."):
                cstatus = st.status(f"Researching decision makers at {p.get('name')}…", expanded=True)
                try:
                    contacts_res = live_research.research_account(
                        p.get("name"), p.get("county") or "", sel_state,
                        icp["funding_segment"], ladder_for(p.get("name", "")),
                        _progress=lambda m: cstatus.write(m))
                    st.session_state[ckey] = contacts_res
                    cstatus.update(label=f"Decision makers — {p.get('name')}", state="complete", expanded=False)
                    st.rerun()
                except Exception as e:
                    cstatus.update(label="Contact research failed", state="error")
                    st.error(f"Contact research failed: {e}")
        else:
            ag = contacts_res.get("agency") or {}
            contacts = contacts_res.get("contacts") or []
            meta = []
            if ag.get("website"):
                meta.append(f"<a href='{ag['website']}' target='_blank'>Website ↗</a>")
            if ag.get("email_pattern"):
                meta.append(f"Email pattern: <b>{ag['email_pattern']}</b>")
            if ag.get("main_phone"):
                meta.append(f"Main line: <b>{ag['main_phone']}</b>")
            if contacts:
                rows = ""
                for c in sorted(contacts, key=lambda x: x.get("rank_order", 99))[:8]:
                    email = c.get("email") or (f"{c['email_guess']} <span style='color:{SLATE};'>(guess)</span>"
                                               if c.get("email_guess") else "—")
                    rows += (f"<tr><td style='padding:5px 9px;'><b>{c.get('name', '')}</b></td>"
                             f"<td style='padding:5px 9px;'>{c.get('title', '')}</td>"
                             f"<td style='padding:5px 9px;font-size:0.86rem;'>{email}</td>"
                             f"<td style='padding:5px 9px;font-size:0.86rem;'>{c.get('phone') or '—'}</td>"
                             f"<td style='padding:5px 9px;'><a href='{c.get('source_url', '#')}' target='_blank'>src ↗</a></td></tr>")
                st.markdown(f"""
                <div class="gn-card teal" style="padding:0.7rem 0.9rem;margin-top:-0.5rem;overflow-x:auto;">
                  <div style="font-size:0.85rem;margin-bottom:4px;">{' · '.join(meta)}</div>
                  <table style="width:100%;border-collapse:collapse;font-size:0.9rem;">
                    <thead><tr style="text-align:left;color:{SLATE};font-size:0.72rem;text-transform:uppercase;">
                      <th style="padding:5px 9px;">Name</th><th style="padding:5px 9px;">Title</th>
                      <th style="padding:5px 9px;">Email</th><th style="padding:5px 9px;">Phone</th>
                      <th style="padding:5px 9px;">Source</th></tr></thead>
                    <tbody>{rows}</tbody></table>
                  <div style="font-size:0.78rem;color:{SLATE};margin-top:4px;">
                    Sourced just now from public pages — verify before you dial. Ordered highest rank first.</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.info(f"No verifiable named contacts surfaced for {p.get('name')} — try the agency "
                        "website's leadership page or the county budget PDF (rosters often hide there).")

    st.markdown("---")
    st.markdown(f'<div style="font-size:0.9rem;color:{SLATE};">Next: run your top pick through '
                f'<b>Research Specific Account/Target</b> for the full funding dossier, then '
                f'<b>Funding Pathfinder</b> for the money conversation and the draft email.</div>',
                unsafe_allow_html=True)
