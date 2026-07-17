"""Procurement Toolkit — grant narrative, AEL codes, Sourcewell, SAFECOM, budget builder.

Uses the current Sourcewell contract (030425-GYS, valid through July 2029).
"""

import streamlit as st
from utils.auth import check_password
check_password()

import pandas as pd
from utils.styles import inject_css, sidebar_brand, page_header, pill

inject_css()
sidebar_brand()

page_header(
    "Step 3 · After agreement",
    "Procurement Toolkit",
    "Everything the agency's grant writer needs, copy/paste ready: justification narrative, "
    "FEMA AEL codes, the Sourcewell fast path, SAFECOM alignment, and a line-item budget.",
)

st.markdown(f"""
<div class="gn-card warn">
    <div class="gn-label" style="color:#B45309;">Contract number correction</div>
    <div class="gn-value">Older Genasys materials reference Sourcewell contract <strong>#091422-GNS</strong>.
    The current contract is <strong>#030425-GYS</strong> (public safety alert and secure messaging tools),
    valid through <strong>July 17, 2029</strong>. Use the new number in every quote, email, and grant narrative.
    <a href="https://www.sourcewell-mn.gov/cooperative-purchasing/030425-GYS">Verify on sourcewell-mn.gov →</a></div>
</div>
""", unsafe_allow_html=True)

tab_narr, tab_ael, tab_safecom, tab_budget = st.tabs(
    ["📄 Grant Narrative", "✅ AEL Codes & Sourcewell", "🛰 SAFECOM Alignment", "💵 Budget Builder"]
)

# ---------------- Grant Narrative ----------------
with tab_narr:
    st.markdown("**Give this to the agency** (Emergency Manager, Police Chief, Fire Chief) to customize "
                "into the Project Narrative / Justification section of their FEMA (EMPG, HSGP, HMGP, AFG) "
                "or state grant application. Fill the fields and copy the result.")

    c1, c2, c3 = st.columns(3)
    with c1:
        n_threats = st.text_input("Local threats", value="wildfires, flash flooding, severe weather",
                                  help="e.g. wildfires, flash flooding, active shooter incidents")
    with c2:
        n_units = st.text_input("Acoustic deployment", value="2 vehicle-mounted and 1 fixed")
    with c3:
        n_total = st.text_input("Total project cost", value="$125,000")

    narrative = f"""PROJECT TITLE: Multi-Agency Intelligent Evacuation Management and Integrated Mass Notification Capability

1. EXECUTIVE SUMMARY / STATEMENT OF NEED

Our jurisdiction faces escalating risks from all-hazard emergencies, including {n_threats}. Current localized response capabilities rely on fragmented communication systems, lagging community notification pipelines, and static, legacy evacuation maps. These deficiencies create significant bottlenecks during high-stress evacuations, putting both first responders and the public at critical risk.

To address these vulnerabilities, this project seeks funding to procure and deploy an integrated, hardware-plus-software ecosystem from Genasys. This deployment will provide our agency with zone-based predictive evacuation management, automated multi-agency coordination, and ultra-clear acoustic localized voice alerting. This system will bridge the gap between incident command and real-time public safety actions, ensuring life-safety instructions reach the public immediately, even if commercial telecom infrastructure fails.

2. PROJECT DESCRIPTION & SCOPE OF WORK

This project involves the comprehensive implementation of the Genasys public safety ecosystem, broken into two critical operational components:

- Intelligent Evacuation Software (Genasys Protect): We will implement an advanced, cloud-based platform to digitize operational zones across our jurisdiction. This software will empower emergency managers, police, and fire chiefs to collaboratively simulate, orchestrate, and execute evacuations using real-time traffic data, fire-spread models, and cross-jurisdictional geographic parameters. It will feature public-facing portals providing clear, visual, zone-by-zone instructions during an active event.

- High-Intelligibility Acoustic Warning Systems (Genasys Acoustics/LRAD): We will deploy {n_units} commercial-off-the-shelf (COTS) long-range acoustic voice systems. Unlike traditional sirens that merely emit an abstract tone, these systems broadcast highly directional, voice-intelligible instructions over vast distances. They ensure that hard-to-reach populations, outdoor recreation areas, and communities with compromised cellular infrastructure receive actionable alerts.

3. STRATEGIC ALIGNMENT WITH FEMA NATIONAL PREPAREDNESS GOALS

This procurement directly supports the FEMA National Preparedness System by bolstering several Core Capabilities:

- Operational Coordination: Genasys Protect provides a single, unified operating picture, allowing disparate agencies (Police, Fire, EMS, Public Works, and Military/National Guard) to synchronize evacuation routing and timing seamlessly.
- Public Information and Warning: By linking zone management to direct communication channels (IPAWS, SMS, and Long-Range Acoustics), the platform ensures the delivery of actionable, accessible, and timely life-safety alerts to the entire affected population.
- Operational Communications: The system acts as a redundant, resilient communication asset. Vehicle-mounted and fixed acoustic arrays allow for tactical on-the-scene communication when terrestrial networks are down.

4. AUTHORIZED EQUIPMENT LIST (AEL) & COMPLIANCE VERIFICATION

The proposed equipment falls strictly within allowable items designated by FEMA's Authorized Equipment List (AEL):

- AEL Item Number: 03OE-03-MEGA (System, Public Address, Handheld or Hand-Carried)
- AEL Item Number: 03OE-03-META (System, Public Address, Mobile/Vehicle Mounted)
- AEL Item Number: 14SW-01-ALRT (System, Alert and Warning)

Compliance Note: All requested hardware consists of Commercial-Off-The-Shelf (COTS) voice systems configured for emergency public broadcast. They do not constitute military-grade acoustic weapons or prohibited items under federal grant guidelines.

5. BUDGET JUSTIFICATION & PROCUREMENT EFFICIENCY

The total project cost is estimated at {n_total}. This covers software licensing, hardware procurement, mounting accessories, installation, and comprehensive operational training for staff.

To satisfy federal competitive bidding requirements while accelerating deployment timelines, this procurement will be executed using pre-negotiated cooperative purchasing through the Sourcewell Public Safety Solutions Contract #030425-GYS. This mechanism eliminates tedious RFP cycles, ensures federally vetted pricing, and guarantees optimal cost-efficiency for the grant allocation."""

    st.code(narrative, language=None)
    st.download_button("Download narrative (.txt)", narrative,
                       file_name="genasys_grant_narrative.txt")

# ---------------- AEL & Sourcewell ----------------
with tab_ael:
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("#### FEMA Authorized Equipment List codes")
        st.markdown("""
        <div class="gn-card green">
            <h4>14SW-01-ALRT</h4>
            <div class="gn-value">System, Alert and Warning — <em>Genasys Protect software & core integrations</em></div>
        </div>
        <div class="gn-card green">
            <h4>03OE-03-META</h4>
            <div class="gn-value">System, Public Address, Mobile/Vehicle Mounted — <em>vehicle-mounted LRAD systems</em></div>
        </div>
        <div class="gn-card green">
            <h4>03OE-03-MEGA</h4>
            <div class="gn-value">System, Public Address, Handheld or Hand-Carried — <em>portable, tactical LRAD devices</em></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        **Sales myth buster:** some buyers think long-range voice systems are restricted under
        federal grant rules. False — Genasys products are **Commercial-Off-The-Shelf (COTS)**
        public address tools, fully authorized under standard FEMA grant rules. Cite the AEL
        codes above directly in the grant narrative.
        """)
    with c2:
        st.markdown("#### Skip the RFP — the Sourcewell advantage")
        st.markdown("""
        <div class="gn-card teal">
            <h4>Sourcewell Contract #030425-GYS</h4>
            <div class="gn-value">
            <strong>Category:</strong> Public safety alert and secure messaging tools (mass notification,
            emergency coordination, zone-based communication, community alerts)<br>
            <strong>Valid through:</strong> July 17, 2029<br>
            <strong>Legal standing:</strong> satisfies municipal competitive-bidding laws in all 50 states<br>
            <strong>Grant compliant:</strong> meets federal Uniform Guidance for spending grant dollars
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        **How it works:**
        1. Client confirms (or obtains — it's free) Sourcewell membership
        2. Client requests a Genasys quote referencing contract **#030425-GYS**
        3. Client issues a direct purchase order — **no RFP cycle**

        Thousands of cities and counties are already registered members — check the
        [Sourcewell registry](https://www.sourcewell-mn.gov/) during qualification.
        """)

# ---------------- SAFECOM ----------------
with tab_safecom:
    st.markdown("When agencies apply for federal emergency-communication funding, proposals are scored "
                "against **CISA SAFECOM guidance**. Use this framework to position Genasys as a textbook "
                "SAFECOM-compliant investment — lift the language directly into the technical narrative.")
    st.markdown("""
    <div class="gn-card navy">
        <h4>1 · Interoperability (the "Technology" lane)</h4>
        <div class="gn-value"><strong>The standard:</strong> systems must share data and voice across manufacturers, disciplines, and jurisdictions.<br>
        <strong>The Genasys alignment:</strong> Protect is platform-agnostic and API-driven — it bridges disconnected agency technologies, integrating CAD feeds, weather data, and traffic monitoring into a single map, then exporting unified alerts across IPAWS (WEA/EAS), SMS, social media, and LRAD speaker arrays simultaneously.</div>
    </div>
    <div class="gn-card navy">
        <h4>2 · Multi-Agency / Multi-Jurisdictional Scope (the "Usage" lane)</h4>
        <div class="gn-value"><strong>The standard:</strong> move away from agency silos toward regional, statewide, multi-agency structures.<br>
        <strong>The Genasys alignment:</strong> evacuations don't stop at city borders. A county EM, a municipal PD, and a state park service see the same zone-based map, with operational handoff of zones as an incident crosses boundaries — SAFECOM's highest threshold for regional coordination.</div>
    </div>
    <div class="gn-card navy">
        <h4>3 · Redundant & Resilient Channels (the "Governance & Plain Language" lane)</h4>
        <div class="gn-value"><strong>The standard:</strong> plain-language alerts (no codes, no abstract tones) with built-in infrastructure redundancy.<br>
        <strong>The Genasys alignment:</strong> tone sirens fail SAFECOM intent — a wail conveys nothing. Genasys acoustics broadcast clear verbal instructions in plain language, multi-lingual, pre-recorded or live. And when an earthquake, cyberattack, or wildfire takes out cell towers, battery-backed, solar-ready arrays keep working with zero dependence on commercial telecom.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Three-point summary for grant writers")
    st.code("""1. SOP Integration: Genasys Protect digitizes and automates Standard Operating Procedures across agencies, moving the jurisdiction up the SAFECOM continuum from "Individual Agency" to "Regional Interoperability."

2. Voice Intelligibility: Genasys LRAD systems meet the strict speech-transmission clarity requirements for high-stress public address, replacing legacy, non-compliant tone sirens.

3. Data Security: The cloud-native software layer complies with modern federal cybersecurity priorities, safeguarding multi-agency critical-infrastructure mappings (such as dam hazard areas) via enterprise-grade access controls.""", language=None)

# ---------------- Budget Builder ----------------
with tab_budget:
    st.markdown("Adjust quantities and unit costs to match the actual Genasys quote, then copy the table "
                "into the **Budget Narrative / Cost Justification** section of the application.")

    default_rows = pd.DataFrame([
        {"Cost Category": "Software Licensing", "Item": "Genasys Protect Platform License (annual — zone management & public alerting portal)", "AEL Code": "14SW-01-ALRT", "Unit Cost": 25000, "Qty": 1,
         "Justification": "Centralized cloud infrastructure to digitize regional evacuation zones, run multi-agency predictive routing simulations, and push real-time spatial data to the public interface. Aligns with Operational Coordination."},
        {"Cost Category": "Hardware", "Item": "Genasys Mobile Acoustic Array (vehicle-mounted LRAD, high-intelligibility directional voice)", "AEL Code": "03OE-03-META", "Unit Cost": 18500, "Qty": 2,
         "Justification": "Tactical public address mounted to emergency vehicles for precise, targeted evacuations in high-risk zones, WUI areas, or areas with complete cellular failure. Aligns with Public Information and Warning."},
        {"Cost Category": "Hardware", "Item": "Genasys Fixed Acoustic Siren/Voice Array (solar-powered, battery-backed, pole-mounted)", "AEL Code": "03OE-03-META", "Unit Cost": 45000, "Qty": 1,
         "Justification": "Installed at a permanent high-risk location (e.g., dam flood path, wildland chokepoint) to deliver automated plain-language acoustic commands during rapid-onset disasters. Aligns with Operational Communications."},
        {"Cost Category": "Professional Services", "Item": "Implementation, deployment & GIS zone-mapping integration", "AEL Code": "N/A (Services)", "Unit Cost": 12500, "Qty": 1,
         "Justification": "Engineering services to ingest local parcel, topographic, and historical hazard data to custom-build operational zone boundaries. Required for baseline operation."},
        {"Cost Category": "Training", "Item": "Multi-agency incident command simulation & system operator training", "AEL Code": "N/A (Training)", "Unit Cost": 5500, "Qty": 1,
         "Justification": "Operational testing, classroom instruction, and live drill scenarios for EM, dispatch, police, and fire personnel — supports SAFECOM interoperability guidelines."},
    ])

    edited = st.data_editor(default_rows, num_rows="dynamic", use_container_width=True,
                            column_config={
                                "Unit Cost": st.column_config.NumberColumn(format="$%d"),
                                "Justification": st.column_config.TextColumn(width="large"),
                            })
    edited["Total"] = edited["Unit Cost"].fillna(0) * edited["Qty"].fillna(0)
    total = int(edited["Total"].sum())
    st.markdown(f"### Total project: **${total:,}**")

    md_lines = ["PROJECT BUDGET DETAIL & COST JUSTIFICATION",
                "Procurement Vehicle: Sourcewell Public Safety Contract #030425-GYS",
                "Funding Source: [Insert Grant Name, e.g., FEMA EMPG / HMGP / HSGP]", "",
                "| Cost Category | Item | FEMA AEL | Unit Cost | Qty | Total | Justification |",
                "|---|---|---|---|---|---|---|"]
    for _, r in edited.iterrows():
        md_lines.append(f"| {r['Cost Category']} | {r['Item']} | {r['AEL Code']} | ${int(r['Unit Cost'] or 0):,} | {int(r['Qty'] or 0)} | ${int(r['Total']):,} | {r['Justification']} |")
    md_lines.append(f"| **TOTAL PROJECT** | | | | | **${total:,}** | Total requested contribution to establish modern, redundant emergency warning and intelligent evacuation capabilities. |")
    budget_md = "\n".join(md_lines)

    cdl1, cdl2 = st.columns(2)
    cdl1.download_button("Download budget (.md table)", budget_md, file_name="genasys_budget_justification.md", use_container_width=True)
    cdl2.download_button("Download budget (.csv)", edited.to_csv(index=False), file_name="genasys_budget.csv", use_container_width=True)
