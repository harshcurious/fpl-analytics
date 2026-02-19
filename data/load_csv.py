import pandas as pd
import os
from typing import Optional, List
import glob


class FPLCoreInsightsLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.available_seasons = self._get_available_seasons()

    def _get_available_seasons(self) -> List[str]:
        if not os.path.exists(self.data_dir):
            return []

        seasons = []
        for item in os.listdir(self.data_dir):
            full_path = os.path.join(self.data_dir, item)
            if os.path.isdir(full_path) and item.startswith("20"):
                seasons.append(item)

        return sorted(seasons)

    def get_latest_season(self) -> Optional[str]:
        if not self.available_seasons:
            return None
        return self.available_seasons[-1]

    def load_player_stats(self, season: Optional[str] = None) -> pd.DataFrame:
        if season is None:
            season = self.get_latest_season()

        if season is None:
            return pd.DataFrame()

        playerstats_path = os.path.join(self.data_dir, season, "player_stats.csv")

        if not os.path.exists(playerstats_path):
            return pd.DataFrame()

        try:
            df = pd.read_csv(playerstats_path)
            return df
        except Exception as e:
            print(f"Error loading player stats: {e}")
            return pd.DataFrame()

    def load_team_stats(self, season: Optional[str] = None) -> pd.DataFrame:
        if season is None:
            season = self.get_latest_season()

        if season is None:
            return pd.DataFrame()

        team_stats_path = os.path.join(self.data_dir, season, "team_stats.csv")

        if not os.path.exists(team_stats_path):
            return pd.DataFrame()

        try:
            df = pd.read_csv(team_stats_path)
            return df
        except Exception as e:
            print(f"Error loading team stats: {e}")
            return pd.DataFrame()

    def load_elo_ratings(self, season: Optional[str] = None) -> pd.DataFrame:
        if season is None:
            season = self.get_latest_season()

        if season is None:
            return pd.DataFrame()

        elo_path = os.path.join(self.data_dir, season, "team_elo.csv")

        if not os.path.exists(elo_path):
            return pd.DataFrame()

        try:
            df = pd.read_csv(elo_path)
            return df
        except Exception as e:
            print(f"Error loading elo ratings: {e}")
            return pd.DataFrame()

    def load_fixture_difficulty(self, season: Optional[str] = None) -> pd.DataFrame:
        if season is None:
            season = self.get_latest_season()

        if season is None:
            return pd.DataFrame()

        fd_path = os.path.join(self.data_dir, season, "fixture_difficulty.csv")

        if not os.path.exists(fd_path):
            return pd.DataFrame()

        try:
            df = pd.read_csv(fd_path)
            return df
        except Exception as e:
            print(f"Error loading fixture difficulty: {e}")
            return pd.DataFrame()

    def load_gameweek_stats(
        self, season: Optional[str] = None, gameweek: Optional[int] = None
    ) -> pd.DataFrame:
        if season is None:
            season = self.get_latest_season()

        if season is None:
            return pd.DataFrame()

        gw_path = os.path.join(self.data_dir, season, "player_gameweek_stats.csv")

        if not os.path.exists(gw_path):
            return pd.DataFrame()

        try:
            df = pd.read_csv(gw_path)
            if gameweek is not None:
                df = df[df["gameweek"] == gameweek]
            return df
        except Exception as e:
            print(f"Error loading gameweek stats: {e}")
            return pd.DataFrame()

    def get_player_form_trend(
        self, player_id: int, num_gw: int = 5, season: Optional[str] = None
    ) -> pd.DataFrame:
        gw_stats = self.load_gameweek_stats(season=season)

        if gw_stats.empty:
            return pd.DataFrame()

        player_data = gw_stats[gw_stats["player_id"] == player_id].sort_values(
            "gameweek", ascending=False
        )

        if player_data.empty:
            return pd.DataFrame()

        return player_data.head(num_gw)


_loader = None


def get_csv_loader(data_dir: str = "data") -> FPLCoreInsightsLoader:
    global _loader
    if _loader is None:
        _loader = FPLCoreInsightsLoader(data_dir)
    return _loader
