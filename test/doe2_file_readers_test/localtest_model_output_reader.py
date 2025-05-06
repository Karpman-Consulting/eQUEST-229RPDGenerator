import unittest
from pathlib import Path

from rpd_generator.config import Config
from rpd_generator.utilities import validate_configuration
from rpd_generator.doe2_file_readers.model_output_reader import (
    get_string_result,
    get_multiple_results,
)


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

        result = get_string_result(
            self.d2_result_dll,
            self.doe2_data_path,
            str(Path(self.test_file).with_suffix("")),
            entry_id,
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

        results = get_multiple_results(
            self.d2_result_dll,
            self.doe2_data_path,
            str(Path(self.test_file).with_suffix("")),
            requests,
        )

        expected_results = [
            15.696036338806152,
            0.29748615622520447,
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

        results = get_multiple_results(
            self.d2_result_dll,
            self.doe2_data_path,
            str(Path(self.test_file).with_suffix("")),
            requests,
        )

        expected_results = [0.07000000029802322, 11982.0, 0.5, 5915.0]

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

        results = get_multiple_results(
            self.d2_result_dll,
            self.doe2_data_path,
            str(Path(self.test_file).with_suffix("")),
            requests,
        )

        expected_results = [0.0, 8.0, 0.0, -99999.0, -99999.0, -99999.0, -99999.0]

        self.assertEqual(expected_results, results)
