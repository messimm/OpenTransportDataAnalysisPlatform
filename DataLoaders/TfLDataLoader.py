# -*- coding: utf-8 -*-
"""Loader for Transport for London line status open data."""

import json
import warnings

import pandas as pd
import requests

from .BasicLoader import BasicDataLoaderModule


class TfLLineStatusLoader(BasicDataLoaderModule):
    """Load and flatten responses from the TfL Unified API Line Status method."""

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg or {}
        self.url = self.cfg.get("url", "https://api.tfl.gov.uk/Line/Mode/tube/Status")
        payload, source = self._load_payload()
        self.data_frame = self._to_dataframe(payload)
        self.data_frame["_source"] = source
        self.centers = pd.unique(self.data_frame.get("line_id", pd.Series(dtype=str)).dropna())
        self.center_labels = self.data_frame

    def _load_payload(self):
        data_path = self.cfg.get("data_path")
        if data_path:
            return self._read_json(data_path), "local_file"
        try:
            response = requests.get(self.url, timeout=self.cfg.get("timeout", 30))
            response.raise_for_status()
            return response.json(), "tfl_api"
        except (requests.RequestException, ValueError) as exc:
            fallback_path = self.cfg.get("fallback_path")
            if not fallback_path:
                raise RuntimeError(f"Cannot load TfL line status: {self.url}") from exc
            warnings.warn(
                f"TfL API is unavailable; using fallback cache: {fallback_path}",
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
        if not isinstance(payload, list):
            raise ValueError("Invalid TfL Line Status payload")
        records = []
        for line in payload:
            statuses = line.get("lineStatuses") or [{}]
            for status in statuses:
                records.append(
                    {
                        "line_id": line.get("id"),
                        "line_name": line.get("name"),
                        "mode": line.get("modeName"),
                        "severity": status.get("statusSeverity"),
                        "status": status.get("statusSeverityDescription"),
                        "reason": status.get("reason"),
                    }
                )
        return pd.DataFrame.from_records(records)

    def labelCenter(self, center):
        return self.data_frame[self.data_frame["line_id"] == center]

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
