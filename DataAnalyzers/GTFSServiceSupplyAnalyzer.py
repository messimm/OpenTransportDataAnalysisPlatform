import pandas as pd

from .BasicAnalyzer import BasicDataAnalysisModule


class GTFSServiceSupplyAnalysis(BasicDataAnalysisModule):
    """Estimate scheduled service supply by route from a static GTFS feed."""

    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.route_types = {str(value) for value in self.cfg.get("route_types", [])}

    def analyze(self, data_loader, data_checker):
        routes = data_loader.getTable("routes").copy()
        trips = data_loader.getTable("trips").copy()
        stop_times = data_loader.getTable("stop_times").copy()
        if self.route_types:
            if "route_type" not in routes:
                raise KeyError("GTFS routes column 'route_type' is required for filtering")
            routes = routes[routes["route_type"].isin(self.route_types)]
            trips = trips[trips["route_id"].isin(routes["route_id"])]
            stop_times = stop_times[stop_times["trip_id"].isin(trips["trip_id"])]
        required = {
            "routes": {"route_id"},
            "trips": {"route_id", "trip_id"},
            "stop_times": {"trip_id", "stop_id", "departure_time"},
        }
        for name, columns in required.items():
            missing = columns - set(data_loader.getTable(name).columns)
            if missing:
                raise KeyError(f"GTFS {name} columns are missing: {', '.join(sorted(missing))}")

        events = trips[["route_id", "trip_id"]].merge(
            stop_times[["trip_id", "stop_id", "departure_time"]], on="trip_id", how="inner"
        )
        supply = events.groupby("route_id").agg(
            trips_count=("trip_id", "nunique"),
            stops_count=("stop_id", "nunique"),
            stop_events=("stop_id", "size"),
            first_departure=("departure_time", "min"),
            last_departure=("departure_time", "max"),
        )
        labels = [column for column in ("route_id", "route_short_name", "route_long_name") if column in routes]
        result = routes[labels].drop_duplicates("route_id").merge(supply, on="route_id", how="left")
        for column in ("trips_count", "stops_count", "stop_events"):
            result[column] = result[column].fillna(0).astype(int)
        result["supply_score"] = result["trips_count"] * result["stops_count"]
        result = result.sort_values("supply_score", ascending=False)
        report = {
            "title": "GTFS scheduled service supply",
            "metrics": {
                "routes_total": int(result["route_id"].nunique()),
                "trips_total": int(trips["trip_id"].nunique()),
                "stops_total": int(stop_times["stop_id"].nunique()),
            },
            "table": result,
        }
        return result, report
