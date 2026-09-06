import numpy as np
import pandas as pd

from .BasicAnalyzer import BasicDataAnalysisModule


class RobustNumericAnomalyAnalysis(BasicDataAnalysisModule):
    """Detect numeric outliers using a robust median absolute deviation score."""

    def __init__(self, cfg):
        self.column = cfg["column"]
        self.threshold = float(cfg.get("threshold", 3.5))

    def analyze(self, data_loader, data_checker):
        data = data_checker.checkFilter(data_loader.getAllData(None)).copy()
        values = pd.to_numeric(data[self.column], errors="coerce")
        median = values.median()
        mad = (values - median).abs().median()
        if pd.isna(mad) or mad == 0:
            score = pd.Series(0.0, index=data.index)
            score.loc[values.notna() & (values != median)] = np.inf
        else:
            score = 0.6745 * (values - median).abs() / mad
        data["robust_anomaly_score"] = score
        data["is_anomaly"] = score > self.threshold
        data = data.sort_values("robust_anomaly_score", ascending=False)
        report = {
            "title": f"Robust anomalies in {self.column}",
            "metrics": {
                "rows_total": len(data),
                "anomalies": int(data["is_anomaly"].sum()),
                "median": median,
                "mad": mad,
                "threshold": self.threshold,
            },
            "table": data,
        }
        return data, report
