import os
import sys
import json
import tempfile
from pathlib import Path
from tempfile import TemporaryDirectory

from rpd_generator.config import Config
from rpd_generator.artifacts.ruleset_project_description import (
    RulesetProjectDescription,
)
from rpd_generator.artifacts.ruleset_model_description import RulesetModelDescription
from rpd_generator.doe2_worker.api import process_inp
from rpd_generator.doe2_file_io.prepare_inp_for_rpd import prepare_inp
from rpd_generator.doe2_file_io.copy_to_temp import copy_files_to_temp_dir
from rpd_generator.doe2_file_io.model_input_reader import ModelInputReader
from rpd_generator.bdl_structure import *
from rpd_generator.utilities import validate_configuration
from rpd_generator.utilities import unit_converter
from rpd_generator.utilities import ensure_valid_rpd


def write_rpd_json_from_inps(project_name: str, inp_path_specs: list):
    """
    This function allows files and model types to be specified together to generate RPD JSON file without the GUI.
    inp_path_specs may contain:
        "no_type_model.inp"
        ("proposed_model.inp", "PROPOSED")
        ("baseline_model.inp", "BASELINE_0")
    :param project_name:
    :param inp_path_specs:
    :return:
    """
    normalized = [
        (
            (Path(spec[0]), spec[1])
            if isinstance(spec, (tuple, list))
            else (Path(spec), None)
        )
        for spec in inp_path_specs
    ]

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        bdl_paths = []
        rmd_types = []

        for inp_path, rmd_type in normalized:
            temp_inp = Path(prepare_inp(inp_path, tmp))
            copy_files_to_temp_dir(inp_path, tmp)

            bdl_path = temp_inp.with_suffix(".BDL")

            process_inp(
                bdlcio_dll=str(Path(Config.EQUEST_INSTALL_PATH) / "Bdlcio32.dll"),
                doe2_data_dir=str(Path(Config.DOE23_DATA_PATH) / "DOE23") + "\\",
                work_dir=str(temp_inp.parent) + "\\",
                file_name=temp_inp.name,
            )

            bdl_paths.append(str(bdl_path))
            rmd_types.append(rmd_type)

        rpd = RulesetProjectDescription(project_name)
        rpd.populate_data_elements()

        rmds = generate_rmd_objects_from_bdls(rpd, ModelInputReader(), bdl_paths)
        for rmd, rmd_type in zip(rmds, rmd_types):
            if rmd_type:
                rmd.type = rmd_type
            rmd.populate_rmd_data()

        # determine output directory
        proposed = next((p for p, t in normalized if t == "PROPOSED"), normalized[0][0])
        output_path = proposed.parent / f"{project_name}.rpd"

        finalize_and_write_rpd(rpd, output_path)


def write_rpd_json_from_bdls(
    project_name: str,
    bdl_path_strs: list[str],
    rpd_file_path: str,
    rpd_testing: bool = False,
):
    """
    Generate RPD JSON file from commented BDL files that have already been created.
    :param project_name:
    :param bdl_path_strs:
    :param rpd_file_path:
    :param rpd_testing: bool
    :return:
    """
    bdl_input_reader = ModelInputReader()
    rpd = RulesetProjectDescription(project_name)
    rpd.populate_data_elements()

    rmds = generate_rmd_objects_from_bdls(rpd, bdl_input_reader, bdl_path_strs)
    for rmd in rmds:
        rmd.populate_rmd_data()

    finalize_and_write_rpd(rpd, rpd_file_path, rpd_testing=rpd_testing)


def write_rpd_json_from_rpd(
    rpd: RulesetProjectDescription,
    rmds: list[RulesetModelDescription],
    rpd_file_path: str,
):
    """
    Generate RPD JSON file from RPD and RMD objects. Called from GUI.
    :param rpd:
    :param rmds:
    :param rpd_file_path:
    :return:
    """
    for rmd in rmds:
        rmd.populate_all_data_groups()
        rmd.insert_all_to_rpd()

    finalize_and_write_rpd(rpd, rpd_file_path)


def safe_path(path):
    # Only modify the path on Windows
    if sys.platform.startswith("win"):
        abs_path = os.path.abspath(path)
        if not abs_path.startswith("\\\\?\\"):
            abs_path = "\\\\?\\" + abs_path
        return abs_path
    return path


def generate_rmd_objects_from_bdls(
    rpd: RulesetProjectDescription,
    bdl_input_reader: ModelInputReader,
    selected_models: list[str],
) -> list[RulesetModelDescription]:
    """
    Generate RMD objects from BDL files. Called during multistep processing.
    :param rpd:
    :param bdl_input_reader:
    :param selected_models:
    :return:
    """
    rmds = []
    for model_path_str in selected_models:
        model_path = Path(model_path_str)
        rmd = RulesetModelDescription(model_path.stem, rpd)
        rmd.file_path = str(model_path.with_suffix(""))

        model_input_data = bdl_input_reader.read_input_bdl_file(str(model_path))
        rmd.doe2_version = model_input_data["doe2_version"]
        if rmd.doe2_version is not None:
            rmd.doe2_data_path = (
                Config.DOE23_DATA_PATH
                if rmd.doe2_version.split("-")[1] == "2.3"
                else Config.DOE22_DATA_PATH
            )

        for command in rmd.COMMAND_PROCESSING_ORDER:
            command_class = bdl_input_reader.bdl_command_dict[command]
            special_handling = {}
            if command == "ZONE":
                special_handling[
                    "ZONE"
                ] = lambda obj, cmd_dict, u_name: rmd.space_map.setdefault(
                    cmd_dict["SPACE"], obj
                )
            if command == "SPACE":
                special_handling["SPACE"] = lambda obj, cmd_dict, u_name: setattr(
                    rmd.space_map[u_name], "space", obj
                )
            _process_command_group(
                command,
                model_input_data["file_commands"],
                command_class,
                rmd,
                special_handling,
            )
        rmds.append(rmd)
    return rmds


def generate_rmd_objects_from_inps(
    rpd, inp_path_strs: list[str], processing_dir: TemporaryDirectory
) -> list[RulesetModelDescription]:
    """
    Generate RMD objects from INP files. Called from GUI to process inp before calling generate_rmd_objects_from_bdls.
    :param rpd:
    :param inp_path_strs:
    :param processing_dir:
    :return:
    """
    temp_dir = Path(processing_dir.name)

    doe23_path = Path(Config.DOE23_DATA_PATH) / "DOE23"
    bdlcio32_path = Path(Config.EQUEST_INSTALL_PATH) / "Bdlcio32.dll"

    bdl_paths = []

    for inp_path_str in inp_path_strs:
        inp_path = Path(inp_path_str)

        # Prepare the inp file and copy to temp
        temp_inp_path = Path(prepare_inp(inp_path, temp_dir))
        copy_files_to_temp_dir(inp_path, temp_dir)

        # Define BDL path
        bdl_path = temp_inp_path.with_suffix(".BDL")

        # Process the inp file to generate the BDL
        process_inp(
            bdlcio_dll=str(bdlcio32_path),
            doe2_data_dir=str(doe23_path) + "\\",
            work_dir=str(temp_inp_path.parent) + "\\",
            file_name=temp_inp_path.name,
        )

        bdl_paths.append(str(bdl_path))

    # Generate RMDs for all BDLs at once
    bdl_input_reader = ModelInputReader()
    rmds = generate_rmd_objects_from_bdls(rpd, bdl_input_reader, bdl_paths)

    return rmds


def finalize_and_write_rpd(
    rpd: RulesetProjectDescription, rpd_file_path: str, rpd_testing: bool = False
):
    """
    Finalize RPD object and write to JSON file.
    :param rpd:
    :param rpd_file_path:
    :param rpd_testing: bool
    :return:
    """
    print("Populating RPD data group...")
    rpd.populate_data_group()
    print("Finalizing RPD data structure...")
    ensure_valid_rpd.make_ids_unique(rpd.rpd_data_structure)
    print("Converting units to schema units...")
    unit_converter.convert_to_schema_units(rpd.rpd_data_structure)
    if not rpd_testing:
        print("Adding supply ducting specifications...")
        rpd.specify_supply_ducting()

    safe_file = safe_path(rpd_file_path)
    with open(safe_file, "w") as f:
        json.dump(rpd.rpd_data_structure, f, indent=4)

    print(f"RPD JSON file created at: {safe_file}")


def _create_obj_instance(u_name, command, command_dict, command_class, rmd):
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
            u_name,
            rmd.bdl_obj_instances[command_dict["parent"]],
            rmd,
        )
    else:
        obj_instance = command_class(u_name, rmd)
    return obj_instance


def _process_command_group(
    command_group: str,
    file_bdl_commands: dict,
    cmd_class,
    rmd: RulesetModelDescription,
    special_handling=None,
):
    for u_name in file_bdl_commands.get(command_group, {}):
        cmd_dict = file_bdl_commands[command_group][u_name]
        obj = _create_obj_instance(u_name, command_group, cmd_dict, cmd_class, rmd)
        if special_handling and command_group in special_handling:
            special_handling[command_group](obj, cmd_dict, u_name)
        obj.add_inputs(cmd_dict)
        rmd.bdl_obj_instances[u_name] = obj


if __name__ == "__main__":
    # Test generating an RPD JSON file from one of the test BDL files
    validate_configuration.find_equest_installation()
    write_rpd_json_from_inps(
        "245 Clarkson Ave",
        [
            (
                r"C:\Users\JacksonJarboe\Karpman Consulting Dropbox\Jackson Jarboe\Test Project\Project 3.inp",
                "BASELINE_0",
            ),
            (
                r"C:\Users\JacksonJarboe\Karpman Consulting Dropbox\Jackson Jarboe\Test Project\Project 3.inp",
                "PROPOSED",
            ),
        ],
    )
    # write_rpd_json_from_bdls(
    #     str(
    #         Path(__file__).parents[1]
    #         / "test"
    #         / "full_rpd_test"
    #         / "E-1"
    #         / "229 Test Case E-1 (PSZHP).BDL"
    #     ),
    #     str(
    #         Path(__file__).parents[1]
    #         / "test"
    #         / "full_rpd_test"
    #         / "E-1"
    #         / "229 Test Case E-1 (PSZHP).json"
    #     ),
    # )
