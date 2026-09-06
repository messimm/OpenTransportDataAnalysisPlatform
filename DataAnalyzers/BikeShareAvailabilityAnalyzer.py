import numpy as np
import pandas as pd

from .BasicAnalyzer import BasicDataAnalysisModule


class BikeShareAvailabilityAnalysis(BasicDataAnalysisModule):
    """Detect empty, near-full and operationally unavailable GBFS stations."""

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.empty_bikes = int(cfg.get("empty_bikes", 0))
        self.full_docks = int(cfg.get("full_docks", 1))
        self.target_ratio = float(cfg.get("target_ratio", 0.5))

    def analyze(self, data_loader, data_checker):
        information_loader, status_loader = data_loader
        information_checker, status_checker = data_checker
        information = information_checker.checkFilter(information_loader.getAllData(None)).copy()
        status = status_checker.checkFilter(status_loader.getAllData(None)).copy()
        required = {"station_id", "num_bikes_available", "num_docks_available"}
        missing = required - set(status.columns)
        if missing:
            raise KeyError(f"GBFS status columns are missing: {', '.join(sorted(missing))}")

        columns = [c for c in ["station_id", "name", "latitude", "longitude", "capacity"] if c in information]
        result = information[columns].merge(status, on="station_id", how="inner", suffixes=("", "_status"))
        if "capacity" not in result:
            result["capacity"] = result["num_bikes_available"] + result["num_docks_available"]
        result["capacity"] = pd.to_numeric(result["capacity"], errors="coerce")
        result = result[result["capacity"] > 0].copy()
        result["availability_ratio"] = result["num_bikes_available"] / result["capacity"]
        result["imbalance_score"] = (result["availability_ratio"] - self.target_ratio).abs()

        operational = pd.Series(True, index=result.index)
        for flag in ("is_installed", "is_renting", "is_returning"):
            if flag in result:
                operational &= result[flag].fillna(0).astype(bool)
        conditions = [
            ~operational,
            result["num_bikes_available"] <= self.empty_bikes,
            result["num_docks_available"] <= self.full_docks,
        ]
        result["availability_state"] = np.select(
            conditions, ["unavailable", "empty", "near_full"], default="balanced"
        )
        return result.sort_values("imbalance_score", ascending=False), result
