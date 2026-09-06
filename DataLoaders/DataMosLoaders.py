# -*- coding: utf-8 -*-
"""Loaders for Moscow open transport datasets from data.mos.ru.

The loaders follow the platform's existing pandas DataFrame-based style and add
small, dataset-specific adapters for common transport datasets. They can read
from a cached CSV/JSON file or directly from the data.mos.ru API when network
access and an API key are available.
"""

from __future__ import annotations

import json
import os
import warnings
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

    API_URL = "https://apidata.mos.ru/v1/datasets/{dataset_id}/rows"

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
        self.source = None
        self.data_frame = self._load_dataframe()
        self.data_frame["_source"] = self.source
        self._normalize_dataframe()
        self._init_centers()

    def _load_dataframe(self) -> pd.DataFrame:
        data_path = self.cfg.get("data_path")
        if data_path:
            self.source = "local_file"
            return self._read_local(data_path)
        try:
            data = self._download_from_api()
            self.source = "data.mos.ru_api"
            return data
        except DataMosApiError:
            fallback_path = self.cfg.get("fallback_path")
            if not fallback_path:
                raise
            warnings.warn(
                f"data.mos.ru API is unavailable; using fallback cache: {fallback_path}",
                RuntimeWarning,
                stacklevel=2,
            )
            self.source = "fallback_cache"
            return self._read_local(fallback_path)

    def _read_local(self, data_path: str) -> pd.DataFrame:
        if str(data_path).lower().endswith(".json"):
            with open(data_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            return self._rows_to_frame(payload).head(self.rows_limit)
        return pd.read_csv(data_path, sep=self.cfg.get("sep", ";"), nrows=self.rows_limit)

    def _download_from_api(self) -> pd.DataFrame:
        params: Dict[str, Any] = {"$top": self.rows_limit}
        api_key = self.cfg.get("api_key") or os.getenv(
            self.cfg.get("api_key_env", "DATA_MOS_API_KEY")
        )
        if api_key:
            params["api_key"] = api_key
        url = self.cfg.get("api_url", self.API_URL).format(dataset_id=self.dataset_id)
        try:
            response = requests.get(url, params=params, timeout=self.cfg.get("timeout", 20))
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise DataMosApiError(
                f"Cannot load data.mos.ru dataset {self.dataset_id}. "
                "Provide a local data_path cache or check network/API access."
            ) from exc
        return self._rows_to_frame(payload)

    def _rows_to_frame(self, payload: Any) -> pd.DataFrame:
        records = []
        if isinstance(payload, list):
            rows = payload
        elif isinstance(payload, dict):
            rows = payload.get("Items", payload.get("items", payload.get("rows", [])))
        else:
            raise ValueError("Unsupported data.mos.ru JSON payload: expected list or object")
        for row in rows:
            cells = row.get("Cells", row) if isinstance(row, dict) else row
            if isinstance(cells, dict):
                records.append(cells)
        return pd.DataFrame.from_records(records)

    def _normalize_dataframe(self) -> None:
        if self.columns_map:
            self.data_frame = self.data_frame.rename(columns=self.columns_map)
        self._extract_geo_coordinates()
        for column in ("latitude", "longitude"):
            if column in self.data_frame.columns:
                self.data_frame[column] = pd.to_numeric(self.data_frame[column], errors="coerce")

    def _extract_geo_coordinates(self) -> None:
        """Normalize GeoJSON points used by many data.mos.ru datasets."""
        if {"latitude", "longitude"}.issubset(self.data_frame.columns):
            return
        for column in ("geoData", "geodata_center", "GeoData"):
            if column not in self.data_frame.columns:
                continue
            coordinates = self.data_frame[column].apply(self._point_coordinates)
            if "longitude" not in self.data_frame.columns:
                self.data_frame["longitude"] = coordinates.str[0]
            if "latitude" not in self.data_frame.columns:
                self.data_frame["latitude"] = coordinates.str[1]
            return

    @staticmethod
    def _point_coordinates(value):
        if not isinstance(value, dict):
            return (None, None)
        coordinates = value.get("coordinates")
        while isinstance(coordinates, list) and len(coordinates) == 1:
            coordinates = coordinates[0]
        if isinstance(coordinates, (list, tuple)) and len(coordinates) >= 2:
            return coordinates[0], coordinates[1]
        return (None, None)

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
        missing = {"latitude", "longitude"} - set(source.columns)
        if missing:
            raise KeyError(f"Geospatial columns are missing: {', '.join(sorted(missing))}")
        cols = [c for c in [self.label_column, "address", "latitude", "longitude"] if c in source.columns]
        return source[cols].dropna(subset=["latitude", "longitude"], how="any")

    def checkAvailability(self) -> bool:
        try:
            url = self.cfg.get("api_url", self.API_URL).format(dataset_id=self.dataset_id)
            params = {"$top": 1}
            api_key = self.cfg.get("api_key") or os.getenv(
                self.cfg.get("api_key_env", "DATA_MOS_API_KEY")
            )
            if api_key:
                params["api_key"] = api_key
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
