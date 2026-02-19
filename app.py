import streamlit as st
import pandas as pd
from data.fetch_api import get_client
from data.load_csv import get_csv_loader
from utils.filters import filter_players, create_filter_sidebar, get_best_value_players
from utils.charts import (
    create_form_trend_chart,
    create_points_distribution_chart,
    create_value_vs_points_scatter,
    create_xg_xa_chart,
    create_radar_chart,
    create_fdr_heatmap,
    create_comparison_bar_chart,
)

st.set_page_config(
    page_title="FPL Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=3600)
def load_player_data():
    client = get_client()
    return client.get_players_df()


@st.cache_data(ttl=3600)
def load_team_data():
    client = get_client()
    return client.get_teams_df()


@st.cache_data(ttl=3600)
def load_gameweek_data():
    client = get_client()
    return client.get_gameweeks()


def main():
    st.title("⚽ FPL Analytics Hub")
    st.markdown(
        "### Analyze and select the best players for your Fantasy Premier League team"
    )

    with st.spinner("Loading FPL data..."):
        players_df = load_player_data()
        teams_df = load_team_data()
        gameweeks_df = load_gameweek_data()

    if players_df.empty:
        st.error("Failed to load FPL data. Please check your internet connection.")
        return

    st.sidebar.success(f"Loaded {len(players_df)} players")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Player Tables",
            "📈 Interactive Charts",
            "⚔️ Player Comparison",
            "👥 Team Analysis",
            "📅 Fixture Difficulty",
        ]
    )

    with tab1:
        st.header("Player Database")

        (
            selected_positions,
            selected_teams,
            price_min,
            price_max,
            min_points,
            min_form,
            search,
        ) = create_filter_sidebar(players_df)

        filtered_df = filter_players(
            players_df,
            positions=selected_positions,
            teams=selected_teams,
            price_min=price_min,
            price_max=price_max,
            points_min=min_points,
            form_min=min_form,
            search_name=search,
        )

        st.metric("Players Found", len(filtered_df))

        display_cols = [
            "web_name",
            "position_name",
            "team_name",
            "price",
            "form",
            "total_points",
            "points_per_million",
            "goals_scored",
            "assists",
            "xG",
            "xA",
        ]

        available_cols = [col for col in display_cols if col in filtered_df.columns]

        display_df = filtered_df[available_cols].copy()
        for col in display_df.columns:
            if display_df[col].dtype == "object":
                display_df[col] = display_df[col].astype(str)

        st.dataframe(
            display_df.style.background_gradient(
                subset=["total_points", "form", "points_per_million"], cmap="Greens"
            ),
            width="stretch",
            height=600,
            hide_index=True,
        )

        st.subheader("Best Value Players")
        best_value = get_best_value_players(filtered_df, min_minutes=450)
        if not best_value.empty:
            st.dataframe(
                best_value[
                    [
                        "web_name",
                        "position_name",
                        "team_name",
                        "price",
                        "total_points",
                        "points_per_million",
                    ]
                ],
                width="stretch",
                hide_index=True,
            )

    with tab2:
        st.header("Interactive Charts")

        chart_type = st.selectbox(
            "Select Chart Type",
            ["Points Distribution", "Value vs Points", "xG vs xA", "Form Trend"],
        )

        if chart_type == "Points Distribution":
            fig = create_points_distribution_chart(players_df)
            st.plotly_chart(fig, width="stretch")

        elif chart_type == "Value vs Points":
            fig = create_value_vs_points_scatter(players_df)
            st.plotly_chart(fig, width="stretch")

        elif chart_type == "xG vs xA":
            fig = create_xg_xa_chart(players_df)
            st.plotly_chart(fig, width="stretch")

        elif chart_type == "Form Trend":
            st.subheader("Select Players for Form Trend")

            col1, col2 = st.columns(2)
            with col1:
                selected_player_1 = st.selectbox(
                    "Player 1", players_df["web_name"].tolist(), index=0
                )
            with col2:
                selected_player_2 = st.selectbox(
                    "Player 2 (optional)",
                    ["None"] + players_df["web_name"].tolist(),
                    index=0,
                )

            player_ids = []
            player_names = []

            p1_id = players_df[players_df["web_name"] == selected_player_1]["id"].iloc[
                0
            ]
            player_ids.append(p1_id)
            player_names.append(selected_player_1)

            if selected_player_2 != "None":
                p2_id = players_df[players_df["web_name"] == selected_player_2][
                    "id"
                ].iloc[0]
                player_ids.append(p2_id)
                player_names.append(selected_player_2)

            csv_loader = get_csv_loader("data")
            gw_stats = csv_loader.load_gameweek_stats()

            fig = create_form_trend_chart(gw_stats, player_ids, player_names)
            st.plotly_chart(fig, width="stretch")

    with tab3:
        st.header("Player Comparison Tool")

        col1, col2, col3 = st.columns(3)

        with col1:
            player1 = st.selectbox("Player 1", players_df["web_name"].tolist(), index=0)
        with col2:
            player2 = st.selectbox(
                "Player 2",
                players_df["web_name"].tolist(),
                index=1 if len(players_df) > 1 else 0,
            )
        with col3:
            player3 = st.selectbox(
                "Player 3 (optional)",
                ["None"] + players_df["web_name"].tolist(),
                index=0,
            )

        selected_players = [player1, player2]
        if player3 != "None":
            selected_players.append(player3)

        comparison_df = players_df[players_df["web_name"].isin(selected_players)]

        st.subheader("Comparison Table")

        compare_cols = [
            "web_name",
            "position_name",
            "team_name",
            "price",
            "total_points",
            "goals_scored",
            "assists",
            "clean_sheets",
            "bonus",
            "xG",
            "xA",
        ]
        available_compare_cols = [
            col for col in compare_cols if col in comparison_df.columns
        ]

        st.dataframe(
            comparison_df[available_compare_cols].set_index("web_name").T,
            width="stretch",
        )

        st.subheader("Visual Comparison")

        metric = st.selectbox(
            "Select Metric to Compare",
            [
                "total_points",
                "goals_scored",
                "assists",
                "xG",
                "xA",
                "form",
                "points_per_million",
            ],
        )

        fig = create_comparison_bar_chart(players_df, selected_players, metric)
        st.plotly_chart(fig, width="stretch")

        st.subheader("Performance Radar")

        for player in selected_players:
            player_data = players_df[players_df["web_name"] == player]
            if not player_data.empty:
                fig = create_radar_chart(player_data, player)
                st.plotly_chart(fig, width="stretch")

    with tab4:
        st.header("Team Analysis")

        st.info("Enter your FPL team by selecting players")

        if "team_players" not in st.session_state:
            st.session_state.team_players = []

        available_players = [
            p
            for p in players_df["web_name"].tolist()
            if p not in st.session_state.team_players
        ]

        col1, col2 = st.columns([2, 1])

        with col1:
            new_player = st.selectbox(
                "Add player to your team",
                available_players,
                index=0 if available_players else 0,
            )

        with col2:
            if st.button("Add Player") and new_player:
                st.session_state.team_players.append(new_player)
                st.rerun()

        if st.session_state.team_players:
            team_df = players_df[
                players_df["web_name"].isin(st.session_state.team_players)
            ]

            st.subheader("Your Team")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Players", len(team_df))
            with col2:
                total_cost = team_df["price"].sum()
                st.metric("Total Cost", f"£{total_cost:.1f}m")
            with col3:
                total_points = team_df["total_points"].sum()
                st.metric("Total Points", total_points)
            with col4:
                avg_form = team_df["form"].mean()
                st.metric("Avg Form", f"{avg_form:.1f}")

            st.subheader("Team Breakdown by Position")
            pos_counts = team_df["position_name"].value_counts()
            st.write(pos_counts.to_dict())

            st.subheader("Transfer Suggestions")

            budget = 15.0
            st.markdown(f"**Transfer Budget: £{budget}m**")

            suggestions = players_df[
                (players_df["price"] <= budget)
                & (~players_df["web_name"].isin(st.session_state.team_players))
            ].nlargest(5, "form")

            st.write("Top 5 players to consider (based on form):")
            st.dataframe(
                suggestions[
                    [
                        "web_name",
                        "position_name",
                        "team_name",
                        "price",
                        "form",
                        "total_points",
                    ]
                ],
                width="stretch",
                hide_index=True,
            )

            if st.button("Clear Team"):
                st.session_state.team_players = []
                st.rerun()
        else:
            st.warning("Add players to your team to see analysis")

    with tab5:
        st.header("Fixture Difficulty Tracker")

        if teams_df.empty:
            st.error("Team data not available")
        else:
            team_list = teams_df["name"].tolist()
            selected_team = st.selectbox("Select Team", team_list)

            team_id = teams_df[teams_df["name"] == selected_team]["id"].iloc[0]

            client = get_client()
            fixtures = client.get_fixtures_with_fdr(team_id, num_gameweeks=5)

            if not fixtures.empty:
                st.subheader(f"{selected_team} - Next 5 Gameweeks")

                def get_difficulty_color(difficulty):
                    colors = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "⚫"}
                    return colors.get(difficulty, "⚪")

                display_fixtures = []
                for _, row in fixtures.iterrows():
                    display_fixtures.append(
                        {
                            "Gameweek": row["gameweek"],
                            "Opponent": row["opponent"],
                            "Venue": row["home_away"],
                            "Difficulty": f"{get_difficulty_color(row['difficulty'])} {row['fdr']} ({row['difficulty']})",
                        }
                    )

                st.table(pd.DataFrame(display_fixtures))

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Difficulty Distribution")
                    difficulty_counts = fixtures["fdr"].value_counts()
                    st.write(difficulty_counts)

                with col2:
                    st.subheader("Home vs Away")
                    venue_counts = fixtures["home_away"].value_counts()
                    st.write(venue_counts)
            else:
                st.warning("No upcoming fixtures available")

            st.subheader("All Teams Fixture Difficulty")

            all_fdr_data = []
            for _, team in teams_df.iterrows():
                team_fixtures = client.get_fixtures_with_fdr(
                    team["id"], num_gameweeks=5
                )
                if not team_fixtures.empty:
                    avg_difficulty = team_fixtures["difficulty"].mean()
                    all_fdr_data.append(
                        {
                            "team": team["short_name"],
                            "gameweek_1": team_fixtures.iloc[0]["difficulty"]
                            if len(team_fixtures) > 0
                            else 0,
                            "gameweek_2": team_fixtures.iloc[1]["difficulty"]
                            if len(team_fixtures) > 1
                            else 0,
                            "gameweek_3": team_fixtures.iloc[2]["difficulty"]
                            if len(team_fixtures) > 2
                            else 0,
                            "gameweek_4": team_fixtures.iloc[3]["difficulty"]
                            if len(team_fixtures) > 3
                            else 0,
                            "gameweek_5": team_fixtures.iloc[4]["difficulty"]
                            if len(team_fixtures) > 4
                            else 0,
                            "avg_difficulty": avg_difficulty,
                        }
                    )

            if all_fdr_data:
                fdr_df = pd.DataFrame(all_fdr_data)
                fdr_df = fdr_df.sort_values("avg_difficulty")

                st.dataframe(
                    fdr_df.style.background_gradient(
                        subset=["avg_difficulty"], cmap="RdYlGn_r"
                    ),
                    width="stretch",
                    hide_index=True,
                )


if __name__ == "__main__":
    main()
