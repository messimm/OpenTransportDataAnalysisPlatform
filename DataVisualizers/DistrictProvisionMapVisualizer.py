import matplotlib.pyplot as plt
from pathlib import Path


class DistrictProvisionMapVisualizer:
    """Save a simple point map for provision analysis results.

    The visualizer intentionally avoids heavy GIS dependencies: it plots object
    longitude/latitude points and colors them by district provision level.
    """

    def __init__(self, cfg):
        self.path_to_save = cfg["path_to_save"]
        self.title = cfg.get("title", "District provision map")
        self.color_map = cfg.get("color_map", {"low": "#d95f02", "medium": "#7570b3", "high": "#1b9e77"})
        self.point_size = cfg.get("point_size", 35)

    def visualize(self, data):
        Path(self.path_to_save).expanduser().parent.mkdir(parents=True, exist_ok=True)
        plt.figure(figsize=(8, 8))
        if data.empty:
            plt.title(self.title)
            plt.text(0.5, 0.5, "No geocoded objects", ha="center", va="center")
            plt.axis("off")
            plt.savefig(self.path_to_save)
            plt.close()
            return

        colors = data.get("provision_level", "medium").map(self.color_map)
        plt.scatter(data["longitude"], data["latitude"], c=colors, s=self.point_size, alpha=0.8, edgecolors="black")
        for level, color in self.color_map.items():
            plt.scatter([], [], c=color, label=level, s=self.point_size)
        plt.title(self.title)
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.legend(title="Provision level")
        plt.grid(True, alpha=0.25)
        plt.tight_layout()
        plt.savefig(self.path_to_save)
        plt.close()
