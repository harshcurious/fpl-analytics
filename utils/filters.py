import pandas as pd
import streamlit as st
from typing import List, Optional, Tuple


def filter_players(
    df: pd.DataFrame,
    positions: Optional[List[str]] = None,
    teams: Optional[List[str]] = None,
    price_min: float = 0.0,
    price_max: float = 15.0,
    points_min: int = 0,
    form_min: float = 0.0,
    search_name: str = "",
) -> pd.DataFrame:
    if df.empty:
        return df

    filtered = df.copy()

    if positions and len(positions) > 0:
        filtered = filtered[filtered["position_name"].isin(positions)]

    if teams and len(teams) > 0:
        filtered = filtered[filtered["team_name"].isin(teams)]

    filtered = filtered[
        (filtered["price"] >= price_min) & (filtered["price"] <= price_max)
    ]

    if points_min > 0:
        filtered = filtered[filtered["total_points"] >= points_min]

    if form_min > 0:
        filtered = filtered[filtered["form"] >= form_min]

    if search_name:
        filtered = filtered[
            filtered["web_name"].str.lower().str.contains(search_name.lower())
            | filtered["second_name"].str.lower().str.contains(search_name.lower())
        ]

    return filtered


def create_filter_sidebar(
    df: pd.DataFrame,
) -> Tuple[List[str], List[str], float, float, int, float, str]:
    st.sidebar.header("Filters")

    positions = (
        df["position_name"].unique().tolist() if "position_name" in df.columns else []
    )
    teams = df["team_name"].unique().tolist() if "team_name" in df.columns else []

    selected_positions = st.sidebar.multiselect(
        "Positions", options=sorted(positions), default=[]
    )

    selected_teams = st.sidebar.multiselect("Teams", options=sorted(teams), default=[])

    price_range = st.sidebar.slider(
        "Price Range (£m)", min_value=0.0, max_value=15.0, value=(0.0, 15.0), step=0.1
    )

    min_points = st.sidebar.slider(
        "Minimum Total Points",
        min_value=0,
        max_value=int(df["total_points"].max()) if not df.empty else 500,
        value=0,
        step=10,
    )

    min_form = st.sidebar.slider(
        "Minimum Form", min_value=0.0, max_value=15.0, value=0.0, step=0.5
    )

    search = st.sidebar.text_input("Search Player", "")

    return (
        selected_positions,
        selected_teams,
        price_range[0],
        price_range[1],
        min_points,
        min_form,
        search,
    )


def get_top_performers(
    df: pd.DataFrame, metric: str = "total_points", n: int = 10
) -> pd.DataFrame:
    if df.empty or metric not in df.columns:
        return pd.DataFrame()

    return df.nlargest(n, metric)


def get_best_value_players(df: pd.DataFrame, min_minutes: int = 450) -> pd.DataFrame:
    if df.empty:
        return df

    filtered = df[df["minutes"] >= min_minutes].copy()

    if "points_per_match" in filtered.columns:
        return filtered.nlargest(20, "points_per_match")

    filtered["points_per_match"] = filtered["total_points"] / filtered["price"].replace(
        0, 1
    )
    return filtered.nlargest(20, "points_per_match")
