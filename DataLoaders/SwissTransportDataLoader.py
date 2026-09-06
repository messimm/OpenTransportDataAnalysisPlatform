# -*- coding: utf-8 -*-
"""Loader for the public transport.opendata.ch stationboard API."""

import json
import warnings

import pandas as pd
import requests

from .BasicLoader import BasicDataLoaderModule


class SwissStationboardLoader(BasicDataLoaderModule):
    """Load upcoming public transport departures for a Swiss station."""

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg or {}
        payload, source = self._load_payload()
        self.data_frame = self._to_dataframe(payload)
        self.data_frame["_source"] = source
        self.centers = pd.unique(self.data_frame.get("station", pd.Series(dtype=str)).dropna())
        self.center_labels = self.data_frame

    def _load_payload(self):
        data_path = self.cfg.get("data_path")
        if data_path:
            return self._read_json(data_path), "local_file"
        url = self.cfg.get("url", "https://transport.opendata.ch/v1/stationboard")
        params = {
            "station": self.cfg.get("station", "Zürich HB"),
            "limit": int(self.cfg.get("limit", 50)),
        }
        try:
            response = requests.get(url, params=params, timeout=self.cfg.get("timeout", 30))
            response.raise_for_status()
            return response.json(), "transport.opendata.ch_api"
        except (requests.RequestException, ValueError) as exc:
            fallback_path = self.cfg.get("fallback_path")
            if not fallback_path:
                raise RuntimeError(f"Cannot load Swiss stationboard: {url}") from exc
            warnings.warn(
                f"Swiss transport API is unavailable; using fallback cache: {fallback_path}",
                RuntimeWarning,
                stacklevel=2,
            )
            return self._read_json(fallback_path), "fallback_cache"

    @staticmethod
    def _read_json(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _to_dataframe(payload):
        station = payload.get("station", {})
        records = []
        for journey in payload.get("stationboard", []):
            stop = journey.get("stop") or {}
            prognosis = stop.get("prognosis") or {}
            records.append(
                {
                    "station": station.get("name"),
                    "line": journey.get("number") or journey.get("name"),
                    "category": journey.get("category"),
                    "destination": journey.get("to"),
                    "platform": stop.get("platform"),
                    "scheduled_departure": stop.get("departure"),
                    "predicted_departure": prognosis.get("departure"),
                    "delay_minutes": stop.get("delay"),
                }
            )
        return pd.DataFrame.from_records(records)

    def labelCenter(self, center):
        return self.data_frame[self.data_frame["station"] == center]

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
