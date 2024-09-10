import numpy as np
import pandas as pd
from .BasicAnalyzer import BasicDataAnalysisModule
class MetroUsageDataAnalysis(BasicDataAnalysisModule):
	def __init__(self, cfg):
		self.thr = cfg["threshold"]
	def analyze(self, data_loader, data_checker):
		my_data = data_loader.getAllData(None)
		my_data_checked = data_checker.checkFilter(my_data)
		my_data_grouped = my_data_checked.groupby(['departure_zid']).sum()
		my_data_grouped = my_data_grouped[["customers_cnt", "customers_cnt_metro"]]
		my_data_grouped["ratio"] = my_data_grouped["customers_cnt_metro"]/my_data_grouped["customers_cnt"]
		my_data_grouped.index = my_data_grouped.index.map(lambda x: data_loader.labelCenter(x)["Name"].values[0])
		m = my_data_grouped["ratio"].mean()
		s = my_data_grouped["ratio"].std()
		upper = my_data_grouped[my_data_grouped["ratio"] > (m + (self.thr*s))].sort_values("ratio")
		lower = my_data_grouped[my_data_grouped["ratio"] < (m - (self.thr*s))].sort_values("ratio")

		return	(my_data_grouped.sort_values("ratio"), (lower, upper, m, s))	