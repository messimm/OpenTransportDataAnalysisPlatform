import pandas as pd

from .BasicAnalyzer import BasicDataAnalysisModule


class ServiceStatusAnalysis(BasicDataAnalysisModule):
    """Rank public transport lines and summarize current disruptions."""

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.healthy_severity = int(cfg.get("healthy_severity", 10))

    def analyze(self, data_loader, data_checker):
        data = data_checker.checkFilter(data_loader.getAllData(None)).copy()
        data["severity"] = pd.to_numeric(data["severity"], errors="coerce")
        data["is_disrupted"] = data["severity"] != self.healthy_severity
        data = data.sort_values(["is_disrupted", "severity"], ascending=[False, True])
        report = {
            "title": "Public transport service status",
            "metrics": {
                "lines_total": int(data["line_id"].nunique()),
                "disrupted_lines": int(data.loc[data["is_disrupted"], "line_id"].nunique()),
                "healthy_severity": self.healthy_severity,
            },
            "table": data,
        }
        return data, report
