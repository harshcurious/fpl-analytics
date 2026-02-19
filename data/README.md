# Data Module Documentation

This module handles all data fetching, loading, and caching for the FPL Analytics application. It provides interfaces for both the live Fantasy Premier League API and local CSV data sources.

## Components

### 1. FPL API Client (`fetch_api.py`)

The `FPLAPIClient` class is the main interface for interacting with the official Fantasy Premier League API. It handles:
- Fetching bootstrap static data (teams, players, events)
- Fetching player summaries and fixtures
- Processing raw API data into Pandas DataFrames
- Calculating derived metrics (e.g., specific form, difficulty ratings)
- Caching responses to minimize API calls and improve performance

**Key Methods:**

- `get_players_df(use_cache=True)`: Returns a processed DataFrame of all players with stats, including calculated columns like `points_per_million`.
- `get_teams_df(use_cache=True)`: Returns a DataFrame of all Premier League teams.
- `get_gameweeks(use_cache=True)`: Returns a DataFrame of gameweek information (deadlines, current status).
- `get_fixtures_with_fdr(team_id, num_gameweeks=5)`: Returns a DataFrame of upcoming fixtures for a specific team with Fixture Difficulty Ratings (FDR).

**Usage Example:**

```python
from data.fetch_api import get_client

client = get_client()

# Get all players
players_df = client.get_players_df()
print(players_df[['web_name', 'total_points', 'now_cost']].head())

# Get specific team's upcoming fixtures
fixtures = client.get_fixtures_with_fdr(team_id=1, num_gameweeks=5)
print(fixtures)
```

### 2. CSV Data Loader (`load_csv.py`)

The `FPLCoreInsightsLoader` class manages loading optional historical and advanced statistics from CSV files. This requires external data to be present in the `data/` directory (see main README for setup).

**Key Methods:**

- `load_player_stats(season=None)`: Loads detailed player stats for a season.
- `load_gameweek_stats(season=None, gameweek=None)`: Loads player stats broken down by gameweek.
- `get_player_form_trend(player_id, num_gw=5)`: Retrieves the last N gameweeks of formatted data for a specific player, useful for trend charts.

**Usage Example:**

```python
from data.load_csv import get_csv_loader

loader = get_csv_loader()

# Load stats for the latest available season
gw_stats = loader.load_gameweek_stats()

# Get form trend for a specific player (e.g., Haaland)
haaland_id = 355
trend = loader.get_player_form_trend(haaland_id)
print(trend)
```

### 3. Caching (`cache.py`)

The `DataCache` class implements a JSON-based file caching system. It stores API responses in the `.cache` directory to allow offline development and reduce load on the FPL API.

- **Storage**: JSON files hashed by key.
- **TTL**: Time-to-live expiration for cache entries (default 1 hour).
- **Metadata**: Tracks upstream timestamps to invalidate cache when source data changes (e.g., e-tags or last-modified dates).

## Directory Structure

```
data/
├── fetch_api.py  # FPL API integration
├── load_csv.py   # CSV data loading
├── cache.py      # Caching logic
└── README.md     # This documentation
```
