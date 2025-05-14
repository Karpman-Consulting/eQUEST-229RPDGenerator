import unittest

from rpd_generator.config import Config
from rpd_generator.artifacts.ruleset_project_description import (
    RulesetProjectDescription,
)
from rpd_generator.artifacts.ruleset_model_description import RulesetModelDescription
from rpd_generator.bdl_structure.bdl_commands.utility_and_economics import (
    ElecMeter,
    BDL_ElecMeterKeywords,
)


class TestTransformer(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.rpd = RulesetProjectDescription("Test RPD")
        self.rmd = RulesetModelDescription("Test RMD", self.rpd)
        self.rmd.doe2_version = "DOE-2.3"
        self.rmd.doe2_data_path = Config.DOE23_DATA_PATH
        self.elec_meter = ElecMeter("Test Elec Meter", self.rmd)

    def test_populate_data_elements_with_transformer(self):
        """Tests that all values populate for a transformer with expected values, given valid inputs"""

        self.elec_meter.keyword_value_pairs = {
            BDL_ElecMeterKeywords.TRANSFORMER_SIZE: 10,
            BDL_ElecMeterKeywords.TRANSFORMER_LOSS: 0.02,
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Test Elec Meter Transformer",
            "capacity": 10000,
            "efficiency": 0.98,
        }
        self.assertDictEqual(
            expected_data_structure,
            self.elec_meter.get_obj("Test Elec Meter Transformer").data_structure,
        )

    def test_populate_data_elements_with_transformer_no_loss(self):
        """Tests that all values populate for a transformer with expected values, given valid inputs"""

        self.elec_meter.keyword_value_pairs = {
            BDL_ElecMeterKeywords.TRANSFORMER_SIZE: 1
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Test Elec Meter Transformer",
            "capacity": 1000,
            "efficiency": 1,
        }
        self.assertDictEqual(
            expected_data_structure,
            self.elec_meter.get_obj("Test Elec Meter Transformer").data_structure,
        )

    def test_populate_data_elements_with_transformer_zero_size(self):
        """Tests that all values populate for a transformer with expected values, given valid inputs"""

        self.elec_meter.keyword_value_pairs = {
            BDL_ElecMeterKeywords.TRANSFORMER_SIZE: 0
        }
        self.rmd.populate_rmd_data(testing=True)
        transformer = self.elec_meter.get_obj("Test Elec Meter Transformer")
        self.assertEqual(None, transformer)
