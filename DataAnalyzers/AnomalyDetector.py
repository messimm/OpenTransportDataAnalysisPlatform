from .BasicAnalyzer import BasicDataAnalysisModule
class AnomalyDetection(BasicDataAnalysisModule):
	def __init__(self, cfg):
		self.selection_columns=cfg["selection_columns"]
		self.selection_values =  cfg["selection_values"]
		self.detection_column = cfg["detection_column"]
		self.N_history = cfg.get("N_history", 2)
		self.thr = cfg.get('threshold', 100)
		self.mode = cfg.get('mode', "value")
		self.ts = cfg.get("ts_column", "ts")
		self.night_flag = cfg.get("night_flag", False)
		self.night_start = cfg.get("night_start", "01:00:00")
		self.night_finish = cfg.get("night_finish", "05:00:00")
		r = requests.get('https://raw.githubusercontent.com/d10xa/holidays-calendar/master/json/calendar.json')
		self.holidays = pd.to_datetime(r.json()["holidays"]).date
	
	def getType(self, date):
		return 'h' if date in self.holidays else 'w'

	def DetectAnomalies(self, data):
		data["ts"]=pd.to_datetime(data[self.ts])
		data["date"]=data["ts"].dt.date
		data["time"]=data["ts"].dt.time
		data["type"]=data["date"].apply(self.getType)
		typical = []
		anomality = []
		data.to_csv("beg_tver.csv")
		for index, row in data.iterrows():
			current_type=row["type"]
			current_time=row["time"]
			current_date=row["date"]
			history = data[data['time']==current_time]
			history = history[history['type']==current_type]
			history = history[history["date"]<current_date]
			if len(history) < self.N_history:
				typical.append(float(row[self.detection_column]))
				anomality.append(False)
			else:
				history = history.sort_values("date")[-self.N_history:]
				val = float(history[self.detection_column].mean())
				if (not self.night_flag):
					night_correction = 0  
				else:
					if current_time > pd.to_datetime(self.night_start).time() and current_time < pd.to_datetime(self.night_finish).time():
				 		night_correction = self.night_thr  
					else:
						night_correction = 0
				typical.append(val)
				if self.mode == "value":
					anomality.append(abs(row[self.detection_column]-val) > self.thr+night_correction)
				else:
					anomality.append(abs(row[self.detection_column]-val) > self.thr*val+night_correction)
		return typical, anomality


	def analyze(self, data_loader, data_checker):
		my_data = None
		for col, val in zip(self.selection_columns, self.selection_values):
			my_data = data_loader.getDataByColumnValue(my_data, col, val)
		my_data = my_data[[self.ts, self.detection_column]]
		typical, anomality = self.DetectAnomalies(my_data)
		my_data["typical"]=typical
		my_data["anomality"]=anomality
		my_data = my_data[[self.ts, self.detection_column, "typical", "anomality"]]
		graphic = my_data[[self.ts, self.detection_column]].copy()
		graphic.columns = ["x", "y"]
		points = graphic[anomality]
		return (my_data, (graphic, points))