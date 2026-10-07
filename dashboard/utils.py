"""Shared helpers for every dashboard page: data fetching, sidebar filters, formatting."""
import os
import sys
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # lets the dashboard import api.db for the fallback below
from api.db import run_query  # noqa: E402

API_URL = os.getenv("API_URL", "http://localhost:8000")

# dashboard key -> API route. The key is also the name of the SQL file.
ENDPOINTS = {
    "meta": "/meta", "kpis": "/kpis", "revenue_monthly": "/revenue/monthly",
    "top_products": "/products/top", "funnel": "/funnel", "cohort": "/cohorts",
    "retention": "/retention/summary", "rfm": "/rfm", "geography": "/geography",
    "delivery": "/delivery", "payments": "/payments",
}
GLOBAL_QUERIES = {"cohort", "rfm", "meta"}  # these queries ignore the sidebar filters


@st.cache_data(ttl=60, show_spinner=False)
def api_online() -> bool:
    try:
        return requests.get(f"{API_URL}/health", timeout=1.5).ok
    except requests.RequestException:
        return False


@st.cache_data(ttl=300, show_spinner=False)
def fetch(key: str, start=None, end=None, state=None, limit=10) -> pd.DataFrame:
    """Get data from the FastAPI backend; if it is unreachable, run the same SQL directly.

    The fallback means the dashboard also works on hosts where only Streamlit is deployed.
    """
    params = {k: v for k, v in {"start": start, "end": end, "state": state}.items() if v}
    if key == "top_products":
        params["limit"] = limit
    try:
        r = requests.get(f"{API_URL}{ENDPOINTS[key]}", params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException:
        data = run_query(key, params)
        if key == "top_products":
            data = data[:limit]
        if key in ("kpis", "retention"):
            data = data[0]
    return pd.DataFrame([data] if isinstance(data, dict) else data)


def setup(page_title: str, icon: str) -> dict:
    """Configure the page, draw the sidebar filters, and return them as a dict."""
    st.set_page_config(page_title=f"{page_title} | Product Analytics", page_icon=icon, layout="wide")
    meta = fetch("meta")
    states = sorted(meta[meta.kind == "state"].value)
    months = sorted(meta[meta.kind == "month"].value)
    st.sidebar.header("Filters")
    start, end = st.sidebar.select_slider("Period", options=months, value=(months[0], months[-1]))
    state = st.sidebar.selectbox("Customer state", ["All"] + states)
    st.sidebar.caption("Cohort & RFM pages always use the full history.")
    st.sidebar.divider()
    st.sidebar.caption("Data source: " + ("🟢 FastAPI backend" if api_online() else "🟡 direct database (API offline)"))
    return {"start": start, "end": end, "state": None if state == "All" else state}


def brl(x) -> str:
    """Format a number as Brazilian Real (the Olist currency)."""
    return "–" if pd.isna(x) else f"R$ {x:,.0f}"


def num(x) -> str:
    return "–" if pd.isna(x) else f"{x:,.0f}"
