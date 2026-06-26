import pandas as pd

from .BasicChecker import BasicChecker


class DataMosGeoChecker(BasicChecker):
    """Basic quality checks for normalized geospatial data.mos.ru adapters."""

    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.require_coordinates = self.cfg.get("require_coordinates", False)

    def check(self, data):
        return len(self.checkFilter(data)) == len(data)

    def checkFilter(self, data):
        result = pd.Series(True, index=data.index)
        if self.require_coordinates and {"latitude", "longitude"}.issubset(data.columns):
            result &= data["latitude"].between(55.0, 56.2) & data["longitude"].between(36.5, 38.5)
        return data[result]
