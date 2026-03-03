"""Unified search across all datasets."""

import pandas as pd


def search_all(query: str, states: pd.DataFrame, cities: pd.DataFrame,
               funding: pd.DataFrame) -> dict:
    """Search states, cities, and funding programs. Returns dict of results."""
    if not query or not query.strip():
        return {"states": pd.DataFrame(), "cities": pd.DataFrame(), "funding": pd.DataFrame()}

    q = query.lower().strip()
    terms = q.split()

    def row_matches(row, cols):
        text = " ".join(str(row[c]).lower() for c in cols if c in row.index)
        return all(t in text for t in terms)

    # Search states
    state_cols = ["state", "key_hazards", "top_programs", "priority_tier"]
    state_mask = states.apply(lambda r: row_matches(r, state_cols), axis=1)
    state_results = states[state_mask]

    # Search cities
    city_cols = ["city_metro", "state", "primary_disaster_risk", "secondary_risks",
                 "target_dept_types", "primary_funding_programs", "priority_tier",
                 "recent_funding_notes"]
    city_mask = cities.apply(lambda r: row_matches(r, city_cols), axis=1)
    city_results = cities[city_mask]

    # Search funding
    fund_cols = ["program_name", "eligible_applicants", "key_eligible_uses",
                 "notes_strategy", "status"]
    fund_mask = funding.apply(lambda r: row_matches(r, fund_cols), axis=1)
    fund_results = funding[fund_mask]

    return {
        "states": state_results,
        "cities": city_results,
        "funding": fund_results,
    }
