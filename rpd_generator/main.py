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

        # Define data groups and their processing containers
        data_group_mappings = [
            (
                [
                    "MATERIAL",
                    "CONSTRUCTION",
                    "SCHEDULE-PD",
                    "FLOOR",
                    "BOILER",
                    "CHILLER",
                    "DW-HEATER",
                    "HEAT-REJECTION",
                    "PUMP",
                    "CIRCULATION-LOOP",
                ],
                rmd,
            ),
            (["SYSTEM", "ZONE"], building_segment),
            (
                [
                    "SPACE",
                    "EXTERIOR-WALL",
                    "INTERIOR-WALL",
                    "UNDERGROUND-WALL",
                    "WINDOW",
                    "DOOR",
                ],
                rmd,
            ),
        ]

        # Process each data group according to its container
        for data_groups, container in data_group_mappings:
            for data_group in data_groups:
                special_handling = {}
                skip_methods = False

                if data_group == "ZONE":
                    special_handling["ZONE"] = (
                        lambda obj, cmd_dict: rmd.space_map.setdefault(
                            cmd_dict["SPACE"], obj
                        )
                    )

                elif data_group == "FLOOR":
                    skip_methods = True

                _process_data_group(
                    data_group,
                    file_bdl_commands,
                    container,
                    rmd.bdl_obj_instances,
                    special_handling,
                    skip_methods,
                )

        # Final integration steps
        building_segment.populate_data_group()
        building_segment.insert_to_rpd(building)
        building.populate_data_group()
        building.insert_to_rpd(rmd)
        rmd.populate_data_group()

        # Output the RMD data structure
        print(json.dumps(rmd.rmd_data_structure, indent=4))

    # fill/replace data with data from the simulation output
    # fill/replace data with data from the GUI inputs


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
    is_child = command in [
        "SPACE",
        "EXTERIOR-WALL",
        "INTERIOR-WALL",
        "UNDERGROUND-WALL",
        "ZONE",
        "WINDOW",
        "DOOR",
    ]
    if is_child:
        obj_instance = command_class(
            command_dict["unique_name"], obj_instance_dict[command_dict["parent"]]
        )
    else:
        obj_instance = command_class(command_dict["unique_name"])
    return obj_instance


def _process_data_group(
    data_group,
    file_bdl_commands,
    container,
    obj_instances,
    special_handling=None,
    skip_methods=False,
):
    for cmd_dict in file_bdl_commands.get(data_group, []):
        obj = _create_obj_instance(data_group, cmd_dict, obj_instances)
        if special_handling and data_group in special_handling:
            special_handling[data_group](obj, cmd_dict)
        obj.add_inputs(cmd_dict)
        obj_instances[cmd_dict["unique_name"]] = obj
        if not skip_methods:
            obj.populate_data_group()
            obj.insert_to_rpd(container)


generate_rpd(
    [
        r"C:\Users\JacksonJarboe\Documents\Development\DOE2-229RPDGenerator\test\example\INP.BDL"
    ]
)
