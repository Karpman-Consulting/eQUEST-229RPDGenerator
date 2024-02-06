from rpd_generator.ruleset_project_description import RulesetProjectDescription
from rpd_generator.ruleset_model_description import RulesetModelDescription
from rpd_generator.building_segment import BuildingSegment
from rpd_generator.building import Building
import doe2_file_readers
from rpd_generator.bdl_structure import *
import json


def generate_rpd(selected_models):
    """
    Generate the RPD data structure (RulesetProjectDescription, RulesetModelDescription, Building, BuildingSegment,
    and all data groups available from doe2_file_readers)
    """
    rpd = RulesetProjectDescription()
    for model in selected_models:
        rmd = RulesetModelDescription("Test RMD")
        building = Building("Test Building")
        building_segment = BuildingSegment("Test Building Segment")
        bdl_input_reader = doe2_file_readers.model_input_reader.ModelInputReader()


        # get all BDL commands from the BDL input file
        file_bdl_commands = bdl_input_reader.read_input_bdl_file(model)

        rmd_data_groups = ["PUMP", "DW-HEATER", "BOILER", "CHILLER", "HEAT-REJECTION", "DW-HEATER", "CIRCULATION-LOOP"]
        # Retrieve commands for the current equipment type
        for data_group in rmd_data_groups:
            # Retrieve commands for the current equipment type
            for cmd_dict in file_bdl_commands.get(data_group, []):
                # Create object instance for the current equipment type
                obj = _create_obj_instance(data_group, cmd_dict, rmd.bdl_obj_instances)
                # Add inputs and populate data
                obj.add_inputs(cmd_dict)
                rmd.bdl_obj_instances[cmd_dict["unique_name"]] = obj
                obj.populate_data_group()
                obj.insert_to_rpd(rmd)

        b_segment_data_groups = ["SYSTEM", "ZONE"]
        # Retrieve commands for the current equipment type
        for data_group in b_segment_data_groups:
            # Retrieve commands for the current equipment type
            for cmd_dict in file_bdl_commands.get(data_group, []):
                # Create object instance for the current equipment type
                obj = _create_obj_instance(data_group, cmd_dict, rmd.bdl_obj_instances)
                if data_group == "ZONE":
                    rmd.space_map[cmd_dict["SPACE"]] = obj
                # Add inputs and populate data
                obj.add_inputs(cmd_dict)
                rmd.bdl_obj_instances[cmd_dict["unique_name"]] = obj
                obj.populate_data_group()
                obj.insert_to_rpd(building_segment)
        building_segment.populate_data_group()
        building_segment.insert_to_rpd(building)

        for cmd_dict in file_bdl_commands.get("FLOOR", []):
            obj = _create_obj_instance("FLOOR", cmd_dict, rmd.bdl_obj_instances)
            obj.add_inputs(cmd_dict)
            rmd.bdl_obj_instances[cmd_dict["unique_name"]] = obj

        zone_data_groups = ["SPACE", "EXTERIOR-WALL", "INTERIOR-WALL", "UNDERGROUND-WALL", "WINDOW", "DOOR"]
        # Retrieve commands for the current equipment type
        for data_group in zone_data_groups:
            # Retrieve commands for the current equipment type
            for cmd_dict in file_bdl_commands.get(data_group, []):
                # Create object instance for the current equipment type
                obj = _create_obj_instance(data_group, cmd_dict, rmd.bdl_obj_instances)
                # Add inputs and populate data
                obj.add_inputs(cmd_dict)
                rmd.bdl_obj_instances[cmd_dict["unique_name"]] = obj
                obj.populate_data_group()
                obj.insert_to_rpd(rmd)

        building.populate_data_group()
        building.insert_to_rpd(rmd)
        rmd.populate_data_group()
        print(json.dumps(rmd.rmd_data_structure, indent=4))


        # iterate through the objects
        # for cmd, lst in file_bdl_commands.items():
        #     for cmd_dict in lst:
        #
        #         obj.add_inputs(cmd_dict)
        #         obj_instance_dict[cmd_dict["unique_name"]] = obj
        # try:
        #     obj.populate_data_elements()
        # except AttributeError:
        #     print(f"populate_data_elements method not yet written for {obj.__class__.__name__}")
        # try:
        #     obj.populate_data_group()
        # except AttributeError:
        #     print(f"populate_data_group method does not apply to {obj.__class__.__name__}")

        # push the rmd object to the rpd list of rmds
        # self.ruleset_model_descriptions.append(rmd.rmd_data_structure)
        # print(rmd.rmd_data_structure)

    # fill/replace data with data from the simulation output
    # fill/replace data with data from the GUI inputs
    # call each object's populate_data_group method


def _create_obj_instance(command, command_dict, obj_instance_dict):
    """
    Create an object instance based on the command type. This is needed to determine the arguments to pass to the
    __init__ methods of each class. Any object with a parent needs to know which parent it belongs to in the model.
    Objects without parents have no parent object passed.

    :param command_dict: Unique name for the instance.
    :param command: BDL command.
    :return: object: Created object instance.
    """
    command_class = RulesetProjectDescription.bdl_command_dict[command]
    is_child = command in ["SPACE", "EXTERIOR-WALL", "INTERIOR-WALL", "UNDERGROUND-WALL", "ZONE", "WINDOW", "DOOR"]
    if is_child:
        obj_instance = command_class(command_dict["unique_name"], obj_instance_dict[command_dict["parent"]])
    else:
        obj_instance = command_class(command_dict["unique_name"])
    return obj_instance


generate_rpd([r"C:\Users\JacksonJarboe\Documents\Development\DOE2-229RPDGenerator\test\example\INP.BDL"])
