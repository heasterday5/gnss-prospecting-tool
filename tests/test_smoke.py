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
