# -*- coding: utf-8 -*-
"""Loader for static General Transit Feed Specification (GTFS) archives."""

from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile
import warnings

import pandas as pd
import requests

from .BasicLoader import BasicDataLoaderModule


class GTFSFeedLoader(BasicDataLoaderModule):
    """Read a GTFS ZIP or unpacked text directory into pandas DataFrames."""

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg or {}
        source_data, self.source = self._load_source()
        self.tables = self._read_tables(source_data)
        for table in self.tables.values():
            table["_source"] = self.source
        self.data_frame = self.tables.get("stops", pd.DataFrame())
        self.centers = pd.unique(self.data_frame.get("stop_id", pd.Series(dtype=str)).dropna())
        self.center_labels = self.data_frame

    def _load_source(self):
        data_path = self.cfg.get("data_path")
        if data_path:
            path = Path(data_path)
            return path if path.is_dir() else path.read_bytes(), "local_file"
        url = self.cfg.get("url")
        if not url:
            raise ValueError("GTFS loader requires 'url' or 'data_path'")
        try:
            response = requests.get(url, timeout=self.cfg.get("timeout", 60))
            response.raise_for_status()
            return response.content, "gtfs_url"
        except requests.RequestException as exc:
            fallback_path = self.cfg.get("fallback_path")
            if not fallback_path:
                raise RuntimeError(f"Cannot load GTFS archive: {url}") from exc
            warnings.warn(
                f"GTFS source is unavailable; using fallback cache: {fallback_path}",
                RuntimeWarning,
                stacklevel=2,
            )
            path = Path(fallback_path)
            return path if path.is_dir() else path.read_bytes(), "fallback_cache"

    @staticmethod
    def _read_tables(source):
        required = ("stops", "routes", "trips", "stop_times")
        if isinstance(source, Path):
            missing = {
                f"{name}.txt"
                for name in required
                if not (source / f"{name}.txt").is_file()
            }
            if missing:
                raise ValueError(f"GTFS tables are missing: {', '.join(sorted(missing))}")
            return {
                name: pd.read_csv(source / f"{name}.txt", dtype=str)
                for name in required
            }
        try:
            with ZipFile(BytesIO(source)) as feed:
                names = set(feed.namelist())
                missing = {f"{name}.txt" for name in required} - names
                if missing:
                    raise ValueError(f"GTFS tables are missing: {', '.join(sorted(missing))}")
                return {
                    name: pd.read_csv(feed.open(f"{name}.txt"), dtype=str)
                    for name in required
                }
        except BadZipFile as exc:
            raise ValueError("Invalid GTFS ZIP archive") from exc

    def getTable(self, name):
        if name not in self.tables:
            raise KeyError(f"Unknown GTFS table: {name}")
        return self.tables[name]

    def labelCenter(self, center):
        return self.data_frame[self.data_frame["stop_id"] == center]

    def getAllData(self, data=None):
        return self.data_frame if data is None else data

    def getDataByColumnValue(self, data, column_name, value):
        source = self.getAllData(data)
        return source[source[column_name] == value]

    def getDataByColumnRange(self, data, column_name, low, high):
        source = self.getAllData(data)
        return source[(source[column_name] > low) & (source[column_name] < high)]

    def getDataByColumnSet(self, data, column_name, values):
        source = self.getAllData(data)
        return source[source[column_name].isin(values)]
