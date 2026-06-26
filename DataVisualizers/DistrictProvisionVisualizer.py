import matplotlib.pyplot as plt


class DistrictProvisionBarVisualizer:
    """Save a district provision bar chart from DistrictObjectProvisionAnalysis."""

    def __init__(self, cfg):
        self.path_to_save = cfg["path_to_save"]
        self.metric = cfg.get("metric", "objects_per_population")
        self.title = cfg.get("title", "District object provision")
        self.xlabel = cfg.get("xlabel", "District")
        self.ylabel = cfg.get("ylabel", self.metric)
        self.top_n = cfg.get("top_n")
        self.color_map = cfg.get("color_map", {"low": "#d95f02", "medium": "#7570b3", "high": "#1b9e77"})

    def visualize(self, data):
        plot_data = data.sort_values(self.metric, ascending=False)
        if self.top_n:
            plot_data = plot_data.head(self.top_n)
        colors = plot_data.get("provision_level", "medium").map(self.color_map) if "provision_level" in plot_data else None
        plt.figure(figsize=(max(8, len(plot_data) * 0.6), 5))
        plt.bar(plot_data["district"], plot_data[self.metric], color=colors)
        plt.title(self.title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(self.path_to_save)
        plt.close()
