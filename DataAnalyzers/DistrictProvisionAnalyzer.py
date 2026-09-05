import pandas as pd

from .BasicAnalyzer import BasicDataAnalysisModule


class DistrictObjectProvisionAnalysis(BasicDataAnalysisModule):
    """Analyze district provision with transport objects per resident.

    Expects two loaders in the pipeline: an object loader and a district
    population loader. The object data must contain a district-like column or it
    can be configured through `object_district_column`.
    """

    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.object_district_column = self.cfg.get("object_district_column", "district")
        self.population_district_column = self.cfg.get("population_district_column", "district")
        self.population_column = self.cfg.get("population_column", "population")
        self.capacity_column = self.cfg.get("capacity_column")
        self.per_population = self.cfg.get("per_population", 100000)
        self.low_threshold = self.cfg.get("low_threshold")
        self.high_threshold = self.cfg.get("high_threshold")
        self.object_name = self.cfg.get("object_name", "objects")
        self.outputs = self.cfg.get("outputs")
        self.top_n = self.cfg.get("top_n", 10)
        if self.per_population <= 0:
            raise ValueError("per_population must be positive")
        if self.top_n <= 0:
            raise ValueError("top_n must be positive")

    def analyze(self, data_loader, data_checker):
        object_loader, population_loader = data_loader
        object_checker, population_checker = data_checker

        objects = object_checker.checkFilter(object_loader.getAllData(None)).copy()
        population = population_checker.checkFilter(population_loader.getAllData(None)).copy()

        if self.object_district_column not in objects.columns:
            raise KeyError(f"Object data must contain '{self.object_district_column}' column")
        if self.population_district_column not in population.columns:
            raise KeyError(f"Population data must contain '{self.population_district_column}' column")
        if self.population_column not in population.columns:
            raise KeyError(f"Population data must contain '{self.population_column}' column")

        objects[self.object_district_column] = objects[self.object_district_column].astype(str).str.strip()
        population[self.population_district_column] = population[self.population_district_column].astype(str).str.strip()
        population[self.population_column] = pd.to_numeric(population[self.population_column], errors="coerce")
        population = population[population[self.population_column] > 0]
        if population.empty:
            raise ValueError("Population data has no valid positive values")
        population = population.groupby(self.population_district_column, as_index=False)[self.population_column].sum()

        grouped = objects.groupby(self.object_district_column).size().rename("object_count").to_frame()
        if self.capacity_column and self.capacity_column in objects.columns:
            grouped["capacity_total"] = pd.to_numeric(objects[self.capacity_column], errors="coerce").groupby(
                objects[self.object_district_column]
            ).sum()

        result = population[[self.population_district_column, self.population_column]].rename(
            columns={self.population_district_column: "district", self.population_column: "population"}
        )
        result = result.merge(grouped, how="left", left_on="district", right_index=True)
        result["object_count"] = result["object_count"].fillna(0).astype(int)
        if "capacity_total" in result.columns:
            result["capacity_total"] = result["capacity_total"].fillna(0)

        result["objects_per_population"] = result["object_count"] / result["population"] * self.per_population
        if "capacity_total" in result.columns:
            result["capacity_per_population"] = result["capacity_total"] / result["population"] * self.per_population

        metric = self.cfg.get("level_metric", "objects_per_population")
        if metric not in result.columns:
            raise KeyError(f"Provision metric '{metric}' is unavailable")
        low_threshold = self.low_threshold if self.low_threshold is not None else result[metric].quantile(0.25)
        high_threshold = self.high_threshold if self.high_threshold is not None else result[metric].quantile(0.75)
        if low_threshold > high_threshold:
            raise ValueError("low_threshold cannot be greater than high_threshold")

        result["provision_level"] = "medium"
        result.loc[result[metric] <= low_threshold, "provision_level"] = "low"
        result.loc[result[metric] >= high_threshold, "provision_level"] = "high"
        if self.low_threshold is None:
            self.low_threshold = result[metric].quantile(0.25)
        if self.high_threshold is None:
            self.high_threshold = result[metric].quantile(0.75)

        result["provision_level"] = "medium"
        result.loc[result[metric] <= self.low_threshold, "provision_level"] = "low"
        result.loc[result[metric] >= self.high_threshold, "provision_level"] = "high"
        result["object_type"] = self.object_name
        result = result.sort_values(metric)

        if not self.outputs:
            return result

        output_map = {
            "summary": result,
            "top_report": self._build_top_report(result, metric),
            "map_points": self._build_map_points(objects, result, metric),
        }
        unknown_outputs = set(self.outputs) - set(output_map)
        if unknown_outputs:
            raise ValueError(f"Unknown analyzer outputs: {', '.join(sorted(unknown_outputs))}")
        return [output_map[name] for name in self.outputs]

    def _build_top_report(self, result, metric):
        sorted_result = result.sort_values(metric, ascending=False)
        return {
            "metric": metric,
            "object_type": self.object_name,
            "top": sorted_result.head(self.top_n).copy(),
            "bottom": sorted_result.tail(self.top_n).sort_values(metric).copy(),
        }

    def _build_map_points(self, objects, result, metric):
        if not {"latitude", "longitude"}.issubset(objects.columns):
            return pd.DataFrame(columns=["district", "latitude", "longitude", metric, "provision_level", "object_type"])
        provision = result[["district", metric, "provision_level", "object_type"]]
        points = objects.rename(columns={self.object_district_column: "district"}).merge(
            provision, how="left", on="district"
        )
        keep_columns = [
            column
            for column in ["district", "latitude", "longitude", metric, "provision_level", "object_type"]
            if column in points.columns
        ]
        return points[keep_columns].dropna(subset=["latitude", "longitude"])
