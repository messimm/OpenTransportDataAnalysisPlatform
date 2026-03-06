# -*- coding: utf-8 -*-


class BasicDataLoaderModule:
    def __init__(self):
        self.centers = []
        self.center_labels = []

    def labelCenter(self, center):
        raise NotImplementedError
