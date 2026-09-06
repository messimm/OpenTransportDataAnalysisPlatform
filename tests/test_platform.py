import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import requests

from DataAnalyzers.DistrictProvisionAnalyzer import DistrictObjectProvisionAnalysis
from DataCheckers.DataFrameFilterChecker import DataFrameColumnFilterChecker
from DataCheckers.DataMosChecker import DataMosGeoChecker
from DataLoaders.DataMosLoaders import MoscowStreetParkingLoader
from DataLoaders.DistrictDataLoaders import DistrictPopulationLoader
from DataLoaders.GBFSDataLoader import GBFSStationInformationLoader
from DataVisualizers.DataFrameToCsvVisualizer import DataFrameToCsvVisualizer
from launch_from_cfg import load_config, pipeline_from_config


FIXTURES = Path(__file__).parent / "fixtures"


class PlatformTests(unittest.TestCase):
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
