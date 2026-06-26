# -*- coding: utf-8 -*-
"""Loaders for Moscow open transport datasets from data.mos.ru.

The loaders follow the platform's existing pandas DataFrame-based style and add
small, dataset-specific adapters for common transport datasets. They can read
from a cached CSV/JSON file or directly from the data.mos.ru API when network
access and an API key are available.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Optional

import pandas as pd
import requests

from .BasicLoader import BasicDataLoaderModule


class DataMosApiError(RuntimeError):
    """Raised when a data.mos.ru dataset cannot be downloaded."""


class DataMosDatasetLoader(BasicDataLoaderModule):
    """Base adapter for tabular datasets published on data.mos.ru.

    Parameters accepted in config:
    - dataset_id: numeric dataset id from https://data.mos.ru/opendata/<id>
    - data_path: optional local CSV/JSON cache; used before network loading
    - api_key: optional API key for the data.mos.ru API
    - rows_limit: max rows to download/read (default: 5000)
    - columns_map: optional mapping from source field names to normalized names
    """

    API_URL = "https://api.data.mos.ru/v1/datasets/{dataset_id}/rows"

    dataset_id: Optional[int] = None
    default_columns_map: Dict[str, str] = {}
    center_column: Optional[str] = None
    label_column: Optional[str] = None

    def __init__(self, cfg: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.cfg = cfg or {}
        self.dataset_id = int(self.cfg.get("dataset_id", self.dataset_id or 0))
        if not self.dataset_id:
            raise ValueError("dataset_id is required for DataMosDatasetLoader")

        self.rows_limit = int(self.cfg.get("rows_limit", 5000))
        self.columns_map = {**self.default_columns_map, **self.cfg.get("columns_map", {})}
        self.data_frame = self._load_dataframe()
        self._normalize_dataframe()
        self._init_centers()

    def _load_dataframe(self) -> pd.DataFrame:
        data_path = self.cfg.get("data_path")
        if data_path:
            return self._read_local(data_path)
        return self._download_from_api()

    def _read_local(self, data_path: str) -> pd.DataFrame:
        if data_path.endswith(".json"):
            with open(data_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            return self._rows_to_frame(payload)
        return pd.read_csv(data_path, sep=self.cfg.get("sep", ";"), nrows=self.rows_limit)

    def _download_from_api(self) -> pd.DataFrame:
        params: Dict[str, Any] = {"$top": self.rows_limit}
        api_key = self.cfg.get("api_key")
        if api_key:
            params["api_key"] = api_key
        url = self.API_URL.format(dataset_id=self.dataset_id)
        try:
            response = requests.get(url, params=params, timeout=self.cfg.get("timeout", 20))
            response.raise_for_status()
        except requests.RequestException as exc:
            raise DataMosApiError(
                f"Cannot load data.mos.ru dataset {self.dataset_id}. "
                "Provide a local data_path cache or check network/API access."
            ) from exc
        return self._rows_to_frame(response.json())

    def _rows_to_frame(self, payload: Any) -> pd.DataFrame:
        records = []
        for row in payload if isinstance(payload, list) else payload.get("Items", []):
            cells = row.get("Cells", row) if isinstance(row, dict) else row
            if isinstance(cells, dict):
                records.append(cells)
        return pd.DataFrame.from_records(records)

    def _normalize_dataframe(self) -> None:
        if self.columns_map:
            self.data_frame = self.data_frame.rename(columns=self.columns_map)
        for column in ("latitude", "longitude"):
            if column in self.data_frame.columns:
                self.data_frame[column] = pd.to_numeric(self.data_frame[column], errors="coerce")

    def _init_centers(self) -> None:
        if self.center_column and self.center_column in self.data_frame.columns:
            self.centers = pd.unique(self.data_frame[self.center_column].dropna())
        else:
            self.centers = list(self.data_frame.index)
        self.center_labels = self.data_frame

    def labelCenter(self, center):
        if self.center_column and self.center_column in self.data_frame.columns:
            return self.data_frame[self.data_frame[self.center_column] == center]
        return self.data_frame.loc[[center]] if center in self.data_frame.index else pd.DataFrame()

    def getAllData(self, data=None):
        return self.data_frame if data is None else data

    def getDataByColumnValue(self, data, column_name, value):
        source = self.getAllData(data)
        return source[source[column_name] == value]

    def getDataByColumnRange(self, data, column_name, low, high):
        source = self.getAllData(data)
        return source[(source[column_name] > low) & (source[column_name] < high)]

    def getDataByColumnSet(self, data, column_name, values: Iterable[Any]):
        source = self.getAllData(data)
        return source[source[column_name].isin(values)]

    def getGeoData(self, data=None):
        source = self.getAllData(data)
        cols = [c for c in [self.label_column, "address", "latitude", "longitude"] if c in source.columns]
        return source[cols].dropna(subset=["latitude", "longitude"], how="any")

    def checkAvailability(self) -> bool:
        try:
            url = self.API_URL.format(dataset_id=self.dataset_id)
            params = {"$top": 1}
            if self.cfg.get("api_key"):
                params["api_key"] = self.cfg["api_key"]
            response = requests.get(url, params=params, timeout=self.cfg.get("timeout", 10))
            return response.ok
        except requests.RequestException:
            return False


class MoscowStreetParkingLoader(DataMosDatasetLoader):
    """Dataset 623: paid street parking places."""

    dataset_id = 623
    center_column = "parking_id"
    label_column = "name"
    default_columns_map = {
        "ParkingName": "name",
        "ParkingNumber": "parking_id",
        "Address": "address",
        "CarCapacity": "capacity",
        "Latitude_WGS84": "latitude",
        "Longitude_WGS84": "longitude",
    }


class MoscowTaxiParkingLoader(DataMosDatasetLoader):
    """Dataset 621: taxi parking places."""

    dataset_id = 621
    center_column = "global_id"
    label_column = "name"
    default_columns_map = {
        "Name": "name",
        "Address": "address",
        "Latitude_WGS84": "latitude",
        "Longitude_WGS84": "longitude",
    }


class MoscowBikeRentalLoader(DataMosDatasetLoader):
    """Dataset 1777: bicycle rental points."""

    dataset_id = 1777
    center_column = "global_id"
    label_column = "name"
    default_columns_map = {
        "Name": "name",
        "Address": "address",
        "Latitude_WGS84": "latitude",
        "Longitude_WGS84": "longitude",
        "IsNetObject": "is_network_object",
    }


class MoscowTransitStopsRoutesLoader(DataMosDatasetLoader):
    """Dataset 60661: surface public transport route/stops schedule records."""

    dataset_id = 60661
    center_column = "route_number"
    label_column = "route_number"
    default_columns_map = {
        "RouteNumber": "route_number",
        "NameOfStop": "stop_name",
        "StationName": "stop_name",
        "Direction": "direction",
        "TransportType": "transport_type",
        "Longitude_WGS84": "longitude",
        "Latitude_WGS84": "latitude",
    }
