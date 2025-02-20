import unittest
from unittest.mock import patch

from rpd_generator.config import Config
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.artifacts.ruleset_project_description import (
    RulesetProjectDescription,
)
from rpd_generator.artifacts.ruleset_model_description import RulesetModelDescription
from rpd_generator.bdl_structure.bdl_commands.circulation_loop import (
    CirculationLoop,
    BDL_CirculationLoopKeywords,
)
from rpd_generator.bdl_structure.bdl_commands.chiller import (
    Chiller,
    BDL_ChillerTypes,
    BDL_CondenserTypes,
)
from rpd_generator.bdl_structure.bdl_commands.curve_fit import (
    CurveFit,
    BDL_CurveFitKeywords,
)
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums

BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_ChillerKeywords = BDLEnums.bdl_enums["ChillerKeywords"]
EnergySourceOptions = SchemaEnums.schema_enums["EnergySourceOptions"]


class TestElectricChillers(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.rpd = RulesetProjectDescription("Test RPD")
        self.rmd = RulesetModelDescription("Test RMD", self.rpd)
        self.rmd.doe2_version = "DOE-2.3"
        self.rmd.doe2_data_path = Config.DOE23_DATA_PATH
        self.chilled_water_loop = CirculationLoop(
            "Chilled Water Loop (Primary)", self.rmd
        )
        self.chiller = Chiller("Chiller 1", self.rmd)
        self.f_t = CurveFit("fT Curve", self.rmd)
        self.f_plr = CurveFit("fPLR Curve", self.rmd)
        self.cap_f_t = CurveFit("CAP-fT Curve", self.rmd)

        self.chilled_water_loop.keyword_value_pairs = {
            BDL_CirculationLoopKeywords.DESIGN_COOL_T: "50",
        }
        self.f_t.keyword_value_pairs = {
            BDL_CurveFitKeywords.COEF: [
                "1.42868233",
                "-0.08227751",
                "0.00030243",
                "0.03622194",
                "-0.00029211",
                "0.00043788",
            ],
            BDL_CurveFitKeywords.TYPE: "BI-QUADRATIC-T",
            BDL_CurveFitKeywords.INPUT_TYPE: "COEFFICIENTS",
            BDL_CurveFitKeywords.OUTPUT_MIN: "-1000000.0000",
            BDL_CurveFitKeywords.OUTPUT_MAX: "1000000.0000",
        }

        self.f_plr.keyword_value_pairs = {
            BDL_CurveFitKeywords.COEF: [
                "0.14703037",
                "-0.00349667",
                "1.01161313",
                "-0.00359697",
                "0.00027167",
                "-0.01164471",
            ],
            BDL_CurveFitKeywords.TYPE: "BI-QUADRATIC-RATIO&DT",
            BDL_CurveFitKeywords.INPUT_TYPE: "COEFFICIENTS",
            BDL_CurveFitKeywords.OUTPUT_MIN: "               -1000000.0000",
            BDL_CurveFitKeywords.OUTPUT_MAX: "                1000000.0000",
        }

        self.cap_f_t.keyword_value_pairs = {
            BDL_CurveFitKeywords.COEF: [
                "-0.38924539",
                "-0.02195141",
                "-0.00027343",
                "0.04974775",
                "-0.00053441",
                "0.00067295",
            ],
            BDL_CurveFitKeywords.TYPE: "BI-QUADRATIC-T",
            BDL_CurveFitKeywords.INPUT_TYPE: "COEFFICIENTS",
            BDL_CurveFitKeywords.OUTPUT_MIN: "               -1000000.0000",
            BDL_CurveFitKeywords.OUTPUT_MAX: "                1000000.0000",
        }

    @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    def test_populate_data_with_centrif_chiller_ahri_auto_sized_plr_na(
        self, mock_get_output_data
    ):
        """Tests that all values populate with expected values, given valid inputs"""
        mock_get_output_data.return_value = {
            "Design Parameters - Capacity": 151941.078125,
            "Design Parameters - Condenser Flow": 36.10254669189453,
            "Design Parameters - Flow": 28.88204002380371,
            "Normalized (ARI) Capacity at Peak (Btu/hr)": 120092.3359375,
            "Normalized (ARI) Entering Condenser Water Temperature (°F)": 70.0,
            "Normalized (ARI) Leaving Chilled Water Temperature (°F)": 44.0,
            "Primary Equipment (Chillers) - Capacity (Btu/hr)": 151941.078125,
        }
        self.chiller.keyword_value_pairs = {
            BDL_ChillerKeywords.TYPE: BDL_ChillerTypes.ELEC_OPEN_CENT,
            BDL_ChillerKeywords.CONDENSER_TYPE: BDL_CondenserTypes.WATER_COOLED,
            BDL_ChillerKeywords.CHW_LOOP: "Chilled Water Loop (Primary)",
            BDL_ChillerKeywords.CW_LOOP: "Condenser Water Loop",
            BDL_ChillerKeywords.EIR_FT: "fT Curve",
            BDL_ChillerKeywords.EIR_FPLR: "fPLR Curve",
            BDL_ChillerKeywords.CAPACITY_FT: "CAP-fT Curve",
            BDL_ChillerKeywords.ELEC_INPUT_RATIO: "0.16",
            BDL_ChillerKeywords.MIN_RATIO: "0.25",
            BDL_ChillerKeywords.RATED_CHW_T: "44",
            BDL_ChillerKeywords.RATED_COND_T: "85",
            BDL_ChillerKeywords.DESIGN_CHW_T: "50",
            BDL_ChillerKeywords.DESIGN_COND_T: "70",
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Chiller 1",
            "compressor_type": "CENTRIFUGAL",
            "energy_source_type": "ELECTRICITY",
            "cooling_loop": "Chilled Water Loop (Primary)",
            "condensing_loop": "Condenser Water Loop",
            "design_entering_condenser_temperature": 70.0,
            "design_leaving_evaporator_temperature": 50.0,
            "rated_entering_condenser_temperature": 85.0,
            "rated_leaving_evaporator_temperature": 44.0,
            "minimum_load_ratio": 0.25,
            "rated_capacity": 0.14486234671295947,
            "design_capacity": 0.151941078125,
            "design_flow_condenser": 36.10254669189453,
            "design_flow_evaporator": 28.88204002380371,
            "is_chilled_water_pump_interlocked": False,
            "is_condenser_water_pump_interlocked": False,
            "capacity_validation_points": [],
            "power_validation_points": [],
            "efficiency_metric_types": [
                "FULL_LOAD_EFFICIENCY_RATED",
                "INTEGRATED_PART_LOAD_VALUE",
            ],
            "efficiency_metric_values": [6.25, 10.801636635546025],
        }
        self.assertEqual(expected_data_structure, self.chiller.chiller_data_structure)

    @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    def test_populate_data_with_centrif_chiller_ahri_hard_coded_cap_plr_na(
        self, mock_get_output_data
    ):
        """Tests that all values populate with expected values, given valid inputs"""
        mock_get_output_data.return_value = {
            "Design Parameters - Capacity": 151941.078125,
            "Design Parameters - Condenser Flow": 36.10254669189453,
            "Design Parameters - Flow": 28.88204002380371,
            "Normalized (ARI) Capacity at Peak (Btu/hr)": 120092.3359375,
            "Normalized (ARI) Entering Condenser Water Temperature (°F)": 70.0,
            "Normalized (ARI) Leaving Chilled Water Temperature (°F)": 44.0,
            "Primary Equipment (Chillers) - Capacity (Btu/hr)": 151941.078125,
        }
        self.chiller.keyword_value_pairs = {
            BDL_ChillerKeywords.TYPE: BDL_ChillerTypes.ELEC_OPEN_CENT,
            BDL_ChillerKeywords.CONDENSER_TYPE: BDL_CondenserTypes.WATER_COOLED,
            BDL_ChillerKeywords.CHW_LOOP: "Chilled Water Loop (Primary)",
            BDL_ChillerKeywords.CW_LOOP: "Condenser Water Loop",
            BDL_ChillerKeywords.CAPACITY: "0.3",
            BDL_ChillerKeywords.EIR_FT: "fT Curve",
            BDL_ChillerKeywords.EIR_FPLR: "fPLR Curve",
            BDL_ChillerKeywords.CAPACITY_FT: "CAP-fT Curve",
            BDL_ChillerKeywords.ELEC_INPUT_RATIO: "0.1758",
            BDL_ChillerKeywords.MIN_RATIO: "0.25",
            BDL_ChillerKeywords.RATED_CHW_T: "44",
            BDL_ChillerKeywords.RATED_COND_T: "85",
            BDL_ChillerKeywords.DESIGN_CHW_T: "50",
            BDL_ChillerKeywords.DESIGN_COND_T: "70",
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Chiller 1",
            "compressor_type": "CENTRIFUGAL",
            "energy_source_type": "ELECTRICITY",
            "cooling_loop": "Chilled Water Loop (Primary)",
            "condensing_loop": "Condenser Water Loop",
            "design_entering_condenser_temperature": 70.0,
            "design_leaving_evaporator_temperature": 50.0,
            "rated_entering_condenser_temperature": 85.0,
            "rated_leaving_evaporator_temperature": 44.0,
            "minimum_load_ratio": 0.25,
            "rated_capacity": 0.3,
            "design_capacity": 0.151941078125,
            "design_flow_condenser": 36.10254669189453,
            "design_flow_evaporator": 28.88204002380371,
            "is_chilled_water_pump_interlocked": False,
            "is_condenser_water_pump_interlocked": False,
            "capacity_validation_points": [],
            "power_validation_points": [],
            "efficiency_metric_types": [
                "FULL_LOAD_EFFICIENCY_RATED",
                "INTEGRATED_PART_LOAD_VALUE",
            ],
            "efficiency_metric_values": [5.688282138794084, 9.830841078995244],
        }
        self.assertEqual(expected_data_structure, self.chiller.chiller_data_structure)

    @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    def test_populate_data_with_centrif_chiller_ahri_auto_sized_plr_def(
        self, mock_get_output_data
    ):
        """Tests that all values populate with expected values, given valid inputs"""
        mock_get_output_data.return_value = {
            "Design Parameters - Capacity": 151769.594,
            "Design Parameters - Condenser Flow": 36.10254669189453,
            "Design Parameters - Flow": 28.88204002380371,
            "Normalized (ARI) Capacity at Peak (Btu/hr)": 120092.3359375,
            "Normalized (ARI) Entering Condenser Water Temperature (°F)": 70.0,
            "Normalized (ARI) Leaving Chilled Water Temperature (°F)": 44.0,
            "Primary Equipment (Chillers) - Capacity (Btu/hr)": 151769.594,
        }
        self.chiller.keyword_value_pairs = {
            BDL_ChillerKeywords.TYPE: BDL_ChillerTypes.ELEC_OPEN_CENT,
            BDL_ChillerKeywords.CONDENSER_TYPE: BDL_CondenserTypes.WATER_COOLED,
            BDL_ChillerKeywords.CHW_LOOP: "Chilled Water Loop (Primary)",
            BDL_ChillerKeywords.CW_LOOP: "Condenser Water Loop",
            BDL_ChillerKeywords.EIR_FT: "fT Curve",
            BDL_ChillerKeywords.EIR_FPLR: "fPLR Curve",
            BDL_ChillerKeywords.CAPACITY_FT: "CAP-fT Curve",
            BDL_ChillerKeywords.ELEC_INPUT_RATIO: "0.1758",
            BDL_ChillerKeywords.MIN_RATIO: "0.25",
            BDL_ChillerKeywords.RATED_CHW_T: "44",
            BDL_ChillerKeywords.RATED_COND_T: "85",
            BDL_ChillerKeywords.RATED_PLR: "0.92",
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Chiller 1",
            "compressor_type": "CENTRIFUGAL",
            "energy_source_type": "ELECTRICITY",
            "cooling_loop": "Chilled Water Loop (Primary)",
            "condensing_loop": "Condenser Water Loop",
            "design_entering_condenser_temperature": 70.0,
            "design_leaving_evaporator_temperature": 44.0,
            "rated_entering_condenser_temperature": 85.0,
            "rated_leaving_evaporator_temperature": 44.0,
            "minimum_load_ratio": 0.25,
            "rated_capacity": 0.1568199065129984,
            "design_capacity": 0.151769594,
            "design_flow_condenser": 36.10254669189453,
            "design_flow_evaporator": 28.88204002380371,
            "is_chilled_water_pump_interlocked": False,
            "is_condenser_water_pump_interlocked": False,
            "capacity_validation_points": [],
            "power_validation_points": [],
            "efficiency_metric_types": [
                "FULL_LOAD_EFFICIENCY_RATED",
                "INTEGRATED_PART_LOAD_VALUE",
            ],
            "efficiency_metric_values": [5.37926770870573, 9.296783224762487],
        }
        self.assertEqual(expected_data_structure, self.chiller.chiller_data_structure)

    @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    def test_populate_data_with_centrif_chiller_ahri_hard_coded_cap_plr_def(
        self, mock_get_output_data
    ):
        """Tests that all values populate with expected values, given valid inputs"""
        mock_get_output_data.return_value = {
            "Design Parameters - Capacity": 151769.594,
            "Design Parameters - Condenser Flow": 36.10254669189453,
            "Design Parameters - Flow": 28.88204002380371,
            "Normalized (ARI) Capacity at Peak (Btu/hr)": 120092.3359375,
            "Normalized (ARI) Entering Condenser Water Temperature (°F)": 70.0,
            "Normalized (ARI) Leaving Chilled Water Temperature (°F)": 44.0,
            "Primary Equipment (Chillers) - Capacity (Btu/hr)": 151769.594,
        }
        self.chiller.keyword_value_pairs = {
            BDL_ChillerKeywords.TYPE: BDL_ChillerTypes.ELEC_OPEN_CENT,
            BDL_ChillerKeywords.CONDENSER_TYPE: BDL_CondenserTypes.WATER_COOLED,
            BDL_ChillerKeywords.CHW_LOOP: "Chilled Water Loop (Primary)",
            BDL_ChillerKeywords.CW_LOOP: "Condenser Water Loop",
            BDL_ChillerKeywords.EIR_FT: "fT Curve",
            BDL_ChillerKeywords.EIR_FPLR: "fPLR Curve",
            BDL_ChillerKeywords.CAPACITY_FT: "CAP-fT Curve",
            BDL_ChillerKeywords.ELEC_INPUT_RATIO: "0.1758",
            BDL_ChillerKeywords.MIN_RATIO: "0.25",
            BDL_ChillerKeywords.RATED_CHW_T: "44",
            BDL_ChillerKeywords.RATED_COND_T: "85",
            BDL_ChillerKeywords.CAPACITY: "0.3",
            BDL_ChillerKeywords.RATED_PLR: "0.92",
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Chiller 1",
            "compressor_type": "CENTRIFUGAL",
            "energy_source_type": "ELECTRICITY",
            "cooling_loop": "Chilled Water Loop (Primary)",
            "condensing_loop": "Condenser Water Loop",
            "design_entering_condenser_temperature": 70.0,
            "design_leaving_evaporator_temperature": 44.0,
            "rated_entering_condenser_temperature": 85.0,
            "rated_leaving_evaporator_temperature": 44.0,
            "minimum_load_ratio": 0.25,
            "rated_capacity": 0.32614840614294044,
            "design_capacity": 0.151769594,
            "design_flow_condenser": 36.10254669189453,
            "design_flow_evaporator": 28.88204002380371,
            "is_chilled_water_pump_interlocked": False,
            "is_condenser_water_pump_interlocked": False,
            "capacity_validation_points": [],
            "power_validation_points": [],
            "efficiency_metric_types": [
                "FULL_LOAD_EFFICIENCY_RATED",
                "INTEGRATED_PART_LOAD_VALUE",
            ],
            "efficiency_metric_values": [5.37926770870573, 9.296783224762487],
        }
        self.assertEqual(expected_data_structure, self.chiller.chiller_data_structure)

    @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    def test_populate_data_with_centrif_chiller_non_ahri_hard_coded_cap_plr_def(
        self, mock_get_output_data
    ):
        """Tests that all values populate with expected values, given valid inputs"""
        mock_get_output_data.return_value = {
            "Design Parameters - Capacity": 151769.594,
            "Design Parameters - Condenser Flow": 36.10254669189453,
            "Design Parameters - Flow": 28.88204002380371,
            "Normalized (ARI) Capacity at Peak (Btu/hr)": 120092.3359375,
            "Normalized (ARI) Entering Condenser Water Temperature (°F)": 70.0,
            "Normalized (ARI) Leaving Chilled Water Temperature (°F)": 44.0,
            "Primary Equipment (Chillers) - Capacity (Btu/hr)": 163886,
        }
        self.chiller.keyword_value_pairs = {
            BDL_ChillerKeywords.TYPE: BDL_ChillerTypes.ELEC_OPEN_CENT,
            BDL_ChillerKeywords.CONDENSER_TYPE: BDL_CondenserTypes.WATER_COOLED,
            BDL_ChillerKeywords.CHW_LOOP: "Chilled Water Loop (Primary)",
            BDL_ChillerKeywords.CW_LOOP: "Condenser Water Loop",
            BDL_ChillerKeywords.EIR_FT: "fT Curve",
            BDL_ChillerKeywords.EIR_FPLR: "fPLR Curve",
            BDL_ChillerKeywords.CAPACITY_FT: "CAP-fT Curve",
            BDL_ChillerKeywords.ELEC_INPUT_RATIO: "0.1229",
            BDL_ChillerKeywords.MIN_RATIO: "0.25",
            BDL_ChillerKeywords.RATED_CHW_T: "50",
            BDL_ChillerKeywords.RATED_COND_T: "75",
            BDL_ChillerKeywords.CAPACITY: "0.163886",
            BDL_ChillerKeywords.RATED_PLR: "0.92",
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Chiller 1",
            "compressor_type": "CENTRIFUGAL",
            "energy_source_type": "ELECTRICITY",
            "cooling_loop": "Chilled Water Loop (Primary)",
            "condensing_loop": "Condenser Water Loop",
            "design_entering_condenser_temperature": 70.0,
            "design_leaving_evaporator_temperature": 44.0,
            "rated_entering_condenser_temperature": 85.0,
            "rated_leaving_evaporator_temperature": 44.0,
            "minimum_load_ratio": 0.25,
            "rated_capacity": 0.16521750752095135,
            "design_capacity": 0.151769594,
            "design_flow_condenser": 36.10254669189453,
            "design_flow_evaporator": 28.88204002380371,
            "is_chilled_water_pump_interlocked": False,
            "is_condenser_water_pump_interlocked": False,
            "capacity_validation_points": [],
            "power_validation_points": [],
            "efficiency_metric_types": [
                "FULL_LOAD_EFFICIENCY_RATED",
                "INTEGRATED_PART_LOAD_VALUE",
            ],
            "efficiency_metric_values": [5.648551274727391, 9.762175741896893],
        }
        self.assertEqual(expected_data_structure, self.chiller.chiller_data_structure)

    @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    def test_populate_data_with_centrif_chiller_non_ahri_auto_sized_plr_def(
        self, mock_get_output_data
    ):
        """Tests that all values populate with expected values, given valid inputs"""
        mock_get_output_data.return_value = {
            "Design Parameters - Capacity": 152000,
            "Design Parameters - Condenser Flow": 36.10254669189453,
            "Design Parameters - Flow": 28.88204002380371,
            "Normalized (ARI) Capacity at Peak (Btu/hr)": 120092.3359375,
            "Normalized (ARI) Entering Condenser Water Temperature (°F)": 70.0,
            "Normalized (ARI) Leaving Chilled Water Temperature (°F)": 44.0,
            "Primary Equipment (Chillers) - Capacity (Btu/hr)": 152000,
        }
        self.chiller.keyword_value_pairs = {
            BDL_ChillerKeywords.TYPE: BDL_ChillerTypes.ELEC_OPEN_CENT,
            BDL_ChillerKeywords.CONDENSER_TYPE: BDL_CondenserTypes.WATER_COOLED,
            BDL_ChillerKeywords.CHW_LOOP: "Chilled Water Loop (Primary)",
            BDL_ChillerKeywords.CW_LOOP: "Condenser Water Loop",
            BDL_ChillerKeywords.EIR_FT: "fT Curve",
            BDL_ChillerKeywords.EIR_FPLR: "fPLR Curve",
            BDL_ChillerKeywords.CAPACITY_FT: "CAP-fT Curve",
            BDL_ChillerKeywords.ELEC_INPUT_RATIO: "0.1758",
            BDL_ChillerKeywords.MIN_RATIO: "0.25",
            BDL_ChillerKeywords.RATED_CHW_T: "50",
            BDL_ChillerKeywords.RATED_COND_T: "75",
            BDL_ChillerKeywords.RATED_PLR: "0.92",
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Chiller 1",
            "compressor_type": "CENTRIFUGAL",
            "energy_source_type": "ELECTRICITY",
            "cooling_loop": "Chilled Water Loop (Primary)",
            "condensing_loop": "Condenser Water Loop",
            "design_entering_condenser_temperature": 70.0,
            "design_leaving_evaporator_temperature": 44.0,
            "rated_entering_condenser_temperature": 85.0,
            "rated_leaving_evaporator_temperature": 44.0,
            "minimum_load_ratio": 0.25,
            "rated_capacity": 0.1570579795448076,
            "design_capacity": 0.152,
            "design_flow_condenser": 36.10254669189453,
            "design_flow_evaporator": 28.88204002380371,
            "is_chilled_water_pump_interlocked": False,
            "is_condenser_water_pump_interlocked": False,
            "capacity_validation_points": [],
            "power_validation_points": [],
            "efficiency_metric_types": [
                "FULL_LOAD_EFFICIENCY_RATED",
                "INTEGRATED_PART_LOAD_VALUE",
            ],
            "efficiency_metric_values": [3.948845003776998, 6.824638217742481],
        }
        self.assertEqual(expected_data_structure, self.chiller.chiller_data_structure)

    @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    def test_populate_data_with_centrif_chiller_non_ahri_hard_coded_cap_plr_na(
        self, mock_get_output_data
    ):
        """Tests that all values populate with expected values, given valid inputs"""
        mock_get_output_data.return_value = {
            "Design Parameters - Capacity": 151941.078125,
            "Design Parameters - Condenser Flow": 36.10254669189453,
            "Design Parameters - Flow": 28.88204002380371,
            "Normalized (ARI) Capacity at Peak (Btu/hr)": 120092.3359375,
            "Normalized (ARI) Entering Condenser Water Temperature (°F)": 70.0,
            "Normalized (ARI) Leaving Chilled Water Temperature (°F)": 44.0,
            "Primary Equipment (Chillers) - Capacity (Btu/hr)": 151941.078125,
        }
        self.chiller.keyword_value_pairs = {
            BDL_ChillerKeywords.TYPE: BDL_ChillerTypes.ELEC_OPEN_CENT,
            BDL_ChillerKeywords.CONDENSER_TYPE: BDL_CondenserTypes.WATER_COOLED,
            BDL_ChillerKeywords.CHW_LOOP: "Chilled Water Loop (Primary)",
            BDL_ChillerKeywords.CW_LOOP: "Condenser Water Loop",
            BDL_ChillerKeywords.CAPACITY: "0.3",
            BDL_ChillerKeywords.EIR_FT: "fT Curve",
            BDL_ChillerKeywords.EIR_FPLR: "fPLR Curve",
            BDL_ChillerKeywords.CAPACITY_FT: "CAP-fT Curve",
            BDL_ChillerKeywords.ELEC_INPUT_RATIO: "0.202",
            BDL_ChillerKeywords.MIN_RATIO: "0.25",
            BDL_ChillerKeywords.RATED_CHW_T: "50",
            BDL_ChillerKeywords.RATED_COND_T: "70",
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Chiller 1",
            "compressor_type": "CENTRIFUGAL",
            "energy_source_type": "ELECTRICITY",
            "cooling_loop": "Chilled Water Loop (Primary)",
            "condensing_loop": "Condenser Water Loop",
            "design_entering_condenser_temperature": 70,
            "design_leaving_evaporator_temperature": 44,
            "rated_entering_condenser_temperature": 85.0,
            "rated_leaving_evaporator_temperature": 44.0,
            "minimum_load_ratio": 0.25,
            "rated_capacity": 0.2860773014625675,
            "design_capacity": 0.151941078125,
            "design_flow_condenser": 36.10254669189453,
            "design_flow_evaporator": 28.88204002380371,
            "is_chilled_water_pump_interlocked": False,
            "is_condenser_water_pump_interlocked": False,
            "capacity_validation_points": [],
            "power_validation_points": [],
            "efficiency_metric_types": [
                "FULL_LOAD_EFFICIENCY_RATED",
                "INTEGRATED_PART_LOAD_VALUE",
            ],
            "efficiency_metric_values": [3.226420253293395, 5.57609907354266],
        }
        self.assertEqual(expected_data_structure, self.chiller.chiller_data_structure)

    @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    def test_populate_data_with_centrif_chiller_non_ahri_hard_coded_cap_plr_na(
        self, mock_get_output_data
    ):
        """Tests that all values populate with expected values, given valid inputs"""
        mock_get_output_data.return_value = {
            "Design Parameters - Capacity": 151941.078125,
            "Design Parameters - Condenser Flow": 36.10254669189453,
            "Design Parameters - Flow": 28.88204002380371,
            "Normalized (ARI) Capacity at Peak (Btu/hr)": 120092.3359375,
            "Normalized (ARI) Entering Condenser Water Temperature (°F)": 70.0,
            "Normalized (ARI) Leaving Chilled Water Temperature (°F)": 44.0,
            "Primary Equipment (Chillers) - Capacity (Btu/hr)": 151941.078125,
        }
        self.chiller.keyword_value_pairs = {
            BDL_ChillerKeywords.TYPE: BDL_ChillerTypes.ELEC_OPEN_CENT,
            BDL_ChillerKeywords.CONDENSER_TYPE: BDL_CondenserTypes.WATER_COOLED,
            BDL_ChillerKeywords.CHW_LOOP: "Chilled Water Loop (Primary)",
            BDL_ChillerKeywords.CW_LOOP: "Condenser Water Loop",
            BDL_ChillerKeywords.CAPACITY: "0.3",
            BDL_ChillerKeywords.EIR_FT: "fT Curve",
            BDL_ChillerKeywords.EIR_FPLR: "fPLR Curve",
            BDL_ChillerKeywords.CAPACITY_FT: "CAP-fT Curve",
            BDL_ChillerKeywords.ELEC_INPUT_RATIO: "0.202",
            BDL_ChillerKeywords.MIN_RATIO: "0.25",
            BDL_ChillerKeywords.RATED_CHW_T: "50",
            BDL_ChillerKeywords.RATED_COND_T: "70",
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Chiller 1",
            "compressor_type": "CENTRIFUGAL",
            "energy_source_type": "ELECTRICITY",
            "cooling_loop": "Chilled Water Loop (Primary)",
            "condensing_loop": "Condenser Water Loop",
            "design_entering_condenser_temperature": 70,
            "design_leaving_evaporator_temperature": 44,
            "rated_entering_condenser_temperature": 85.0,
            "rated_leaving_evaporator_temperature": 44.0,
            "minimum_load_ratio": 0.25,
            "rated_capacity": 0.2860773014625675,
            "design_capacity": 0.151941078125,
            "design_flow_condenser": 36.10254669189453,
            "design_flow_evaporator": 28.88204002380371,
            "is_chilled_water_pump_interlocked": False,
            "is_condenser_water_pump_interlocked": False,
            "capacity_validation_points": [],
            "power_validation_points": [],
            "efficiency_metric_types": [
                "FULL_LOAD_EFFICIENCY_RATED",
                "INTEGRATED_PART_LOAD_VALUE",
            ],
            "efficiency_metric_values": [3.226420253293395, 5.57609907354266],
        }
        self.assertEqual(expected_data_structure, self.chiller.chiller_data_structure)

    @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    def test_populate_data_with_centrif_chiller_non_ahri_auto_sized_plr_na(
        self, mock_get_output_data
    ):
        """Tests that all values populate with expected values, given valid inputs"""
        mock_get_output_data.return_value = {
            "Design Parameters - Capacity": 152000,
            "Design Parameters - Condenser Flow": 36.10254669189453,
            "Design Parameters - Flow": 28.88204002380371,
            "Normalized (ARI) Capacity at Peak (Btu/hr)": 120092.3359375,
            "Normalized (ARI) Entering Condenser Water Temperature (°F)": 70.0,
            "Normalized (ARI) Leaving Chilled Water Temperature (°F)": 44.0,
            "Primary Equipment (Chillers) - Capacity (Btu/hr)": 152000,
        }
        self.chiller.keyword_value_pairs = {
            BDL_ChillerKeywords.TYPE: BDL_ChillerTypes.ELEC_OPEN_CENT,
            BDL_ChillerKeywords.CONDENSER_TYPE: BDL_CondenserTypes.WATER_COOLED,
            BDL_ChillerKeywords.CHW_LOOP: "Chilled Water Loop (Primary)",
            BDL_ChillerKeywords.CW_LOOP: "Condenser Water Loop",
            BDL_ChillerKeywords.EIR_FT: "fT Curve",
            BDL_ChillerKeywords.EIR_FPLR: "fPLR Curve",
            BDL_ChillerKeywords.CAPACITY_FT: "CAP-fT Curve",
            BDL_ChillerKeywords.ELEC_INPUT_RATIO: "0.1758",
            BDL_ChillerKeywords.MIN_RATIO: "0.25",
            BDL_ChillerKeywords.RATED_CHW_T: "50",
            BDL_ChillerKeywords.RATED_COND_T: "75",
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Chiller 1",
            "compressor_type": "CENTRIFUGAL",
            "energy_source_type": "ELECTRICITY",
            "cooling_loop": "Chilled Water Loop (Primary)",
            "condensing_loop": "Condenser Water Loop",
            "design_entering_condenser_temperature": 70.0,
            "design_leaving_evaporator_temperature": 44.0,
            "rated_entering_condenser_temperature": 85.0,
            "rated_leaving_evaporator_temperature": 44.0,
            "minimum_load_ratio": 0.25,
            "rated_capacity": 0.1444661171908111,
            "design_capacity": 0.152,
            "design_flow_condenser": 36.10254669189453,
            "design_flow_evaporator": 28.88204002380371,
            "is_chilled_water_pump_interlocked": False,
            "is_condenser_water_pump_interlocked": False,
            "capacity_validation_points": [],
            "power_validation_points": [],
            "efficiency_metric_types": [
                "FULL_LOAD_EFFICIENCY_RATED",
                "INTEGRATED_PART_LOAD_VALUE",
            ],
            "efficiency_metric_values": [4.222623076739573, 7.29779841980996],
        }
        self.assertEqual(expected_data_structure, self.chiller.chiller_data_structure)

    @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    def test_populate_data_with_data_input_type_performance_curve(
        self, mock_get_output_data
    ):
        """Tests that all values populate with expected values, given valid inputs"""
        mock_get_output_data.return_value = {
            "Design Parameters - Capacity": 152000,
            "Design Parameters - Condenser Flow": 36.10254669189453,
            "Design Parameters - Flow": 28.88204002380371,
            "Normalized (ARI) Capacity at Peak (Btu/hr)": 120092.3359375,
            "Normalized (ARI) Entering Condenser Water Temperature (°F)": 70.0,
            "Normalized (ARI) Leaving Chilled Water Temperature (°F)": 44.0,
            "Primary Equipment (Chillers) - Capacity (Btu/hr)": 152000,
        }
        self.f_plr.keyword_value_pairs = {
            BDL_CurveFitKeywords.TYPE: "BI-QUADRATIC-T",
            BDL_CurveFitKeywords.INPUT_TYPE: "DATA",
            BDL_CurveFitKeywords.OUTPUT_MIN: "-1000000.0000",
            BDL_CurveFitKeywords.OUTPUT_MAX: "1000000.0000",
        }
        self.chiller.keyword_value_pairs = {
            BDL_ChillerKeywords.TYPE: BDL_ChillerTypes.ELEC_OPEN_CENT,
            BDL_ChillerKeywords.CONDENSER_TYPE: BDL_CondenserTypes.WATER_COOLED,
            BDL_ChillerKeywords.CHW_LOOP: "Chilled Water Loop (Primary)",
            BDL_ChillerKeywords.CW_LOOP: "Condenser Water Loop",
            BDL_ChillerKeywords.EIR_FT: "fT Curve",
            BDL_ChillerKeywords.EIR_FPLR: "fPLR Curve",
            BDL_ChillerKeywords.CAPACITY_FT: "CAP-fT Curve",
            BDL_ChillerKeywords.ELEC_INPUT_RATIO: "0.1758",
            BDL_ChillerKeywords.MIN_RATIO: "0.25",
            BDL_ChillerKeywords.RATED_CHW_T: "50",
            BDL_ChillerKeywords.RATED_COND_T: "75",
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Chiller 1",
            "notes": "Performance curve INPUT-TYPE of DATA is not currently supported for determining and populating chiller IPLV.",
            "compressor_type": "CENTRIFUGAL",
            "energy_source_type": "ELECTRICITY",
            "cooling_loop": "Chilled Water Loop (Primary)",
            "condensing_loop": "Condenser Water Loop",
            "design_entering_condenser_temperature": 70.0,
            "design_leaving_evaporator_temperature": 44.0,
            "rated_entering_condenser_temperature": 75.0,
            "rated_leaving_evaporator_temperature": 50.0,
            "minimum_load_ratio": 0.25,
            "design_capacity": 0.152,
            "design_flow_condenser": 36.10254669189453,
            "design_flow_evaporator": 28.88204002380371,
            "is_chilled_water_pump_interlocked": False,
            "is_condenser_water_pump_interlocked": False,
            "capacity_validation_points": [],
            "power_validation_points": [],
            "efficiency_metric_types": ["OTHER"],
            "efficiency_metric_values": [5.688282138794084],
        }
        self.assertEqual(expected_data_structure, self.chiller.chiller_data_structure)


class TestEngineChillers(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.rpd = RulesetProjectDescription("Test RPD")
        self.rmd = RulesetModelDescription("Test RMD", self.rpd)
        self.rmd.doe2_version = "DOE-2.3"
        self.rmd.doe2_data_path = Config.DOE23_DATA_PATH
        self.chilled_water_loop = CirculationLoop(
            "Chilled Water Loop (Primary)", self.rmd
        )
        self.chiller = Chiller("Chiller 1", self.rmd)
        self.f_t = CurveFit("fT Curve", self.rmd)
        self.f_plr = CurveFit("fPLR Curve", self.rmd)
        self.cap_f_t = CurveFit("CAP-fT Curve", self.rmd)

        self.chilled_water_loop.keyword_value_pairs = {
            BDL_CirculationLoopKeywords.DESIGN_COOL_T: "50",
        }

        self.f_t.keyword_value_pairs = {
            BDL_CurveFitKeywords.COEF: [
                "-0.38924539",
                "-0.02195141",
                "-0.00027343",
                "0.04974775",
                "-0.00053441",
                "0.00067295",
            ],
            BDL_CurveFitKeywords.TYPE: "BI-QUADRATIC-T",
            BDL_CurveFitKeywords.INPUT_TYPE: "COEFFICIENTS",
            BDL_CurveFitKeywords.OUTPUT_MIN: "-1000000.0000",
            BDL_CurveFitKeywords.OUTPUT_MAX: "1000000.0000",
        }

        self.f_plr.keyword_value_pairs = {
            BDL_CurveFitKeywords.COEF: [
                "0.14703037",
                "-0.00349667",
                "1.01161313",
                "-0.00359697",
                "0.00027167",
                "-0.01164471",
            ],
            BDL_CurveFitKeywords.TYPE: "BI-QUADRATIC-RATIO&DT",
            BDL_CurveFitKeywords.INPUT_TYPE: "COEFFICIENTS",
            BDL_CurveFitKeywords.OUTPUT_MIN: "               -1000000.0000",
            BDL_CurveFitKeywords.OUTPUT_MAX: "                1000000.0000",
        }

        self.cap_f_t.keyword_value_pairs = {
            BDL_CurveFitKeywords.COEF: [
                "-0.38924539",
                "-0.02195141",
                "-0.00027343",
                "0.04974775",
                "-0.00053441",
                "0.00067295",
            ],
            BDL_CurveFitKeywords.TYPE: "BI-QUADRATIC-T",
            BDL_CurveFitKeywords.INPUT_TYPE: "COEFFICIENTS",
            BDL_CurveFitKeywords.OUTPUT_MIN: "               -1000000.0000",
            BDL_CurveFitKeywords.OUTPUT_MAX: "                1000000.0000",
        }

    @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    def test_populate_data_with_engine_chiller(self, mock_get_output_data):
        """Tests the branch of logic associated with engine chillers to ensure the correct values are populated"""
        mock_get_output_data.return_value = {
            "Design Parameters - Capacity": 151941.078125,
            "Design Parameters - Condenser Flow": 35.50693130493164,
            "Design Parameters - Flow": 28.40554428100586,
            "Normalized (ARI) Capacity at Peak (Btu/hr)": 120092.3359375,
            "Normalized (ARI) Entering Condenser Water Temperature (°F)": 85.0,
            "Normalized (ARI) Leaving Chilled Water Temperature (°F)": 44.0,
            "Primary Equipment (Chillers) - Capacity (Btu/hr)": 113584.79986733246,
        }
        self.chiller.keyword_value_pairs = {
            BDL_ChillerKeywords.TYPE: BDL_ChillerTypes.ENGINE,
            BDL_ChillerKeywords.CONDENSER_TYPE: BDL_CondenserTypes.WATER_COOLED,
            BDL_ChillerKeywords.CHW_LOOP: "Chilled Water Loop (Primary)",
            BDL_ChillerKeywords.CW_LOOP: "Condenser Water Loop",
            BDL_ChillerKeywords.HIR_FT: "fT Curve",
            BDL_ChillerKeywords.HIR_FPLR: "fPLR Curve",
            BDL_ChillerKeywords.CAPACITY_FT: "CAP-fT Curve",
            BDL_ChillerKeywords.HEAT_INPUT_RATIO: "0.16",
            BDL_ChillerKeywords.MIN_RATIO: "0.25",
            BDL_ChillerKeywords.RATED_CHW_T: "44",
            BDL_ChillerKeywords.RATED_COND_T: "85",
            BDL_ChillerKeywords.DESIGN_CHW_T: "50",
            BDL_ChillerKeywords.DESIGN_COND_T: "70",
        }

        self.rmd.populate_rmd_data(testing=True)
        expected_data_structure = {
            "id": "Chiller 1",
            "compressor_type": "OTHER",
            "cooling_loop": "Chilled Water Loop (Primary)",
            "condensing_loop": "Condenser Water Loop",
            "energy_source_type": "NATURAL_GAS",
            "design_entering_condenser_temperature": 85.0,
            "design_leaving_evaporator_temperature": 50.0,
            "rated_entering_condenser_temperature": 85.0,
            "rated_leaving_evaporator_temperature": 44.0,
            "minimum_load_ratio": 0.25,
            "rated_capacity": 0.10742989267538551,
            "design_capacity": 0.151941078125,
            "design_flow_condenser": 35.50693130493164,
            "design_flow_evaporator": 28.40554428100586,
            "is_chilled_water_pump_interlocked": False,
            "is_condenser_water_pump_interlocked": False,
            "capacity_validation_points": [],
            "power_validation_points": [],
            "efficiency_metric_types": [
                "FULL_LOAD_EFFICIENCY_RATED",
                "INTEGRATED_PART_LOAD_VALUE",
            ],
            "efficiency_metric_values": [6.25, 8.009551132788362],
        }
        self.assertEqual(expected_data_structure, self.chiller.chiller_data_structure)
