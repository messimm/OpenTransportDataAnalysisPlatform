import pandas as pd

from .BasicAnalyzer import BasicDataAnalysisModule


class DeparturePunctualityAnalysis(BasicDataAnalysisModule):
    """Classify upcoming departures by reported/predicted delay."""

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.delay_threshold = float(cfg.get("delay_threshold_minutes", 3))

    def analyze(self, data_loader, data_checker):
        data = data_checker.checkFilter(data_loader.getAllData(None)).copy()
        delay = pd.to_numeric(data.get("delay_minutes"), errors="coerce")
        scheduled = pd.to_datetime(data["scheduled_departure"], errors="coerce", utc=True)
        predicted = pd.to_datetime(data.get("predicted_departure"), errors="coerce", utc=True)
        calculated = (predicted - scheduled).dt.total_seconds() / 60
        data["delay_minutes"] = delay.fillna(calculated)
        data["punctuality_state"] = "unknown"
        known = data["delay_minutes"].notna()
        data.loc[known & (data["delay_minutes"] < self.delay_threshold), "punctuality_state"] = "on_time"
        data.loc[known & (data["delay_minutes"] >= self.delay_threshold), "punctuality_state"] = "delayed"
        data = data.sort_values("delay_minutes", ascending=False, na_position="last")
        report = {
            "title": "Upcoming departure punctuality",
            "metrics": {
                "departures_total": len(data),
                "delayed_departures": int((data["punctuality_state"] == "delayed").sum()),
                "unknown_predictions": int((data["punctuality_state"] == "unknown").sum()),
                "delay_threshold_minutes": self.delay_threshold,
            },
            "table": data,
        }
        return data, report
