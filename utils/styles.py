"""Genasys design system — colors, CSS, and reusable HTML components.

Modeled on genasys.com: clean white canvas, deep navy, teal + lime accents,
modern sans-serif (Inter), uppercase kickers, generous cards.
"""

import streamlit as st

# Genasys brand palette
NAVY = "#163443"
NAVY_DARK = "#0D2330"
TEAL = "#56C8DA"
GREEN = "#ABCF38"
GREEN_DARK = "#96B830"
CHARCOAL = "#262A2D"
GRAY = "#D9D9D9"
GRAY_LIGHT = "#F4F6F7"
SLATE = "#5A6B75"

STATUS_COLORS = {
    "ACTIVE": ("#15803D", "#DCFCE7"),
    "OPEN": ("#15803D", "#DCFCE7"),
    "DELAYED": ("#B45309", "#FEF3C7"),
    "UNCERTAIN": ("#B45309", "#FEF3C7"),
    "POST-DISASTER": ("#0E7490", "#CFFAFE"),
    "CANCELED": ("#B91C1C", "#FEE2E2"),
    "REPLACED": ("#6D28D9", "#EDE9FE"),
    "DISRUPTED": ("#B91C1C", "#FEE2E2"),
}

TIER_COLORS = {
    "Tier 1 - Immediate": ("#B91C1C", "#FEE2E2"),
    "Tier 1": ("#B91C1C", "#FEE2E2"),
    "Tier 2 - High Priority": ("#C2410C", "#FFEDD5"),
    "Tier 2": ("#C2410C", "#FFEDD5"),
    "Tier 3 - Medium Priority": ("#A16207", "#FEF9C3"),
    "Tier 3": ("#A16207", "#FEF9C3"),
    "Tier 4 - Monitor": ("#15803D", "#DCFCE7"),
    "Tier 4": ("#15803D", "#DCFCE7"),
}


def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"], .stMarkdown, .stButton, .stTextInput, .stSelectbox {{
        font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif !important;
    }}

    .block-container {{ padding-top: 2.2rem; max-width: 1200px; }}

    h1, h2, h3 {{ color: {NAVY}; font-weight: 800 !important; letter-spacing: -0.02em; }}

    /* ---------- Page header ---------- */
    .gn-kicker {{
        color: {GREEN_DARK}; font-size: 0.78rem; font-weight: 800;
        letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 0.2rem;
    }}
    .gn-title {{
        color: {NAVY}; font-size: 2.1rem; font-weight: 900;
        letter-spacing: -0.03em; line-height: 1.1; margin: 0 0 0.4rem 0;
    }}
    .gn-subtitle {{ color: {SLATE}; font-size: 1.02rem; max-width: 760px; margin: 0 0 0.6rem 0; }}
    .gn-rule {{
        width: 64px; height: 4px; border-radius: 2px; margin: 0.7rem 0 1.2rem 0;
        background: linear-gradient(90deg, {GREEN} 0%, {TEAL} 100%);
    }}

    /* ---------- Hero band ---------- */
    .gn-hero {{
        background: linear-gradient(120deg, {NAVY_DARK} 0%, {NAVY} 55%, #1E4A60 100%);
        border-radius: 16px; padding: 2.4rem 2.6rem; margin-bottom: 1.6rem;
        border-bottom: 4px solid {GREEN};
    }}
    .gn-hero .gn-kicker {{ color: {GREEN}; }}
    .gn-hero h1 {{
        color: #FFFFFF !important; font-size: 2.3rem; font-weight: 900;
        letter-spacing: -0.03em; line-height: 1.15; margin: 0 0 0.6rem 0;
    }}
    .gn-hero p {{ color: rgba(255,255,255,0.85); font-size: 1.05rem; max-width: 720px; margin: 0; }}
    .gn-hero .accent {{ color: {TEAL}; }}

    /* ---------- Cards ---------- */
    .gn-card {{
        background: #FFFFFF; border: 1px solid #E5E9EB; border-radius: 14px;
        padding: 1.3rem 1.4rem; margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(22,52,67,0.06);
        transition: box-shadow .15s ease, transform .15s ease;
    }}
    .gn-card:hover {{ box-shadow: 0 6px 18px rgba(22,52,67,0.12); }}
    .gn-card h4 {{ color: {NAVY}; margin: 0 0 0.45rem 0; font-weight: 800; }}
    .gn-card.green {{ border-left: 4px solid {GREEN}; }}
    .gn-card.teal {{ border-left: 4px solid {TEAL}; }}
    .gn-card.navy {{ border-left: 4px solid {NAVY}; }}
    .gn-card.warn {{ border-left: 4px solid #D97706; background: #FFFDF5; }}

    .gn-label {{
        font-size: 0.72rem; font-weight: 800; letter-spacing: 0.1em;
        text-transform: uppercase; color: {SLATE}; margin-bottom: 0.15rem;
    }}
    .gn-value {{ color: {CHARCOAL}; font-size: 0.95rem; }}

    /* ---------- Metric cards ---------- */
    .gn-metric {{
        background: linear-gradient(135deg, {NAVY} 0%, #1E4A60 100%);
        color: white; padding: 1.2rem 1.3rem; border-radius: 14px; height: 100%;
        border-bottom: 3px solid {GREEN};
    }}
    .gn-metric .value {{ font-size: 1.75rem; font-weight: 900; margin: 0.25rem 0; letter-spacing: -0.02em; }}
    .gn-metric .label {{ font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.85; }}
    .gn-metric .detail {{ font-size: 0.78rem; opacity: 0.7; margin-top: 0.2rem; }}

    /* ---------- Pills & badges ---------- */
    .gn-pill {{
        display: inline-block; padding: 2px 12px; border-radius: 999px;
        font-weight: 700; font-size: 0.78rem; white-space: nowrap;
    }}
    .gn-step {{
        display: inline-flex; align-items: center; justify-content: center;
        width: 26px; height: 26px; border-radius: 50%; background: {GREEN};
        color: {NAVY}; font-weight: 800; font-size: 0.85rem; margin-right: 10px; flex: 0 0 26px;
    }}
    .gn-steprow {{ display: flex; align-items: flex-start; margin: 0.55rem 0; }}
    .gn-steprow .body {{ color: {CHARCOAL}; font-size: 0.95rem; }}

    /* ---------- Links & buttons ---------- */
    .stMarkdown a {{ color: #1D7A8C !important; font-weight: 600; text-decoration: none; }}
    .stMarkdown a:hover {{ color: {NAVY} !important; text-decoration: underline; }}

    .stButton > button[kind="primary"], .stFormSubmitButton > button, .stDownloadButton > button {{
        background-color: {GREEN} !important; color: {NAVY} !important;
        border: none !important; font-weight: 700 !important; border-radius: 8px !important;
    }}
    .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {{
        background-color: {GREEN_DARK} !important; color: {NAVY} !important;
    }}
    .stButton > button[kind="secondary"] {{
        border: 1.5px solid {NAVY} !important; color: {NAVY} !important;
        font-weight: 700 !important; border-radius: 8px !important; background: white !important;
    }}

    hr {{ border-color: #E5E9EB !important; }}

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab"] {{ font-weight: 700; color: {SLATE}; }}
    .stTabs [aria-selected="true"] {{ color: {NAVY} !important; }}
    .stTabs [data-baseweb="tab-highlight"] {{ background-color: {GREEN} !important; }}

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {NAVY} 0%, {NAVY_DARK} 100%);
    }}
    [data-testid="stSidebar"] * {{ color: rgba(255,255,255,0.92) !important; }}
    [data-testid="stSidebar"] a:hover {{ color: {GREEN} !important; }}
    [data-testid="stSidebarNav"] a {{ font-weight: 600; font-size: 0.92rem; }}
    [data-testid="stSidebarNav"] a[aria-current="page"] {{
        background: rgba(171,207,56,0.16); border-radius: 8px;
    }}
    [data-testid="stSidebarNav"] a[aria-current="page"] span {{ color: {GREEN} !important; }}

    /* Hide Streamlit chrome */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)


def sidebar_brand():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1.1rem 0 0.6rem;text-align:center;">
            <div style="font-size:1.45rem;font-weight:900;letter-spacing:0.16em;color:#FFFFFF;">
                GENASYS<span style="color:{GREEN};">.</span>
            </div>
            <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:{TEAL} !important;margin-top:2px;">
                Funding Intelligence
            </div>
            <div style="font-size:0.7rem;opacity:0.65;margin-top:4px;">Ready when it matters</div>
        </div>
        <hr style="border-color:rgba(255,255,255,0.15);margin:0.4rem 0 0.6rem;">
        """, unsafe_allow_html=True)


def page_header(kicker: str, title: str, subtitle: str = ""):
    sub = f'<p class="gn-subtitle">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div class="gn-kicker">{kicker}</div>
    <div class="gn-title">{title}</div>
    {sub}
    <div class="gn-rule"></div>
    """, unsafe_allow_html=True)


def hero(kicker: str, title_html: str, subtitle: str):
    st.markdown(f"""
    <div class="gn-hero">
        <div class="gn-kicker">{kicker}</div>
        <h1>{title_html}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def pill(text: str, fg: str, bg: str) -> str:
    return f'<span class="gn-pill" style="background:{bg};color:{fg};">{text}</span>'


def status_badge(status: str) -> str:
    key = str(status).upper().strip()
    for k, (fg, bg) in STATUS_COLORS.items():
        if key.startswith(k):
            return pill(status, fg, bg)
    return pill(status, "#6B7280", "#F3F4F6")


def tier_badge(tier: str) -> str:
    label = tier.split(" - ")[0] if " - " in str(tier) else str(tier)
    fg, bg = TIER_COLORS.get(str(tier), ("#6B7280", "#F3F4F6"))
    return pill(label, fg, bg)


def score_pill(score) -> str:
    try:
        val = float(score)
    except (ValueError, TypeError):
        return str(score)
    if val >= 8:
        fg, bg = "#B91C1C", "#FEE2E2"
    elif val >= 5:
        fg, bg = "#A16207", "#FEF9C3"
    else:
        fg, bg = "#15803D", "#DCFCE7"
    return pill(f"{val:g}", fg, bg)


def metric_card(label: str, value: str, detail: str = "") -> str:
    detail_html = f'<div class="detail">{detail}</div>' if detail else ""
    return f'<div class="gn-metric"><div class="label">{label}</div><div class="value">{value}</div>{detail_html}</div>'


def steps_html(steps: list) -> str:
    rows = "".join(
        f'<div class="gn-steprow"><span class="gn-step">{i+1}</span><span class="body">{s}</span></div>'
        for i, s in enumerate(steps)
    )
    return rows
