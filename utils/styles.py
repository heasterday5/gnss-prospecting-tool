"""Tier badges, score colors, CSS helpers."""

import streamlit as st

# Color constants
TIER_COLORS = {
    "Tier 1 - Immediate": ("#DC2626", "#FEE2E2"),       # red
    "Tier 2 - High Priority": ("#EA580C", "#FED7AA"),    # orange
    "Tier 3 - Medium Priority": ("#CA8A04", "#FEF9C3"),  # yellow
    "Tier 4 - Monitor": ("#16A34A", "#DCFCE7"),          # green
}

STATUS_COLORS = {
    "ACTIVE": ("#16A34A", "#DCFCE7"),
    "DELAYED": ("#CA8A04", "#FEF9C3"),
    "UNCERTAIN": ("#CA8A04", "#FEF9C3"),
    "CANCELED": ("#DC2626", "#FEE2E2"),
    "DISRUPTED": ("#DC2626", "#FEE2E2"),
}


def tier_badge(tier: str) -> str:
    label = tier.split(" - ")[0] if " - " in tier else tier
    fg, bg = TIER_COLORS.get(tier, ("#6B7280", "#F3F4F6"))
    return f'<span style="background:{bg};color:{fg};padding:2px 10px;border-radius:12px;font-weight:600;font-size:0.85em;white-space:nowrap;">{label}</span>'


def status_badge(status: str) -> str:
    key = status.upper().strip()
    # Handle partial matches like "ACTIVE (NY only)" or "ACTIVE (reauth pending)"
    for k in STATUS_COLORS:
        if key.startswith(k):
            fg, bg = STATUS_COLORS[k]
            return f'<span style="background:{bg};color:{fg};padding:2px 10px;border-radius:12px;font-weight:600;font-size:0.85em;">{status}</span>'
    fg, bg = "#6B7280", "#F3F4F6"
    return f'<span style="background:{bg};color:{fg};padding:2px 10px;border-radius:12px;font-weight:600;font-size:0.85em;">{status}</span>'


def score_color(score, as_bg=False) -> str:
    try:
        val = float(score)
    except (ValueError, TypeError):
        return "#6B7280"
    if val >= 8:
        return "#FEE2E2" if as_bg else "#DC2626"
    elif val >= 5:
        return "#FEF9C3" if as_bg else "#CA8A04"
    else:
        return "#DCFCE7" if as_bg else "#16A34A"


def score_pill(score) -> str:
    try:
        val = float(score)
    except (ValueError, TypeError):
        return str(score)
    fg = score_color(val)
    bg = score_color(val, as_bg=True)
    return f'<span style="background:{bg};color:{fg};padding:2px 8px;border-radius:8px;font-weight:700;font-size:0.9em;">{val}</span>'


def inject_css():
    st.markdown("""
    <style>
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1B2A4A 0%, #2563EB 100%);
        color: white; padding: 1.2rem; border-radius: 12px;
        text-align: center; height: 100%;
    }
    .metric-card .value { font-size: 1.8rem; font-weight: 800; margin: 0.3rem 0; }
    .metric-card .label { font-size: 0.85rem; opacity: 0.9; }
    .metric-card .detail { font-size: 0.75rem; opacity: 0.7; margin-top: 0.3rem; }

    /* Department cards */
    .dept-card {
        background: #F8FAFC; border: 1px solid #E2E8F0;
        border-radius: 12px; padding: 1.2rem; height: 100%;
        transition: box-shadow 0.2s;
    }
    .dept-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .dept-card h4 { color: #1B2A4A; margin: 0 0 0.5rem 0; }

    /* Funding card */
    .funding-card {
        background: white; border: 1px solid #E2E8F0;
        border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B2A4A 0%, #0F172A 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox label { color: rgba(255,255,255,0.8) !important; }
    </style>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, detail: str = "") -> str:
    detail_html = f'<div class="detail">{detail}</div>' if detail else ""
    return f"""
    <div class="metric-card">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        {detail_html}
    </div>
    """
