from .BasicAnalyzer import BasicDataAnalysisModule


class GeoObjectInventoryAnalysis(BasicDataAnalysisModule):
    """Prepare a cleaned object table and map points for a geospatial registry."""

    def __init__(self, cfg=None):
        self.cfg = cfg or {}

    def analyze(self, data_loader, data_checker):
        data = data_checker.checkFilter(data_loader.getAllData(None)).copy()
        required = {"latitude", "longitude"}
        missing = required - set(data.columns)
        if missing:
            raise KeyError(f"Geo columns are missing: {', '.join(sorted(missing))}")
        data["latitude"] = data["latitude"].astype(float)
        data["longitude"] = data["longitude"].astype(float)
        return data, data
