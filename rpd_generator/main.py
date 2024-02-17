from rpd_generator.ruleset_project_description import RulesetProjectDescription
from rpd_generator.ruleset_model_description import RulesetModelDescription
from rpd_generator.building_segment import BuildingSegment
from rpd_generator.building import Building
from doe2_file_readers.model_input_reader import ModelInputReader
from rpd_generator.bdl_structure import *
import json
import os

"""Once development is complete, this can be replaced with a list of all bdl_command attribute values from classes that 
inherit from BaseNode or BaseDefinition. Each class will also need a priority attribute in this case.
For now, this is a list of BDL commands that are ready to be processed, in the order they should be processed."""
COMMAND_PROCESSING_ORDER = [
    "RUN-PERIOD-PD",
    "SITE-PARAMETERS",
    "MASTER-METERS",
    "FUEL-METER",
    "ELEC-METER",
    "STEAM-METER",
    "CHW-METER",
    "MATERIAL",
    "CONSTRUCTION",
    "SCHEDULE-PD",
    "BOILER",
    "CHILLER",
    "DW-HEATER",
    "HEAT-REJECTION",
    "PUMP",
    "CIRCULATION-LOOP",
    "FLOOR",
    "SYSTEM",
    "ZONE",
    "SPACE",
    "EXTERIOR-WALL",
    "INTERIOR-WALL",
    "UNDERGROUND-WALL",
    "WINDOW",
    "DOOR",
]


def generate_rpd_json(selected_models):
    """
    Generate the RMDs, use Default Building and Building Segment, and write to JSON without GUI inputs
    """
    rmds, json_file_path = generate_rmds(selected_models)
    rpd, json_file_path = generate_rpd(rmds, json_file_path)
    write_rpd_json(rpd, json_file_path)


def generate_rmds(selected_models):
    """
    Generate the RPD data structure (RulesetProjectDescription, RulesetModelDescription, Building, BuildingSegment,
    and all data groups available from doe2_file_readers)
    """
    # Set the output directory to the directory of the first selected model
    output_dir = os.path.dirname(selected_models[0])

    # Get the base file name from the first selected model and replace its extension with .json
    base_file_name = os.path.basename(selected_models[0])
    json_file_name = os.path.splitext(base_file_name)[0] + ".json"

    # Construct the full path to the new JSON file in the same directory as model_path
    json_file_path = os.path.join(output_dir, json_file_name)

    rmds = []
    # Iterate through each selected model, creating a RulesetModelDescription for each
    for model_path in selected_models:
        rmd = RulesetModelDescription(os.path.splitext(os.path.basename(model_path))[0])

        # Set up default building and building segment
        default_building = Building("Default Building")
        default_building_segment = BuildingSegment(
            "Default Building Segment", default_building
        )
        rmd.bdl_obj_instances["Default Building"] = default_building
        rmd.bdl_obj_instances["Default Building Segment"] = default_building_segment

        # get all BDL commands from the BDL input file
        bdl_input_reader = ModelInputReader()
        file_bdl_commands = bdl_input_reader.read_input_bdl_file(model_path)

        # Process each data group in the order specified in COMMAND_PROCESSING_ORDER
        for command in COMMAND_PROCESSING_ORDER:
            special_handling = {}
            if command == "ZONE":
                special_handling["ZONE"] = (
                    lambda obj, cmd_dict: rmd.space_map.setdefault(
                        cmd_dict["SPACE"], obj
                    )
                )
            # Process the command group by creating object instances and populating the rmd object instance dictionary
            _process_command_group(
                command,
                file_bdl_commands,
                rmd,
                special_handling,
            )
        rmds.append(rmd)
    return rmds, json_file_path


def generate_rpd(rmds, json_file_path):
    rpd = RulesetProjectDescription()
    for rmd in rmds:
        rmd.bdl_obj_instances["ASHRAE 229"] = rpd
        # Once all objects have been created, populate data elements
        for obj_instance in rmd.bdl_obj_instances.values():
            if isinstance(obj_instance, BaseNode) or isinstance(obj_instance, BaseDefinition):
                obj_instance.populate_data_elements()
        # Once all data elements are populated, populate the data group and insert the object into the rpd
        for obj_instance in rmd.bdl_obj_instances.values():
            if isinstance(obj_instance, BaseNode):
                obj_instance.populate_data_group()
                obj_instance.insert_to_rpd(rmd)

        # Final integration steps
        rmd.bdl_obj_instances["Default Building Segment"].populate_data_group()
        rmd.bdl_obj_instances["Default Building Segment"].insert_to_rpd()
        rmd.bdl_obj_instances["Default Building"].populate_data_group()
        rmd.bdl_obj_instances["Default Building"].insert_to_rpd(rmd)
        rmd.populate_data_group()
        rmd.insert_to_rpd(rpd)

    rpd.populate_data_group()
    return rpd, json_file_path


def write_rpd_json(rpd, json_file_path):
    # Save the JSON data to the file
    with open(json_file_path, "w") as json_file:
        json.dump(rpd.rpd_data_structure, json_file, indent=4)


def _create_obj_instance(command, command_dict, rmd):
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
    inherits_base_node = issubclass(command_class, BaseNode)

    if inherits_base_node and is_child:
        obj_instance = command_class(
            command_dict["unique_name"],
            rmd.bdl_obj_instances[command_dict["parent"]],
            rmd,
        )
    else:
        obj_instance = command_class(command_dict["unique_name"], rmd)
    return obj_instance


def _process_command_group(
    data_group,
    file_bdl_commands,
    rmd,
    special_handling=None,
):
    """
    Process the data group and create object instances for each command in the data group.
    :param data_group:
    :param file_bdl_commands:
    :param rmd:
    :param special_handling:
    :return:
    """
    for cmd_dict in file_bdl_commands.get(data_group, []):
        obj = _create_obj_instance(data_group, cmd_dict, rmd)
        if special_handling and data_group in special_handling:
            special_handling[data_group](obj, cmd_dict)
        obj.add_inputs(cmd_dict)
        rmd.bdl_obj_instances[cmd_dict["unique_name"]] = obj


generate_rpd_json(
    [
        r"C:\Users\JacksonJarboe\Documents\Development\DOE2-229RPDGenerator\test\example\INP.BDL"
    ]
)
