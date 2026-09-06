from pathlib import Path

import matplotlib.pyplot as plt


class GeoPointMapVisualizer:
    """Save longitude/latitude objects as a dependency-light PNG point map."""

    def __init__(self, cfg):
        self.path_to_save = cfg["path_to_save"]
        self.title = cfg.get("title", "Transport objects")
        self.point_size = cfg.get("point_size", 14)
        self.color = cfg.get("color", "#0077b6")
        self.color_column = cfg.get("color_column")
        self.colormap = cfg.get("colormap", "tab10")

    def visualize(self, data):
        Path(self.path_to_save).expanduser().parent.mkdir(parents=True, exist_ok=True)
        _, axis = plt.subplots(figsize=(8, 8))
        colors = data[self.color_column] if self.color_column else self.color
        scatter = axis.scatter(
            data["longitude"],
            data["latitude"],
            s=self.point_size,
            c=colors,
            cmap=self.colormap if self.color_column else None,
            alpha=0.75,
            edgecolors="none",
        )
        if self.color_column:
            plt.colorbar(scatter, ax=axis, label=self.color_column)
        axis.set(title=self.title, xlabel="Longitude", ylabel="Latitude")
        axis.grid(True, alpha=0.2)
        plt.tight_layout()
        plt.savefig(self.path_to_save, dpi=150)
        plt.close()
