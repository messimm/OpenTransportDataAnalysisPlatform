import matplotlib.pyplot as plt
from pathlib import Path


class ScatterPlotVisualizer:
    def __init__(self, cfg):
        self.path_to_save = cfg["path_to_save"]
        self.name = cfg["name"]
        self.xlabel = cfg["xlabel"]
        self.ylabel = cfg["ylabel"]
        self.legend = cfg["legend"]

    def visualize(self, data):
        Path(self.path_to_save).expanduser().parent.mkdir(parents=True, exist_ok=True)
        plt.figure()
        scatter = plt.scatter(x=data["x"], y=data["y"], c=data["color"])
        plt.title(self.name)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.legend(*scatter.legend_elements(), loc="lower left", title=self.legend)
        plt.plot()
        plt.savefig(self.path_to_save)
        plt.close()
