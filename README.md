# FPL Analytics Hub

A comprehensive Fantasy Premier League analytics webapp built with Streamlit.

## Features

- **Player Tables with Filters**: Filter and sort players by position, team, price, form, and points
- **Interactive Charts**: Visualize player data with points distribution, value vs points, xG vs xA, and form trends
- **Player Comparison Tool**: Compare multiple players side-by-side with radar charts
- **Team Analysis**: Build and analyze your FPL team with transfer suggestions
- **Fixture Difficulty Tracker**: View upcoming fixtures with FDR for all teams

## Installation

1. Navigate to the project directory:
```bash
cd fpl-analytics
```
2. Install dependencies and create the environment automatically:
```bash
uv sync
```

## Usage

Run the Streamlit app:
```bash
uv run streamlit run app.py
```

The app will open in your browser at http://localhost:8501

## Optional: Add FPL Core Insights Data

For advanced stats, download FPL Core Insights CSV data from:
https://github.com/olbauday/FPL-Core-Insights

Place the data folders in `fpl-analytics/data/` with the naming convention:
```
data/2025-2026/player_stats.csv
data/2025-2026/team_stats.csv
data/2025-2026/team_elo.csv
data/2025-2026/fixture_difficulty.csv
data/2025-2026/player_gameweek_stats.csv
```

## Tech Stack

- **Streamlit**: Web framework
- **Pandas**: Data processing
- **Plotly**: Interactive charts
- **Requests**: FPL API integration

## Module Documentation

Detailed documentation for the project's core modules:

- **[Data Module](data/README.md)**: Details on API integration, data fetching, and caching strategies.
- **[Utils Module](utils/README.md)**: Documentation for charting functions and data filtering logic.
