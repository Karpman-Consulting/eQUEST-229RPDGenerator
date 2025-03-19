import unittest
from pathlib import Path

from rpd_generator.doe2_file_readers.model_input_reader import ModelInputReader


class TestModelInputReader(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.model_input_reader = ModelInputReader()

        self.test_file = str(
            Path(__file__).parents[2]
            / "test"
            / "full_rpd_test"
            / "E-1"
            / "229 Test Case E-1 (PSZHP).BDL"
        )

    def test_read_doe2_version(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertEqual("DOE-2.3-50e", data["doe2_version"])

    def test_read_zone_commands(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertEqual(5, len(data["file_commands"]["ZONE"]))

    def test_read_material_commands(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertEqual(25, len(data["file_commands"]["MATERIAL"]))

    def test_read_schedule_commands(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertEqual(12, len(data["file_commands"]["SCHEDULE-PD"]))

    def test_read_library_entries(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertDictEqual(
            {
                "command": "MATERIAL",
                "TYPE": "RESISTANCE",
                "RESISTANCE": "                      0.7500",
            },
            data["file_commands"]["MATERIAL"]["Carpet & No Pad"],
        )

    def test_raw_read_library_curve_fit_coef(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertEqual(
            ["0", "0.99945700", "0.00054300"],
            data["file_commands"]["CURVE-FIT"]["DW-Gas-Pilotless-HIR-fPLR"]["COEF"],
        )

    def test_raw_read_user_curve_fit_coef(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertEqual(
            ["0.74721", "-0.038874", "0.000313", "0.027638", "-0.000133", "-8e-006"],
            data["file_commands"]["CURVE-FIT"]["Coef Curve Fit"]["COEF"],
        )

    def test_special_read_curve_fit_coef_data(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertEqual(
            [
                "1.91015875",
                "-0.03367849",
                "0.00015359",
                "-0.01582364",
                "0.00015079",
                "0.00036306",
            ],
            data["file_commands"]["CURVE-FIT"]["Data Curve Fit"]["COEFFICIENT"],
        )
