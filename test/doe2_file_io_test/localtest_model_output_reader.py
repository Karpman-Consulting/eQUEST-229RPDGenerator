import unittest
from pathlib import Path

from rpd_generator.config import Config
from rpd_generator.utilities import validate_configuration
from rpd_generator.doe2_worker.api import get_string_result_32, get_multiple_results_32


# THIS CAN ONLY BE RUN LOCALLY. DO NOT RUN ON CI/CD
validate_configuration.find_equest_installation()


class TestModelInputReader(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.d2_result_dll = str(Path(Config.EQUEST_INSTALL_PATH) / "D2Result.dll")
        self.doe2_data_path = Config.DOE23_DATA_PATH
        self.test_file = str(
            Path(__file__).parents[2]
            / "test"
            / "full_rpd_test"
            / "E-2"
            / "229 Test Case E-2 (CHW VAV).BDL"
        )

    def test_get_string_result(self):
        entry_id = 1101006

        result = get_string_result_32(
            d2_result_dll=self.d2_result_dll,
            doe2_data_dir=self.doe2_data_path,
            project_fname=str(Path(self.test_file).with_suffix("")),
            entry_id=entry_id,
        )

        expected_result = "DENVER INTL AP    CO"

        self.assertEqual(expected_result, result)

    def test_get_multiple_results_simple(self):
        requests = [
            (2401002, "", "Hot Water Pumps"),
            (2401005, "", "Hot Water Pumps"),
            (2401006, "", "Hot Water Pumps"),
            (2401007, "", "Hot Water Pumps"),
        ]

        results = get_multiple_results_32(
            d2_result_dll=self.d2_result_dll,
            doe2_data_dir=self.doe2_data_path,
            project_fname=str(Path(self.test_file).with_suffix("")),
            requests=requests,
        )

        expected_results = [
            15.756841659545898,
            0.29863861203193665,
            0.7699999809265137,
            0.5960000157356262,
        ]

        self.assertEqual(expected_results, results)

    def test_get_multiple_results_cost(self):
        requests = [
            (3005012, "Custom Elec Rate", ""),
            (3005013, "Custom Elec Rate", ""),
            (3005012, "Custom Gas Rate", ""),
            (3005013, "Custom Gas Rate", ""),
        ]

        results = get_multiple_results_32(
            d2_result_dll=self.d2_result_dll,
            doe2_data_dir=self.doe2_data_path,
            project_fname=str(Path(self.test_file).with_suffix("")),
            requests=requests,
        )

        expected_results = [0.07000000774860382, 11612.0, 0.5, 4951.0]

        self.assertEqual(expected_results, results)

    def test_get_multiple_results_cost_bug(self):
        """
        This test demonstrates that output requests are sometimes not fulfilled based on the combination of requests.
        The Custom Elec and Gas Rate requestss are not fulfilled when combined with the FM1 requests.
        However, in the previous test, they are fulfilled when they are on their own.
        """
        requests = [
            (2310067, "FM1", ""),
            (2310068, "FM1", ""),
            (2310069, "FM1", ""),
            (3005012, "Custom Elec Rate", ""),
            (3005013, "Custom Elec Rate", ""),
            (3005012, "Custom Gas Rate", ""),
            (3005013, "Custom Gas Rate", ""),
        ]

        results = get_multiple_results_32(
            d2_result_dll=self.d2_result_dll,
            doe2_data_dir=self.doe2_data_path,
            project_fname=str(Path(self.test_file).with_suffix("")),
            requests=requests,
        )

        expected_results = [0.0, 8.0, 0.0, -99999.0, -99999.0, -99999.0, -99999.0]

        self.assertEqual(expected_results, results)
