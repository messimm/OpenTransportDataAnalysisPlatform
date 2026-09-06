# -*- coding: utf-8 -*-
"""Loader for public GBFS bicycle and scooter sharing feeds."""

import json
import warnings

import pandas as pd
import requests

from .BasicLoader import BasicDataLoaderModule


class GBFSStationInformationLoader(BasicDataLoaderModule):
    """Read a GBFS station_information feed from the web or a local cache."""

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg or {}
        self.url = self.cfg.get("url")
        self.rows_limit = int(self.cfg.get("rows_limit", 5000))
        self.source = None
        payload = self._load_payload()
        self.data_frame = self._to_dataframe(payload).head(self.rows_limit)
        self.data_frame["_source"] = self.source
        self.centers = pd.unique(self.data_frame.get("station_id", pd.Series(dtype=str)).dropna())
        self.center_labels = self.data_frame

    def _load_payload(self):
        data_path = self.cfg.get("data_path")
        if data_path:
            self.source = "local_file"
            return self._read_json(data_path)
        if not self.url:
            raise ValueError("GBFS loader requires 'url' or 'data_path'")
        try:
            response = requests.get(self.url, timeout=self.cfg.get("timeout", 30))
            response.raise_for_status()
            self.source = "gbfs_api"
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            fallback_path = self.cfg.get("fallback_path")
            if not fallback_path:
                raise RuntimeError(f"Cannot load GBFS feed: {self.url}") from exc
            warnings.warn(
                f"GBFS feed is unavailable; using fallback cache: {fallback_path}",
                RuntimeWarning,
                stacklevel=2,
            )
            self.source = "fallback_cache"
            return self._read_json(fallback_path)

    @staticmethod
    def _read_json(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _to_dataframe(payload):
        data = payload.get("data", {}) if isinstance(payload, dict) else {}
        stations = data.get("stations", []) if isinstance(data, dict) else []
        if not isinstance(stations, list):
            raise ValueError("Invalid GBFS station_information payload")
        frame = pd.DataFrame.from_records(stations)
        return frame.rename(
            columns={
                "lat": "latitude",
                "lon": "longitude",
                "num_docks_available": "capacity",
            }
        )

    def labelCenter(self, center):
        return self.data_frame[self.data_frame["station_id"] == center]

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


class GBFSStationStatusLoader(GBFSStationInformationLoader):
    """Read the real-time GBFS station_status feed."""

    @staticmethod
    def _to_dataframe(payload):
        data = payload.get("data", {}) if isinstance(payload, dict) else {}
        stations = data.get("stations", []) if isinstance(data, dict) else []
        if not isinstance(stations, list):
            raise ValueError("Invalid GBFS station_status payload")
        return pd.DataFrame.from_records(stations)
