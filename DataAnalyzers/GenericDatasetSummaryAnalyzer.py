from .BasicAnalyzer import BasicDataAnalysisModule


class GenericDatasetSummaryAnalysis(BasicDataAnalysisModule):
    """Small compatibility analyzer for static open datasets.

    It reports row/column counts, coordinate availability and, optionally,
    descriptive statistics for a configured numeric/grouping column.
    """

    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.group_column = self.cfg.get("group_column")

    def analyze(self, data_loader, data_checker):
        data = data_loader.getAllData(None)
        checked = data_checker.checkFilter(data)
        summary = {
            "rows": len(data),
            "valid_rows": len(checked),
            "columns": len(data.columns),
            "has_coordinates": {"latitude", "longitude"}.issubset(data.columns),
            "compatible_with_geo_visualization": hasattr(data_loader, "getGeoData"),
            "compatible_with_column_filters": all(
                hasattr(data_loader, name)
                for name in ["getDataByColumnValue", "getDataByColumnRange", "getDataByColumnSet"]
            ),
        }
        if self.group_column and self.group_column in checked.columns:
            summary[f"{self.group_column}_non_empty"] = int(checked[self.group_column].notna().sum())
        return checked.head(self.cfg.get("preview_rows", 100)).assign(**summary)
