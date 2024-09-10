import numpy as np
import pandas as pd
from .BasicChecker import BasicChecker
class MobileOperatorChecker(BasicChecker):
	def __init__(self, cfg):
		self.cfg = cfg
	def _check_metro(self, data):
		return data['customers_cnt_metro'] <= data['customers_cnt']
	def _check_home_work(self, data):
		return data['customers_cnt_home_work'] <= data['customers_cnt']
	def _check_work_home(self, data):
		return data['customers_cnt_work_home'] <= data['customers_cnt']

	def check(self, data):
		result = True
		for checker in [self._check_metro, self._check_home_work, self._check_work_home]:
			result = checker(data).all() and result	
		return result

	def checkFilter(self, data):
		result = self._check_metro(data)
		for checker in [self._check_home_work, self._check_work_home]:
			result	= np.logical_and(result, checker(data))
		return data[result]	