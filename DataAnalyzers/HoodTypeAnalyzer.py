from .BasicAnalyzer import BasicDataAnalysisModule
class HoodTypeAnalysis(BasicDataAnalysisModule):
	def __init__(self, cfg):
		self.n_clusters = cfg["n_clusters"]

	def analyze(self, data_loader, data_checker):
		static = data_loader.getStaticData(None)
		moscow_static = data_loader.getMoscowData(static, "departure_zid")
		maxs = moscow_static.groupby(["departure_zid"]).max()["customers_cnt_static"]
		moscow_night = data_loader.getDataByTime(moscow_static, pd.to_datetime("01:00:00").time(), pd.to_datetime("06:00:00").time()) 
		moscow_day = data_loader.getDataByTime(moscow_static, pd.to_datetime("11:00:00").time(), pd.to_datetime("17:00:00").time())
		moscow_day = data_loader.getDataByDayType(moscow_day, "weekdays")
		moscow_night = moscow_night[["departure_zid", "customers_cnt_static"]].groupby(["departure_zid"]).mean()
		moscow_day = moscow_day[["departure_zid","customers_cnt_static"]].groupby(["departure_zid"]).mean()
		moscow_night["night_rate"] = moscow_night["customers_cnt_static"] / maxs
		moscow_day["day_rate"] = moscow_day["customers_cnt_static"] / maxs
		data_for_cluster = moscow_day
		data_for_cluster["night_rate"] = moscow_night["night_rate"]
		data_for_cluster = data_for_cluster[["day_rate", "night_rate"]]
		clusterizer = KMeans(n_clusters=5)
		types = clusterizer.fit_predict(data_for_cluster)
		data_for_cluster["type"] = types
		data_for_cluster.index = data_for_cluster.index.map(lambda x: data_loader.labelCenter(x)["Name"].values[0])
		data_for_plot = data_for_cluster.copy()
		data_for_plot.columns = ["x", "y", "color"]
		return (data_for_cluster, data_for_plot)