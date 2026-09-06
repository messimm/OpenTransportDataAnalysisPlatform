from pathlib import Path


class DataFrameToCsvVisualizer:
    """Save a pandas DataFrame to CSV without optional Excel dependencies."""

    def __init__(self, cfg):
        self.path_to_save = cfg["path_to_save"]
        self.index = cfg.get("index", False)

    def visualize(self, data):
        Path(self.path_to_save).expanduser().parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(self.path_to_save, index=self.index)
