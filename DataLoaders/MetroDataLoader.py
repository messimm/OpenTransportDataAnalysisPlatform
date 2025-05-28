class MetroDataLoader(BasicDataLoaderModule):
	def __init__(self, cfg):
		self.data_frame = pd.read_csv(cfg["data_path"], nrows=50000000, sep=";", names=["ts","id_vest","id_val","number_ticket","number_crystal","type_ticket","type_pass","trip_num","trips"])
		self.centers = np.unique(self.data_frame["id_vest"])
		self.center_labels = pd.read_csv(cfg["labels"], sep=";", encoding="utf-8")
	def labelCenter(self, center):
		return self.center_labels[self.center_labels["PL_ID"]==center]

	def getAllData(self, data):
		if data is None:
			return self.data_frame
		else:
			return data

	def getDataByColumnValue(self, data, column_name, value):
		if data is None:
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
	def getDataByTimeRange(self, data, t1, t2):
		data['time']=pd.to_datetime(data['ts']).dt.time
		return data[np.logical_and(data["time"] > t1, data["time"] < t2)]