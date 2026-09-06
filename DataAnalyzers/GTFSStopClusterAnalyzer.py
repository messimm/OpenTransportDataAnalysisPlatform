import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from .BasicAnalyzer import BasicDataAnalysisModule


class GTFSStopClusterAnalysis(BasicDataAnalysisModule):
    """Cluster GTFS stops by location and scheduled service intensity."""

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.n_clusters = int(cfg.get("n_clusters", 4))
        self.random_state = int(cfg.get("random_state", 42))

    def analyze(self, data_loader, data_checker):
        stops = data_loader.getTable("stops").copy()
        stop_times = data_loader.getTable("stop_times")
        counts = stop_times.groupby("stop_id").size().rename("stop_events")
        data = stops.merge(counts, on="stop_id", how="left")
        data["stop_events"] = data["stop_events"].fillna(0)
        data = data.rename(columns={"stop_lat": "latitude", "stop_lon": "longitude"})
        data = data_checker.checkFilter(data)
        features = data[["latitude", "longitude"]].apply(pd.to_numeric, errors="coerce")
        features["service_intensity"] = np.log1p(data["stop_events"].astype(float))
        valid = features.notna().all(axis=1)
        data = data.loc[valid].copy()
        if len(data) < self.n_clusters:
            raise ValueError("n_clusters cannot exceed the number of valid stops")
        data["latitude"] = features.loc[valid, "latitude"]
        data["longitude"] = features.loc[valid, "longitude"]
        data["cluster"] = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10,
        ).fit_predict(StandardScaler().fit_transform(features.loc[valid]))
        return data, data
