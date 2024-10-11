import unittest
from unittest.mock import patch

from rpd_generator.config import Config
from rpd_generator.schema.schema_enums import SchemaEnums

Config.set_active_ruleset("ASHRAE 90.1-2019")
SchemaEnums.update_schema_enum(Config.ACTIVE_RULESET)

from rpd_generator.artifacts.ruleset_model_description import RulesetModelDescription
from rpd_generator.bdl_structure.bdl_commands.floor import Floor
from rpd_generator.bdl_structure.bdl_commands.interior_wall import *


class TestInteriorWalls(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.rmd = RulesetModelDescription("Test RMD")
        self.rmd.doe2_version = "DOE-2.3"
        self.rmd.doe2_data_path = Config.DOE23_DATA_PATH
        self.floor = Floor("Floor 1", self.rmd)
        self.interior_wall = InteriorWall("Interior Wall 1", self.floor, self.rmd)

    # @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    # def test_populate_data_with_interior_wall(self, mock_get_output_data):
    #     mock_get_output_data.return_value = {}
    #
    #     self.interior_wall.keyword_value_pairs = {}
    #
    #     self.interior_wall.populate_data_elements()
    #     self.interior_wall.populate_data_group()
    #
    #     expected_data_structure = {}
    #
    #     self.assertEqual(expected_data_structure, self.interior_wall.interior_wall_data_structure)
