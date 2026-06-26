class DistrictProvisionTopReportVisualizer:
    """Save top/bottom district provision report as text and optional CSV files."""

    def __init__(self, cfg):
        self.path_to_save = cfg["path_to_save"]
        self.csv_prefix = cfg.get("csv_prefix")
        self.columns = cfg.get("columns")

    def visualize(self, data):
        metric = data["metric"]
        top = data["top"]
        bottom = data["bottom"]
        columns = self.columns or [
            column
            for column in ["district", "population", "object_count", "capacity_total", metric, "provision_level"]
            if column in top.columns or column in bottom.columns
        ]

        with open(self.path_to_save, "w", encoding="utf-8") as f:
            f.write(f"Provision report for {data['object_type']}\n")
            f.write(f"Metric: {metric}\n\n")
            f.write("TOP districts\n")
            f.write(top[columns].to_string(index=False))
            f.write("\n\nBOTTOM districts\n")
            f.write(bottom[columns].to_string(index=False))
            f.write("\n")

        if self.csv_prefix:
            top[columns].to_csv(f"{self.csv_prefix}_top.csv", index=False)
            bottom[columns].to_csv(f"{self.csv_prefix}_bottom.csv", index=False)
