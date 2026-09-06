from pathlib import Path


class StructuredTextReportVisualizer:
    """Write a title, scalar metrics and an optional table to UTF-8 text."""

    def __init__(self, cfg):
        self.path_to_save = cfg["path_to_save"]

    def visualize(self, data):
        path = Path(self.path_to_save).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            file.write(f"{data.get('title', 'Report')}\n\n")
            for name, value in data.get("metrics", {}).items():
                file.write(f"{name}: {value}\n")
            table = data.get("table")
            if table is not None:
                file.write("\n")
                file.write(table.to_string(index=False))
                file.write("\n")
