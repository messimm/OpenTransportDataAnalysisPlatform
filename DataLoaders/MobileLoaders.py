import numpy as np
import pandas as pd

from .BasicLoader import BasicDataLoaderModule


class MobileOperatorsLoader(BasicDataLoaderModule):
    def __init__(self, cfg):
        self.data_frame = pd.read_csv(cfg["data_path"], nrows=500, sep=";")
        self.centers = np.unique(self.data_frame["departure_zid"])
        self.center_labels = pd.read_csv(cfg["labels"], sep=";")

    def labelCenter(self, center):
        return self.center_labels[self.center_labels["zone_id"] == center]

    def getAllData(self, data):
        return self.data_frame if data is None else data

    def getDataByColumnValue(self, data, column_name, value):
        source = self.data_frame if data is None else data
        return source[source[column_name] == value]

    def getDataByColumnRange(self, data, column_name, low, high):
        source = self.data_frame if data is None else data
        return source[(source[column_name] > low) & (source[column_name] < high)]

    def getDataByColumnSet(self, data, column_name, values):
        source = self.data_frame if data is None else data
        return source[source[column_name].isin(values)]

    def getStaticData(self, data):
        source = self.data_frame if data is None else data
        return source[source["departure_zid"] == source["arrival_zid"]]
