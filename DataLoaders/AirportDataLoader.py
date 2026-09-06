# -*- coding: utf-8 -*-
"""Loader for the public OurAirports airport inventory."""

from io import BytesIO
import warnings

import pandas as pd
import requests

from .BasicLoader import BasicDataLoaderModule


class OurAirportsLoader(BasicDataLoaderModule):
    """Load the worldwide OurAirports CSV dataset with an offline fallback."""

    DEFAULT_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg or {}
        self.rows_limit = int(self.cfg.get("rows_limit", 100000))
        self.data_frame, source = self._load_dataframe()
        self.data_frame = self.data_frame.head(self.rows_limit).rename(
            columns={
                "ident": "airport_id",
                "latitude_deg": "latitude",
                "longitude_deg": "longitude",
                "iso_country": "country_code",
                "municipality": "city",
            }
        )
        self.data_frame["_source"] = source
        self.centers = pd.unique(self.data_frame.get("airport_id", pd.Series(dtype=str)).dropna())
        self.center_labels = self.data_frame

    def _load_dataframe(self):
        data_path = self.cfg.get("data_path")
        if data_path:
            return pd.read_csv(data_path), "local_file"
        url = self.cfg.get("url", self.DEFAULT_URL)
        try:
            response = requests.get(url, timeout=self.cfg.get("timeout", 60))
            response.raise_for_status()
            return pd.read_csv(BytesIO(response.content)), "ourairports_url"
        except (requests.RequestException, ValueError) as exc:
            fallback_path = self.cfg.get("fallback_path")
            if not fallback_path:
                raise RuntimeError(f"Cannot load airport dataset: {url}") from exc
            warnings.warn(
                f"OurAirports source is unavailable; using fallback cache: {fallback_path}",
                RuntimeWarning,
                stacklevel=2,
            )
            return pd.read_csv(fallback_path), "fallback_cache"

    def labelCenter(self, center):
        return self.data_frame[self.data_frame["airport_id"] == center]

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
