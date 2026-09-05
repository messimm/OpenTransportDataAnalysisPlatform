import pandas as pd

from .BasicChecker import BasicChecker


class DataFrameColumnFilterChecker(BasicChecker):
    """Reusable DataFrame filter configured by simple column predicates."""

    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.not_empty = self.cfg.get("not_empty", [])
        self.in_values = self.cfg.get("in_values", {})
        self.ranges = self.cfg.get("ranges", {})

    def check(self, data):
        return len(self.checkFilter(data)) == len(data)

    def checkFilter(self, data):
        result = pd.Series(True, index=data.index)
        for column in self.not_empty:
            if column in data.columns:
                result &= data[column].notna() & (data[column].astype(str).str.len() > 0)
        for column, values in self.in_values.items():
            if column in data.columns:
                result &= data[column].isin(values)
        for column, bounds in self.ranges.items():
            if column in data.columns:
                low = bounds.get("min", float("-inf"))
                high = bounds.get("max", float("inf"))
                numeric = pd.to_numeric(data[column], errors="coerce")
                result &= numeric.between(low, high, inclusive="both")
        return data[result]
