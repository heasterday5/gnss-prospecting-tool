"""Competitive landscape + incident map for the Start Here dossier.

Plots known vendor deployments (Genasys vs. competitors) and documented
alert/evacuation incidents on a county-centroid map, scoped to a state.
Data: deployments.csv and incidents.csv — curated, sourced, not exhaustive.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.styles import NAVY, GREEN, TEAL, SLATE
from utils.data_loader import load_deployments, load_incidents, load_counties

VENDOR_COLORS = {
    "Genasys": "#5B8F22",
    "Everbridge": "#E4572E",
    "CodeRED": "#8B5CF6",
    "Rave": "#0E7490",
    "Hyper-Reach": "#B45309",
    "Regroup": "#A16207",
    "Konexus": "#6D28D9",
    "Perimeter": "#BE185D",
}
INCIDENT_COLOR = "#DC2626"
SUCCESS_COLOR = "#0E7490"

INCIDENT_LABELS = {
    "siren_failure": "Sirens failed / not activated",
    "alert_not_sent": "No alert sent",
    "alert_delayed": "Alert delayed",
    "optin_gap": "Opt-in coverage gap",
    "infrastructure_failure": "Comms infrastructure failed",
    "false_alarm": "False alarm",
    "evacuation_challenge": "Evacuation challenge",
    "success_reference": "Zone-evacuation success",
}


def _vendor_color(v):
    return VENDOR_COLORS.get(str(v).split(":")[0], "#5A6B75")


@st.cache_data
def _geocoded(state: str):
    """Deployments and incidents for a state, joined to county centroids."""
    counties = load_counties()
    cent = counties[counties["state"] == state][["county", "lat", "lon"]]

    dep = load_deployments()
    dep = dep[dep["state"] == state].merge(cent, on="county", how="left").dropna(subset=["lat"])
    inc = load_incidents()
    inc = inc[inc["state"] == state].merge(cent, on="county", how="left").dropna(subset=["lat"])
    return dep, inc


def render_landscape(state: str, county_label, jurisdiction: str) -> list:
    """Render the map + takeaway cards. Returns markdown lines for the dossier."""
    md = []
    dep, inc = _geocoded(state)

    if dep.empty and inc.empty:
        st.info(f"No mapped deployments or incidents for {state} yet — the dataset is curated and "
                "growing. Check the county 'emergency alerts' page to identify the incumbent vendor.")
        return md

    fig = go.Figure()

    # deployments, grouped by vendor family so the legend reads cleanly
    dep = dep.copy()
    dep["vendor_family"] = dep["vendor"].astype(str).str.split(":").str[0]
    for vendor, grp in dep.groupby("vendor_family"):
        is_gen = vendor == "Genasys"
        fig.add_trace(go.Scattergeo(
            lat=grp["lat"].astype(float) + (0.015 * (grp.groupby(["lat"]).cumcount())),
            lon=grp["lon"].astype(float) + (0.02 * (grp.groupby(["lon"]).cumcount())),
            text=[f"<b>{r.jurisdiction}</b><br>{r.vendor} — {r.product_category.replace('_', ' ')}"
                  f"<br>{r.detail}<br><i>noted {r.year_noted}</i>" for r in grp.itertuples()],
            hoverinfo="text",
            name=f"{'★ ' if is_gen else ''}{vendor} ({len(grp)})",
            mode="markers",
            marker=dict(size=13 if is_gen else 10,
                        color=_vendor_color(vendor),
                        symbol="star" if is_gen else "circle",
                        line=dict(width=1, color="white")),
        ))

    # incidents
    if not inc.empty:
        inc = inc.copy()
        fails = inc[inc["incident_type"] != "success_reference"]
        wins = inc[inc["incident_type"] == "success_reference"]
        for sub, color, name, symbol in ((fails, INCIDENT_COLOR, f"⚠ Notification failures ({len(fails)})", "triangle-up"),
                                         (wins, SUCCESS_COLOR, f"✓ Zone-evac successes ({len(wins)})", "diamond")):
            if sub.empty:
                continue
            fig.add_trace(go.Scattergeo(
                lat=sub["lat"].astype(float) - 0.03,
                lon=sub["lon"].astype(float) - 0.03,
                text=[f"<b>{r.place} — {r.year}</b><br>{str(r.hazard).title()}: "
                      f"{INCIDENT_LABELS.get(r.incident_type, r.incident_type)}<br>{r.what_happened}"
                      for r in sub.itertuples()],
                hoverinfo="text",
                name=name,
                mode="markers",
                marker=dict(size=12, color=color, symbol=symbol, line=dict(width=1, color="white")),
            ))

    fig.update_geos(scope="usa", fitbounds="locations",
                    showland=True, landcolor="#F4F6F7",
                    showsubunits=True, subunitcolor="#D9D9D9", subunitwidth=1.2,
                    showlakes=False)
    fig.update_layout(height=460, margin=dict(l=0, r=0, t=8, b=0),
                      legend=dict(orientation="h", yanchor="bottom", y=-0.08, font=dict(size=12)),
                      paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("Curated from public sources (alert-signup pages, news, press releases) — not exhaustive. "
               "Hover any marker for the detail + year. Tell us what you learn in the field and we'll add it.")

    # ---- takeaway cards
    c1, c2, c3 = st.columns(3, gap="medium")

    in_county = dep[dep["county"] == county_label] if county_label else dep.iloc[0:0]
    inc_county = inc[inc["county"] == county_label] if county_label else inc.iloc[0:0]
    gen_refs = dep[dep["vendor_family"] == "Genasys"]
    comp_county = in_county[in_county["vendor_family"] != "Genasys"]

    with c1:
        title = f"In {county_label}" if county_label else "Pick a county above"
        if not in_county.empty or not inc_county.empty:
            items = ""
            for r in in_county.itertuples():
                items += (f'<div style="padding:4px 0;border-bottom:1px solid #EEF1F2;font-size:0.85rem;">'
                          f'<b style="color:{_vendor_color(r.vendor_family)};">{r.vendor}</b> — {r.jurisdiction} '
                          f'<a href="{r.source_url}" target="_blank">↗</a></div>')
            for r in inc_county.itertuples():
                items += (f'<div style="padding:4px 0;border-bottom:1px solid #EEF1F2;font-size:0.85rem;">'
                          f'<b style="color:{INCIDENT_COLOR};">{r.year} {str(r.hazard)}</b> — '
                          f'{INCIDENT_LABELS.get(r.incident_type, r.incident_type)} '
                          f'<a href="{r.source_url}" target="_blank">↗</a></div>')
            body = items
        else:
            body = ('<div style="font-size:0.85rem;color:#5A6B75;">Nothing documented yet in this county — '
                    'their "emergency alerts" signup page names the incumbent in one click (see Plans links above).</div>')
        st.markdown(f'<div class="gn-card navy" style="padding:0.9rem 1.1rem;"><div style="font-weight:800;'
                    f'color:{NAVY};margin-bottom:0.4rem;">📍 {title}</div>{body}</div>', unsafe_allow_html=True)

    with c2:
        if not gen_refs.empty:
            items = "".join(
                f'<div style="padding:4px 0;border-bottom:1px solid #EEF1F2;font-size:0.85rem;">'
                f'<b>{r.jurisdiction}</b> — {r.detail} <a href="{r.source_url}" target="_blank">↗</a></div>'
                for r in gen_refs.head(6).itertuples())
            note = ('<div style="font-size:0.8rem;color:#5A6B75;margin-top:0.4rem;font-style:italic;">'
                    'Name-drop these: "your neighbors in X already run zone-based evacuation with us."</div>')
        else:
            items = ('<div style="font-size:0.85rem;color:#5A6B75;">No documented in-state customer yet — '
                     'use the nearest-state reference from the map, or ask sales leadership for the current list.</div>')
            note = ""
        st.markdown(f'<div class="gn-card green" style="padding:0.9rem 1.1rem;"><div style="font-weight:800;'
                    f'color:{NAVY};margin-bottom:0.4rem;">★ Genasys references in {state}</div>{items}{note}</div>',
                    unsafe_allow_html=True)

    with c3:
        recent = inc[inc["incident_type"] != "success_reference"].sort_values("year", ascending=False).head(5)
        if not recent.empty:
            items = "".join(
                f'<div style="padding:4px 0;border-bottom:1px solid #EEF1F2;font-size:0.85rem;">'
                f'<b>{r.place} {r.year}</b> — {r.what_happened} <a href="{r.source_url}" target="_blank">↗</a></div>'
                for r in recent.itertuples())
        else:
            items = '<div style="font-size:0.85rem;color:#5A6B75;">No documented incidents in-state in the dataset.</div>'
        st.markdown(f'<div class="gn-card warn" style="padding:0.9rem 1.1rem;"><div style="font-weight:800;'
                    f'color:{NAVY};margin-bottom:0.4rem;">⚠️ Incidents to reference (respectfully)</div>{items}'
                    f'<div style="font-size:0.8rem;color:#5A6B75;margin-top:0.4rem;font-style:italic;">'
                    f'Frame as lessons; never blame: "after {recent.iloc[0]["place"] if not recent.empty else "recent events"}, '
                    f'many agencies re-checked their own alerting reach."</div></div>', unsafe_allow_html=True)

    # ---- displacement angle
    if not comp_county.empty:
        v = comp_county.iloc[0]
        st.markdown(f"""
        <div class="gn-card teal" style="padding:0.9rem 1.2rem;margin-top:0.6rem;">
          <div style="font-weight:800;color:{NAVY};">🎯 Displacement angle</div>
          <div style="font-size:0.9rem;color:#262A2D;">{v['jurisdiction']} runs <b>{v['vendor']}</b>
          ({str(v['product_category']).replace('_', ' ')}). Check GovSpend for the contract renewal date —
          outreach lands best 6–9 months out. Genasys Protect complements or replaces opt-in systems:
          zone-based, no signup required, works when cell coverage fails. The expiring-contract play in the
          Signal Playbook has the full talk track and email.</div>
        </div>""", unsafe_allow_html=True)

    # ---- dossier lines
    md.append("\n## Competitive landscape & incidents\n")
    for r in in_county.itertuples():
        md.append(f"- IN COUNTY: {r.jurisdiction} uses {r.vendor} ({r.product_category}) — {r.detail} [{r.source_url}]")
    for r in gen_refs.head(6).itertuples():
        md.append(f"- GENASYS REFERENCE ({state}): {r.jurisdiction} — {r.detail} [{r.source_url}]")
    for r in inc.sort_values("year", ascending=False).head(5).itertuples():
        md.append(f"- INCIDENT: {r.place} {r.year} ({r.hazard}) — {r.what_happened} [{r.source_url}]")
    return md
