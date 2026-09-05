from pathlib import Path


class DataFrameToExcelVisualizer:
    def __init__(self, cfg):
        self.path_to_save = cfg["path_to_save"]

    def visualize(self, data):
        Path(self.path_to_save).expanduser().parent.mkdir(parents=True, exist_ok=True)
        data.to_excel(self.path_to_save)
