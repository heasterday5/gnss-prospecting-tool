"""Cached data loading for all datasets."""

import json
import os
import pandas as pd
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


@st.cache_data
def load_states() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(DATA_DIR, "states.csv"))
    return df


@st.cache_data
def load_cities() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(DATA_DIR, "cities.csv"))
    return df


@st.cache_data
def load_funding() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(DATA_DIR, "funding_programs.csv"))
    return df


@st.cache_data
def load_department_types() -> list[dict]:
    with open(os.path.join(DATA_DIR, "department_types.json")) as f:
        return json.load(f)


@st.cache_data
def load_global_targets() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(DATA_DIR, "global_targets.csv"))
    return df


@st.cache_data
def load_state_grants() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(DATA_DIR, "state_grant_directory.csv"))
    return df


@st.cache_data
def load_metrics() -> dict:
    with open(os.path.join(DATA_DIR, "metrics.json")) as f:
        return json.load(f)


def load_tracker() -> pd.DataFrame:
    """Load tracker (not cached since it can be modified)."""
    path = os.path.join(DATA_DIR, "tracker.csv")
    return pd.read_csv(path)


def save_tracker(df: pd.DataFrame):
    path = os.path.join(DATA_DIR, "tracker.csv")
    df.to_csv(path, index=False)
