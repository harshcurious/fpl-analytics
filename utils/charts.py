import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List


def create_form_trend_chart(
    df: pd.DataFrame, player_ids: List[int], player_names: List[str]
) -> go.Figure:
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No form data available")
        return fig

    fig = go.Figure()

    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

    for i, player_id in enumerate(player_ids):
        player_data = df[df["player_id"] == player_id].sort_values("gameweek")

        if not player_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=player_data["gameweek"],
                    y=player_data["total_points"],
                    mode="lines+markers",
                    name=player_names[i]
                    if i < len(player_names)
                    else f"Player {player_id}",
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8),
                )
            )

    fig.update_layout(
        title="Player Form Trend (Points per Gameweek)",
        xaxis_title="Gameweek",
        yaxis_title="Points",
        hovermode="x unified",
        template="plotly_white",
        height=400,
    )

    return fig


def create_points_distribution_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty or "position_name" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig

    fig = px.box(
        df,
        x="position_name",
        y="total_points",
        color="position_name",
        title="Points Distribution by Position",
        template="plotly_white",
    )

    fig.update_layout(xaxis_title="Position", yaxis_title="Total Points", height=400)

    return fig


def create_value_vs_points_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig

    fig = px.scatter(
        df,
        x="price",
        y="total_points",
        color="position_name",
        hover_name="web_name",
        size="form",
        title="Value vs Points (size = form)",
        template="plotly_white",
        color_discrete_map={
            "Goalkeeper": "#FFD93D",
            "Defender": "#6BCB77",
            "Midfielder": "#4D96FF",
            "Forward": "#FF6B6B",
        },
    )

    fig.update_layout(xaxis_title="Price (£m)", yaxis_title="Total Points", height=500)

    return fig


def create_xg_xa_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig

    fig = px.scatter(
        df,
        x="xG",
        y="xA",
        color="position_name",
        hover_name="web_name",
        size="total_points",
        title="Expected Goals vs Expected Assists",
        template="plotly_white",
        color_discrete_map={
            "Goalkeeper": "#FFD93D",
            "Defender": "#6BCB77",
            "Midfielder": "#4D96FF",
            "Forward": "#FF6B6B",
        },
    )

    fig.update_layout(
        xaxis_title="Expected Goals (xG)",
        yaxis_title="Expected Assists (xA)",
        height=500,
    )

    return fig


def create_radar_chart(player_data: pd.DataFrame, player_name: str) -> go.Figure:
    if player_data.empty:
        fig = go.Figure()
        fig.update_layout(title="No player data available")
        return fig

    categories = ["Goals", "Assists", "Clean Sheets", "Bonus", "xG", "xA"]

    values = [
        player_data.get("goals_scored", 0).iloc[0] if not player_data.empty else 0,
        player_data.get("assists", 0).iloc[0] if not player_data.empty else 0,
        player_data.get("clean_sheets", 0).iloc[0] if not player_data.empty else 0,
        player_data.get("bonus", 0).iloc[0] if not player_data.empty else 0,
        player_data.get("xG", 0).iloc[0] if not player_data.empty else 0,
        player_data.get("xA", 0).iloc[0] if not player_data.empty else 0,
    ]

    values += values[:1]
    angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
    angles += angles[:1]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=angles,
            fill="toself",
            name=player_name,
            line_color="#4ECDC4",
            fillcolor="rgba(78, 205, 196, 0.3)",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
            )
        ),
        showlegend=True,
        title=f"{player_name} - Performance Radar",
        height=400,
    )

    return fig


def create_fdr_heatmap(fixtures_df: pd.DataFrame, teams: List[str]) -> go.Figure:
    if fixtures_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No fixture data available")
        return fig

    pivot_data = fixtures_df.pivot_table(
        index="team", columns="gameweek", values="difficulty", aggfunc="first"
    ).fillna(0)

    colorscale = [
        [0, "#6BCB77"],
        [0.25, "#96CEB4"],
        [0.5, "#FFEAA7"],
        [0.75, "#FF6B6B"],
        [1, "#C0392B"],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale=colorscale,
            text=pivot_data.values,
            texttemplate="%{text}",
            textfont={"size": 12},
        )
    )

    fig.update_layout(
        title="Fixture Difficulty Rating (FDR) Heatmap",
        xaxis_title="Gameweek",
        yaxis_title="Team",
        height=max(400, len(teams) * 20),
    )

    return fig


def create_comparison_bar_chart(
    df: pd.DataFrame, players: List[str], metric: str
) -> go.Figure:
    if df.empty or not players:
        fig = go.Figure()
        fig.update_layout(title="No comparison data available")
        return fig

    player_data = df[df["web_name"].isin(players)]

    if player_data.empty:
        fig = go.Figure()
        fig.update_layout(title="Players not found")
        return fig

    fig = px.bar(
        player_data,
        x="web_name",
        y=metric,
        color="position_name",
        title=f"Player Comparison - {metric}",
        template="plotly_white",
        color_discrete_map={
            "Goalkeeper": "#FFD93D",
            "Defender": "#6BCB77",
            "Midfielder": "#4D96FF",
            "Forward": "#FF6B6B",
        },
    )

    fig.update_layout(xaxis_title="Player", yaxis_title=metric, height=400)

    return fig
