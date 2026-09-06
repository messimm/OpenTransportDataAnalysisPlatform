# -*- coding: utf-8 -*-
"""Loaders for district-level reference datasets used in provision analysis."""

import pandas as pd

from .BasicLoader import BasicDataLoaderModule


class DistrictPopulationLoader(BasicDataLoaderModule):
    """Load district population data from CSV/JSON.

    Expected normalized columns are `district` and `population`. Source files can
    use custom names configured through `district_column` and `population_column`.
    """

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg or {}
        self.data_path = self.cfg["data_path"]
        self.district_column = self.cfg.get("district_column", "district")
        self.population_column = self.cfg.get("population_column", "population")
        self.data_frame = self._load_dataframe()
        self._normalize_dataframe()
        self.centers = pd.unique(self.data_frame["district"].dropna())
        self.center_labels = self.data_frame

    def _load_dataframe(self):
        if self.data_path.endswith(".json"):
            return pd.read_json(self.data_path)
        return pd.read_csv(self.data_path, sep=self.cfg.get("sep", ";"))

    def _normalize_dataframe(self):
        self.data_frame = self.data_frame.rename(
            columns={self.district_column: "district", self.population_column: "population"}
        )
        missing = {"district", "population"} - set(self.data_frame.columns)
        if missing:
            raise KeyError(f"Population columns are missing: {', '.join(sorted(missing))}")
        self.data_frame["district"] = self.data_frame["district"].astype("string").str.strip()
        self.data_frame["population"] = pd.to_numeric(self.data_frame["population"], errors="coerce")
        self.data_frame = self.data_frame.dropna(subset=["district", "population"])
        self.data_frame = self.data_frame[self.data_frame["district"] != ""]
        self.data_frame = self.data_frame.groupby("district", as_index=False)["population"].sum()

    def labelCenter(self, center):
        return self.data_frame[self.data_frame["district"] == center]

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
