import numpy as np
import pandas as pd
class TextReportMetroUsageVisualizer():
	def __init__(self, cfg):
		self.pattern = cfg["pattern"]
		self.path_to_save = cfg["path_to_save"]
	def visualize(self, data):
		lower, upper, m, s = data
		str_low = []
		for i, row in lower.iterrows():
			str_low.append(i+": " + str(np.round(row["ratio"], 3)*100)+"%\n")
		str_high = []
		for i, row in upper.iterrows():
			str_high.append(i+": " + str(np.round(row["ratio"], 3)*100)+"%\n")
		print("".join(str_low))
		print("".join(str_high))
		with open(self.pattern, "r") as f:
			lines = f.readlines()
		lines[1]=lines[1]+str(np.round(m, 3)*100)+"%"+"\n"
		lines[2]=lines[2]+str(np.round(s, 3)*100)+"\n"
		lines[3]=lines[3]+"\n"+"".join(str_low)+"\n"
		lines[4]=lines[4]+"\n"+"".join(str_high)+"\n"
		with open(self.path_to_save, "w") as f:
			lines = f.writelines(lines)