import unittest
import os
from rpd_generator.config import Config
from rpd_generator.utilities import validate_configuration
from rpd_generator.schema.schema_enums import SchemaEnums

Config.set_active_ruleset("ASHRAE 90.1-2019")
SchemaEnums.update_schema_enum(Config.ACTIVE_RULESET)
validate_configuration.find_equest_installation()

from rpd_generator.artifacts.ruleset_model_description import RulesetModelDescription
from rpd_generator.bdl_structure.bdl_commands.boiler import Boiler
from rpd_generator.bdl_structure.bdl_commands.meters import MasterMeters, FuelMeter
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums

BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_BoilerKeywords = BDLEnums.bdl_enums["BoilerKeywords"]
BDL_BoilerTypes = BDLEnums.bdl_enums["BoilerTypes"]
BDL_FuelTypes = BDLEnums.bdl_enums["FuelTypes"]
BDL_FuelMeterKeywords = BDLEnums.bdl_enums["FuelMeterKeywords"]
BoilerCombustionOptions = SchemaEnums.schema_enums["BoilerCombustionOptions"]
EnergySourceOptions = SchemaEnums.schema_enums["EnergySourceOptions"]
BoilerEfficiencyMetricOptions = SchemaEnums.schema_enums[
    "BoilerEfficiencyMetricOptions"
]


class TestFuelBoiler(unittest.TestCase):

    def setUp(self):
        self.rmd = RulesetModelDescription("Test RMD")
        self.rmd.doe2_version = "DOE-2.3"
        self.rmd.doe2_data_path = Config.DOE23_DATA_PATH
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.rmd.file_path = os.path.abspath(
            os.path.join(script_dir, "../../full_rpd_test/E-2/229 Test Case E-2 (CHW VAV)")
        )
        self.boiler = Boiler("Boiler 1", self.rmd)

    def test_populate_data_elements_with_fuel_meter(self):
        fuel_meter = FuelMeter("Test Fuel Meter", self.rmd)
        fuel_meter.keyword_value_pairs = {
            BDL_FuelMeterKeywords.TYPE: BDL_FuelTypes.METHANOL
        }
        self.rmd.bdl_obj_instances = {"Test Fuel Meter": fuel_meter}

        self.boiler.keyword_value_pairs = {
            BDL_BoilerKeywords.TYPE: BDL_BoilerTypes.HW_BOILER,
            BDL_BoilerKeywords.FUEL_METER: "Test Fuel Meter",
            BDL_BoilerKeywords.HW_LOOP: "test_loop",
            BDL_BoilerKeywords.MIN_RATIO: "0.33",
        }

        self.boiler.populate_data_elements()
        self.boiler.populate_data_group()

        expected_data_structure = {
            "id": "Boiler 1",
            "draft_type": "NATURAL",
            "energy_source_type": "OTHER",
            "output_validation_points": [],
            "loop": "test_loop",
            "auxiliary_power": 0.0,
            "design_capacity": 0.17634653125,
            "rated_capacity": 0.17634653125,
            "minimum_load_ratio": 0.33,
            "efficiency": [0.9000089372091853, 0.9200089372091853, 0.9085816425247832],
            "efficiency_metrics": ["THERMAL", "COMBUSTION", "ANNUAL_FUEL_UTILIZATION"],
        }

        self.assertDictEqual(self.boiler.boiler_data_structure, expected_data_structure)

    def test_populate_data_elements_without_fuel_meter(self):
        self.rmd.bdl_obj_instances = {}

        self.boiler.keyword_value_pairs = {
            BDL_BoilerKeywords.TYPE: BDL_BoilerTypes.HW_BOILER_W_DRAFT,
            BDL_BoilerKeywords.HW_LOOP: "test_loop",
            BDL_BoilerKeywords.MIN_RATIO: "0.33",
        }

        self.boiler.populate_data_elements()
        self.boiler.populate_data_group()

        expected_data_structure = {
            "id": "Boiler 1",
            "draft_type": "FORCED",
            "energy_source_type": "NATURAL-GAS",
            "output_validation_points": [],
            "loop": "test_loop",
            "auxiliary_power": 0.0,
            "design_capacity": 0.17634653125,
            "rated_capacity": 0.17634653125,
            "minimum_load_ratio": 0.33,
            "efficiency": [0.9000089372091853, 0.9200089372091853, 0.9085816425247832],
            "efficiency_metrics": ["THERMAL", "COMBUSTION", "ANNUAL_FUEL_UTILIZATION"],
        }

        self.assertDictEqual(self.boiler.boiler_data_structure, expected_data_structure)


class TestElectricBoiler(unittest.TestCase):

    def setUp(self):
        self.rmd = RulesetModelDescription("Test RMD")
        self.rmd.doe2_version = "DOE-2.3"
        self.rmd.doe2_data_path = Config.DOE23_DATA_PATH
        self.boiler = Boiler("Boiler 1", self.rmd)

    def test_populate_data_elements_electric_boiler(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.rmd.file_path = os.path.abspath(
            os.path.join(script_dir, "../output_references/Electric Boiler")
        )
        self.rmd.bdl_obj_instances = {}

        self.boiler.keyword_value_pairs = {
            BDL_BoilerKeywords.TYPE: BDL_BoilerTypes.ELEC_HW_BOILER,
            BDL_BoilerKeywords.HW_LOOP: "test_loop",
            BDL_BoilerKeywords.MIN_RATIO: "0.33",
        }

        self.boiler.populate_data_elements()
        self.boiler.populate_data_group()

        expected_data_structure = {
            "id": "Boiler 1",
            "draft_type": "NATURAL",
            "energy_source_type": "ELECTRICITY",
            "output_validation_points": [],
            "loop": "test_loop",
            "auxiliary_power": 0.0,
            "design_capacity": 0.8822398124999999,
            "rated_capacity": 0.8822398124999999,
            "minimum_load_ratio": 0.33,
            "efficiency": [0.9803921751955851],
            "efficiency_metrics": ["THERMAL"],
        }

        self.assertDictEqual(self.boiler.boiler_data_structure, expected_data_structure)

    def test_populate_data_elements_electric_steam_boiler_1EIR(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.rmd.file_path = os.path.abspath(
            os.path.join(script_dir, "../output_references/Electric Boiler - 1EIR")
        )
        self.rmd.bdl_obj_instances = {}

        self.boiler.keyword_value_pairs = {
            BDL_BoilerKeywords.TYPE: BDL_BoilerTypes.ELEC_STM_BOILER,
            BDL_BoilerKeywords.HW_LOOP: "test_loop",
            BDL_BoilerKeywords.MIN_RATIO: "0.33",
        }

        self.boiler.populate_data_elements()
        self.boiler.populate_data_group()

        expected_data_structure = {
            "id": "Boiler 1",
            "draft_type": "NATURAL",
            "energy_source_type": "ELECTRICITY",
            "output_validation_points": [],
            "loop": "test_loop",
            "auxiliary_power": 0.0,
            "design_capacity": 0.8822398124999999,
            "rated_capacity": 0.8822398124999999,
            "minimum_load_ratio": 0.33,
            "efficiency": [1, 1, 1],
            "efficiency_metrics": ["THERMAL", "COMBUSTION", "ANNUAL_FUEL_UTILIZATION"],
        }

        self.assertDictEqual(self.boiler.boiler_data_structure, expected_data_structure)
