from pathlib import Path

import matplotlib.pyplot as plt


class GeoPointMapVisualizer:
    """Save longitude/latitude objects as a dependency-light PNG point map."""

    def __init__(self, cfg):
        self.path_to_save = cfg["path_to_save"]
        self.title = cfg.get("title", "Transport objects")
        self.point_size = cfg.get("point_size", 14)
        self.color = cfg.get("color", "#0077b6")

    def visualize(self, data):
        Path(self.path_to_save).expanduser().parent.mkdir(parents=True, exist_ok=True)
        _, axis = plt.subplots(figsize=(8, 8))
        axis.scatter(
            data["longitude"],
            data["latitude"],
            s=self.point_size,
            c=self.color,
            alpha=0.75,
            edgecolors="none",
        )
        axis.set(title=self.title, xlabel="Longitude", ylabel="Latitude")
        axis.grid(True, alpha=0.2)
        plt.tight_layout()
        plt.savefig(self.path_to_save, dpi=150)
        plt.close()
