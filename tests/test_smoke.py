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


@pytest.mark.parametrize("page", PAGES, ids=[os.path.basename(p) for p in PAGES])
def test_page_renders(page):
    at = _run(page)
    assert not at.exception, f"{os.path.basename(page)} raised: {at.exception}"


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
