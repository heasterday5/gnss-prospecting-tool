"""Funding recommendation engine.

Given who you're talking to (department type), where (state), and what you've
observed (signals), produce a ranked stack of funding programs with reasons.
"""

import pandas as pd
from utils.data_loader import load_funding, load_signals, load_states

# Department type → eligibility column in funding_programs.csv
DEPT_COL_MAP = {
    "Fire / EMS Departments": "fire_ems",
    "Police / Law Enforcement": "police",
    "Emergency Management Agencies": "emergency_mgmt",
    "Utilities (Power, Water, Gas)": "utilities",
    "Critical Infrastructure Operators": "critical_infra",
    "Cities / Counties / Municipalities": "cities_counties",
    "Events / Venues / Mass Gatherings": "events_venues",
    "Tribal Nations": "tribal",
    "Armed Forces / Military": None,  # DoD budget lines, not FEMA grants
}

STATUS_RANK = {"OPEN": 0, "ACTIVE": 1, "POST-DISASTER": 2, "DELAYED": 3, "UNCERTAIN": 4, "CANCELED": 5}


def recommend(dept_type: str, state: str, signal_ids: list) -> dict:
    """Return ranked program recommendations + the signal plays that fired."""
    funding = load_funding()
    signals = {s["id"]: s for s in load_signals()}
    fired = [signals[sid] for sid in signal_ids if sid in signals]

    # 1. Base eligibility from department type
    col = DEPT_COL_MAP.get(dept_type)
    if col and col in funding.columns:
        eligible_keys = set(funding[funding[col].astype(str).str.strip() == "X"]["program_key"])
    else:
        eligible_keys = set(funding["program_key"])

    # 2. Score: signal-recommended programs float to the top
    signal_votes = {}
    signal_reasons = {}
    for s in fired:
        for i, pk in enumerate(s.get("programs", [])):
            weight = 3 - min(i, 2)  # first-listed program gets the strongest vote
            signal_votes[pk] = signal_votes.get(pk, 0) + weight
            signal_reasons.setdefault(pk, []).append(s["label"])

    # 3. State priority programs get a nudge
    states_df = load_states()
    srow = states_df[states_df["state"] == state]
    state_programs = str(srow.iloc[0]["top_programs"]) if not srow.empty else ""

    recs = []
    for _, fp in funding.iterrows():
        pk = fp["program_key"]
        in_dept = pk in eligible_keys
        votes = signal_votes.get(pk, 0)
        if not in_dept and votes == 0:
            continue
        status = str(fp["status"]).upper()
        if status in ("CANCELED",) and votes == 0:
            continue
        state_match = pk.split("_")[0] in state_programs or str(fp["program_name"]).split(" ")[0] in state_programs
        score = votes * 10 + (4 if in_dept else 0) + (3 if state_match else 0) - STATUS_RANK.get(status, 3)
        if status == "OPEN":
            score += 15  # a live application window beats everything
        recs.append({
            "program": fp.to_dict(),
            "score": score,
            "signal_reasons": signal_reasons.get(pk, []),
            "dept_eligible": in_dept,
            "state_priority": state_match,
        })

    recs.sort(key=lambda r: r["score"], reverse=True)
    return {"recommendations": recs, "fired_signals": fired}
