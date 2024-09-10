import pandas as pd
class DataFrameToExcelVisualizer():
	def __init__(self, cfg):
		self.path_to_save = cfg["path_to_save"]
	def visualize(self, data):
		data.to_excel(self.path_to_save)