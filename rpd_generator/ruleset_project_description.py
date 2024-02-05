from rpd_generator.ruleset_model_description import RulesetModelDescription
import doe2_file_readers
from rpd_generator.bdl_structure import *

OUTPUT_SCHEMA_ASHRAE901_2019 = "OUTPUT_SCHEMA_ASHRAE901_2019"


class RulesetProjectDescription:
    """
    This class is used to store project-level data and generate the project description for a project. Object will be
    instantiated upon opening the GUI
    """

    bdl_command_dict = doe2_file_readers.model_input_reader.ModelInputReader.bdl_command_dict

    def __init__(self):
        self.selected_models = []

        self.rpd_data_structure = {}

        # data elements with children
        self.ruleset_model_descriptions = []
        self.calendar = {}
        self.weather = {}

        # data elements with no children
        self.reporting_name = None
        self.notes = None
        self.data_timestamp = None
        self.data_version = None
        self.compliance_path = None
        self.output_format_type = OUTPUT_SCHEMA_ASHRAE901_2019

    def populate_data_group(self):
        """
        Populate the RPD data group (only data elements directly under the RPD Data Group)
        """
        self.rpd_data_structure["ASHRAE 229"] = {
            "ruleset_model_descriptions": self.ruleset_model_descriptions,
            "calendar": self.calendar,
            "weather": self.weather,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "data_timestamp",
            "data_version",
            "compliance_path",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.rpd_data_structure["ASHRAE 229"][attr] = value

    def generate_rpd(self):
        """
        Generate the RPD data structure (RulesetProjectDescription, RulesetModelDescription, Building, BuildingSegment,
        and all data groups available from doe2_file_readers)
        """

        for model in self.selected_models:
            rmd = RulesetModelDescription("Test RMD")
            bdl_input_reader = doe2_file_readers.model_input_reader.ModelInputReader()
            # get all BDL commands from the BDL input file
            file_bdl_commands = bdl_input_reader.read_input_bdl_file(model)
            # iterate through the objects
            for cmd, lst in file_bdl_commands.items():
                for cmd_dict in lst:
                    obj = self._create_obj_instance(cmd_dict["unique_name"], cmd)
                    obj.add_inputs(cmd_dict)
                    print(obj.keyword_value_pairs)

                    # try:
                    #     obj.populate_data_elements()
                    # except AttributeError:
                    #     print(f"populate_data_elements method not yet written for {obj.__class__.__name__}")
                    # try:
                    #     obj.populate_data_group()
                    # except AttributeError:
                    #     print(f"populate_data_group method does not apply to {obj.__class__.__name__}")

            # push the rmd object to the rpd list of rmds
            self.ruleset_model_descriptions.append(rmd)

        # fill/replace data with data from the simulation output
        # fill/replace data with data from the GUI inputs
        # call each object's populate_data_group method

    @staticmethod
    def _determine_instance_type(command_class):
        """
        Determine the type of BDL command class.

        :param command_class: Command class to be determined.
        :return: tuple: tuple contains booleans stating if the class is parent, child, int_ext_wall, or space.
        """
        is_parent = issubclass(command_class, ParentNode) or issubclass(
            command_class, ParentDefinition
        )
        is_child = issubclass(command_class, ChildNode)
        is_int_ext_wall = (
            command_class.__name__ == "ExteriorWall"
            or command_class.__name__ == "InteriorWall"
        )
        is_space = command_class.__name__ == "Space"

        return is_parent, is_child, is_int_ext_wall, is_space

    def _set_current_parent(self, obj):
        """
        Keep track of the most recent floor, space, or other parent objects. Floor and space objects are stored
        separately to ensure that the correct parent is set for child objects in multi-tiered nodes.
        :param obj:
        :return: None
        """
        if isinstance(obj, RulesetProjectDescription.bdl_command_dict["FLOOR"]):
            self.current_parent_floor = obj
        elif isinstance(obj, RulesetProjectDescription.bdl_command_dict["SPACE"]):
            self.current_parent_space = obj
        else:
            self.current_parent = obj

    def _create_obj_instance(self, unique_name, command):
        """
        Create an object instance based on the command type. This is needed to determine the arguments to pass to the
        __init__ methods of each class. Any object with a parent needs to know which parent it belongs to in the model.
        Objects without parents have no parent object passed.

        :param unique_name: Unique name for the instance.
        :param command: BDL command.
        :return: object: Created object instance.
        """
        command_class = RulesetProjectDescription.bdl_command_dict[command]
        is_parent, is_child, is_int_ext_wall, is_space = self._determine_instance_type(
            command_class
        )

        if is_int_ext_wall:
            obj_instance = command_class(unique_name, self.current_parent_space)
            self._set_current_parent(obj_instance)
        elif is_space:
            obj_instance = command_class(unique_name, self.current_parent_floor)
            self._set_current_parent(obj_instance)
        elif is_child:
            obj_instance = command_class(unique_name, self.current_parent)
        elif is_parent:
            obj_instance = command_class(unique_name)
            self._set_current_parent(obj_instance)
        else:
            obj_instance = command_class(unique_name)

        return obj_instance


rpd = RulesetProjectDescription()
rpd.selected_models = [f"../test/example/CHR HOSP.bdl"]
rpd.generate_rpd()
