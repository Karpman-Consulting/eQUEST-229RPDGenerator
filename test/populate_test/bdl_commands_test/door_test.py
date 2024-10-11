import unittest
from unittest.mock import patch

from rpd_generator.config import Config
from rpd_generator.schema.schema_enums import SchemaEnums

Config.set_active_ruleset("ASHRAE 90.1-2019")
SchemaEnums.update_schema_enum(Config.ACTIVE_RULESET)

from rpd_generator.artifacts.ruleset_model_description import RulesetModelDescription
from rpd_generator.bdl_structure.bdl_commands.floor import Floor
from rpd_generator.bdl_structure.bdl_commands.space import Space
from rpd_generator.bdl_structure.bdl_commands.exterior_wall import ExteriorWall
from rpd_generator.bdl_structure.bdl_commands.door import *


class TestDoor(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.rmd = RulesetModelDescription("Test RMD")
        self.rmd.doe2_version = "DOE-2.3"
        self.rmd.doe2_data_path = Config.DOE23_DATA_PATH
        self.floor = Floor("Floor 1", self.rmd)
        self.space = Space("Space 1", self.floor, self.rmd)
        self.exterior_wall = ExteriorWall("Exterior Wall 1", self.space, self.rmd)
        self.door = Door("Door 1", self.exterior_wall, self.rmd)

    # @patch("rpd_generator.bdl_structure.base_node.BaseNode.get_output_data")
    # def test_populate_data_with_door(self, mock_get_output_data):
    #     mock_get_output_data.return_value = {}
    #
    #     self.door.keyword_value_pairs = {}
    #
    #     self.door.populate_data_elements()
    #     self.door.populate_data_group()
    #
    #     expected_data_structure = {}
    #
    #     self.assertEqual(expected_data_structure, self.door.door_data_structure)
