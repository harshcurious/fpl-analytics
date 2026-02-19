import requests
import pandas as pd
from typing import Dict, List, Optional
import time
from pathlib import Path
import os
import hashlib

from .cache import DataCache, cached_fetch


class FPLAPIClient:
    BASE_URL = "https://fantasy.premierleague.com/api"
    CACHE_DIR = Path(__file__).parent / ".cache"

    def __init__(self, use_cache: bool = True):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        self._cache = DataCache(str(self.CACHE_DIR)) if use_cache else None
        self._cached_bootstrap = None

    def _get(self, endpoint: str, retries: int = 3) -> Dict:
        url = f"{self.BASE_URL}/{endpoint}/"
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(2**attempt)
                else:
                    raise e
        return {}

    def get_bootstrap_static(self, use_cache: bool = True) -> Dict:
        if use_cache and self._cache:
            return cached_fetch(
                self._cache,
                "bootstrap_static_data",
                self._fetch_bootstrap,
                lambda: self._fetch_bootstrap_timestamp(),
            )
        return self._fetch_bootstrap()

    def _fetch_bootstrap(self) -> Dict:
        return self._get("bootstrap-static")

    def _fetch_bootstrap_timestamp(self) -> str:
        data = self._get("bootstrap-static")
        last_updated = data.get("last_updated")
        if last_updated:
            return last_updated
        return str(hashlib.md5(str(data.get("elements", [])[:1]).encode()).hexdigest())

    def get_player_summary(self, player_id: int) -> Dict:
        return self._get(f"element-summary/{player_id}")

    def get_team(self, team_id: int) -> Dict:
        return self._get(f"teams/{team_id}")

    def get_fixtures(
        self, team_id: Optional[int] = None, gameweek: Optional[int] = None
    ) -> List[Dict]:
        fixtures = self._get("fixtures")

        if team_id:
            fixtures = [
                f for f in fixtures if f["team_a"] == team_id or f["team_h"] == team_id
            ]
        if gameweek:
            fixtures = [f for f in fixtures if f.get("event") == gameweek]

        return fixtures

    def get_players_df(self, use_cache: bool = True) -> pd.DataFrame:
        if use_cache and self._cache:
            upstream_ts = self._cache.get_upstream_timestamp("bootstrap_static_data")
            cached_ts = self._cache.get_upstream_timestamp("players_df")

            if upstream_ts and cached_ts == upstream_ts:
                cached = self._cache.get("players_df")
                if cached is not None and isinstance(cached, pd.DataFrame):
                    return cached

        data = self.get_bootstrap_static(use_cache=use_cache)

        if not data or "elements" not in data:
            return pd.DataFrame()

        players = data["elements"]
        teams = {t["id"]: t["name"] for t in data.get("teams", [])}
        positions = {
            pt["id"]: pt["singular_name"] for pt in data.get("element_types", [])
        }

        df = pd.DataFrame(players)

        if df.empty:
            return df

        df["team_name"] = df["team"].map(teams)
        df["position_name"] = df["element_type"].map(positions)
        df["price"] = df["now_cost"] / 10

        numeric_cols = [
            "form",
            "total_points",
            "minutes",
            "goals_scored",
            "assists",
            "clean_sheets",
            "bonus",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            else:
                df[col] = 0

        optional_cols = {
            "expected_goals": "xG",
            "expected_assists": "xA",
            "threat": "threat",
            "creativity": "creativity",
            "influence": "influence",
            "selected_by_percent": "selected_by_percent",
            "transfers_in": "transfers_in",
            "transfers_out": "transfers_out",
            "value_change": "value_change",
            "chance_of_playing_next_round": "chance_of_playing_next_round",
        }

        for old_col, new_col in optional_cols.items():
            default = 100 if old_col == "chance_of_playing_next_round" else 0
            if old_col in df.columns:
                series = df[old_col]
                if hasattr(series, "apply"):
                    df[new_col] = pd.to_numeric(series, errors="coerce").fillna(default)
                else:
                    df[new_col] = default
            else:
                df[new_col] = default

        df["value"] = df["price"]
        df["points_per_million"] = df["total_points"] / df["price"].replace(0, 1)

        if use_cache and self._cache:
            self._cache.set(
                "players_df",
                df,
                upstream_timestamp=self._cache.get_upstream_timestamp(
                    "bootstrap_static_data"
                ),
            )

        return df

    def get_teams_df(self, use_cache: bool = True) -> pd.DataFrame:
        if use_cache and self._cache:
            upstream_ts = self._cache.get_upstream_timestamp("bootstrap_static_data")
            cached_ts = self._cache.get_upstream_timestamp("teams_df")

            if upstream_ts and cached_ts == upstream_ts:
                cached = self._cache.get("teams_df")
                if cached is not None and isinstance(cached, pd.DataFrame):
                    return cached

        data = self.get_bootstrap_static(use_cache=use_cache)
        if not data or "teams" not in data:
            return pd.DataFrame()

        teams = data["teams"]
        df = pd.DataFrame(teams)

        if not df.empty:
            df["name"] = df["name"].str.strip()
            df["short_name"] = df["short_name"].str.strip()

        if use_cache and self._cache:
            self._cache.set(
                "teams_df",
                df,
                upstream_timestamp=self._cache.get_upstream_timestamp(
                    "bootstrap_static_data"
                ),
            )

        return df

    def get_gameweeks(self, use_cache: bool = True) -> pd.DataFrame:
        if use_cache and self._cache:
            upstream_ts = self._cache.get_upstream_timestamp("bootstrap_static_data")
            cached_ts = self._cache.get_upstream_timestamp("gameweeks_df")

            if upstream_ts and cached_ts == upstream_ts:
                cached = self._cache.get("gameweeks_df")
                if cached is not None and isinstance(cached, pd.DataFrame):
                    return cached

        data = self.get_bootstrap_static(use_cache=use_cache)
        if not data or "events" not in data:
            return pd.DataFrame()

        gameweeks = data["events"]
        df = pd.DataFrame(gameweeks)

        if not df.empty:
            df["is_current"] = df.get("is_current", False)
            df["is_next"] = df.get("is_next", False)
            df["is_prev"] = df.get("is_previous", False)

        if use_cache and self._cache:
            self._cache.set(
                "gameweeks_df",
                df,
                upstream_timestamp=self._cache.get_upstream_timestamp(
                    "bootstrap_static_data"
                ),
            )

        return df

    def get_fixtures_with_fdr(
        self, team_id: int, num_gameweeks: int = 5
    ) -> pd.DataFrame:
        fixtures = self.get_fixtures(team_id=team_id)
        teams_df = self.get_teams_df()

        if not fixtures or not isinstance(fixtures, list) or teams_df.empty:
            return pd.DataFrame()

        all_fixtures = []
        for f in fixtures[: num_gameweeks * 2]:
            gw = f.get("event")
            if gw is None:
                continue

            if f["team_a"] == team_id:
                opp = (
                    teams_df[teams_df["id"] == f["team_h"]].iloc[0]
                    if len(teams_df[teams_df["id"] == f["team_h"]]) > 0
                    else None
                )
                home = False
            else:
                opp = (
                    teams_df[teams_df["id"] == f["team_a"]].iloc[0]
                    if len(teams_df[teams_df["id"] == f["team_a"]]) > 0
                    else None
                )
                home = True

            if opp is not None:
                difficulty = f.get(
                    "team_a_difficulty" if home else "team_h_difficulty", 3
                )
                all_fixtures.append(
                    {
                        "gameweek": gw,
                        "opponent": opp["short_name"],
                        "home_away": "Home" if home else "Away",
                        "difficulty": difficulty,
                        "fdr": self._difficulty_to_fdr(difficulty),
                    }
                )

        return pd.DataFrame(all_fixtures)

    @staticmethod
    def _difficulty_to_fdr(difficulty: int) -> str:
        fdr_map = {1: "Easy", 2: "Medium", 3: "Hard", 4: "Very Hard", 5: "Extreme"}
        return fdr_map.get(difficulty, "Unknown")


_client = None


def get_client() -> FPLAPIClient:
    global _client
    if _client is None:
        _client = FPLAPIClient()
    return _client
