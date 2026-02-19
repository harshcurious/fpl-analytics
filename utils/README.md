# Utils Module Documentation

This module contains utility functions for data visualization and filtering within the FPL Analytics application. It segregates logic for generating Plotly charts and processing DataFrame filters.

## Components

### 1. Charts (`charts.py`)

The `charts.py` module provides functions to generate interactive Plotly figures. These functions accept Pandas DataFrames and return `plotly.graph_objects.Figure` objects ready for rendering in Streamlit.

**Key Functions:**

- **Performance Analysis**:
    - `create_points_distribution_chart(df)`: Box plot of total points by position.
    - `create_value_vs_points_scatter(df)`: Scatter plot comparing price vs points, sized by form.
    - `create_form_trend_chart(df, player_ids, player_names)`: Line chart showing points history over gameweeks.

- **Advanced Metrics**:
    - `create_xg_xa_chart(df)`: Scatter plot of Expected Goals (xG) vs Expected Assists (xA).
    - `create_radar_chart(player_data, player_name)`: Radar chart comparing goals, assists, clean sheets, bonus, xG, and xA.
    - `create_comparison_bar_chart(df, players, metric)`: Bar chart comparing specific metrics across selected players.

- **Fixture Difficulty**:
    - `create_fdr_heatmap(fixtures_df, teams)`: Heatmap visualizing fixture difficulty over upcoming gameweeks.

**Usage Example:**

```python
import streamlit as st
from utils.charts import create_value_vs_points_scatter
from data.fetch_api import get_client

client = get_client()
df = client.get_players_df()

# Generate and display chart
fig = create_value_vs_points_scatter(df)
st.plotly_chart(fig)
```

### 2. Filters (`filters.py`)

The `filters.py` module handles the logic for filtering player data based on user inputs and generating the sidebar UI controls.

**Key Functions:**

- `create_filter_sidebar(df)`: Renders Streamlit sidebar widgets (sliders, multiselects) and returns the selected values.
- `filter_players(...)`: Applies the selected filters to the players DataFrame.
    - Supports filtering by: Position, Team, Price range, Minimum points, Minimum form, Name search.
- `get_best_value_players(df, min_minutes=450)`: Calculates points per million and returns top value players.

**Usage Example:**

```python
from utils.filters import filter_players

# Filter for budget midfielders with good form
filtered_df = filter_players(
    players_df,
    positions=['Midfielder'],
    price_max=6.5,
    form_min=5.0
)
```

## Directory Structure

```
utils/
├── charts.py   # Plotly visualization functions
├── filters.py  # Data filtering and UI controls
└── README.md   # This documentation
```
