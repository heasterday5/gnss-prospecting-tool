"""Cached data loading for all datasets."""

import json
import os
import pandas as pd
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _read_json(name):
    with open(os.path.join(DATA_DIR, name)) as f:
        return json.load(f)


@st.cache_data
def load_states() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "states.csv"))


@st.cache_data
def load_cities() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "cities.csv"))


@st.cache_data
def load_funding() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "funding_programs.csv"))


@st.cache_data
def load_department_types() -> list:
    return _read_json("department_types.json")


@st.cache_data
def load_global_targets() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "global_targets.csv"))


@st.cache_data
def load_counties() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "counties.csv"), dtype={"fips": str})


@st.cache_data
def load_state_grants() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "state_grant_directory.csv"))


@st.cache_data
def load_contact_ladders() -> list:
    return _read_json("contact_ladders.json")


@st.cache_data
def load_deployments() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "deployments.csv"))


@st.cache_data
def load_incidents() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "incidents.csv"))


@st.cache_data
def load_em_directories() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "em_contact_directories.csv"))


@st.cache_data
def load_icp_profiles() -> list:
    return _read_json("icp_profiles.json")


@st.cache_data
def load_metrics() -> dict:
    return _read_json("metrics.json")


@st.cache_data
def load_signals() -> list:
    return _read_json("signals.json")


@st.cache_data
def load_email_templates() -> list:
    return _read_json("email_templates.json")


@st.cache_data
def load_personas() -> list:
    return _read_json("personas.json")


@st.cache_data
def load_trends() -> list:
    return _read_json("trends.json")


def get_template(template_id: str):
    for t in load_email_templates():
        if t["id"] == template_id:
            return t
    return None


def get_state_row(state: str):
    df = load_state_grants()
    row = df[df["State"].str.strip() == state]
    return row.iloc[0] if not row.empty else None
