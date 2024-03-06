from rpd_generator.ruleset_project_description import RulesetProjectDescription
from rpd_generator.ruleset_model_description import RulesetModelDescription
from rpd_generator.building_segment import BuildingSegment
from rpd_generator.building import Building
from rpd_generator.doe2_file_readers import model_input_reader
from rpd_generator.bdl_structure import *
import json
from pathlib import Path

"""Once development is complete, this can be replaced with a list of all bdl_command attribute values from classes that 
inherit from BaseNode or BaseDefinition. Each class will also need a priority attribute in this case.
For now, this is a list of BDL commands that are ready to be processed, in the order they should be processed."""
COMMAND_PROCESSING_ORDER = [
    "RUN-PERIOD-PD",
    "SITE-PARAMETERS",
    "MASTER-METERS",  # Master meters must populate bofore other meters and before Systems, Boilers, DW-Heaters, Chillers
    "FUEL-METER",  # Meters must populate before Systems, Boilers, DW-Heaters, Chillers
    "ELEC-METER",  # Meters must populate before Systems, Boilers, DW-Heaters, Chillers
    "STEAM-METER",  # Meters must populate before Systems, Boilers, DW-Heaters, Chillers
    "CHW-METER",  # Meters must populate before Systems, Boilers, DW-Heaters, Chillers
    "FIXED-SHADE",
    "GLASS-TYPE",
    "MATERIAL",
    "CONSTRUCTION",
    "SCHEDULE-PD",
    "PUMP",  # Pumps must populate before Boiler, Chiller, Heat-Rejection, and Circulation-Loop
    "CIRCULATION-LOOP",  # Circulation loops must populate before Boiler, Chiller, DWHeater, Heat-Rejection
    "BOILER",
    "CHILLER",
    "DW-HEATER",
    "HEAT-REJECTION",
    "FLOOR",  # Floors must populate before Spaces
    "SYSTEM",  # Systems must populate before Zones
    "ZONE",  # Zones must populate before Spaces
    "SPACE",  # Spaces must populate before Surfaces
    "EXTERIOR-WALL",  # Exterior walls must populate before Windows and Doors
    "INTERIOR-WALL",  # Interior walls must populate before Windows and Doors
    "UNDERGROUND-WALL",
    "WINDOW",
    "DOOR",
]


def generate_rpd_json(selected_models, dll_path, doe2_data_path):
    """
    Generate the RMDs, use Default Building and Building Segment, and write to JSON without GUI inputs
    """
    rmds, json_file_path = generate_rmd_obj_instances(
        selected_models, dll_path, doe2_data_path
    )
    rpd, json_file_path = generate_rpd(rmds, json_file_path)
    write_rpd_json(rpd, json_file_path)


def generate_rmd_obj_instances(selected_models, dll_path, doe2_data_path):
    """
    Generate the RMD data structures (RulesetModelDescription, Building, BuildingSegment, and all BDL object instances
    from the ModelInputReader) for each selected model.
    :param selected_models: List of selected models
    :param dll_path: (str) Path to the D2Result.dll file
    :param doe2_data_path: (bytes) Path to the DOE-2 data directory

    """
    # Convert the first selected model path from str to Path and set the output directory to the directory of that model
    output_dir = Path(selected_models[0]).parent

    # Get the base file name from the first selected model and replace its extension with .json
    json_file_name = Path(selected_models[0]).with_suffix(".json").name

    # Construct the full path to the new JSON file in the same directory as model_path
    json_file_path = output_dir / json_file_name

    rmds = []
    # Iterate through each selected model, creating a RulesetModelDescription for each
    for model_path_str in selected_models:
        model_path = Path(model_path_str)
        rmd = RulesetModelDescription(model_path.stem)
        rmd.dll_path = str(dll_path)  # Convert Path objects to strings if necessary
        rmd.doe2_data_path = doe2_data_path
        rmd.file_path = str(
            model_path.with_suffix("")
        )  # Convert to string and remove extension

        # Set up default building and building segment
        default_building = Building("Default Building", rmd)
        default_building_segment = BuildingSegment(
            "Default Building Segment", default_building
        )
        rmd.bdl_obj_instances["Default Building"] = default_building
        rmd.bdl_obj_instances["Default Building Segment"] = default_building_segment

        # get all BDL commands from the BDL input file
        bdl_input_reader = model_input_reader.ModelInputReader()
        file_bdl_commands = bdl_input_reader.read_input_bdl_file(
            str(model_path)
        )  # Convert Path to string

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
    return rmds, str(json_file_path)


def generate_rpd(rmds, json_file_path):
    rpd = RulesetProjectDescription()
    for rmd in rmds:

        rmd.bdl_obj_instances["ASHRAE 229"] = rpd

        # Once all objects have been created, populate data elements
        for obj_instance in rmd.bdl_obj_instances.values():
            if isinstance(obj_instance, BaseNode) or isinstance(
                obj_instance, BaseDefinition
            ):
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
    ],
    r"C:\Program Files (x86)\eQUEST 3-65-7175\D2Result.dll",
    r"C:\\Users\\JacksonJarboe\\Documents\\eQUEST 3-65-7175 Data\\DOE23\\",
)
