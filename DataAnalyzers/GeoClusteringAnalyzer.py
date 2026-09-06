import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from .BasicAnalyzer import BasicDataAnalysisModule


class GeoKMeansAnalysis(BasicDataAnalysisModule):
    """Cluster transport objects by coordinates and optional numeric features."""

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.n_clusters = int(cfg.get("n_clusters", 5))
        self.feature_columns = cfg.get("feature_columns", ["latitude", "longitude"])
        self.random_state = int(cfg.get("random_state", 42))

    def analyze(self, data_loader, data_checker):
        data = data_checker.checkFilter(data_loader.getAllData(None)).copy()
        missing = set(self.feature_columns) - set(data.columns)
        if missing:
            raise KeyError(f"Clustering columns are missing: {', '.join(sorted(missing))}")
        features = data[self.feature_columns].apply(pd.to_numeric, errors="coerce")
        valid = features.notna().all(axis=1)
        data = data.loc[valid].copy()
        features = features.loc[valid]
        if len(data) < self.n_clusters:
            raise ValueError("n_clusters cannot exceed the number of valid objects")
        scaled = StandardScaler().fit_transform(features)
        data["cluster"] = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10,
        ).fit_predict(scaled)
        return data, data
