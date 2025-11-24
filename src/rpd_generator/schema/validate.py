import json
from pathlib import Path
import jsonschema

from rpd_generator.config import Config
from rpd_generator.utilities.jsonpath_utils import find_all, find_all_by_jsonpaths

file_dir = Path(__file__).parent

SCHEMA_FILENAME = Config.ACTIVE_RULESET.SCHEMA_FILENAME
SCHEMA_ENUM_FILENAME = Config.ACTIVE_RULESET.enum_schema_filename
SCHEMA_OUTPUT_FILENAME = Config.ACTIVE_RULESET.output_schema_filename
SCHEMA_PATH = file_dir / SCHEMA_FILENAME
SCHEMA_ENUM_PATH = file_dir / SCHEMA_ENUM_FILENAME
SCHEMA_OUTPUT_PATH = file_dir / SCHEMA_OUTPUT_FILENAME


def check_fluid_loop_association(rpd: dict) -> list:
    mismatch_list = []

    fluid_loop_id_jsonpaths = [
        "$.ruleset_model_descriptions[*].fluid_loops[*].id",
        "$.ruleset_model_descriptions[*].fluid_loops[*].child_loops[*].id",
    ]

    fluid_reference_jsonpaths = [
        "$.ruleset_model_descriptions[*].chillers[*].cooling_loop",
        "$.ruleset_model_descriptions[*].chillers[*].condensing_loop",
        "$.ruleset_model_descriptions[*].chillers[*].heat_recovery_loop",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*].heating_system.hot_water_loop",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*].heating_system.water_source_heat_pump_loop",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*].cooling_system.chilled_water_loop",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*].cooling_system.condenser_water_loop",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].spaces[*].miscellaneous_equipment[*].energy_from_loop",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].spaces[*].miscellaneous_equipment[*].remaining_fraction_to_loop",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].terminals[*].cooling_from_loop",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].terminals[*].heating_from_loop",
        "$.ruleset_model_descriptions[*].service_water_heating_equipment[*].hot_water_loop",
        "$.ruleset_model_descriptions[*].heat_rejections[*].loop",
        "$.ruleset_model_descriptions[*].boilers[*].loop",
        "$.ruleset_model_descriptions[*].service_water_heating_equipment[*].hot_water_loop",
        "$.ruleset_model_descriptions[*].external_fluid_sources[*].loop",
    ]

    fluid_loop_id_list = find_all_by_jsonpaths(fluid_loop_id_jsonpaths, rpd)

    referenced_id_list = find_all_by_jsonpaths(
        fluid_reference_jsonpaths,
        rpd,
    )

    for fluid_loop_id in referenced_id_list:
        if fluid_loop_id not in fluid_loop_id_list:
            mismatch_list.append(fluid_loop_id)

    return mismatch_list


def check_zone_association(rpd: dict) -> list:
    mismatch_list = []
    zone_reference_jsonpaths = [
        "$.ruleset_model_descriptions[*].buildings[*].elevators[*].motor_location_zone",
        "$.ruleset_model_descriptions[*].buildings[*].elevators[*].cab_location_zone",
        "$.ruleset_model_descriptions[*].buildings[*].refrigerated_cases[*].zone",
        "$.ruleset_model_descriptions[*].service_water_heating_equipment[*].compressor_zone",
        "$.ruleset_model_descriptions[*].service_water_heating_equipment[*].compressor_heat_rejection_zone",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].zonal_exhaust_fan.motor_location_zone",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].terminals[*].fan.motor_location_zone",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*].fan_system.supply_fans[*].motor_location_zone",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*].fan_system.return_fans[*].motor_location_zone",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*].fan_system.relief_fans[*].motor_location_zone",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*].fan_system.exhaust_fans[*].motor_location_zone",
        "$.ruleset_model_descriptions[*].service_water_heating_equipment[*].tank.location_zone",
        "$.ruleset_model_descriptions[*].service_water_heating_equipment[*].solar_thermal_systems[*].tank.location_zone",
        "$.ruleset_model_descriptions[*].service_water_heating_distribution_systems[*].tanks[*].location_zone",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].surfaces[*].adjacent_zone",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].transfer_airflow_source_zone",
        "$.ruleset_model_descriptions[*].service_water_heating_distribution_systems[*].service_water_piping[*].location_zone",
    ]
    zone_id_list = find_all(
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].id",
        rpd,
    )
    referenced_id_list = find_all_by_jsonpaths(zone_reference_jsonpaths, rpd)

    for zone_id in referenced_id_list:
        if zone_id not in zone_id_list:
            mismatch_list.append(zone_id)
    return mismatch_list


def check_schedule_association(rpd: dict) -> list:
    mismatch_list = []

    schedule_id_list = find_all("$.ruleset_model_descriptions[*].schedules[*].id", rpd)
    schedule_reference_jsonpaths = [
        "$.ruleset_model_descriptions[*].buildings[*].elevators[*].cab_motor_multiplier_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].elevators[*].cab_ventilation_fan_multiplier_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].elevators[*].cab_lighting_multiplier_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].refrigerated_cases[*].power_multiplier_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].exterior_lighting[*].multiplier_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].infiltration.multiplier_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].thermostat_cooling_setpoint_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].thermostat_heating_setpoint_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].minimum_humidity_setpoint_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].maximum_humidity_setpoint_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].exhaust_airflow_rate_multiplier_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].spaces[*].occupant_multiplier_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].spaces[*].interior_lighting[*].lighting_multiplier_schedule",
        "$.ruleset_model_descriptions[*].service_water_heating_distribution_systems[*].flow_multiplier_schedule",
        "$.ruleset_model_descriptions[*].service_water_heating_distribution_systems[*].entering_water_mains_temperature_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].spaces[*].service_water_heating_uses[*].use_multiplier_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].building_open_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].terminals[*].minimum_outdoor_airflow_multiplier_schedule",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].spaces[*].miscellaneous_equipment[*].multiplier_schedule",
        "$.ruleset_model_descriptions[*].fluid_loops[*].cooling_or_condensing_design_and_control.operation_schedule",
        "$.ruleset_model_descriptions[*].fluid_loops[*].heating_design_and_control.operation_schedule",
        "$.ruleset_model_descriptions[*].fluid_loops[*].child_loops[*].cooling_or_condensing_design_and_control.operation_schedule",
        "$.ruleset_model_descriptions[*].fluid_loops[*].child_loops[*].heating_design_and_control.operation_schedule",
        "$.ruleset_model_descriptions[*].heating_ventilation_air_conditioning_systems[*].fan_system.supply_air_temperature_reset_schedule",
        "$.ruleset_model_descriptions[*].heating_ventilation_air_conditioning_systems[*].fan_system.operating_schedule",
    ]

    referenced_id_list = find_all_by_jsonpaths(schedule_reference_jsonpaths, rpd)

    for schedule_id in referenced_id_list:
        if schedule_id not in schedule_id_list:
            mismatch_list.append(schedule_id)
    return mismatch_list


def check_fluid_loop_or_piping_association(rpd: dict) -> list:
    mismatch_list = []
    fluid_loop_or_piping_id_jsonpaths = [
        "$.ruleset_model_descriptions[*].fluid_loops[*].id",
        "$.ruleset_model_descriptions[*].service_water_heating_distribution_systems[*].service_water_piping[*].id",
        "$.ruleset_model_descriptions[*].fluid_loops[*].child_loops[*].id",
    ]

    fluid_loop_or_piping_id_list = find_all_by_jsonpaths(
        fluid_loop_or_piping_id_jsonpaths, rpd
    )

    referenced_fluid_loop_or_piping_id_list = find_all(
        "$.ruleset_model_descriptions[*].pumps[*].loop_or_piping",
        rpd,
    )
    for fluid_loop_or_piping_id in referenced_fluid_loop_or_piping_id_list:
        if fluid_loop_or_piping_id not in fluid_loop_or_piping_id_list:
            mismatch_list.append(fluid_loop_or_piping_id)
    return mismatch_list


def check_service_water_heating_association(rpd: dict) -> list:
    mismatch_list = []
    service_water_heating_id_list = find_all(
        "$.ruleset_model_descriptions[*].service_water_heating_distribution_systems[*].id",
        rpd,
    )

    service_water_heating_reference_jsonpaths = [
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].spaces[*].service_water_heating_uses[*].served_by_distribution_system",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].served_by_service_water_heating_system",
        "$.ruleset_model_descriptions[*].service_water_heating_equipment[*].distribution_system",
    ]

    referenced_service_water_heating_id_list = find_all_by_jsonpaths(
        service_water_heating_reference_jsonpaths, rpd
    )

    for service_water_heating_id in referenced_service_water_heating_id_list:
        if service_water_heating_id not in service_water_heating_id_list:
            mismatch_list.append(service_water_heating_id)
    return mismatch_list


def check_hvac_association(rpd: dict) -> list:
    mismatch_list = []
    hvac_id_list = find_all(
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*].id",
        rpd,
    )
    served_by_hvac_id_list = find_all(
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].terminals[*].served_by_heating_ventilating_air_conditioning_system",
        rpd,
    )
    for hvac_id in served_by_hvac_id_list:
        if hvac_id not in hvac_id_list:
            mismatch_list.append(hvac_id)
    return mismatch_list


def check_unique_ids_in_ruleset_model_descriptions(rmd: dict) -> str:
    ruleset_model_descriptions = rmd.get("ruleset_model_descriptions", [])

    bad_paths = []
    for rmd_index, rmd in enumerate(ruleset_model_descriptions):
        paths = json_paths_to_lists(rmd)

        for list_path in paths:
            ids = find_all(list_path + "[*].id", rmd)
            if len(ids) != len(set(ids)):
                bad_path = f"ruleset_model_descriptions[{rmd_index}]{list_path[1:]}"
                bad_paths.append(bad_path)

    error_msg = f"Non-unique ids for paths: {'; '.join(bad_paths)}" if bad_paths else ""

    return error_msg


def json_paths_to_lists(val: dict | list, path="$") -> set:
    paths = set()
    if isinstance(val, dict):
        paths = json_paths_to_lists_from_dict(val, path)
    elif isinstance(val, list):
        paths = json_paths_to_lists_from_list(val, path)

    return paths


def json_paths_to_lists_from_dict(rmd: dict, path: str) -> set:
    paths = set()
    for key, val in rmd.items():
        new_path = f"{path}.{key}"
        new_paths = json_paths_to_lists(val, new_path)
        paths = paths.union(new_paths)

    return paths


def json_paths_to_lists_from_list(rmd_list: list, path: str) -> list:
    paths = {path}
    for rmd in rmd_list:
        new_path = f"{path}[*]"
        new_paths = json_paths_to_lists(rmd, new_path)
        paths = paths.union(new_paths)

    return paths


def non_schema_validate_rmd(rmd_obj):
    error = []
    unique_id_error = check_unique_ids_in_ruleset_model_descriptions(rmd_obj)
    passed = not unique_id_error
    if not passed:
        error.append(unique_id_error)

    mismatch_hvac_errors = check_hvac_association(rmd_obj)
    passed = passed and not mismatch_hvac_errors
    if mismatch_hvac_errors:
        error.append(
            f"Cannot find HVAC systems {mismatch_hvac_errors} in the HeatingVentilationAirConditioningSystems data group."
        )

    mismatch_zone_errors = check_zone_association(rmd_obj)
    passed = passed and not mismatch_zone_errors
    if mismatch_zone_errors:
        error.append(
            f"Cannot find zones {mismatch_zone_errors} in the Zone data group."
        )

    mismatch_fluid_loop_errors = check_fluid_loop_association(rmd_obj)
    passed = passed and not mismatch_fluid_loop_errors
    if mismatch_fluid_loop_errors:
        error.append(
            f"Cannot find fluid loop {mismatch_fluid_loop_errors} in the FluidLoop data group."
        )

    mismatch_schedule_errors = check_schedule_association(rmd_obj)
    passed = passed and not mismatch_schedule_errors
    if mismatch_schedule_errors:
        error.append(
            f"Cannot find schedule {mismatch_schedule_errors} in the Schedule data group."
        )

    mismatch_fluid_loop_piping_errors = check_fluid_loop_or_piping_association(rmd_obj)
    passed = passed and not mismatch_fluid_loop_piping_errors
    if mismatch_fluid_loop_piping_errors:
        error.append(
            f"Cannot find piping {mismatch_fluid_loop_piping_errors} in the FluidLoop or ServiceWaterHeatingDistributionSystems data group."
        )

    mismatch_service_water_heating_errors = check_service_water_heating_association(
        rmd_obj
    )
    passed = passed and not mismatch_service_water_heating_errors
    if mismatch_service_water_heating_errors:
        error.append(
            f"Cannot find service water heating {mismatch_service_water_heating_errors} in the ServiceWaterHeatingDistributionSystems data group."
        )

    return {"passed": passed, "error": error if error else None}


def schema_validate_rmd(rmd_obj):
    with open(SCHEMA_PATH) as json_file:
        schema = json.load(json_file)
    with open(SCHEMA_ENUM_PATH) as json_file:
        schema_enum = json.load(json_file)
    with open(SCHEMA_OUTPUT_PATH) as json_file:
        schema_output = json.load(json_file)

    schema_map = {
        SCHEMA_FILENAME: schema,
        SCHEMA_ENUM_FILENAME: schema_enum,
        SCHEMA_OUTPUT_FILENAME: schema_output,
    }
    resolver = jsonschema.RefResolver.from_schema(schema, store=schema_map)

    validator = jsonschema.validators.validator_for(schema)
    validator = validator(schema, resolver=resolver)

    try:
        validator.validate(rmd_obj)
        return {"passed": True, "error": None}
    except jsonschema.exceptions.ValidationError as err:
        return {"passed": False, "error": "schema invalid: " + err.message}


def validate_rmd(rmd_obj, test=False):
    result = schema_validate_rmd(rmd_obj)

    if result["passed"] and not test:
        result = non_schema_validate_rmd(rmd_obj)

    return result
