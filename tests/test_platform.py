import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import requests

from DataAnalyzers.DistrictProvisionAnalyzer import DistrictObjectProvisionAnalysis
from DataAnalyzers.BikeShareAvailabilityAnalyzer import BikeShareAvailabilityAnalysis
from DataAnalyzers.ServiceStatusAnalyzer import ServiceStatusAnalysis
from DataAnalyzers.GTFSServiceSupplyAnalyzer import GTFSServiceSupplyAnalysis
from DataAnalyzers.DeparturePunctualityAnalyzer import DeparturePunctualityAnalysis
from DataAnalyzers.GeoClusteringAnalyzer import GeoKMeansAnalysis
from DataAnalyzers.GTFSStopClusterAnalyzer import GTFSStopClusterAnalysis
from DataAnalyzers.RobustAnomalyAnalyzer import RobustNumericAnomalyAnalysis
from DataCheckers.DataFrameFilterChecker import DataFrameColumnFilterChecker
from DataCheckers.DataMosChecker import DataMosGeoChecker
from DataLoaders.DataMosLoaders import MoscowStreetParkingLoader
from DataLoaders.DistrictDataLoaders import DistrictPopulationLoader
from DataLoaders.GBFSDataLoader import GBFSStationInformationLoader, GBFSStationStatusLoader
from DataLoaders.TfLDataLoader import TfLLineStatusLoader
from DataLoaders.GTFSDataLoader import GTFSFeedLoader
from DataLoaders.SwissTransportDataLoader import SwissStationboardLoader
from DataLoaders.AirportDataLoader import OurAirportsLoader
from DataVisualizers.DataFrameToCsvVisualizer import DataFrameToCsvVisualizer
from launch_from_cfg import load_config, pipeline_from_config


FIXTURES = Path(__file__).parent / "fixtures"


class PlatformTests(unittest.TestCase):
    def test_airport_clustering_is_reproducible(self):
        loader = OurAirportsLoader(
            {"data_path": str(FIXTURES / "ourairports_sample.csv")}
        )
        checker = DataFrameColumnFilterChecker({"not_empty": ["airport_id"]})
        table, points = GeoKMeansAnalysis(
            {"n_clusters": 3, "random_state": 42}
        ).analyze(loader, checker)
        self.assertEqual(table["cluster"].nunique(), 3)
        self.assertEqual(table["cluster"].tolist(), points["cluster"].tolist())

    def test_gtfs_station_clustering_uses_service_intensity(self):
        loader = GTFSFeedLoader({"data_path": str(FIXTURES / "gtfs_sample")})
        checker = DataFrameColumnFilterChecker({"not_empty": ["stop_id"]})
        table, _ = GTFSStopClusterAnalysis({"n_clusters": 2}).analyze(loader, checker)
        self.assertIn("stop_events", table)
        self.assertEqual(table["cluster"].nunique(), 2)

    def test_robust_anomaly_detection_finds_large_delay(self):
        loader = SwissStationboardLoader(
            {"data_path": str(FIXTURES / "swiss_stationboard_anomaly.json")}
        )
        checker = DataFrameColumnFilterChecker({"ranges": {"delay_minutes": {"min": 0}}})
        table, report = RobustNumericAnomalyAnalysis(
            {"column": "delay_minutes", "threshold": 3.5}
        ).analyze(loader, checker)
        self.assertEqual(report["metrics"]["anomalies"], 1)
        self.assertEqual(table.iloc[0]["delay_minutes"], 30)

    def test_commuter_rail_filter_keeps_gtfs_route_type_two(self):
        loader = GTFSFeedLoader({"data_path": str(FIXTURES / "gtfs_sample")})
        table, _ = GTFSServiceSupplyAnalysis({"route_types": [2]}).analyze(loader, None)
        self.assertEqual(table["route_id"].tolist(), ["R1"])

    def test_gtfs_service_supply_ranks_routes(self):
        loader = GTFSFeedLoader({"data_path": str(FIXTURES / "gtfs_sample")})
        table, report = GTFSServiceSupplyAnalysis().analyze(loader, None)
        self.assertEqual(table.iloc[0]["route_id"], "R1")
        self.assertEqual(report["metrics"]["trips_total"], 3)
        self.assertEqual(report["metrics"]["stops_total"], 3)

    def test_departure_punctuality_classifies_delays(self):
        loader = SwissStationboardLoader(
            {"data_path": str(FIXTURES / "swiss_stationboard.json")}
        )
        checker = DataFrameColumnFilterChecker({"not_empty": ["line"]})
        table, report = DeparturePunctualityAnalysis(
            {"delay_threshold_minutes": 3}
        ).analyze(loader, checker)
        self.assertEqual(report["metrics"]["delayed_departures"], 1)
        self.assertEqual(report["metrics"]["unknown_predictions"], 1)
        self.assertEqual(table.iloc[0]["punctuality_state"], "delayed")

    def test_bikeshare_availability_detects_empty_and_full_stations(self):
        information = GBFSStationInformationLoader(
            {"data_path": str(FIXTURES / "gbfs_station_information.json")}
        )
        status = GBFSStationStatusLoader(
            {"data_path": str(FIXTURES / "gbfs_station_status.json")}
        )
        checker = DataFrameColumnFilterChecker({"not_empty": ["station_id"]})
        table, points = BikeShareAvailabilityAnalysis().analyze(
            [information, status], [checker, checker]
        )
        states = set(table["availability_state"])
        self.assertIn("empty", states)
        self.assertIn("near_full", states)
        self.assertEqual(len(points), 3)

    def test_tfl_status_analysis_reports_disruption(self):
        loader = TfLLineStatusLoader(
            {"data_path": str(FIXTURES / "tfl_line_status.json")}
        )
        checker = DataFrameColumnFilterChecker({"not_empty": ["line_id", "status"]})
        table, report = ServiceStatusAnalysis().analyze(loader, checker)
        self.assertEqual(report["metrics"]["lines_total"], 3)
        self.assertEqual(report["metrics"]["disrupted_lines"], 1)
        self.assertEqual(table.iloc[0]["line_id"], "district")

    @patch("DataLoaders.GBFSDataLoader.requests.get")
    def test_gbfs_online_config_downloads_and_writes_csv_and_map(self, get):
        response = get.return_value
        response.raise_for_status.return_value = None
        response.json.return_value = json.loads(
            (FIXTURES / "gbfs_station_information.json").read_text(encoding="utf-8")
        )
        config = load_config("Configs/WorldGBFSBikeStationsOnline.json")
        with tempfile.TemporaryDirectory() as directory:
            for visualizer in config["DataVisualizers"]:
                visualizer["Parameters"]["path_to_save"] = str(
                    Path(directory) / Path(visualizer["Parameters"]["path_to_save"]).name
                )
            pipeline_from_config(config)
            self.assertTrue((Path(directory) / "world_gbfs_bike_stations.csv").is_file())
            self.assertTrue((Path(directory) / "world_gbfs_bike_stations_map.png").is_file())

    @patch("DataLoaders.GBFSDataLoader.requests.get")
    def test_gbfs_loader_falls_back_when_network_is_unavailable(self, get):
        get.side_effect = requests.ConnectionError("offline")
        loader = GBFSStationInformationLoader(
            {
                "url": "https://example.invalid/station_information.json",
                "fallback_path": str(FIXTURES / "gbfs_station_information.json"),
            }
        )
        self.assertEqual(loader.source, "fallback_cache")
        self.assertEqual(len(loader.getAllData()), 3)

    @patch("DataLoaders.DataMosLoaders.requests.get")
    def test_online_loader_uses_data_mos_api_and_normalizes_geojson(self, get):
        response = get.return_value
        response.raise_for_status.return_value = None
        response.json.return_value = [
            {
                "Cells": {
                    "ParkingName": "Online parking",
                    "ParkingNumber": "P1",
                    "geoData": {"type": "Point", "coordinates": [37.61, 55.75]},
                }
            }
        ]
        loader = MoscowStreetParkingLoader({"rows_limit": 1})
        row = loader.getAllData().iloc[0]
        self.assertEqual(row["longitude"], 37.61)
        self.assertEqual(row["latitude"], 55.75)
        self.assertIn("apidata.mos.ru", get.call_args.args[0])

    @patch("DataLoaders.DataMosLoaders.requests.get")
    def test_online_config_downloads_and_writes_output(self, get):
        response = get.return_value
        response.raise_for_status.return_value = None
        response.json.return_value = [
            {
                "Cells": {
                    "ParkingName": "Online parking",
                    "ParkingNumber": "P1",
                    "CarCapacity": 12,
                    "geoData": {"type": "Point", "coordinates": [37.61, 55.75]},
                }
            }
        ]
        config = load_config("Configs/DataMosStreetParkingOnline.json")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "online.csv"
            config["DataVisualizers"][0]["Parameters"]["path_to_save"] = str(output)
            pipeline_from_config(config)
            self.assertTrue(output.is_file())
            self.assertIn("Online parking", output.read_text(encoding="utf-8"))

    def test_datamos_loader_normalizes_and_limits_json(self):
        loader = MoscowStreetParkingLoader(
            {"data_path": str(FIXTURES / "datamos_district_rows.json"), "rows_limit": 1}
        )
        self.assertEqual(len(loader.getAllData()), 1)
        self.assertIn("capacity", loader.getAllData().columns)

    def test_geo_operations_require_coordinates(self):
        loader = MoscowStreetParkingLoader({"data_path": str(FIXTURES / "datamos_rows.json")})
        self.assertEqual(len(loader.getGeoData()), 1)
        with self.assertRaises(KeyError):
            DataMosGeoChecker({"require_coordinates": True}).checkFilter(pd.DataFrame({"name": ["x"]}))

    def test_filter_reports_configuration_error_for_missing_column(self):
        checker = DataFrameColumnFilterChecker({"not_empty": ["district"]})
        with self.assertRaises(KeyError):
            checker.checkFilter(pd.DataFrame({"name": ["x"]}))

    def test_provision_analysis_handles_zero_object_district(self):
        objects = MoscowStreetParkingLoader(
            {
                "data_path": str(FIXTURES / "datamos_district_rows.json"),
                "columns_map": {"District": "district"},
            }
        )
        population = DistrictPopulationLoader({"data_path": str(FIXTURES / "district_population.csv")})
        object_checker = DataFrameColumnFilterChecker({"not_empty": ["district"]})
        population_checker = DataFrameColumnFilterChecker({"ranges": {"population": {"min": 1}}})
        result = DistrictObjectProvisionAnalysis(
            {"capacity_column": "capacity", "level_metric": "capacity_per_population"}
        ).analyze([objects, population], [object_checker, population_checker])
        basmanny = result[result["district"] == "Басманный район"].iloc[0]
        self.assertEqual(basmanny["object_count"], 0)
        self.assertEqual(basmanny["capacity_per_population"], 0)

    def test_csv_visualizer_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "result.csv"
            DataFrameToCsvVisualizer({"path_to_save": str(output)}).visualize(pd.DataFrame({"x": [1]}))
            self.assertTrue(output.is_file())

    def test_example_pipeline_runs_offline(self):
        config = load_config("Configs/DataMosStreetParkingDistrictProvision.json")
        with tempfile.TemporaryDirectory() as directory:
            for visualizer in config["DataVisualizers"]:
                params = visualizer["Parameters"]
                for key in ("path_to_save", "csv_prefix"):
                    if key in params:
                        params[key] = str(Path(directory) / Path(params[key]).name)
            pipeline_from_config(config)
            self.assertTrue((Path(directory) / "street_parking_district_provision_summary.csv").is_file())
            self.assertTrue((Path(directory) / "street_parking_district_provision_map.png").is_file())


if __name__ == "__main__":
    unittest.main()
