import pandas as pd
from sklearn.cluster import KMeans

from .BasicAnalyzer import BasicDataAnalysisModule


class HoodTypeAnalysis(BasicDataAnalysisModule):
    def __init__(self, cfg):
        self.n_clusters = cfg.get("n_clusters", 5)

    def analyze(self, data_loader, data_checker):
        required_methods = ["getStaticData", "getMoscowData", "getDataByTime", "getDataByDayType", "labelCenter"]
        missing = [name for name in required_methods if not hasattr(data_loader, name)]
        if missing:
            raise AttributeError(f"HoodTypeAnalysis requires loader methods: {', '.join(missing)}")

        static = data_loader.getStaticData(None)
        moscow_static = data_loader.getMoscowData(static, "departure_zid")
        maxs = moscow_static.groupby(["departure_zid"]).max()["customers_cnt_static"]
        moscow_night = data_loader.getDataByTime(
            moscow_static,
            pd.to_datetime("01:00:00").time(),
            pd.to_datetime("06:00:00").time(),
        )
        moscow_day = data_loader.getDataByTime(
            moscow_static,
            pd.to_datetime("11:00:00").time(),
            pd.to_datetime("17:00:00").time(),
        )
        moscow_day = data_loader.getDataByDayType(moscow_day, "weekdays")
        moscow_night = moscow_night[["departure_zid", "customers_cnt_static"]].groupby(["departure_zid"]).mean()
        moscow_day = moscow_day[["departure_zid", "customers_cnt_static"]].groupby(["departure_zid"]).mean()
        moscow_night["night_rate"] = moscow_night["customers_cnt_static"] / maxs
        moscow_day["day_rate"] = moscow_day["customers_cnt_static"] / maxs

        data_for_cluster = moscow_day.copy()
        data_for_cluster["night_rate"] = moscow_night["night_rate"]
        data_for_cluster = data_for_cluster[["day_rate", "night_rate"]].dropna()

        clusterizer = KMeans(n_clusters=self.n_clusters)
        types = clusterizer.fit_predict(data_for_cluster)
        data_for_cluster["type"] = types
        data_for_cluster.index = data_for_cluster.index.map(lambda x: data_loader.labelCenter(x)["Name"].values[0])

        data_for_plot = data_for_cluster.copy()
        data_for_plot.columns = ["x", "y", "color"]
        return data_for_cluster, data_for_plot
