import json
import os
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, Optional, Callable
import pandas as pd


class DataCache:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self._metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        with open(self.metadata_file, "w") as f:
            json.dump(self._metadata, f, indent=2)

    def _get_cache_key(self, key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.json"

    def get(self, key: str) -> Optional[Any]:
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            with open(cache_path, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "_dataframe_" in data:
                    return pd.DataFrame(data["data"])
                return data
        return None

    def set(self, key: str, value: Any, upstream_timestamp: Optional[str] = None):
        cache_path = self._get_cache_path(key)

        if isinstance(value, pd.DataFrame):
            data_to_store = {
                "_dataframe_": True,
                "data": value.to_dict(orient="records"),
            }
        else:
            data_to_store = value

        with open(cache_path, "w") as f:
            json.dump(data_to_store, f, indent=2, default=self._json_serialize)

        if upstream_timestamp:
            self._metadata[key] = {"upstream_timestamp": upstream_timestamp}
            self._save_metadata()

    def get_upstream_timestamp(self, key: str) -> Optional[str]:
        return self._metadata.get(key, {}).get("upstream_timestamp")

    def _json_serialize(self, obj):
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        if hasattr(obj, "tolist"):
            return obj.tolist()
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def cached_fetch(
    cache: DataCache,
    cache_key: str,
    fetch_func: Callable,
    get_upstream_timestamp: Optional[Callable] = None,
    ttl: int = 3600,
) -> Any:
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        local_timestamp = cache.get_upstream_timestamp(cache_key)

        if get_upstream_timestamp:
            try:
                upstream_timestamp = get_upstream_timestamp()
            except Exception:
                upstream_timestamp = None

            if upstream_timestamp and local_timestamp == upstream_timestamp:
                return cached_data

            if local_timestamp is None:
                if (
                    time.time() - os.path.getmtime(cache._get_cache_path(cache_key))
                    < ttl
                ):
                    return cached_data
        else:
            cache_path = cache._get_cache_path(cache_key)
            if cache_path.exists():
                mtime = os.path.getmtime(cache_path)
                if time.time() - mtime < ttl:
                    return cached_data

    data = fetch_func()

    upstream_ts = None
    if get_upstream_timestamp:
        try:
            upstream_ts = get_upstream_timestamp()
        except Exception:
            pass

    cache.set(cache_key, data, upstream_timestamp=upstream_ts)
    return data
