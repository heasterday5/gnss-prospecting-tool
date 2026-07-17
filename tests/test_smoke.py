"""Smoke tests: every page renders without exceptions; Start Here builds a dossier.

Run:  python3 -m pytest tests/ -q
"""

import glob
import os

import pytest
from streamlit.testing.v1 import AppTest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = sorted(glob.glob(os.path.join(ROOT, "pages", "*.py"))) + [os.path.join(ROOT, "app.py")]


def _run(path, **session):
    at = AppTest.from_file(path, default_timeout=30)
    at.session_state["authenticated"] = True
    for k, v in session.items():
        at.session_state[k] = v
    at.run()
    return at


def _assert_html_markdown_safe(at, ctx=""):
    """HTML passed to st.markdown must contain no blank lines (they end the
    raw-HTML block) and no 4-space-indented lines (code block after a blank).
    md_html() guarantees this; this guards every render path."""
    for m in at.markdown:
        v = str(m.value)
        if not v.lstrip().startswith("<"):
            continue
        lines = v.splitlines()
        assert not any(not ln.strip() for ln in lines), \
            f"{ctx}: blank/whitespace-only line inside HTML markdown: {v[:120]!r}"
        assert not any(ln.startswith("    ") for ln in lines), \
            f"{ctx}: 4-space-indented line inside HTML markdown: {v[:120]!r}"


@pytest.mark.parametrize("page", PAGES, ids=[os.path.basename(p) for p in PAGES])
def test_page_renders(page):
    at = _run(page)
    assert not at.exception, f"{os.path.basename(page)} raised: {at.exception}"
    _assert_html_markdown_safe(at, os.path.basename(page))


def test_start_here_builds_dossier():
    page = os.path.join(ROOT, "pages", "0_Start_Here.py")
    at = _run(page)
    # type an account with state + county + segment embedded
    at.text_input[0].set_value("Sacramento County OES, California").run()
    assert not at.exception

    body = "\n".join(str(m.value) for m in at.markdown)
    body += "\n".join(str(c.value) for c in at.caption)
    # auto-guess picked up state and county
    assert "06067" in body, "Sacramento County FIPS should appear in the risk section"
    # deterministic deep links present
    assert "experience.arcgis.com" in body, "RAPT link missing"
    assert "fema.gov/disaster/declarations?field_dv2_state_territory_tribal_value=CA" in body
    assert "atsdr.cdc.gov" in body, "SVI link missing"
    assert "google.com/search?q=" in body, "pre-built plan searches missing"
    assert "hazard+mitigation+plan" in body.replace("%22", ""), "HMP search missing"
    assert "030425-gys" in body.lower(), "Sourcewell contract link missing"
    # funding layer rendered from the recommend engine
    assert "Layer 1" in body and "Layer 2" in body and "Layer 3" in body


def test_start_here_segment_guess():
    page = os.path.join(ROOT, "pages", "0_Start_Here.py")
    at = _run(page)
    at.text_input[0].set_value("City of Boulder Fire Department, Colorado").run()
    assert not at.exception
    # segment selectbox should have auto-guessed Fire / EMS
    assert at.selectbox[1].value == "Fire / EMS Departments" or \
           at.selectbox[2].value == "Fire / EMS Departments"


def test_pathfinder_prefill_from_session():
    page = os.path.join(ROOT, "pages", "1_Funding_Pathfinder.py")
    at = _run(page, pf_dept="Fire / EMS Departments", pf_state="Colorado")
    assert not at.exception
    assert at.selectbox[0].value == "Fire / EMS Departments"
    assert at.selectbox[1].value == "Colorado"


def test_start_here_people_section():
    page = os.path.join(ROOT, "pages", "0_Start_Here.py")
    at = _run(page)
    at.text_input[0].set_value("Sacramento County Sheriff, California").run()
    assert not at.exception
    body = "\n".join(str(m.value) for m in at.markdown)
    # sheriff ladder should fire (account contains 'sheriff')
    assert "Undersheriff" in body, "Sheriff ladder should render for sheriff accounts"
    assert "linkedin.com/search/results/people" in body, "LinkedIn deep links missing"
    assert "highest rank" in body.lower(), "rank-order rule missing"


def test_start_here_police_ladder_order():
    """The BDR hierarchy: Chief first, divisions intact, highest→lowest."""
    page = os.path.join(ROOT, "pages", "0_Start_Here.py")
    at = _run(page)
    at.text_input[0].set_value("City of Fresno Police Department, California").run()
    assert not at.exception
    body = "\n".join(str(m.value) for m in at.markdown)
    for needle in ["Administration", "Patrol / Operations", "CID / Investigations"]:
        assert needle in body, f"division '{needle}' missing from police ladder"
    assert body.find("Chief") < body.find("Detectives"), "rank order broken"


def test_live_research_parser():
    """The live-research JSON extractor must survive prose-wrapped and fenced output."""
    from utils.live_research import _parse_result
    fenced = 'Here is what I found.\n```json\n{"agency": {"official_name": "X"}, "contacts": []}\n```\nDone.'
    assert _parse_result(fenced)["agency"]["official_name"] == "X"
    bare = 'Result: {"agency": {"official_name": "Y"}, "contacts": [{"name": "A"}]} trailing'
    assert _parse_result(bare)["contacts"][0]["name"] == "A"


def test_landscape_data_integrity():
    """Deployments/incidents rows must geocode against counties.csv county names."""
    import pandas as pd
    counties = pd.read_csv(os.path.join(ROOT, "data", "counties.csv"))
    valid = set(zip(counties["state"], counties["county"]))

    dep = pd.read_csv(os.path.join(ROOT, "data", "deployments.csv"))
    bad = [(r.state, r.county) for r in dep.itertuples() if (r.state, r.county) not in valid]
    assert not bad, f"deployments.csv rows that won't geocode: {bad[:8]}"
    assert (dep["vendor"].astype(str).str.len() > 0).all()

    inc = pd.read_csv(os.path.join(ROOT, "data", "incidents.csv"))
    bad = [(r.state, r.county) for r in inc.itertuples() if (r.state, r.county) not in valid]
    assert not bad, f"incidents.csv rows that won't geocode: {bad[:8]}"
    assert inc["year"].between(2000, 2026).all(), "incident years out of range"


def test_find_potential_focus_renders_icp():
    page = os.path.join(ROOT, "pages", "2_Find_Potential_Focus.py")
    at = _run(page)
    assert not at.exception
    body = "\n".join(str(m.value) for m in at.markdown)
    labels = at.selectbox[1].options
    assert "Fire & Emergency Management" in labels
    assert "Law Enforcement" in labels
    assert "Military & Defense" in labels
    assert "Enterprise — Critical Infrastructure" in labels
    # without an API key the setup card shows (never silently hidden)
    assert "live-research connection" in body or "Build the" in body
    # product dropdown present with all four products, segment-appropriate default
    ms = at.multiselect[0]
    assert set(ms.options) == {"Evertel", "Protect", "Acoustics", "LRAD"}
    assert ms.value == ["Protect", "Acoustics"], "Fire & EM should default to Protect + Acoustics"


def test_find_potential_focus_le_defaults():
    page = os.path.join(ROOT, "pages", "2_Find_Potential_Focus.py")
    at = _run(page)
    at.selectbox[1].set_value("Law Enforcement").run()
    assert not at.exception
    assert at.multiselect[0].value == ["Evertel", "LRAD"], \
        "Law Enforcement should default to Evertel + LRAD"


def test_resource_links_page():
    page = os.path.join(ROOT, "pages", "11_Resource_Links.py")
    at = _run(page)
    assert not at.exception
    body = "\n".join(str(m.value) for m in at.markdown)
    assert "govspend.com" in body.lower()
    assert "030425-gys" in body.lower()
    assert "hubspot.com" in body.lower()


def test_icp_profiles_valid():
    import json
    icps = json.load(open(os.path.join(ROOT, "data", "icp_profiles.json")))
    assert len(icps) == 5
    for p in icps:
        assert p["best_fit"] and p["caution_signals"] and p["decision_makers"]
        assert p["funding_segment"], f"{p['id']} missing funding_segment"


def test_router_navigation():
    at = _run(os.path.join(ROOT, "app.py"))
    assert not at.exception


def test_research_functions_not_cache_data_wrapped():
    """research_account/find_prospects stream progress into caller-owned
    st.status blocks — st.cache_data replay forbids that (crashes on 1.39+).
    They must use the shared cache_resource store instead."""
    import inspect
    from utils import live_research, live_prospecting
    for fn in (live_research.research_account, live_prospecting.find_prospects):
        assert not hasattr(fn, "clear"), f"{fn.__name__} is st.cache_data-wrapped again"
        assert "cache_get" in inspect.getsource(fn), f"{fn.__name__} lost its result cache"
        assert "cache_put" in inspect.getsource(fn), f"{fn.__name__} lost its result cache"


def test_fpf_dirty_model_text_renders_safely(monkeypatch):
    """Model output with newlines/HTML must not break card rendering.

    Newlines inside interpolated fields defeat Streamlit's dedent, turning the
    indented card template into a literal markdown code block (the raw-HTML bug).
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-not-real")
    page = os.path.join(ROOT, "pages", "2_Find_Potential_Focus.py")
    dirty = {
        "market_notes": "line one\n\nline two",
        "prospects": [{
            "rank": 1, "name": "Wheeling-Ohio County HSEM", "county": "Ohio County",
            "population_served": "42,000", "fit_score": 95, "tier": "Prime",
            "why_fit": ["flood\nkilled eight people", "<script>alert(1)</script> declaration"],
            "caution_flags": ["pop under\n50k gate"],
            "incumbent": "Everbridge\n(statewide)",
            "recent_events": "June 2025 flood (8 dead);\nDR-4884",
            "product_angle": "Acoustics lead:\nvoice sirens",
            "source_urls": ["https://example.com/a", "javascript:alert(1)"],
        }, {
            # the "clean-looking" prospect that broke rendering: empty optional
            # fields left whitespace-only template lines -> markdown code block
            "rank": 2, "name": "Kanawha County EM", "county": "Kanawha County",
            "population_served": None, "fit_score": 88, "tier": "Strong",
            "why_fit": [], "caution_flags": [], "incumbent": None,
            "recent_events": None, "product_angle": "", "source_urls": [],
        }],
    }
    at = AppTest.from_file(page, default_timeout=30)
    at.session_state["authenticated"] = True
    at.session_state["fpf::Texas::fire_em::Acoustics+Protect"] = dirty
    at.run()
    assert not at.exception
    body = "\n".join(str(m.value) for m in at.markdown)
    assert "Wheeling-Ohio County HSEM" in body
    assert "Kanawha County EM" in body
    # newlines collapsed → dedent survives → no code-block regression
    assert "flood killed eight people" in body
    assert "line one line two" in body
    # model HTML escaped, hostile URL neutralized
    assert "<script>" not in body
    assert 'href="javascript:' not in body and "href='javascript:" not in body
    # the structural invariant: no blank or indented lines in any HTML block
    _assert_html_markdown_safe(at, "fpf dirty data")
