import pandas as pd
import numpy as np
from .BasicLoader import BasicDataLoaderModule
class MobileOperatorsLoader(BasicDataLoaderModule):
	def __init__(self, cfg):
		self.data_frame = pd.read_csv(cfg["data_path"], nrows=500, sep=";")
		self.centers = np.unique(self.data_frame["departure_zid"])
		self.center_labels = pd.read_csv(cfg["labels"], sep=";")

	def labelCenter(self, center):
		return self.center_labels[self.center_labels["zone_id"]==center]

	def getAllData(self, data):
		if data is None:
			return self.data_frame
		else:
			return data

	def getDataByColumnValue(self, data, column_name, value):
		if data == None:
			return self.data_frame[self.data_frame[column_name]==value]
		else:
			return data[data[column_name]==value]

	def getDataByColumnRange(self, data, column_name, low, high):
		if data == None:
			return self.data_frame[(self.data_frame[column_name]>low) & (self.data_frame[column_name]<high)]
		else:
			return data[(data[column_name]>low) & (data[column_name]<high)]

	def getDataByColumnSet(self, data, column_name, values):
		if data == None:
			return self.data_frame[self.data_frame[column_name].isin(values)]
		else:
			return data[data[column_name].isin(values)]

	def getStaticData(self, data):
		if data == None:
			return self.data_frame[self.data_frame['departure_zid']==self.data_frame['arrival_zid']]
		else:
			return data[data['departure_zid']==data['arrival_zid']]
