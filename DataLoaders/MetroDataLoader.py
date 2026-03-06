import numpy as np
import pandas as pd

from .BasicLoader import BasicDataLoaderModule


class MetroDataLoader(BasicDataLoaderModule):
    def __init__(self, cfg):
        self.data_frame = pd.read_csv(
            cfg["data_path"],
            nrows=50000000,
            sep=";",
            names=[
                "ts",
                "id_vest",
                "id_val",
                "number_ticket",
                "number_crystal",
                "type_ticket",
                "type_pass",
                "trip_num",
                "trips",
            ],
        )
        self.centers = np.unique(self.data_frame["id_vest"])
        self.center_labels = pd.read_csv(cfg["labels"], sep=";", encoding="utf-8")

    def labelCenter(self, center):
        return self.center_labels[self.center_labels["PL_ID"] == center]

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

    def getDataByTimeRange(self, data, t1, t2):
        source = self.data_frame if data is None else data
        source = source.copy()
        source["time"] = pd.to_datetime(source["ts"]).dt.time
        return source[np.logical_and(source["time"] > t1, source["time"] < t2)]
